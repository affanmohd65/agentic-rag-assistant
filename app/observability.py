"""
Observability and monitoring using Langfuse + OpenTelemetry.
Tracks latency, tokens, errors, and user behavior.
"""
import os
import time
import json
from typing import Any, Optional
from datetime import datetime
import uuid

from langfuse import Langfuse
from langfuse.decorators import langfuse_context, observe
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from loguru import logger


# ===== Langfuse Setup =====
LANGFUSE_ENABLED = os.getenv("LANGFUSE_ENABLED", "false").lower() == "true"
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")

langfuse_client = None
if LANGFUSE_ENABLED and LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY:
    langfuse_client = Langfuse(
        public_key=LANGFUSE_PUBLIC_KEY,
        secret_key=LANGFUSE_SECRET_KEY,
        base_url=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
    )
    logger.info("Langfuse enabled")
else:
    logger.info("Langfuse disabled (set LANGFUSE_ENABLED=true and provide API keys)")


# ===== OpenTelemetry Setup =====
def init_opentelemetry():
    """Initialize OpenTelemetry tracing and metrics."""
    # Jaeger exporter for distributed tracing
    jaeger_exporter = JaegerExporter(
        agent_host_name=os.getenv("JAEGER_HOST", "localhost"),
        agent_port=int(os.getenv("JAEGER_PORT", 6831)),
    )
    
    trace_provider = TracerProvider()
    trace_provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
    trace.set_tracer_provider(trace_provider)
    
    # Prometheus for metrics
    prometheus_reader = PrometheusMetricReader()
    meter_provider = MeterProvider(metric_readers=[prometheus_reader])
    metrics.set_meter_provider(meter_provider)
    
    # Auto-instrumentation
    RequestsInstrumentor().instrument()
    SQLAlchemyInstrumentor().instrument()
    
    logger.info("OpenTelemetry initialized with Jaeger and Prometheus")
    return trace.get_tracer(__name__), meter_provider.get_meter(__name__)


try:
    tracer, meter = init_opentelemetry()
except Exception as e:
    logger.warning(f"OpenTelemetry initialization failed: {e}")
    tracer = None
    meter = None


# ===== Monitoring Classes =====

class QueryObserver:
    """Track query metrics and performance."""
    
    def __init__(self, query_id: str, query: str):
        self.query_id = query_id
        self.query = query
        self.start_time = time.time()
        self.metadata = {
            "query_id": query_id,
            "query": query,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def log_to_langfuse(self, result: dict, model: str, tokens: int, error: Optional[str] = None):
        """Log query to Langfuse."""
        if not langfuse_client:
            return
        
        try:
            langfuse_client.trace(
                name="agent_query",
                input={"query": self.query},
                output={"answer": result.get("final_answer", "")},
                metadata=self.metadata,
                tags=["agent", model],
            )
            
            # Log generation event
            langfuse_client.generation(
                name="query_generation",
                input=self.query,
                output=result.get("final_answer", ""),
                model=model,
                usage={
                    "input_tokens": tokens // 2,  # Estimate
                    "output_tokens": tokens // 2
                },
                metadata=self.metadata
            )
            
            if error:
                langfuse_client.event(
                    name="query_error",
                    input=self.query,
                    output=error,
                    level="error"
                )
        except Exception as e:
            logger.warning(f"Langfuse logging failed: {e}")
    
    def log_to_opentelemetry(self, result: dict, model: str, tokens: int):
        """Log metrics to OpenTelemetry."""
        if not tracer or not meter:
            return
        
        try:
            # Create span
            with tracer.start_as_current_span("query_execution") as span:
                latency = (time.time() - self.start_time) * 1000  # ms
                
                span.set_attribute("query", self.query)
                span.set_attribute("model", model)
                span.set_attribute("tokens", tokens)
                span.set_attribute("latency_ms", latency)
                
                # Record metrics
                query_counter = meter.create_counter(
                    name="queries_total",
                    description="Total queries processed"
                )
                query_counter.add(1, {"model": model})
                
                latency_histogram = meter.create_histogram(
                    name="query_latency_ms",
                    description="Query latency in milliseconds"
                )
                latency_histogram.record(latency, {"model": model})
                
                token_counter = meter.create_counter(
                    name="tokens_total",
                    description="Total tokens used"
                )
                token_counter.add(tokens, {"model": model})
        except Exception as e:
            logger.warning(f"OpenTelemetry logging failed: {e}")


class PerformanceMonitor:
    """Monitor overall system performance."""
    
    def __init__(self):
        self.metrics = {
            "total_queries": 0,
            "total_latency_ms": 0,
            "total_tokens": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "errors": 0
        }
    
    def record_query(self, latency_ms: float, tokens: int, cache_hit: bool, error: bool = False):
        """Record query metrics."""
        self.metrics["total_queries"] += 1
        self.metrics["total_latency_ms"] += latency_ms
        self.metrics["total_tokens"] += tokens
        
        if cache_hit:
            self.metrics["cache_hits"] += 1
        else:
            self.metrics["cache_misses"] += 1
        
        if error:
            self.metrics["errors"] += 1
    
    def get_stats(self) -> dict:
        """Get aggregated statistics."""
        total_queries = self.metrics["total_queries"]
        if total_queries == 0:
            return self.metrics
        
        return {
            **self.metrics,
            "avg_latency_ms": self.metrics["total_latency_ms"] / total_queries,
            "avg_tokens": self.metrics["total_tokens"] / total_queries,
            "cache_hit_rate": self.metrics["cache_hits"] / total_queries,
            "error_rate": self.metrics["errors"] / total_queries
        }
    
    def log_stats(self):
        """Log statistics to logger."""
        stats = self.get_stats()
        logger.info(f"Performance Stats: {json.dumps(stats, indent=2)}")


class EvaluationLogger:
    """Log RAGAS evaluation scores."""
    
    @staticmethod
    def log_evaluation(query: str, response: str, contexts: list, scores: dict):
        """Log evaluation results to database."""
        from app.database import SessionLocal, EvaluationScore
        
        try:
            db = SessionLocal()
            eval_entry = EvaluationScore(
                id=str(uuid.uuid4()),
                query=query,
                response=response,
                retrieved_contexts=contexts,
                faithfulness=scores.get("faithfulness", 0),
                answer_relevancy=scores.get("answer_relevancy", 0),
                context_recall=scores.get("context_recall", 0),
                context_precision=scores.get("context_precision", 0),
                model_used=scores.get("model", "unknown")
            )
            db.add(eval_entry)
            db.commit()
            logger.info(f"Evaluation logged: {eval_entry.id}")
        except Exception as e:
            logger.error(f"Evaluation logging failed: {e}")
        finally:
            db.close()


# Global instances
_performance_monitor = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get or initialize performance monitor."""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


def create_query_observer(query: str) -> QueryObserver:
    """Create a new query observer."""
    return QueryObserver(str(uuid.uuid4()), query)
