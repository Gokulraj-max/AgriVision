import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image
import io
from agrivision.database.session import init_db, SessionLocal
from agrivision.database.models import User, Farm, Inspection
from agrivision.services.image_service import ImageService
from agrivision.services.classification_service import ClassificationService
from agrivision.services.detection_service import DetectionService
from agrivision.services.segmentation_service import SegmentationService
from agrivision.services.severity_service import SeverityService
from agrivision.services.weather_service import WeatherService
from agrivision.services.recommendation_service import RecommendationService
from agrivision.services.history_service import HistoryService
from agrivision.config import SAMPLES_DIR

def run_all_tests():
    print("========================================")
    print("AGRIVISION AI — COMPONENT UNIT & INTEGRATION TESTS")
    print("========================================")

    # 1. DB Init
    print("\n[Test 1] Testing Database Initialization...")
    init_db()
    db = SessionLocal()
    user = db.query(User).first()
    assert user is not None, "User should be seeded"
    farms = db.query(Farm).all()
    assert len(farms) >= 2, "Default farms should be seeded"
    print(f"  --> DB initialized. Found {len(farms)} seeded farms.")

    # 2. Image Service
    print("\n[Test 2] Testing Image Validation & Loading...")
    sample_path = SAMPLES_DIR / "sample_early_blight.jpg"
    assert sample_path.exists(), "Sample image should exist"
    with open(sample_path, "rb") as f:
        bytes_data = f.read()
    val = ImageService.validate_and_load(bytes_data, "test.jpg")
    assert val["valid"] is True, "Image should be valid"
    assert val["is_foliage"] is True, "Foliage should be detected"
    print(f"  --> Image valid: {val['width']}x{val['height']}, green ratio: {val['green_ratio']:.3f}")

    # 3. Classification Service
    print("\n[Test 3] Testing Foliar Disease Classification (Model 1)...")
    cls_svc = ClassificationService()
    pred = cls_svc.predict(val["image"])
    assert "predicted_disease" in pred
    assert "confidence" in pred
    assert len(pred["top_classes"]) > 0
    print(f"  --> Predicted: {pred['disease_display']} (Confidence: {pred['confidence']*100:.1f}%)")

    # 4. Detection Service (YOLO)
    print("\n[Test 4] Testing Symptom Defect Localization (Model 2)...")
    det_svc = DetectionService()
    det = det_svc.detect_symptoms(val["image"], pred["predicted_disease"])
    assert "detections" in det
    assert "visualized_image_url" in det
    print(f"  --> Detected {det['count']} symptom defect regions.")

    # 5. Segmentation Service (U-Net)
    print("\n[Test 5] Testing Lesion Segmentation (Model 3)...")
    seg_svc = SegmentationService()
    seg = seg_svc.segment_leaf_and_disease(val["image"], pred["predicted_disease"])
    assert seg["total_leaf_pixels"] > 0
    assert seg["mask_url"] is not None
    assert seg["overlay_url"] is not None
    print(f"  --> Total Leaf Pixels: {seg['total_leaf_pixels']:,} | Affected Pixels: {seg['affected_pixels']:,}")

    # 6. Severity Service
    print("\n[Test 6] Testing Severity Estimation (Model 5)...")
    sev = SeverityService.calculate_severity(seg["affected_pixels"], seg["total_leaf_pixels"])
    assert sev["affected_area_percentage"] >= 0.0
    print(f"  --> Estimated Foliar Severity: {sev['affected_area_percentage']}% ({sev['severity_level']})")

    # 7. Weather Service
    print("\n[Test 7] Testing Epidemiological Microclimate Risk (Model 4)...")
    w_svc = WeatherService()
    w_risk = w_svc.assess_risk(temperature=26.0, humidity=85.0, rainfall=6.0, growth_stage="Fruiting")
    assert "risk_score" in w_risk
    assert "risk_level" in w_risk
    print(f"  --> Disease Risk Index: {w_risk['risk_score']}% ({w_risk['risk_level']})")

    # 8. Guidance Engine
    print("\n[Test 8] Testing Validated Agronomic Guidance Engine...")
    guidance = RecommendationService.get_guidance(pred["predicted_disease"])
    assert "immediate_actions" in guidance
    assert "regulatory_warning" in guidance
    print(f"  --> Guidance loaded: {guidance['title']}")

    # 9. History Service
    print("\n[Test 9] Testing Historical Record Persistence...")
    inspection = HistoryService.create_inspection(
        db=db,
        farm_id=farms[0].farm_id,
        image_url="/samples/sample_early_blight.jpg",
        filename="sample_early_blight.jpg",
        classification_result=pred,
        detection_result=det,
        segmentation_result=seg,
        severity_result=sev,
        weather_result={"temperature": 26.0, "humidity": 85.0, "rainfall": 6.0, **w_risk}
    )
    assert inspection.inspection_id is not None
    print(f"  --> Inspection saved to DB. ID: {inspection.inspection_id}")

    # 10. Expert Feedback
    print("\n[Test 10] Testing Agronomist Feedback Workflow...")
    fb = HistoryService.add_expert_feedback(
        db=db,
        inspection_id=inspection.inspection_id,
        verified_disease="Tomato___Early_blight",
        agreement="agree",
        comments="Confirmed Alternaria solani pycnidia in concentric target ring pattern.",
        expert_name="Dr. V. Rao"
    )
    assert fb.feedback_id is not None
    updated_insp = HistoryService.get_inspection_by_id(db, inspection.inspection_id)
    assert updated_insp.status == "expert_verified"
    print(f"  --> Expert verification saved. Inspection status updated to: {updated_insp.status}")

    db.close()
    print("\n========================================")
    print("ALL 10 UNIT & INTEGRATION TESTS COMPLETED SUCCESSFULLY!")
    print("========================================")

if __name__ == "__main__":
    run_all_tests()
