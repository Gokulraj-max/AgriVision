import io
import uuid
from typing import Optional, List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from PIL import Image
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.app.database.session import get_db
from backend.app.database.models import Farm, Inspection, DiseasePrediction, InspectionImage, WeatherRecord
from backend.app.services.classifier import ClassifierService
from backend.app.services.detector import DetectorService
from backend.app.services.segmenter import SegmenterService
from backend.app.services.severity import SeverityService
from backend.app.services.weather_risk import WeatherRiskService
from backend.app.services.voice_service import VoiceService
from backend.app.core.config import UPLOAD_DIR

router = APIRouter(prefix="/inspections", tags=["Inspections"])

classifier_svc = ClassifierService()
detector_svc = DetectorService()
segmenter_svc = SegmenterService()

@router.post("")
def create_inspection(
    file: UploadFile = File(...),
    farm_id: Optional[str] = Form(None),
    crop_hint: Optional[str] = Form(None),
    temperature: Optional[float] = Form(26.0),
    humidity: Optional[float] = Form(75.0),
    rainfall: Optional[float] = Form(2.0),
    wind_speed: Optional[float] = Form(5.0),
    growth_stage: Optional[str] = Form("Vegetative"),
    db: Session = Depends(get_db)
):
    """
    Complete Cloud Inspection Analysis:
    1. Saves original photograph
    2. Identifies crop species
    3. Multi-crop disease classification
    4. YOLO symptom defect localization
    5. U-Net lesion pixel segmentation
    6. Severity percentage calculation
    7. Weather risk forecasting
    8. Multilingual spoken diagnosis generation
    9. Persists to database
    """
    if not farm_id or hasattr(farm_id, "default"):
        default_farm = db.query(Farm).first()
        farm_id = default_farm.farm_id if default_farm else "farm-north-block"

    content = file.file.read()
    image = Image.open(io.BytesIO(content)).convert("RGB")

    # 1. Save original image
    orig_filename = f"leaf_{uuid.uuid4().hex[:10]}.jpg"
    orig_path = UPLOAD_DIR / orig_filename
    image.save(orig_path, format="JPEG", quality=90)
    orig_url = f"/uploads/{orig_filename}"

    # 2. Crop identification
    crop_id_res = classifier_svc.identify_crop(image, requested_crop=crop_hint)
    active_crop = crop_id_res["identified_crop"] if crop_id_res["foliage_detected"] else "Tomato"

    # 3. Disease Classification
    diag_res = classifier_svc.diagnose_disease(image, crop=active_crop)
    is_healthy = "healthy" in diag_res["disease_name"].lower()

    # 4. YOLO Symptom Defect Localization
    detect_res = detector_svc.detect_symptoms(image, crop=active_crop, disease=diag_res["disease_name"])

    # 5. U-Net Lesion Segmentation
    seg_res = segmenter_svc.segment_foliar_lesions(image, is_healthy=is_healthy)

    # 6. Severity Calculation
    sev_res = SeverityService.calculate(seg_res["affected_pixels"], seg_res["total_leaf_pixels"], is_healthy=is_healthy)

    # 7. Weather Risk Forecasting
    weather_res = WeatherRiskService.forecast_risk(
        temperature=temperature or 26.0,
        humidity=humidity or 75.0,
        rainfall=rainfall or 2.0,
        wind_speed=wind_speed or 5.0,
        crop=active_crop,
        growth_stage=growth_stage or "Vegetative"
    )

    # 8. Spoken Voice text
    spoken_en = VoiceService.format_spoken_diagnosis(active_crop, diag_res["display_name"], diag_res["confidence"], sev_res["affected_area_percent"], "en")
    spoken_ta = VoiceService.format_spoken_diagnosis(active_crop, diag_res["display_name_ta"], diag_res["confidence"], sev_res["affected_area_percent"], "ta")

    # 9. Commit to Database
    inspection = Inspection(
        farm_id=farm_id,
        crop=active_crop,
        image_url=orig_url,
        predicted_disease=diag_res["predicted_class"],
        disease_display=diag_res["display_name"],
        disease_display_ta=diag_res["display_name_ta"],
        confidence=diag_res["confidence"],
        severity_estimate=sev_res["affected_area_percent"],
        severity_level=sev_res["severity_level"],
        status="needs_review" if diag_res["needs_expert_review"] else "completed",
        inspection_type="mobile_camera",
        visual_evidence={
            "detection": detect_res,
            "segmentation": seg_res,
            "severity": sev_res,
            "top_candidates": diag_res["top_candidates"],
            "spoken_audio": {
                "en": spoken_en,
                "ta": spoken_ta
            }
        }
    )
    db.add(inspection)
    db.flush()

    # Image relation
    img_rec = InspectionImage(
        inspection_id=inspection.inspection_id,
        original_url=orig_url,
        bbox_overlay_url=detect_res["visualized_image_url"],
        mask_url=seg_res["mask_url"],
        heatmap_url=seg_res["heatmap_url"]
    )
    db.add(img_rec)

    # Prediction detail relation
    pred_rec = DiseasePrediction(
        inspection_id=inspection.inspection_id,
        crop_identified=active_crop,
        disease_name=diag_res["disease_name"],
        confidence=diag_res["confidence"],
        model_version="AgriVision-v2.0",
        probabilities={c["display_name"]: c["probability"] for c in diag_res["top_candidates"]}
    )
    db.add(pred_rec)

    # Weather relation
    w_rec = WeatherRecord(
        farm_id=farm_id,
        inspection_id=inspection.inspection_id,
        temperature=weather_res["temperature"],
        humidity=weather_res["humidity"],
        rainfall=weather_res["rainfall"],
        wind_speed=weather_res["wind_speed"],
        risk_score=weather_res["risk_score"],
        risk_level=weather_res["risk_level"]
    )
    db.add(w_rec)

    db.commit()
    db.refresh(inspection)

    return {
        "success": True,
        "inspection_id": inspection.inspection_id,
        "farm_id": farm_id,
        "crop": active_crop,
        "diagnosis": diag_res,
        "detection": detect_res,
        "segmentation": seg_res,
        "severity": sev_res,
        "weather_risk": weather_res,
        "spoken_en": spoken_en,
        "spoken_ta": spoken_ta,
        "image_url": orig_url,
        "created_at": inspection.created_at.isoformat()
    }

