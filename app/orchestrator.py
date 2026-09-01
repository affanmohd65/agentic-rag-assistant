"""
LangGraph-based Agent Orchestrator.
Modern approach using LangGraph for complex agent workflows.
Replaces the simple agent loop with a graph-based orchestration.
"""
from typing import TypedDict, Annotated, Sequence, Optional, Any
from dataclasses import dataclass
import json
from datetime import datetime
import uuid
import ast
import operator

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from loguru import logger

from app.hybrid_search import get_search_engine
from app.model_router import get_model_router, ModelProvider
from app.llm_client import get_llm_client
from app.database import SessionLocal, QueryCache, EvaluationScore
import hashlib


# ===== State Definition =====
class AgentState(TypedDict):
    """State for the agent graph."""
    query: str
    messages: Annotated[Sequence[HumanMessage | AIMessage], operator.add]
    next_action: Optional[str]  # "calculator", "retriever", "answer", END
    intermediate_steps: list[tuple[str, str]]  # (tool_name, result)
    final_answer: str
    reasoning_trace: list[str]
    model_used: ModelProvider
    tokens_used: int
    latency_ms: float
    cache_hit: bool


@dataclass
class ToolResult:
    """Result from a tool execution."""
    tool_name: str
    output: str
    error: Optional[str] = None


# ===== Tools using @tool decorator =====

@tool
def calculator_tool(expression: str) -> str:
    """Calculate mathematical expressions safely using AST."""
    try:
        # Parse the expression
        tree = ast.parse(expression, mode="eval")
        
        # Check for safe operations only
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                return json.dumps({"error": "Function calls not allowed"})
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                return json.dumps({"error": "Imports not allowed"})
        
        # Evaluate safely
        result = eval(compile(tree, "<string>", "eval"))
        return json.dumps({"result": result})
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool
def retriever_tool(query: str, top_k: int = 3) -> str:
    """Retrieve documents from knowledge base using hybrid search."""
    try:
        search_engine = get_search_engine()
        results = search_engine.hybrid_search(query, top_k=top_k)
        
        if not results:
            return json.dumps({"documents": [], "message": "No documents found"})
        
        documents = [
            {"text": r["text"], "score": r["score"], "method": r.get("method", "unknown")}
            for r in results
        ]
        return json.dumps({"documents": documents})
    except Exception as e:
        return json.dumps({"error": str(e)})


# ===== Graph Nodes =====

