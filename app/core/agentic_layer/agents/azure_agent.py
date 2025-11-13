import os
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

from app.core.agentic_layer.agents.base_agent import BaseAgent
from app.core.agentic_layer.agent_registry import register_agent


@register_agent("azure")
class AzureAgent(BaseAgent):
    def __init__(self, model="openai/gpt-4o", memory=None):
        super().__init__(name="azure", model=model, memory=memory)

        # Environment token
        self.token = os.environ.get("GITHUB_TOKEN")
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
