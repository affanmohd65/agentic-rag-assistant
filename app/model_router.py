"""
Model Router: Intelligent selection of LLM based on task type, latency requirements, and cost.
Routes queries to Ollama (free, local), Groq (free API tier), or Claude (premium).
"""
import os
from typing import Literal
from enum import Enum
from loguru import logger


class ModelProvider(str, Enum):
    """Available model providers."""
    OLLAMA = "ollama"      # Local, free
    GROQ = "groq"          # API, free tier
    CLAUDE = "claude"      # Paid, high quality
    GPT4 = "gpt4"          # Paid, high quality


class ModelRouter:
    """Route queries to appropriate LLM based on requirements."""
    
    # Model capabilities and costs (latency ms, tokens/1M)
    MODELS = {
        ModelProvider.OLLAMA: {
            "models": ["mistral", "neural-chat", "orca-mini"],
            "latency": 200,      # Fast, local
            "cost": 0,           # Free
            "quality": "medium",
            "local": True
        },
        ModelProvider.GROQ: {
            "models": ["mixtral-8x7b-32768", "llama-70b-8192"],
            "latency": 50,       # Very fast
            "cost": 0,           # Free tier
            "quality": "high",
            "local": False
        },
        ModelProvider.CLAUDE: {
            "models": ["claude-3-sonnet", "claude-3-haiku"],
            "latency": 100,
            "cost": 0.003,       # $3 per 1M tokens (input)
            "quality": "very_high",
            "local": False
        },
        ModelProvider.GPT4: {
            "models": ["gpt-4-turbo", "gpt-4o"],
            "latency": 150,
            "cost": 0.01,        # $10 per 1M tokens (input)
            "quality": "very_high",
            "local": False
        }
    }
    
    def __init__(self):
        self.ollama_available = self._check_ollama()
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.claude_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.gpt4_api_key = os.getenv("OPENAI_API_KEY")
        
        logger.info(f"Model Router initialized:")
        logger.info(f"  - Ollama available: {self.ollama_available}")
        logger.info(f"  - Groq API key: {'set' if self.groq_api_key else 'not set'}")
        logger.info(f"  - Claude API key: {'set' if self.claude_api_key else 'not set'}")
        logger.info(f"  - GPT-4 API key: {'set' if self.gpt4_api_key else 'not set'}")

    def _check_ollama(self) -> bool:
        """Check if Ollama is running locally."""
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            return response.status_code == 200
        except Exception:
            return False

    def route(
        self,
        task_type: Literal["calculation", "retrieval", "reasoning", "summary"],
        token_budget: int = 500,
        latency_critical: bool = False,
        prefer_free: bool = True
    ) -> str:
        """
        Route query to best model.
        
        Args:
            task_type: Type of task (calculation/retrieval/reasoning/summary)
            token_budget: Maximum tokens to spend
            latency_critical: If True, prefer faster models
            prefer_free: If True, prefer free models
        
        Returns:
            Model provider name
        """
        # Task-specific routing
        if task_type == "calculation":
            # Calculations work fine with any model, use cheapest
            return self._route_to_cheapest()
        
        elif task_type == "retrieval":
            # Retrieval doesn't need complex reasoning, use fast/cheap
            if latency_critical:
                return ModelProvider.GROQ if self.groq_api_key else ModelProvider.OLLAMA
            return self._route_to_cheapest()
        
        elif task_type == "reasoning":
            # Complex reasoning benefits from better models
            if not prefer_free:
                if self.claude_api_key:
                    return ModelProvider.CLAUDE
                if self.gpt4_api_key:
                    return ModelProvider.GPT4
            
            # Fall back to free options
            if self.groq_api_key:
                return ModelProvider.GROQ
            return ModelProvider.OLLAMA if self.ollama_available else ModelProvider.GROQ
        
        elif task_type == "summary":
            # Summaries benefit from better models
            if not prefer_free and self.claude_api_key:
                return ModelProvider.CLAUDE
            if self.groq_api_key:
                return ModelProvider.GROQ
            return ModelProvider.OLLAMA if self.ollama_available else ModelProvider.GROQ
        
        # Default routing
        return self._route_to_cheapest()

    def _route_to_cheapest(self) -> str:
        """Route to cheapest available option."""
        # Priority: Ollama (free) > Groq (free) > Claude/GPT4 (paid)
        if self.ollama_available:
            return ModelProvider.OLLAMA
        if self.groq_api_key:
            return ModelProvider.GROQ
        if self.claude_api_key:
            return ModelProvider.CLAUDE
        if self.gpt4_api_key:
            return ModelProvider.GPT4
        return ModelProvider.OLLAMA  # Default fallback

    def get_model_name(self, provider: ModelProvider) -> str:
        """Get default model name for provider."""
        return self.MODELS[provider]["models"][0]

    def get_available_providers(self) -> list[ModelProvider]:
        """Get list of currently available providers."""
        available = []
        if self.ollama_available:
            available.append(ModelProvider.OLLAMA)
        if self.groq_api_key:
            available.append(ModelProvider.GROQ)
        if self.claude_api_key:
            available.append(ModelProvider.CLAUDE)
        if self.gpt4_api_key:
            available.append(ModelProvider.GPT4)
        return available


# Global instance
_router = None


def get_model_router() -> ModelRouter:
    """Get or initialize the model router."""
    global _router
    if _router is None:
        _router = ModelRouter()
    return _router
