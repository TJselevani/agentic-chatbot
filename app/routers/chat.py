from fastapi import APIRouter
from fastapi import HTTPException
from app.core.conversation.orchastrator import OrchestratorResponse, ConversationOrchestrator
from app.main2 import ChatResponse, ChatRequest
from lib.logger.color_logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat"])

# Global orchestrator instance
orchestrator = ConversationOrchestrator()


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint

    Handles:
    - Intent classification (PyTorch model)
    - FAQ retrieval (RAG)
    - Tool execution
    - Multi-turn conversations
    """

    try:
        logger.info(f"Processing message from user {request.user_id}: {request.message}")

        # Process message through orchestrator
        response: OrchestratorResponse = await orchestrator.process_message(
            user_id=request.user_id,
            message=request.message,
            session_id=request.session_id
        )

        # Get session ID from state
        state = orchestrator.state_manager.get_or_create_state(
            request.user_id,
            request.session_id
        )

        return ChatResponse(
            message=response.message,
            response_type=response.response_type.value,
            intent=response.intent,
            confidence=response.confidence,
            session_id=state.session_id,
            requires_followup=response.requires_followup,
            next_step=response.next_step,
            metadata=response.metadata
        )

    except Exception as e:
        logger.error(f"Error processing chat: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")
