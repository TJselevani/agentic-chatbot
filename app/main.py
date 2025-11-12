# app/routers/chat.py

from fastapi import APIRouter, Request
from app.core.memory.memory_manager import PersistentMemory
from app.core.intent_layer.intent_classifier import get_intent
from app.core.agentic_layer.agents.agent import agentic_router  # where your LangChain agent lives

router = APIRouter()

@router.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_id = data.get("user_id", "anonymous")
    session_id = data.get("session_id", "default")
    message = data["message"]

    # Load persistent memory
    memory_handler = PersistentMemory(user_id, session_id)
    memory = memory_handler.get_memory()

    # Detect intent using PyTorch
    intent = get_intent(message)

    agent = agentic_router(memory)

    # Pass context to LangChain agent
    response = await agent.run(message, intent)

    # Save memory after each response
    memory_handler.save()

    return {"response": response}
