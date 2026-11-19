from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from agrivision.database.session import get_db
from agrivision.database.models import Farm, User
from agrivision.services.history_service import HistoryService

router = APIRouter(prefix="/api/v1/farms", tags=["Farms"])

class FarmCreateRequest(BaseModel):
    name: str
    crop_type: Optional[str] = "Tomato"
    location: Optional[str] = "Sector 4, Agro Zone"
    latitude: Optional[float] = 19.9975
    longitude: Optional[float] = 73.7898

@router.get("")
def list_farms(db: Session = Depends(get_db)):
    """List all registered farms."""
    farms = db.query(Farm).all()
    return [
        {
            "farm_id": f.farm_id,
            "name": f.name,
            "crop_type": f.crop_type,
            "location": f.location,
            "latitude": f.latitude,
            "longitude": f.longitude,
            "created_at": f.created_at.isoformat()
        }
        for f in farms
    ]

@router.post("")
def register_farm(payload: FarmCreateRequest, db: Session = Depends(get_db)):
    """Registers a new farm."""
    user = db.query(User).first()
    user_id = user.user_id if user else "default-user-001"

    new_farm = Farm(
        name=payload.name,
        crop_type=payload.crop_type,
        location=payload.location,
        latitude=payload.latitude,
        longitude=payload.longitude,
        user_id=user_id
    )
    db.add(new_farm)
    db.commit()
    db.refresh(new_farm)
    return {
        "success": True,
        "farm_id": new_farm.farm_id,
        "name": new_farm.name,
        "crop_type": new_farm.crop_type,
        "location": new_farm.location
    }

@router.get("/{farm_id}/health")
def get_farm_health(farm_id: str, db: Session = Depends(get_db)):
    """Farm health summary, disease prevalence, and risk index."""
    summary = HistoryService.get_farm_health_summary(db, farm_id)
    if "error" in summary:
        raise HTTPException(status_code=404, detail=summary["error"])
    return summary
