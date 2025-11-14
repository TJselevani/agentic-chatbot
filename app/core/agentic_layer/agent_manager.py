# app/core/agentic_layer/agent_manager.py
import logging
from typing import Optional, Dict, Any

from app.core.agentic_layer.agents.azure_agent import AzureAgent
from app.core.agentic_layer.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class AgentManager:
    """
    Manages and routes between multiple AI agents.
    Primary agent: Azure (GitHub Models API)
    """

    def __init__(self):
        self.agents: Dict[str, type] = {
            "azure": AzureAgent,
        }
        self.default_agent = "azure"
        self._agent_instances: Dict[str, BaseAgent] = {}

        logger.info(f"AgentManager initialized with agents: {list(self.agents.keys())}")

    def get_agent(self, name: Optional[str] = None) -> BaseAgent:
        """
        Retrieve a specific agent by name (singleton pattern).
        """
        name = name or self.default_agent

        if name not in self.agents:
            raise ValueError(
                f"Agent '{name}' not found. Available: {list(self.agents.keys())}"
            )

        # Return cached instance if exists
        if name in self._agent_instances:
            return self._agent_instances[name]

        # Create new instance
        agent_class = self.agents[name]
        agent_instance = agent_class()
        self._agent_instances[name] = agent_instance

        return agent_instance

    def route_by_intent(self, intent: str, message: str) -> BaseAgent:
        """
        Route to appropriate agent based on intent.
        Currently all intents use the same agent, but can be extended.
        """

        # You can add specialized agents for different intents
        # For example:
        # if intent == "technical":
        #     return self.get_agent("technical_agent")

        # For now, use default agent for all
        return self.get_agent(self.default_agent)

    def run(
            self,
            message: str,
            intent: Optional[str] = None,
            context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Route and execute message with the appropriate agent.
        """

        if intent:
            agent = self.route_by_intent(intent, message)
        else:
            agent = self.get_agent()

        logger.info(f"Routing message to agent: {agent.__class__.__name__}")

        try:
            # Add context to message if provided
            if context:
                enhanced_message = self._enhance_message_with_context(message, context)
                return agent.run(enhanced_message)
            else:
                return agent.run(message)

        except Exception as e:
            logger.error(f"Agent execution error: {e}")
            raise RuntimeError(f"Agent {agent.__class__.__name__} failed: {str(e)}")

    def _enhance_message_with_context(
            self,
            message: str,
            context: Dict[str, Any]
    ) -> str:
        """Add context to message for better agent understanding"""

        context_str = ""

        if context.get("conversation_history"):
            history = context["conversation_history"][-3:]  # Last 3 messages
            context_str += "\n\nRecent conversation:\n"
            for msg in history:
                context_str += f"- {msg['role']}: {msg['content']}\n"

        if context.get("user_info"):
            user_info = context["user_info"]
            context_str += f"\n\nUser context: {user_info}\n"

        if context.get("current_flow"):
            flow = context["current_flow"]
            context_str += f"\n\nCurrent flow: {flow}\n"

        return f"{context_str}\n\nUser message: {message}"

    def list_agents(self) -> list:
        """List all available agents"""
        return list(self.agents.keys())

    def register_agent(self, name: str, agent_class: type):
        """Dynamically register a new agent"""
        if not issubclass(agent_class, BaseAgent):
            raise TypeError(f"{agent_class} must be a subclass of BaseAgent")

        self.agents[name] = agent_class
        logger.info(f"Registered new agent: {name}")