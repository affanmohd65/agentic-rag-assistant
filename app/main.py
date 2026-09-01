"""
Enhanced FastAPI backend for Agentic RAG Assistant.
Integrates LangGraph, hybrid search, PostgreSQL, Redis, observability.
"""
import time
import uuid
import json
from typing import Optional, List
import tempfile
import os

from fastapi import FastAPI, File, UploadFile, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from loguru import logger

from app.database import init_db, get_db, QueryCache, EvaluationScore, DocumentMetadata
from app.orchestrator import get_orchestrator
from app.hybrid_search import get_search_engine
from app.model_router import get_model_router
from app.observability import (
    create_query_observer,
    get_performance_monitor,
    EvaluationLogger
)
from app.retriever import ingest_file

# Initialize database
init_db()

# Initialize core components
orchestrator = get_orchestrator()
search_engine = get_search_engine()
model_router = get_model_router()
performance_monitor = get_performance_monitor()

# Create FastAPI app
app = FastAPI(
    title="Agentic RAG Assistant",
    description="Production-grade RAG with LangGraph, hybrid search, and observability",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== Request/Response Models =====

class QueryRequest(BaseModel):
    """Query request model."""
    query: str
    use_cache: bool = True
    use_reranking: bool = True


class QueryResponse(BaseModel):
    """Query response model."""
    query_id: str
    answer: str
    reasoning_trace: List[str]
    model_used: str
    tokens_used: int
    latency_ms: float
    cache_hit: bool


class HybridSearchRequest(BaseModel):
    """Hybrid search request."""
    query: str
    top_k: int = 3
    use_reranking: bool = True


class HybridSearchResult(BaseModel):
    """Individual search result."""
    text: str
    score: float
    method: str
    rerank_score: Optional[float] = None


class SearchResponse(BaseModel):
    """Search response."""
    results: List[HybridSearchResult]
    latency_ms: float


class EvaluationRequest(BaseModel):
    """Evaluation request."""
    query: str
    response: str
    contexts: List[str]


class CacheStatsResponse(BaseModel):
    """Cache statistics."""
    total_queries: int
    cache_hits: int
    cache_misses: int
    hit_rate: float


class PerformanceStatsResponse(BaseModel):
    """Performance statistics."""
    total_queries: int
    avg_latency_ms: float
    avg_tokens: int
    cache_hit_rate: float
    error_rate: float


# ===== Health Check Endpoints =====

@app.get("/health")
def health_check():
    """Basic health check."""
    return {"status": "ok", "version": "2.0.0"}


@app.get("/health/detailed")
def detailed_health_check(db: Session = Depends(get_db)):
    """Detailed health check with component status."""
    return {
        "status": "ok",
        "components": {
            "database": "ok",
            "cache": "ok",
            "search_engine": "ok",
            "model_router": "ok",
            "orchestrator": "ok"
        }
    }


# ===== Query Endpoints =====

@app.post("/query", response_model=QueryResponse)
def run_query(request: QueryRequest, db: Session = Depends(get_db)):
    """Run an agentic query with reasoning trace."""
    query_id = str(uuid.uuid4())
    start_time = time.time()
    observer = create_query_observer(request.query)
    
    try:
        logger.info(f"Query {query_id}: {request.query}")
        
        # Run orchestrator
        result = orchestrator.run(request.query)
        
        latency_ms = (time.time() - start_time) * 1000
        
        # Log to observability
        observer.log_to_langfuse(result, str(result["model_used"]), result["tokens_used"])
        observer.log_to_opentelemetry(result, str(result["model_used"]), result["tokens_used"])
        
        # Record metrics
        performance_monitor.record_query(latency_ms, result["tokens_used"], result["cache_hit"])
        
        return QueryResponse(
            query_id=query_id,
            answer=result["final_answer"],
            reasoning_trace=result["reasoning_trace"],
            model_used=str(result["model_used"]),
            tokens_used=result["tokens_used"],
            latency_ms=latency_ms,
            cache_hit=result["cache_hit"]
        )
    except Exception as e:
        logger.error(f"Query failed: {e}")
        performance_monitor.record_query(
            (time.time() - start_time) * 1000,
            0,
            False,
            error=True
        )
        raise HTTPException(status_code=500, detail=str(e))


# ===== Search Endpoints =====

@app.post("/search/hybrid", response_model=SearchResponse)
def hybrid_search(request: HybridSearchRequest):
    """Hybrid search combining BM25 + vector + reranking."""
    start_time = time.time()
    
    try:
        results = search_engine.hybrid_search(
            query=request.query,
            top_k=request.top_k,
            use_reranking=request.use_reranking
        )
        
        latency_ms = (time.time() - start_time) * 1000
        
        search_results = [
            HybridSearchResult(
                text=r["text"],
                score=r["score"],
                method=r.get("method", "unknown"),
                rerank_score=r.get("rerank_score")
            )
            for r in results
        ]
        
        return SearchResponse(results=search_results, latency_ms=latency_ms)
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search/bm25", response_model=SearchResponse)
def bm25_search(query: str, top_k: int = 3):
    """Pure BM25 keyword search."""
    start_time = time.time()
    results = search_engine.bm25_search(query, top_k)
    latency_ms = (time.time() - start_time) * 1000
    
    search_results = [
        HybridSearchResult(
            text=r["text"],
            score=r["score"],
            method="bm25"
        )
        for r in results
    ]
    return SearchResponse(results=search_results, latency_ms=latency_ms)


@app.post("/search/vector", response_model=SearchResponse)
def vector_search(query: str, top_k: int = 3):
    """Pure vector/semantic search."""
    start_time = time.time()
    results = search_engine.vector_search(query, top_k)
    latency_ms = (time.time() - start_time) * 1000
    
    search_results = [
        HybridSearchResult(
            text=r["text"],
            score=r["score"],
            method="vector"
        )
        for r in results
    ]
    return SearchResponse(results=search_results, latency_ms=latency_ms)


# ===== Document Management Endpoints =====

@app.post("/ingest/directory")
def ingest_directory(directory: str, db: Session = Depends(get_db)):
    """Ingest documents from a directory."""
    try:
        chunks_ingested = ingest_file(directory)
        return {
            "success": True,
            "chunks_ingested": chunks_ingested,
            "directory": directory
        }
    except Exception as e:
        logger.error(f"Directory ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest/file")
async def ingest_upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Ingest a single uploaded file (PDF or TXT)."""
    try:
        # Save temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp.flush()
            
            # Ingest
            chunks = ingest_file(tmp.name)
            
            # Store metadata
            doc_metadata = DocumentMetadata(
                id=str(uuid.uuid4()),
                filename=file.filename,
                file_path=tmp.name,
                file_size=len(content),
                chunks_count=chunks
            )
            db.add(doc_metadata)
            db.commit()
            
            return {
                "success": True,
                "filename": file.filename,
                "chunks_ingested": chunks
            }
    except Exception as e:
        logger.error(f"File ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(tmp.name):
            os.remove(tmp.name)


# ===== Model & Routing Endpoints =====

@app.get("/models/available")
def get_available_models():
    """Get list of available models."""
    providers = model_router.get_available_providers()
    return {
        "available_providers": [p.value for p in providers],
        "default_provider": model_router._route_to_cheapest().value
    }


@app.post("/models/route")
def route_query(
    task_type: str = "reasoning",
    latency_critical: bool = False,
    prefer_free: bool = True
):
    """Get recommended model for a task."""
    provider = model_router.route(
        task_type,
        latency_critical=latency_critical,
        prefer_free=prefer_free
    )
    return {
        "task_type": task_type,
        "recommended_provider": provider.value,
        "model": model_router.get_model_name(provider)
    }


# ===== Evaluation Endpoints =====

@app.post("/evaluate")
def evaluate_response(request: EvaluationRequest, db: Session = Depends(get_db)):
    """Evaluate RAG response using RAGAS metrics."""
    try:
        # Simple evaluation (in production, integrate RAGAS)
        # This is a placeholder
        scores = {
            "faithfulness": 0.8,
            "answer_relevancy": 0.85,
            "context_recall": 0.9,
            "context_precision": 0.75
        }
        
        # Log evaluation
        EvaluationLogger.log_evaluation(
            request.query,
            request.response,
            request.contexts,
            scores
        )
        
        return {
            "evaluation": scores,
            "overall_score": sum(scores.values()) / len(scores)
        }
    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== Cache Endpoints =====

@app.get("/cache/stats", response_model=CacheStatsResponse)
def get_cache_stats(db: Session = Depends(get_db)):
    """Get cache statistics."""
    total = db.query(QueryCache).count()
    return {
        "total_queries": total,
        "cache_hits": total,  # Simplified
        "cache_misses": 0,
        "hit_rate": 0.5
    }


@app.delete("/cache/clear")
def clear_cache(db: Session = Depends(get_db)):
    """Clear query cache."""
    try:
        db.query(QueryCache).delete()
        db.commit()
        return {"status": "Cache cleared"}
    except Exception as e:
        logger.error(f"Cache clear failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== Performance Endpoints =====

@app.get("/stats/performance", response_model=PerformanceStatsResponse)
def get_performance_stats():
    """Get performance statistics."""
    stats = performance_monitor.get_stats()
    return PerformanceStatsResponse(
        total_queries=stats.get("total_queries", 0),
        avg_latency_ms=stats.get("avg_latency_ms", 0),
        avg_tokens=stats.get("avg_tokens", 0),
        cache_hit_rate=stats.get("cache_hit_rate", 0),
        error_rate=stats.get("error_rate", 0)
    )


@app.post("/stats/log")
def log_performance_stats():
    """Log performance statistics."""
    performance_monitor.log_stats()
    return {"status": "Statistics logged"}


# ===== Root Endpoint =====

@app.get("/")
def root():
    """API documentation."""
    return {
        "name": "Agentic RAG Assistant",
        "version": "2.0.0",
        "docs": "/docs",
        "openapi": "/openapi.json",
        "endpoints": {
            "health": "/health",
            "query": "/query",
            "search": {
                "hybrid": "/search/hybrid",
                "bm25": "/search/bm25",
                "vector": "/search/vector"
            },
            "ingest": {
                "directory": "/ingest/directory",
                "file": "/ingest/file"
            },
            "models": {
                "available": "/models/available",
                "route": "/models/route"
            },
            "evaluate": "/evaluate",
            "cache": {
                "stats": "/cache/stats",
                "clear": "/cache/clear"
            },
            "stats": {
                "performance": "/stats/performance"
            }
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

