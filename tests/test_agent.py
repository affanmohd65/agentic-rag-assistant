from app.agent import AgenticRAGAssistant
from app.llm_client import MockLLMClient

def test_agent_answers_directly_for_plain_question():
    agent = AgenticRAGAssistant(llm_client=MockLLMClient())
    state = agent.run("hello there")
    assert state.final_answer is not None

def test_agent_uses_calculator_tool_for_math():
    agent = AgenticRAGAssistant(llm_client=MockLLMClient())
    state = agent.run("calculate 2 + 2")
    assert any("calculator" in h for h in state.history)
