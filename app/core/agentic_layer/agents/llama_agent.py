from llama_cpp import Llama

from app.core.agentic_layer.agent_registry import register_agent
from app.core.agentic_layer.agents.base_agent import BaseAgent


@register_agent("local_llama")
class LocalLlamaAgent(BaseAgent):
    def __init__(self, model_path="models/llama-3-8b.gguf", memory=None):
        super().__init__("local_llama", model_path, memory=memory)

        self.llm = Llama(
            model_path=model_path,
            n_ctx=4096,
            chat_format="llama-3"
        )

    def run(self, message: str):
        output = self.llm.create_chat_completion(
            messages=[{"role": "user", "content": message}]
        )
        return output["choices"][0]["message"]["content"]

    def get_llm(self):
        from app.core.agentic_layer.llm_wrappers import BaseLLMWrapper
        return BaseLLMWrapper(agent=self)
