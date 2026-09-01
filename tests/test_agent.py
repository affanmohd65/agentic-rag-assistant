from app.agent import AgenticRAGAssistant
from app.llm_client import BaseLLMClient, GroqClient, LLMResponse, MockLLMClient, get_llm_client

def test_agent_answers_directly_for_plain_question():
    class DirectAnswerClient(BaseLLMClient):
        def complete(self, prompt, tools=None):
            return LLMResponse(text="Hello from the assistant.")

    agent = AgenticRAGAssistant(llm_client=DirectAnswerClient())
    state = agent.run("hello there")
    assert state.final_answer == "Hello from the assistant."

def test_agent_uses_calculator_tool_for_math():
    agent = AgenticRAGAssistant(llm_client=MockLLMClient())
    state = agent.run("calculate 2 + 2")
    assert any("calculator" in h for h in state.history)


def test_groq_provider_is_selected_when_configured(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "groq")
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    monkeypatch.setenv("GROQ_MODEL", "openai/gpt-oss-120b")
    initialized_with = {}

    def fake_init(self, api_key, model):
        initialized_with["api_key"] = api_key
        initialized_with["model"] = model

    monkeypatch.setattr(GroqClient, "__init__", fake_init)

    assert isinstance(get_llm_client(), GroqClient)
    assert initialized_with == {"api_key": "test-key", "model": "openai/gpt-oss-120b"}


def test_agent_generates_answer_after_retrieval(monkeypatch):
    class RetrievalThenAnswerClient(BaseLLMClient):
        def __init__(self):
            self.tools_arguments = []

        def complete(self, prompt, tools=None):
            self.tools_arguments.append(tools)
            if tools:
                return LLMResponse(text="", tool_call={"name": "retriever", "arguments": {"query": prompt}})
            return LLMResponse(text="A final answer based on the context.")

    monkeypatch.setattr("app.agent.retrieve", lambda query: [{"text": "Relevant context", "source": "test"}])
    client = RetrievalThenAnswerClient()
    state = AgenticRAGAssistant(llm_client=client, max_steps=1).run("What is AutoGen?")

    assert state.final_answer == "A final answer based on the context."
    assert client.tools_arguments == [[{}], None]
