from langchain.tools import BaseTool
from typing import Any

class ReusableTool(BaseTool):
    """
    Base class for reusable agent tools.
    """

    def _run(self, *args, **kwargs) -> Any:
        raise NotImplementedError("Tool must implement the _run method.")

    async def _arun(self, *args, **kwargs) -> Any:
        raise NotImplementedError("Async version not implemented.")