@router.get("")
def list_inspections(farm_id: Optional[str] = None, limit: int = 50, db: Session = Depends(get_db)):
    query = db.query(Inspection)
    if farm_id:
        query = query.filter(Inspection.farm_id == farm_id)
    inspections = query.order_by(desc(Inspection.created_at)).limit(limit).all()

    return [
        {
            "inspection_id": i.inspection_id,
            "farm_id": i.farm_id,
            "crop": i.crop,
            "image_url": i.image_url,
            "predicted_disease": i.predicted_disease,
            "disease_display": i.disease_display,
            "disease_display_ta": i.disease_display_ta,
            "confidence": i.confidence,
            "severity_estimate": i.severity_estimate,
            "severity_level": i.severity_level,
            "status": i.status,
            "created_at": i.created_at.isoformat()
        }
        for i in inspections
    ]

@router.get("/{inspection_id}")
def get_inspection_detail(inspection_id: str, db: Session = Depends(get_db)):
    insp = db.query(Inspection).filter(Inspection.inspection_id == inspection_id).first()
    if not insp:
        raise HTTPException(status_code=404, detail="Inspection report not found")

    feedbacks = [
        {
            "feedback_id": fb.feedback_id,
            "verified_disease": fb.verified_disease,
            "agreement": fb.agreement,
            "comments": fb.comments,
            "expert_name": fb.expert_name,
            "submitted_at": fb.submitted_at.isoformat()
        }
        for fb in insp.feedback
    ]

    return {
        "inspection_id": insp.inspection_id,
        "farm_id": insp.farm_id,
        "crop": insp.crop,
        "image_url": insp.image_url,
        "disease_display": insp.disease_display,
        "disease_display_ta": insp.disease_display_ta,
        "confidence": insp.confidence,
        "severity_estimate": insp.severity_estimate,
        "severity_level": insp.severity_level,
        "status": insp.status,
        "visual_evidence": insp.visual_evidence,
        "feedback": feedbacks,
        "created_at": insp.created_at.isoformat()
    }
