from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.database.models import ExpertFeedback, Inspection

router = APIRouter(prefix="/feedback", tags=["Expert Verification"])

class FeedbackCreate(BaseModel):
    inspection_id: str
    verified_disease: str
    agreement: str = "agree"  # agree, disagree, uncertain
    comments: Optional[str] = ""
    expert_name: Optional[str] = "Agricultural Officer"

@router.post("")
def submit_feedback(payload: FeedbackCreate, db: Session = Depends(get_db)):
    insp = db.query(Inspection).filter(Inspection.inspection_id == payload.inspection_id).first()
    if not insp:
        raise HTTPException(status_code=404, detail="Inspection not found")

    fb = ExpertFeedback(
        inspection_id=payload.inspection_id,
        verified_disease=payload.verified_disease,
        agreement=payload.agreement,
        comments=payload.comments,
        expert_name=payload.expert_name
    )
    db.add(fb)

    # Update inspection status
    insp.status = "expert_verified"
    if payload.agreement == "disagree":
        insp.disease_display = f"{payload.verified_disease} (Agronomist Corrected)"

    db.commit()
    db.refresh(fb)

    return {
        "success": True,
        "feedback_id": fb.feedback_id,
        "inspection_status": insp.status,
        "verified_disease": fb.verified_disease
    }
