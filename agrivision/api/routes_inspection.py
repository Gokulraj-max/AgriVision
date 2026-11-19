from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from agrivision.database.session import get_db
from agrivision.services.image_service import ImageService
from agrivision.services.classification_service import ClassificationService
from agrivision.services.detection_service import DetectionService
from agrivision.services.segmentation_service import SegmentationService
from agrivision.services.severity_service import SeverityService
from agrivision.services.weather_service import WeatherService
from agrivision.services.recommendation_service import RecommendationService
from agrivision.services.history_service import HistoryService
from agrivision.database.models import Farm

router = APIRouter(prefix="/api/v1", tags=["Inspection"])

# Initialize singletons
classification_svc = ClassificationService()
detection_svc = DetectionService()
segmentation_svc = SegmentationService()
weather_svc = WeatherService()

@router.post("/inspect")
def inspect_crop_image(
    file: UploadFile = File(...),
    farm_id: Optional[str] = Form(None),
    temperature: Optional[float] = Form(25.0),
    humidity: Optional[float] = Form(75.0),
    rainfall: Optional[float] = Form(2.0),
    growth_stage: Optional[str] = Form("Vegetative"),
    db: Session = Depends(get_db)
):
    """
    Main End-to-End AgriVision Pipeline:
    1. Validation & Preprocessing
    2. Deep Learning Classification (PyTorch ResNet/CNN)
    3. YOLO Symptom Bounding Box Detection
    4. PyTorch U-Net Affected-Region Segmentation
    5. Computer Vision Severity Estimation
    6. Weather Epidemiological Risk Modeling
    7. Agronomic Recommendation Generation
    8. Historical Persistence
    """
    # 1. Fallback farm assignment if not selected
    if not farm_id or hasattr(farm_id, "default"):
        default_farm = db.query(Farm).first()
        farm_id = default_farm.farm_id if default_farm else "farm-north-block"

    # Safe float conversions
    try:
        temp_val = float(temperature) if not hasattr(temperature, "default") else 25.0
    except (ValueError, TypeError):
        temp_val = 25.0

    try:
        hum_val = float(humidity) if not hasattr(humidity, "default") else 75.0
    except (ValueError, TypeError):
        hum_val = 75.0

    try:
        rain_val = float(rainfall) if not hasattr(rainfall, "default") else 2.0
    except (ValueError, TypeError):
        rain_val = 2.0

    stage_val = str(growth_stage) if not hasattr(growth_stage, "default") else "Vegetative"

    # Read image bytes synchronously
    contents = file.file.read()
    val_result = ImageService.validate_and_load(contents, file.filename)
    if not val_result["valid"]:
        raise HTTPException(status_code=400, detail=val_result["error"])

    pil_img = val_result["image"]
    is_foliage = val_result["is_foliage"]

    # Save original image
    image_url, abs_path = ImageService.save_image(pil_img, prefix="leaf_orig")

    # 2. Disease Classification (Model 1)
    class_res = classification_svc.predict(pil_img, foliage_valid=is_foliage)

    # 3. Disease Detection (Model 2 - YOLO BBoxes)
    detect_res = detection_svc.detect_symptoms(pil_img, class_res["predicted_disease"])

    # 4. Disease Segmentation (Model 3 - U-Net)
    seg_res = segmentation_svc.segment_leaf_and_disease(pil_img, class_res["predicted_disease"])

    # 5. Severity Estimation (Model 5 - CV Affected %)
    is_healthy = ("healthy" in class_res["predicted_disease"].lower())
    severity_res = SeverityService.calculate_severity(
        affected_pixels=seg_res["affected_pixels"],
        leaf_pixels=seg_res["total_leaf_pixels"],
        is_healthy=is_healthy
    )

    # 6. Weather Risk Prediction (Model 4)
    weather_risk = weather_svc.assess_risk(
        temperature=temp_val,
        humidity=hum_val,
        rainfall=rain_val,
        growth_stage=stage_val
    )
    weather_combined = {
        "temperature": temp_val,
        "humidity": hum_val,
        "rainfall": rain_val,
        "growth_stage": stage_val,
        **weather_risk
    }

    # 7. Agricultural Guidance
    guidance = RecommendationService.get_guidance(class_res["predicted_disease"])

    # 8. Save Inspection to History DB
    inspection = HistoryService.create_inspection(
        db=db,
        farm_id=farm_id,
        image_url=image_url,
        filename=file.filename,
        classification_result=class_res,
        detection_result=detect_res,
        segmentation_result=seg_res,
        severity_result=severity_res,
        weather_result=weather_combined
    )

    return {
        "success": True,
        "inspection_id": inspection.inspection_id,
        "farm_id": farm_id,
        "image_url": image_url,
        "created_at": inspection.created_at.isoformat(),
        "foliage_warning": val_result.get("error"),
        "classification": class_res,
        "detection": detect_res,
        "segmentation": seg_res,
        "severity": severity_res,
        "weather_risk": weather_combined,
        "guidance": guidance,
        "status": inspection.status
    }


