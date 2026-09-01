"""A minimal agentic loop for retrieval and calculation tasks."""
from dataclasses import dataclass, field

from app.llm_client import get_llm_client
from app.retriever import retrieve
from app.tools import calculator


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
            tools = [{}] if step == 0 else None
            response = self.llm.complete(prompt, tools=tools)
            if response.tool_call is None:
                state.final_answer = response.text
                state.history.append(f"step {step}: answered directly")
                break

            name = response.tool_call["name"]
            arguments = response.tool_call["arguments"]
            if name == "calculator":
                result = calculator(arguments["expression"])
                state.history.append(
                    f"step {step}: called calculator({arguments['expression']}) -> {result}"
                )
                prompt = f"Tool result: {result}. Original question: {query}. Give the final answer."
            elif name == "retriever":
                chunks = retrieve(arguments["query"])
                context = "\n".join(chunk["text"] for chunk in chunks) or "(no relevant documents found)"
                state.history.append(f"step {step}: retrieved {len(chunks)} chunk(s)")
                prompt = f"Context:\n{context}\n\nQuestion: {query}\nAnswer using the context."
            else:
                state.final_answer = "unknown tool requested"
                break

        if state.final_answer is None:
            final = self.llm.complete(prompt, tools=None)
            state.final_answer = final.text
        return state
