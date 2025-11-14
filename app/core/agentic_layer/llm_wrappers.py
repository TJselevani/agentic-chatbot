from typing import Any
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from pydantic import Field, SkipValidation


class BaseLLMWrapper(BaseChatModel):
    """
    A universal LangChain-compatible wrapper for any custom LLM agent.
    Each agent must expose a `.run(text)` method.
    """

    agent: SkipValidation[Any] = Field(...)  # Declare agent as a Pydantic field

    class Config:
        arbitrary_types_allowed = True  # Allow non-pydantic types

    @property
    def _llm_type(self) -> str:
        return f"{self.agent.name}_wrapper"

    def _generate(self, messages, stop=None, **kwargs) -> ChatResult:
        user_message = messages[-1].content

        # Call the custom agent
        text = self.agent.run(user_message)

        ai_msg = AIMessage(content=text)
        generation = ChatGeneration(message=ai_msg)

        return ChatResult(generations=[generation])