@router.post("/inspect/batch")
def inspect_crop_images_batch(
    files: List[UploadFile] = File(...),
    farm_id: Optional[str] = Form(None),
    temperature: Optional[float] = Form(25.0),
    humidity: Optional[float] = Form(75.0),
    rainfall: Optional[float] = Form(2.0),
    growth_stage: Optional[str] = Form("Vegetative"),
    db: Session = Depends(get_db)
):
    """Batch processes multiple crop leaf images."""
    if not farm_id or hasattr(farm_id, "default"):
        default_farm = db.query(Farm).first()
        farm_id = default_farm.farm_id if default_farm else "farm-north-block"

    try:
        temp_val = float(temperature) if not hasattr(temperature, "default") else 25.0
    except (ValueError, TypeError):
        temp_val = 25.0

    try:
        hum_val = float(humidity) if not hasattr(humidity, "default") else 75.0
    except (ValueError, TypeError):
        hum_val = 75.0

    try:
        rain_val = float(rainfall) if not hasattr(rainfall, "default") else 2.0
    except (ValueError, TypeError):
        rain_val = 2.0

    stage_val = str(growth_stage) if not hasattr(growth_stage, "default") else "Vegetative"

    results = []
    for file in files:
        try:
            contents = file.file.read()
            val_result = ImageService.validate_and_load(contents, file.filename)
            if not val_result["valid"]:
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "error": val_result["error"]
                })
                continue

            pil_img = val_result["image"]
            image_url, _ = ImageService.save_image(pil_img, prefix="batch")

            class_res = classification_svc.predict(pil_img, foliage_valid=val_result["is_foliage"])
            detect_res = detection_svc.detect_symptoms(pil_img, class_res["predicted_disease"])
            seg_res = segmentation_svc.segment_leaf_and_disease(pil_img, class_res["predicted_disease"])

            is_healthy = ("healthy" in class_res["predicted_disease"].lower())
            severity_res = SeverityService.calculate_severity(
                affected_pixels=seg_res["affected_pixels"],
                leaf_pixels=seg_res["total_leaf_pixels"],
                is_healthy=is_healthy
            )

            weather_risk = weather_svc.assess_risk(temp_val, hum_val, rain_val, stage_val)
            weather_combined = {
                "temperature": temp_val,
                "humidity": hum_val,
                "rainfall": rain_val,
                "growth_stage": stage_val,
                **weather_risk
            }

            inspection = HistoryService.create_inspection(
                db=db,
                farm_id=farm_id,
                image_url=image_url,
                filename=file.filename,
                classification_result=class_res,
                detection_result=detect_res,
                segmentation_result=seg_res,
                severity_result=severity_res,
                weather_result=weather_combined
            )

            results.append({
                "filename": file.filename,
                "inspection_id": inspection.inspection_id,
                "success": True,
                "predicted_disease": class_res["disease_display"],
                "confidence": class_res["confidence"],
                "severity_percentage": severity_res["affected_area_percentage"],
                "severity_level": severity_res["severity_level"],
                "status": inspection.status,
                "image_url": image_url
            })
        except Exception as e:
            results.append({
                "filename": file.filename,
                "success": False,
                "error": str(e)
            })

    return {
        "total_processed": len(results),
        "successful": sum(1 for r in results if r["success"]),
        "results": results
    }


@router.get("/inspections")
def list_inspections(
    farm_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Retrieve historical inspections."""
    inspections = HistoryService.get_inspections(db, farm_id=farm_id, limit=limit, offset=offset)
    return [
        {
            "inspection_id": i.inspection_id,
            "farm_id": i.farm_id,
            "image_url": i.image_url,
            "filename": i.original_filename,
            "predicted_disease": i.predicted_disease,
            "disease_display": i.disease_display,
            "confidence": i.confidence,
            "severity_estimate": i.severity_estimate,
            "severity_level": i.severity_level,
            "status": i.status,
            "created_at": i.created_at.isoformat()
        }
        for i in inspections
    ]


@router.get("/inspections/{inspection_id}")
def get_inspection_detail(inspection_id: str, db: Session = Depends(get_db)):
    """Retrieve comprehensive details of a single inspection."""
    insp = HistoryService.get_inspection_by_id(db, inspection_id)
    if not insp:
        raise HTTPException(status_code=404, detail="Inspection not found")

    guidance = RecommendationService.get_guidance(insp.predicted_disease)

    # Weather record
    weather_dict = None
    if insp.weather_record:
        wr = insp.weather_record
        weather_dict = {
            "temperature": wr.temperature,
            "humidity": wr.humidity,
            "rainfall": wr.rainfall,
            "growth_stage": wr.growth_stage,
            "risk_score": wr.risk_score,
            "risk_level": wr.risk_level,
            "favorable_conditions": wr.favorable_conditions,
            "recorded_at": wr.recorded_at.isoformat()
        }

    # Feedback records
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
        "image_url": insp.image_url,
        "filename": insp.original_filename,
        "predicted_disease": insp.predicted_disease,
        "disease_display": insp.disease_display,
        "confidence": insp.confidence,
        "severity_estimate": insp.severity_estimate,
        "severity_level": insp.severity_level,
        "status": insp.status,
        "visual_evidence": insp.visual_evidence,
        "weather": weather_dict,
        "guidance": guidance,
        "feedback": feedbacks,
        "created_at": insp.created_at.isoformat()
    }
