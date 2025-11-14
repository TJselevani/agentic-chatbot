from app.core.agentic_layer.agents.base_agent import BaseAgent
from app.core.agentic_layer.agent_registry import register_agent
from app.core.rag_layer.rag_engine import RagEngine


@register_agent("rag")
class RagAgent(BaseAgent):
    """
    RAG Agent that uses another agent's LLM inside RAG.
    """

    def __init__(self, llm_agent=None, memory=None):
        super().__init__("rag", model=None, memory=memory)

        if llm_agent is None:
            raise ValueError("RagAgent requires an llm_agent.")

        self.llm_agent = llm_agent
        self.rag_engine = RagEngine(llm=self.llm_agent.get_llm())

    def run(self, message: str):
        return self.rag_engine.run(message)
