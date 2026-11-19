from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.database.models import Farm, User, Inspection

router = APIRouter(prefix="/farms", tags=["Farm Management"])

class FarmCreate(BaseModel):
    name: str
    location: Optional[str] = "Agro District, Sector 4"
    latitude: Optional[float] = 19.9975
    longitude: Optional[float] = 73.7898
    area_hectares: Optional[float] = 5.0
    crop_type: Optional[str] = "Tomato"

@router.get("")
def list_farms(db: Session = Depends(get_db)):
    farms = db.query(Farm).all()
    results = []
    for f in farms:
        inspections_count = len(f.inspections)
        results.append({
            "farm_id": f.farm_id,
            "name": f.name,
            "location": f.location,
            "latitude": f.latitude,
            "longitude": f.longitude,
            "area_hectares": f.area_hectares,
            "inspections_count": inspections_count,
            "created_at": f.created_at.isoformat()
        })
    return {
        "farms": results,
        "total": len(results)
    }

@router.post("")
def create_farm(payload: FarmCreate, db: Session = Depends(get_db)):
    user = db.query(User).first()
    farm = Farm(
        user_id=user.user_id if user else "farmer-patel-001",
        name=payload.name,
        location=payload.location,
        latitude=payload.latitude,
        longitude=payload.longitude,
        area_hectares=payload.area_hectares
    )
    db.add(farm)
    db.commit()
    db.refresh(farm)
    return {
        "success": True,
        "farm_id": farm.farm_id,
        "name": farm.name,
        "location": farm.location,
        "area_hectares": farm.area_hectares
    }

@router.get("/{farm_id}/health")
def get_farm_health_summary(farm_id: str, db: Session = Depends(get_db)):
    farm = db.query(Farm).filter(Farm.farm_id == farm_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    inspections = db.query(Inspection).filter(Inspection.farm_id == farm_id).all()
    total = len(inspections)
    if total == 0:
        return {
            "farm_id": farm.farm_id,
            "name": farm.name,
            "location": farm.location,
            "health_score": 100.0,
            "total_inspections": 0,
            "healthy_count": 0,
            "diseased_count": 0,
            "average_severity": 0.0,
            "disease_distribution": {},
            "recent_inspections": []
        }

    healthy_count = sum(1 for i in inspections if "healthy" in i.predicted_disease.lower())
    diseased_count = total - healthy_count
    avg_severity = sum(i.severity_estimate for i in inspections) / total
    health_score = max(0.0, round(((healthy_count / total) * 100.0) - (avg_severity * 0.4), 1))

    dist = {}
    for i in inspections:
        disp = i.disease_display or i.predicted_disease
        dist[disp] = dist.get(disp, 0) + 1

    recent = [
        {
            "inspection_id": i.inspection_id,
            "crop": i.crop,
            "disease_display": i.disease_display,
            "severity_estimate": i.severity_estimate,
            "severity_level": i.severity_level,
            "image_url": i.image_url,
            "created_at": i.created_at.strftime("%Y-%m-%d %H:%M")
        }
        for i in sorted(inspections, key=lambda x: x.created_at, reverse=True)[:5]
    ]

    return {
        "farm_id": farm.farm_id,
        "name": farm.name,
        "location": farm.location,
        "health_score": health_score,
        "total_inspections": total,
        "healthy_count": healthy_count,
        "diseased_count": diseased_count,
        "average_severity": round(avg_severity, 2),
        "disease_distribution": dist,
        "recent_inspections": recent
    }
