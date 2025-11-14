import os
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

from app.config import settings
from app.core.agentic_layer.agents.base_agent import BaseAgent
from app.core.agentic_layer.agent_registry import register_agent


@register_agent("azure")
class AzureAgent(BaseAgent):
    def __init__(self, model="openai/gpt-4o", memory=None):
        super().__init__(name="azure", model=model, memory=memory)

        # Environment token
        self.token = settings.GITHUB_KEY
        self.endpoint = "https://models.github.ai/inference"

        # Azure client
        self.client = ChatCompletionsClient(
            endpoint=self.endpoint,
            credential=AzureKeyCredential(self.token),
        )

    def run(self, message: str) -> str:
        """Send a message to the Azure inference endpoint"""
        response = self.client.complete(
            messages=[
                SystemMessage("You are a helpful assistant."),
                UserMessage(message),
            ],
            model=self.model,
        )
        return response.choices[0].message.content

    def get_llm(self):
        from app.core.agentic_layer.llm_wrappers import BaseLLMWrapper
        return BaseLLMWrapper(agent=self)

    def get_llm2(self):
        """
        Returns a LangChain-compatible LLM that uses AzureAgent internally.
        """
        from langchain_core.language_models.chat_models import BaseChatModel
        from langchain_core.messages import AIMessage
        from langchain_core.outputs import ChatGeneration, ChatResult

        class AzureLangChainWrapper(BaseChatModel):

            def __init__(self, azure_agent):
                self.azure_agent = azure_agent

            @property
            def _llm_type(self) -> str:
                return "azure_custom"

            def _generate(self, messages, stop=None, **kwargs) -> ChatResult:
                # Extract last user message
                user_message = messages[-1].content

                # Use your Azure agent to generate output
                text = self.azure_agent.run(user_message)

                # Wrap the string into LangChain message objects
                ai_msg = AIMessage(content=text)

                generation = ChatGeneration(message=ai_msg)

                return ChatResult(generations=[generation])

        return AzureLangChainWrapper(self)
