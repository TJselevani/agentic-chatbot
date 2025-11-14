from app.core.agentic_layer.agents.base_agent import BaseAgent
from app.core.intent_layer.intent_classifier import get_intent
from app.core.agentic_layer.agent_registry import register_agent


@register_agent("PyTorch")
class IntentAgent(BaseAgent):
    def __init__(self, model=None, memory=None):
        super().__init__(name="PyTorch", model=model, memory=memory)
    """A simple wrapper around your PyTorch intent classifier."""

    def run(self, message: str):
        intent = get_intent(message)
        return f"🧠 Classified intent: {intent}"

    def get_llm(self):
        from app.core.agentic_layer.llm_wrappers import BaseLLMWrapper
        return BaseLLMWrapper(agent=self)
