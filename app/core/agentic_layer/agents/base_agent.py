# app/core/agentic_layer/agents/base_agent.py
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List


class BaseAgent(ABC):
    """
    Abstract base class for all AI agents.
    Defines the interface that all agents must implement.
    """

    def __init__(
            self,
            name: str = "base_agent",
            model: str = "default",
            memory: Optional[Any] = None
    ):
        self.name = name
        self.model = model
        self.memory = memory
        self.conversation_history: List[Dict[str, str]] = []

    @abstractmethod
    def run(self, message: str, **kwargs) -> str:
        """
        Process a message and return a response.
        This must be implemented by all concrete agents.
        """
        pass

    def add_to_history(self, role: str, content: str):
        """Add message to conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": content
        })

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []

    def get_history(self, last_n: Optional[int] = None) -> List[Dict[str, str]]:
        """Get conversation history"""
        if last_n:
            return self.conversation_history[-last_n:]
        return self.conversation_history

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name}, model={self.model})"