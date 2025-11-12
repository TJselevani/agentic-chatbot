from fastapi import APIRouter, Request
from app.core.intent_layer.intent_classifier import get_intent
from app.core.agentic_layer.agents.agent_manager import handle_agentic_action
from app.core.rag_layer.rag_engine import handle_faq
from app.core.translator import detect_and_translate

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/")
async def chat_endpoint(request: Request):
    data = await request.json()
    message = data.get("message")

    # Optional: Detect and translate to English
    message_en, lang = detect_and_translate(message)

    # Classify intent
    intent = get_intent(message_en)

    if intent == "faq":
        response = handle_faq(message_en)
    else:
        response = handle_agentic_action(intent, message_en)

    # Translate back to user language
    final_response = detect_and_translate(response, target_lang=lang)
    return {"intent": intent, "response": final_response}