class OrchestratorGraph:
    """LangGraph-based agent orchestrator."""
    
    def __init__(self, max_steps: int = 3):
        self.max_steps = max_steps
        self.model_router = get_model_router()
        self.search_engine = get_search_engine()
        self.graph = self._build_graph()
        logger.info("LangGraph orchestrator initialized")
    
    def _build_graph(self) -> StateGraph:
        """Build the agent graph."""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("router", self.route_node)
        workflow.add_node("calculator", self.calculator_node)
        workflow.add_node("retriever", self.retriever_node)
        workflow.add_node("answer", self.answer_node)
        
        # Add edges
        workflow.set_entry_point("router")
        
        workflow.add_conditional_edges(
            "router",
            lambda x: x["next_action"],
            {
                "calculator": "calculator",
                "retriever": "retriever",
                "answer": "answer"
            }
        )
        
        workflow.add_edge("calculator", "answer")
        workflow.add_edge("retriever", "answer")
        workflow.add_edge("answer", END)
        
        return workflow.compile()
    
    def route_node(self, state: AgentState) -> AgentState:
        """Route query to appropriate tool or direct answer."""
        query = state["query"]
        messages = state["messages"]
        
        # Determine task type
        if any(keyword in query.lower() for keyword in ["calculate", "compute", "what is", "+", "-", "*", "/"]):
            task_type = "calculation"
        elif any(keyword in query.lower() for keyword in ["what", "how", "tell me", "explain", "about"]):
            task_type = "reasoning"
        else:
            task_type = "retrieval"
        
        # Route to best model
        model = self.model_router.route(task_type, prefer_free=True)
        state["model_used"] = model
        
        # Decide next action based on query
        if self._is_calculation(query):
            state["next_action"] = "calculator"
            state["reasoning_trace"].append("🧮 Routing to calculator tool")
        elif self._should_retrieve(query):
            state["next_action"] = "retriever"
            state["reasoning_trace"].append("📚 Routing to document retrieval")
        else:
            state["next_action"] = "answer"
            state["reasoning_trace"].append("💡 Answering directly from knowledge")
        
        return state
    
    def calculator_node(self, state: AgentState) -> AgentState:
        """Execute calculator tool."""
        query = state["query"]
        state["reasoning_trace"].append(f"Running calculator: {query}")
        
        try:
            result = calculator_tool.invoke({"expression": query})
            result_dict = json.loads(result)
            state["intermediate_steps"].append(("calculator", json.dumps(result_dict)))
        except Exception as e:
            state["reasoning_trace"].append(f"❌ Calculator error: {str(e)}")
            state["intermediate_steps"].append(("calculator", json.dumps({"error": str(e)})))
        
        return state
    
    def retriever_node(self, state: AgentState) -> AgentState:
        """Execute retriever tool."""
        query = state["query"]
        state["reasoning_trace"].append(f"Searching documents: {query}")
        
        try:
            result = retriever_tool.invoke({"query": query})
            result_dict = json.loads(result)
            state["intermediate_steps"].append(("retriever", json.dumps(result_dict)))
            
            # Log retrieved document count
            doc_count = len(result_dict.get("documents", []))
            state["reasoning_trace"].append(f"Found {doc_count} relevant documents")
        except Exception as e:
            state["reasoning_trace"].append(f"❌ Retrieval error: {str(e)}")
            state["intermediate_steps"].append(("retriever", json.dumps({"error": str(e)})))
        
        return state
    
    def answer_node(self, state: AgentState) -> AgentState:
        """Generate final answer based on intermediate steps."""
        state["reasoning_trace"].append("🎯 Generating final answer")
        
        # Build context from intermediate steps
        context = ""
        for tool_name, result in state["intermediate_steps"]:
            context += f"\n{tool_name} result: {result}"
        
        # Simple answer generation (in production, use LLM)
        if context:
            state["final_answer"] = f"Based on the search results and tools: {context}"
        else:
            state["final_answer"] = "I don't have enough information to answer this question."
        
        return state
    
    @staticmethod
    def _is_calculation(query: str) -> bool:
        """Check if query is a calculation."""
        keywords = ["calculate", "compute", "what is", "+", "-", "*", "/", "="]
        return any(kw in query.lower() for kw in keywords)
    
    @staticmethod
    def _should_retrieve(query: str) -> bool:
        """Check if query needs document retrieval."""
        keywords = ["what", "how", "explain", "tell me", "about", "policy", "return", "information"]
        return any(kw in query.lower() for kw in keywords)
    
    def run(self, query: str) -> dict:
        """Execute the agent graph."""
        initial_state = AgentState(
            query=query,
            messages=[HumanMessage(content=query)],
            next_action=None,
            intermediate_steps=[],
            final_answer="",
            reasoning_trace=[],
            model_used=ModelProvider.OLLAMA,
            tokens_used=0,
            latency_ms=0,
            cache_hit=False
        )
        
        # Check cache first
        db = SessionLocal()
        try:
            cache_entry = db.query(QueryCache).filter(
                QueryCache.query == query
            ).first()
            
            if cache_entry:
                initial_state["cache_hit"] = True
                initial_state["final_answer"] = cache_entry.response
                initial_state["reasoning_trace"].append("✅ Retrieved from cache")
                return initial_state
        finally:
            db.close()
        
        # Run the graph
        try:
            output = self.graph.invoke(initial_state)
            
            # Cache the result
            self._cache_result(query, output)
            
            return output
        except Exception as e:
            logger.error(f"Graph execution failed: {e}")
            return initial_state
    
    def _cache_result(self, query: str, result: AgentState):
        """Cache the query result."""
        try:
            db = SessionLocal()
            cache_entry = QueryCache(
                id=str(uuid.uuid4()),
                query=query,
                response=result["final_answer"],
                reasoning_trace=result["reasoning_trace"],
                model_used=result["model_used"].value,
                latency_ms=result["latency_ms"]
            )
            db.add(cache_entry)
            db.commit()
        except Exception as e:
            logger.warning(f"Cache write failed: {e}")
        finally:
            db.close()


# Global instance
_orchestrator = None


def get_orchestrator(max_steps: int = 3) -> OrchestratorGraph:
    """Get or initialize the orchestrator."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = OrchestratorGraph(max_steps=max_steps)
    return _orchestrator
