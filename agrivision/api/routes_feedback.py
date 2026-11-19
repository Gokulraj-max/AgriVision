from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from agrivision.database.session import get_db
from agrivision.services.history_service import HistoryService
from agrivision.config import DISEASE_DISPLAY_NAMES

router = APIRouter(prefix="/api/v1/feedback", tags=["Expert Feedback"])

class FeedbackRequest(BaseModel):
    inspection_id: str
    verified_disease: str
    agreement: str = "agree"  # "agree", "disagree", "uncertain"
    comments: Optional[str] = ""
    expert_name: Optional[str] = "Agricultural Officer"

@router.post("")
def submit_expert_feedback(payload: FeedbackRequest, db: Session = Depends(get_db)):
    """
    Records human-in-the-loop expert agricultural verification
    and marks inspection status.
    """
    insp = HistoryService.get_inspection_by_id(db, payload.inspection_id)
    if not insp:
        raise HTTPException(status_code=404, detail="Inspection not found")

    fb = HistoryService.add_expert_feedback(
        db=db,
        inspection_id=payload.inspection_id,
        verified_disease=payload.verified_disease,
        agreement=payload.agreement,
        comments=payload.comments,
        expert_name=payload.expert_name
    )

    return {
        "success": True,
        "feedback_id": fb.feedback_id,
        "inspection_id": fb.inspection_id,
        "verified_disease": fb.verified_disease,
        "agreement": fb.agreement,
        "inspection_status": "expert_verified",
        "submitted_at": fb.submitted_at.isoformat()
    }
