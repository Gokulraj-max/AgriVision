import io
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import Optional
from PIL import Image
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.services.classifier import ClassifierService
from backend.app.services.detector import DetectorService
from backend.app.services.segmenter import SegmenterService
from backend.app.services.severity import SeverityService
from backend.app.services.weather_risk import WeatherRiskService
from backend.app.core.config import UPLOAD_DIR
import uuid

router = APIRouter(prefix="/ai", tags=["AI Inference Pipeline"])

classifier_svc = ClassifierService()
detector_svc = DetectorService()
segmenter_svc = SegmenterService()

@router.post("/crop-id")
def identify_crop_only(file: UploadFile = File(...)):
    """Stage 1: Determines crop species and foliage validity."""
    content = file.file.read()
    image = Image.open(io.BytesIO(content)).convert("RGB")
    result = classifier_svc.identify_crop(image)
    return result

@router.post("/classify")
def classify_disease(file: UploadFile = File(...), crop: Optional[str] = Form("Tomato")):
    """Stage 2: Multi-crop foliar disease classification."""
    content = file.file.read()
    image = Image.open(io.BytesIO(content)).convert("RGB")
    
    # 1. Identify crop if not specified
    if not crop:
        crop_id_res = classifier_svc.identify_crop(image)
        crop = crop_id_res["identified_crop"]

    # 2. Diagnose disease
    diag = classifier_svc.diagnose_disease(image, crop)
    return diag

@router.post("/detect")
def detect_symptoms(file: UploadFile = File(...), crop: Optional[str] = Form("Tomato"), disease: Optional[str] = Form("Early Blight")):
    """Stage 3: YOLO-based symptom bounding box defect localization."""
    content = file.file.read()
    image = Image.open(io.BytesIO(content)).convert("RGB")
    return detector_svc.detect_symptoms(image, crop, disease)

@router.post("/segment")
def segment_lesions(file: UploadFile = File(...), is_healthy: Optional[bool] = Form(False)):
    """Stage 4: U-Net lesion segmentation and canopy mask calculation."""
    content = file.file.read()
    image = Image.open(io.BytesIO(content)).convert("RGB")
    return segmenter_svc.segment_foliar_lesions(image, is_healthy)
