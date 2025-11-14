from langchain_core.messages import AIMessage

from app.core.agentic_layer.agents.base_agent import BaseAgent
from app.core.agentic_layer.agent_registry import register_agent
from langchain_anthropic import ChatAnthropic  # Anthropic Claude integration


@register_agent("claude")
class ClaudeAgent(BaseAgent):
    def __init__(self, model="claude-3-opus", memory=None):
        super().__init__(name="claude", model=model, memory=memory)
        self.llm = ChatAnthropic(
            model=model,  # "claude-haiku-4-5-20251001",
            temperature=0,
            max_tokens=1024,
            timeout=None,
            max_retries=2,
        )

    def run(self, message: str) -> AIMessage:
        return self.llm.invoke(message)

    def get_llm(self):
        from app.core.agentic_layer.llm_wrappers import BaseLLMWrapper
        return BaseLLMWrapper(agent=self)
