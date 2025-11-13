# app/core/agentic_layer/agent_manager.py
import logging
from typing import Optional

from app.core.agentic_layer.agents.gpt_4o_mini import GPT4oMiniAgent
from app.core.agentic_layer.agents.intent_agent import IntentAgent
from app.core.agentic_layer.agents.azure_agent import AzureAgent

logger = logging.getLogger(__name__)


class AgentManager:
    """Manages and routes between multiple AI agents."""

    def __init__(self):
        self.agents = {
            "GPT4o": GPT4oMiniAgent,
            "intent": IntentAgent,
            "azure": AzureAgent,
        }
        self.default_agent = "langchain"
        logger.info(f"AgentManager initialized with agents: {list(self.agents.keys())}")

    def get_agent(self, name: Optional[str] = None):
        """Retrieve a specific agent by name."""
        name = name or self.default_agent
        if name not in self.agents:
            raise ValueError(
                f"Agent '{name}' not found. Available: {list(self.agents.keys())}"
            )
        return self.agents[name]()

    def route_by_intent(self, message: str):
        """Use intent classifier to route to the right agent."""
        # example: integrate your PyTorch intent classifier here
        from app.core.intent_layer.intent_classifier import get_intent

        intent = get_intent(message)

        if "book" in intent:
            return self.get_agent("langchain")
        elif "recover" in intent:
            return self.get_agent("azure")
        else:
            return self.get_agent("intent")

    def run(self, message: str):
        """Route and execute message with the appropriate agent."""
        agent = self.route_by_intent(message)
        logger.info(f"Routing message to agent: {agent.__class__.__name__}")

        if hasattr(agent, "run"):
            return agent.run(message)
        elif callable(agent):
            return agent(message)
        else:
            raise RuntimeError(f"Agent {agent} does not support .run() or call().")
