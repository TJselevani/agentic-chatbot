from app.core.agentic_layer.agents.base_agent import BaseAgent
from app.core.agentic_layer.agent_registry import register_agent
from langchain_openai import ChatOpenAI  # Replace with GROK SDK if available


@register_agent("grok")
class GrokAgent(BaseAgent):
    def __init__(self, model="grok", memory=None):
        super().__init__(name="grok",model=model, memory=memory)
        # Example: using OpenAI wrapper until GROK SDK is available
        self.llm = ChatOpenAI(model=model, temperature=0.5)
        self.memory = memory

    def run(self, message: str):
        return self.llm.invoke(message)

    def get_llm(self):
        from app.core.agentic_layer.llm_wrappers import BaseLLMWrapper
        return BaseLLMWrapper(agent=self)
