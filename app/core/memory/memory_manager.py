# app/memory/memory_mana.py

from langchain.memory import ConversationBufferMemory
from app.memory.conversation_store import load_conversation, save_conversation

class PersistentMemory:
    def __init__(self, user_id: str, session_id: str):
        self.user_id = user_id
        self.session_id = session_id
        self.memory = ConversationBufferMemory(return_messages=True)
        self._load_from_store()

    def _load_from_store(self):
        history = load_conversation(self.user_id, self.session_id)
        for turn in history:
            self.memory.chat_memory.add_user_message(turn["user"])
            self.memory.chat_memory.add_ai_message(turn["assistant"])

    def save(self):
        messages = []
        for pair in self.memory.chat_memory.messages:
            if pair.type == "human":
                user_msg = pair.content
            elif pair.type == "ai":
                assistant_msg = pair.content
                messages.append({"user": user_msg, "assistant": assistant_msg})
        save_conversation(self.user_id, self.session_id, messages)

    def get_memory(self):
        return self.memory
