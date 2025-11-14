# app/core/conversation_state.py
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import redis
from app.config import settings


@dataclass
class ConversationState:
    """Represents the state of a conversation"""

    user_id: str
    session_id: str
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)

    # Conversation history
    messages: List[Dict[str, Any]] = field(default_factory=list)

    # Multi-turn flow state
    current_flow: Optional[str] = None
    flow_step: Optional[str] = None
    flow_data: Dict[str, Any] = field(default_factory=dict)

    # User context
    user_context: Dict[str, Any] = field(default_factory=dict)

    def add_message(self, role: str, content: str, metadata: Dict = None):
        """Add a message to conversation history"""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        })
        self.last_updated = datetime.now()

    def start_flow(self, flow_name: str, initial_data: Dict = None):
        """Start a multi-turn conversation flow"""
        self.current_flow = flow_name
        self.flow_step = "initiated"
        self.flow_data = initial_data or {}
        self.last_updated = datetime.now()

    def end_flow(self):
        """End current flow"""
        self.current_flow = None
        self.flow_step = None
        self.flow_data = {}
        self.last_updated = datetime.now()

    def is_in_flow(self) -> bool:
        """Check if currently in a multi-turn flow"""
        return self.current_flow is not None

    def get_recent_messages(self, n: int = 5) -> List[Dict]:
        """Get last n messages"""
        return self.messages[-n:] if self.messages else []

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "user_id": self.user_id,
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "messages": self.messages,
            "current_flow": self.current_flow,
            "flow_step": self.flow_step,
            "flow_data": self.flow_data,
            "user_context": self.user_context,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'ConversationState':
        """Create from dictionary"""
        return cls(
            user_id=data["user_id"],
            session_id=data["session_id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            last_updated=datetime.fromisoformat(data["last_updated"]),
            messages=data.get("messages", []),
            current_flow=data.get("current_flow"),
            flow_step=data.get("flow_step"),
            flow_data=data.get("flow_data", {}),
            user_context=data.get("user_context", {}),
        )


class ConversationStateManager:
    """Manages conversation states with Redis persistence"""

    def __init__(self, redis_client: redis.Redis = None):
        self.redis_client = redis_client or self._get_redis_client()
        self.use_redis = self.redis_client is not None

        # In-memory fallback
        self.memory_store: Dict[str, ConversationState] = {}

    def _get_redis_client(self) -> Optional[redis.Redis]:
        """Initialize Redis client if available"""
        try:
            if hasattr(settings, 'REDIS_URL') and settings.REDIS_URL:
                client = redis.from_url(settings.REDIS_URL, decode_responses=True)
                client.ping()
                print("✅ Connected to Redis for conversation state")
                return client
        except Exception as e:
            print(f"⚠️ Redis not available, using in-memory storage: {e}")
        return None

    def _get_key(self, user_id: str, session_id: str) -> str:
        """Generate Redis key"""
        return f"conversation:{user_id}:{session_id}"

    def get_or_create_state(
            self,
            user_id: str,
            session_id: Optional[str] = None
    ) -> ConversationState:
        """Get existing state or create new one"""

        session_id = session_id or f"session_{datetime.now().timestamp()}"
        key = self._get_key(user_id, session_id)

        # Try Redis first
        if self.use_redis:
            try:
                data = self.redis_client.get(key)
                if data:
                    return ConversationState.from_dict(json.loads(data))
            except Exception as e:
                print(f"⚠️ Redis read error: {e}")

        # Check memory store
        if key in self.memory_store:
            return self.memory_store[key]

        # Create new state
        state = ConversationState(user_id=user_id, session_id=session_id)
        self.save_state(state)
        return state

    def save_state(self, state: ConversationState):
        """Save conversation state"""

        key = self._get_key(state.user_id, state.session_id)
        data = json.dumps(state.to_dict())

        # Save to Redis
        if self.use_redis:
            try:
                # Expire after 24 hours
                self.redis_client.setex(key, 86400, data)
            except Exception as e:
                print(f"⚠️ Redis write error: {e}")

        # Save to memory
        self.memory_store[key] = state

    def delete_state(self, user_id: str, session_id: str):
        """Delete conversation state"""

        key = self._get_key(user_id, session_id)

        if self.use_redis:
            try:
                self.redis_client.delete(key)
            except Exception as e:
                print(f"⚠️ Redis delete error: {e}")

        if key in self.memory_store:
            del self.memory_store[key]

    def get_user_sessions(self, user_id: str) -> List[str]:
        """Get all session IDs for a user"""

        if self.use_redis:
            try:
                pattern = f"conversation:{user_id}:*"
                keys = self.redis_client.keys(pattern)
                return [key.split(":")[-1] for key in keys]
            except Exception as e:
                print(f"⚠️ Redis scan error: {e}")

        # Fallback to memory
        pattern = f"conversation:{user_id}:"
        return [
            key.split(":")[-1]
            for key in self.memory_store.keys()
            if key.startswith(pattern)
        ]