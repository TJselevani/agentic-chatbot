from langchain_classic.memory import ConversationBufferMemory


class ConversationManager:
    def __init__(self):
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    def update(self, user_input: str, bot_output: str):
        """Add messages to memory."""
        self.memory.chat_memory.add_user_message(user_input)
        self.memory.chat_memory.add_ai_message(bot_output)

    def get_context(self):
        """Retrieve full conversation history."""
        return self.memory.load_memory_variables({})["chat_history"]
