from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.database.models import Inspection, Farm

router = APIRouter(prefix="/reports", tags=["Inspection Reports"])

@router.get("/{inspection_id}")
def generate_inspection_report(inspection_id: str, db: Session = Depends(get_db)):
    insp = db.query(Inspection).filter(Inspection.inspection_id == inspection_id).first()
    if not insp:
        raise HTTPException(status_code=404, detail="Inspection not found")

    farm = insp.farm
    return {
        "report_id": f"REP-{insp.inspection_id[:8].upper()}",
        "generated_at": insp.created_at.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "farm_name": farm.name if farm else "General Field",
        "location": farm.location if farm else "N/A",
        "crop": insp.crop,
        "primary_diagnosis": insp.disease_display,
        "primary_diagnosis_ta": insp.disease_display_ta,
        "confidence": f"{insp.confidence * 100:.1f}%",
        "foliar_severity": f"{insp.severity_estimate}% ({insp.severity_level})",
        "status": insp.status,
        "image_url": insp.image_url,
        "visual_evidence": insp.visual_evidence,
        "verified_by": [fb.expert_name for fb in insp.feedback] if insp.feedback else "Automated AI Analysis",
        "regulatory_notice": "This document is an AI-assisted precision agricultural screening report. Follow local extension pesticide guidelines."
    }
