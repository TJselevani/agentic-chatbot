from app.core.agentic_layer.agents.base_agent import BaseAgent
from app.core.agentic_layer.agent_registry import register_agent
from langchain_openai import ChatOpenAI  # Replace with DeepSeek SDK if available


@register_agent("deepseek")
class DeepSeekAgent(BaseAgent):
    def __init__(self, model="deepseek-chat", memory=None):
        super().__init__(name="deepseek", model=model, memory=memory)
        self.llm = ChatOpenAI(model=model, temperature=0.5)
        self.memory = memory

    def run(self, message: str):
        return self.llm.invoke(message)
