from fastapi import APIRouter
from fastapi import HTTPException
from app.core.conversation.orchastrator import ConversationOrchestrator
from lib.logger.color_logger import setup_logger
logger = setup_logger(__name__)

router = APIRouter(prefix="/session", tags=["Session"])

orchestrator = ConversationOrchestrator()

@router.get("/{user_id}")
async def get_user_sessions(user_id: str):
    """
    Get all sessions for a user
    """

    try:
        sessions = orchestrator.state_manager.get_user_sessions(user_id)
        return {
            "user_id": user_id,
            "sessions": sessions,
            "total": len(sessions)
        }

    except Exception as e:
        logger.error(f"Error getting sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}/{session_id}")
async def get_session_state(user_id: str, session_id: str):
    """
    Get conversation state for a specific session
    """

    try:
        state = orchestrator.state_manager.get_or_create_state(user_id, session_id)
        return state.to_dict()

    except Exception as e:
        logger.error(f"Error getting session state: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{user_id}/{session_id}")
async def delete_session(user_id: str, session_id: str):
    """
    Delete a conversation session
    """

    try:
        orchestrator.state_manager.delete_state(user_id, session_id)
        return {
            "status": "success",
            "message": f"Session {session_id} deleted"
        }

    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))