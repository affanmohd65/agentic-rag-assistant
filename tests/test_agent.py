from app.agent import AgenticRAGAssistant
from app.llm_client import GroqClient, MockLLMClient, get_llm_client

def test_agent_answers_directly_for_plain_question():
    agent = AgenticRAGAssistant(llm_client=MockLLMClient())
    state = agent.run("hello there")
    assert state.final_answer is not None

def test_agent_uses_calculator_tool_for_math():
    agent = AgenticRAGAssistant(llm_client=MockLLMClient())
    state = agent.run("calculate 2 + 2")
    assert any("calculator" in h for h in state.history)


def test_groq_provider_is_selected_when_configured(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "groq")
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    monkeypatch.setattr(GroqClient, "__init__", lambda self, api_key: None)

    assert isinstance(get_llm_client(), GroqClient)
