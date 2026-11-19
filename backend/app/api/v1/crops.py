from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.database.models import Crop, CropCycle
from ml.configs.crop_disease_catalog import SUPPORTED_CROPS, CROP_DISEASE_REGISTRY

router = APIRouter(prefix="/crops", tags=["Crop Information"])

@router.get("/supported")
def get_supported_crops():
    """Lists all 7 supported crop categories and diseases."""
    crops_info = []
    for crop in SUPPORTED_CROPS:
        diseases = [
            {
                "id": k,
                "disease": v["disease"],
                "display_name": v["display_name"],
                "display_name_ta": v["display_name_ta"]
            }
            for k, v in CROP_DISEASE_REGISTRY.items()
            if v["crop"] == crop
        ]
        crops_info.append({
            "name": crop,
            "diseases_count": len(diseases),
            "diseases": diseases
        })
    return {
        "crops": SUPPORTED_CROPS,
        "crops_info": crops_info,
        "registry": CROP_DISEASE_REGISTRY,
        "total_crops": len(SUPPORTED_CROPS),
        "total_diseases": len(CROP_DISEASE_REGISTRY)
    }

@router.get("")
def list_crops(db: Session = Depends(get_db)):
    crops = db.query(Crop).all()
    return [
        {
            "crop_id": c.crop_id,
            "name": c.name,
            "scientific_name": c.scientific_name,
            "variety": c.variety,
            "category": c.category
        }
        for c in crops
    ]
