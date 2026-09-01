"""
Minimal agentic loop: LLM decides whether to call a tool (retriever /
calculator) or answer directly, tool result is fed back in, loop repeats
up to max_steps. This is the same core pattern LangGraph implements with
more machinery — this version is dependency-light and easy to explain
in an interview.
"""
from dataclasses import dataclass, field
from app.llm_client import get_llm_client
from app.tools import calculator
from app.retriever import retrieve


@dataclass
class AgentState:
    query: str
    history: list[str] = field(default_factory=list)
    final_answer: str | None = None


class AgenticRAGAssistant:
    def __init__(self, llm_client=None, max_steps: int = 3):
        self.llm = llm_client or get_llm_client()
        self.max_steps = max_steps

    def run(self, query: str) -> AgentState:
        state = AgentState(query=query)
        prompt = query
        for step in range(self.max_steps):
            response = self.llm.complete(prompt, tools=[{}])  # tools flag: allow tool use
            if response.tool_call is None:
                state.final_answer = response.text
                state.history.append(f"step {step}: answered directly")
                break

            name = response.tool_call["name"]
            args = response.tool_call["arguments"]
            if name == "calculator":
                result = calculator(args["expression"])
                state.history.append(f"step {step}: called calculator({args['expression']}) -> {result}")
                prompt = f"Tool result: {result}. Original question: {query}. Give the final answer."
            elif name == "retriever":
                chunks = retrieve(args["query"])
                context = "\n".join(c["text"] for c in chunks) or "(no relevant documents found)"
                state.history.append(f"step {step}: retrieved {len(chunks)} chunk(s)")
                prompt = f"Context:\n{context}\n\nQuestion: {query}\nAnswer using the context."
            else:
                state.final_answer = "unknown tool requested"
                break
        else:
            state.final_answer = state.final_answer or "max steps reached without a final answer"

        if state.final_answer is None:
            final = self.llm.complete(prompt, tools=None)
            state.final_answer = final.text
        return state
