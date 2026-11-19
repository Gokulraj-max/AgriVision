from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.database.models import ChatHistory, User
from backend.app.services.rag_assistant import AgriculturalRAGAssistant
from backend.app.services.voice_service import VoiceService

router = APIRouter(prefix="/assistant", tags=["Conversational AI Assistant"])

assistant_svc = AgriculturalRAGAssistant()

class ChatRequest(BaseModel):
    query: Optional[str] = None
    message: Optional[str] = None
    context_crop: Optional[str] = "Tomato"
    crop: Optional[str] = None
    language: Optional[str] = "en"
    user_id: Optional[str] = None

class VoiceRequest(BaseModel):
    text: str
    language: Optional[str] = "en"

@router.post("/chat")
def ask_assistant(payload: ChatRequest, db: Session = Depends(get_db)):
    """
    Multilingual Conversational Agricultural Assistant (Tamil & English).
    Uses RAG knowledge base for certified crop pathology guidance.
    """
    user_query = payload.query or payload.message or "How to protect crops?"
    crop_ctx = payload.crop or payload.context_crop or "Tomato"
    
    response_data = assistant_svc.answer_query(user_query, context_crop=crop_ctx)

    # Log to chat history
    user = db.query(User).first()
    chat_log = ChatHistory(
        user_id=user.user_id if user else "farmer-patel-001",
        query=user_query,
        response=response_data["answer"],
        language=response_data["language"],
        context_crop=crop_ctx
    )
    db.add(chat_log)
    db.commit()

    # Add TTS voice config
    voice_cfg = VoiceService.get_speech_config(response_data["language"])

    return {
        **response_data,
        "reply": response_data["answer"],
        "voice_config": voice_cfg
    }

@router.post("/voice")
def synthesize_voice_cue(payload: VoiceRequest):
    """Returns Web Speech / Native TTS metadata for voice feedback."""
    cfg = VoiceService.get_speech_config(payload.language)
    return {
        "text": payload.text,
        "language": payload.language,
        "voice_config": cfg
    }
