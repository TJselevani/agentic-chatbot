from fastapi import APIRouter, Request
from app.core.rag_layer.rag_engine import handle_faq
from app.core.agentic_layer.agent_manager import handle_agentic_action
from app.core.multilingual_layer.translator import Translator

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/")
async def chat_endpoint(request: Request):
    data = await request.json()
    message = data.get("message")
    translator = Translator()

    # Optional translation
    message_en, lang = translator.detect_language(message)

    intent = get_intent(message_en)

    if intent == "faq":
        response = handle_faq(message_en)
    else:
        response = handle_agentic_action(intent, message_en)

    final_response = translator.detect_and_translate(response, target_lang=lang)
    return {"intent": intent, "response": final_response}
