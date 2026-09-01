"""
LLM client abstraction.

Supports OpenAI, Anthropic, or a deterministic "mock" mode so the whole
app runs and is fully testable without any API key or network access.
This is the pattern real production systems use to keep CI cheap and fast.
"""
import os
from dataclasses import dataclass


@dataclass
class LLMResponse:
    text: str
    tool_call: dict | None = None


class BaseLLMClient:
    def complete(self, prompt: str, tools: list[dict] | None = None) -> LLMResponse:
        raise NotImplementedError


class MockLLMClient(BaseLLMClient):
    """
    Deterministic stand-in LLM used for local dev, tests, and CI.
    Very small rule set: if the prompt mentions numbers/math, call the
    calculator tool; otherwise call the retriever tool; otherwise answer
    directly. This is intentionally simple — swap in OpenAIClient /
    AnthropicClient for real generation.
    """

    def complete(self, prompt: str, tools: list[dict] | None = None) -> LLMResponse:
        lower = prompt.lower()
        # Once a tool result has already been folded back into the prompt
        # (either "Tool result:" or "Context:"), answer directly instead
        # of calling the same tool again — mirrors how a real LLM stops
        # tool-calling once it has enough information.
        if lower.startswith("tool result:") or lower.startswith("context:"):
            return LLMResponse(text=_synthesize_answer(prompt))
        if tools:
            if any(ch.isdigit() for ch in prompt) and ("calculate" in lower or "+" in prompt or "*" in prompt):
                return LLMResponse(text="", tool_call={"name": "calculator", "arguments": {"expression": _extract_expression(prompt)}})
            return LLMResponse(text="", tool_call={"name": "retriever", "arguments": {"query": prompt}})
        return LLMResponse(text=f"[mock answer for]: {prompt[:120]}")


def _synthesize_answer(prompt: str) -> str:
    # Naive extractive "answer": return the retrieved context / tool result
    # verbatim, prefixed for clarity. A real LLM would synthesize a proper
    # natural-language answer from this same context.
    if "context:" in prompt.lower():
        context = prompt.split("Question:")[0].replace("Context:", "").strip()
        return f"[mock synthesized answer from retrieved context]: {context[:300]}"
    return f"[mock synthesized answer]: {prompt[:200]}"


def _extract_expression(prompt: str) -> str:
    import re
    match = re.search(r"[\d\.\s\+\-\*/\(\)]{3,}", prompt)
    return match.group(0).strip() if match else "0"


class OpenAIClient(BaseLLMClient):
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def complete(self, prompt: str, tools: list[dict] | None = None) -> LLMResponse:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        return LLMResponse(text=resp.choices[0].message.content)


class AnthropicClient(BaseLLMClient):
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-6"):
        import anthropic
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def complete(self, prompt: str, tools: list[dict] | None = None) -> LLMResponse:
        resp = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}],
        )
        return LLMResponse(text=resp.content[0].text)


def get_llm_client() -> BaseLLMClient:
    provider = os.getenv("LLM_PROVIDER", "mock").lower()
    if provider == "openai" and os.getenv("OPENAI_API_KEY"):
        return OpenAIClient(os.environ["OPENAI_API_KEY"])
    if provider == "anthropic" and os.getenv("ANTHROPIC_API_KEY"):
        return AnthropicClient(os.environ["ANTHROPIC_API_KEY"])
    return MockLLMClient()
