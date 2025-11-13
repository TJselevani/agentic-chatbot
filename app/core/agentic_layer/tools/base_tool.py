from abc import ABC, abstractmethod
from langchain_core.tools import BaseTool


class ReusableTool(BaseTool, ABC):
    """
    Base interface for reusable tools.
    """

    name: str = "base_tool"
    description: str = "Base reusable tool"

    @abstractmethod
    def _run(self, *args, **kwargs) -> str:
        """Concrete tools must implement this."""
        pass

    async def _arun(self, *args, **kwargs) -> str:
        """Optional async version."""
        raise NotImplementedError("Async not implemented.")
