# app/core/agentic_layer/agents/base_agent.py
from abc import ABC, abstractmethod

class BaseAgent(ABC):
    """
    Abstract base class for all agents.
    Provides a consistent interface and optional memory handling.
    """

    def __init__(self, name: str, model: str = None, memory=None):
        self.name = name
        self.model = model
        self.memory = memory

    @abstractmethod
    def run(self, message: str) -> str:
        """
        Run the agent with a user message.
        Must be implemented by subclasses.
        """
        pass

    def __repr__(self):
        return f"<Agent name={self.name}, model={self.model}>"
