from app.core.agentic_layer.agents.base_agent import BaseAgent
from app.core.agentic_layer.agent_registry import register_agent
from langchain_ollama import OllamaLLM  # Ollama integration


@register_agent("ollama")
class OllamaAgent(BaseAgent):
    def __init__(self, model="llama2", memory=None):
        super().__init__(name="ollama", model=model, memory=memory)
        self.llm = OllamaLLM(model=model)

    def run(self, message: str) -> str:
        return self.llm.invoke(message)
