from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from agrivision.database.models import (
    Inspection,
    DiseasePrediction,
    WeatherRecord,
    ExpertFeedback,
    Farm
)

class HistoryService:
    @staticmethod
    def create_inspection(
        db: Session,
        farm_id: str,
        image_url: str,
        filename: str,
        classification_result: dict,
        detection_result: dict,
        segmentation_result: dict,
        severity_result: dict,
        weather_result: dict = None
    ) -> Inspection:
        # Create inspection entity
        inspection = Inspection(
            farm_id=farm_id,
            image_url=image_url,
            original_filename=filename,
            predicted_disease=classification_result["predicted_disease"],
            disease_display=classification_result["disease_display"],
            confidence=classification_result["confidence"],
            severity_estimate=severity_result["affected_area_percentage"],
            severity_level=severity_result["severity_level"],
            status=classification_result["status"],
            visual_evidence={
                "detection": detection_result,
                "segmentation": {
                    "mask_url": segmentation_result["mask_url"],
                    "overlay_url": segmentation_result["overlay_url"],
                    "affected_pixels": segmentation_result["affected_pixels"],
                    "total_leaf_pixels": segmentation_result["total_leaf_pixels"]
                },
                "severity": severity_result,
                "top_classes": classification_result.get("top_classes", [])
            }
        )
        db.add(inspection)
        db.flush()

        # Create disease prediction detail entity
        disease_pred = DiseasePrediction(
            inspection_id=inspection.inspection_id,
            model_version="ResNet50-PlantVillage-v1.0",
            prediction_result=classification_result["predicted_disease"],
            confidence_score=classification_result["confidence"],
            probabilities=classification_result.get("probabilities", {})
        )
        db.add(disease_pred)

        # Create weather record if provided
        if weather_result:
            weather_rec = WeatherRecord(
                farm_id=farm_id,
                inspection_id=inspection.inspection_id,
                temperature=weather_result.get("temperature", 24.0),
                humidity=weather_result.get("humidity", 75.0),
                rainfall=weather_result.get("rainfall", 2.0),
                growth_stage=weather_result.get("growth_stage", "Vegetative"),
                risk_score=weather_result.get("risk_score", 40.0),
                risk_level=weather_result.get("risk_level", "Moderate"),
                favorable_conditions=weather_result.get("favorable_conditions", "")
            )
            db.add(weather_rec)

        db.commit()
        db.refresh(inspection)
        return inspection

    @staticmethod
    def get_inspections(db: Session, farm_id: str = None, limit: int = 50, offset: int = 0):
        query = db.query(Inspection)
        if farm_id:
            query = query.filter(Inspection.farm_id == farm_id)
        return query.order_by(desc(Inspection.created_at)).offset(offset).limit(limit).all()

    @staticmethod
    def get_inspection_by_id(db: Session, inspection_id: str):
        return db.query(Inspection).filter(Inspection.inspection_id == inspection_id).first()

    @staticmethod
    def add_expert_feedback(
        db: Session,
        inspection_id: str,
        verified_disease: str,
        agreement: str,
        comments: str,
        expert_name: str
    ):
        feedback = ExpertFeedback(
            inspection_id=inspection_id,
            verified_disease=verified_disease,
            agreement=agreement,
            comments=comments,
            expert_name=expert_name
        )
        db.add(feedback)

        # Update inspection status if verified
        insp = db.query(Inspection).filter(Inspection.inspection_id == inspection_id).first()
        if insp:
            insp.status = "expert_verified"
            if agreement == "disagree":
                insp.predicted_disease = verified_disease
                insp.disease_display = f"{verified_disease} (Verified by {expert_name})"

        db.commit()
        db.refresh(feedback)
        return feedback

    @staticmethod
    def get_farm_health_summary(db: Session, farm_id: str) -> dict:
        farm = db.query(Farm).filter(Farm.farm_id == farm_id).first()
        if not farm:
            return {"error": "Farm not found"}

        inspections = db.query(Inspection).filter(Inspection.farm_id == farm_id).all()
        total_inspections = len(inspections)

        if total_inspections == 0:
            return {
                "farm_id": farm.farm_id,
                "farm_name": farm.name,
                "crop_type": farm.crop_type,
                "location": farm.location,
                "total_inspections": 0,
                "healthy_count": 0,
                "diseased_count": 0,
                "health_score": 100.0,
                "average_severity": 0.0,
                "disease_distribution": {},
                "recent_inspections": []
            }

        healthy_count = sum(1 for i in inspections if "healthy" in i.predicted_disease.lower())
        diseased_count = total_inspections - healthy_count
        avg_severity = float(sum(i.severity_estimate for i in inspections) / total_inspections)

        # Overall farm health index (0 to 100)
        healthy_ratio = (healthy_count / total_inspections) * 100
        health_score = max(0.0, round(healthy_ratio - (avg_severity * 0.5), 1))

        # Disease breakdown
        disease_counts = {}
        for i in inspections:
            disp = i.disease_display or i.predicted_disease
            disease_counts[disp] = disease_counts.get(disp, 0) + 1

        recent = [
            {
                "inspection_id": i.inspection_id,
                "disease_display": i.disease_display,
                "confidence": i.confidence,
                "severity_estimate": i.severity_estimate,
                "severity_level": i.severity_level,
                "image_url": i.image_url,
                "created_at": i.created_at.strftime("%Y-%m-%d %H:%M")
            }
            for i in sorted(inspections, key=lambda x: x.created_at, reverse=True)[:5]
        ]

        return {
            "farm_id": farm.farm_id,
            "farm_name": farm.name,
            "crop_type": farm.crop_type,
            "location": farm.location,
            "total_inspections": total_inspections,
            "healthy_count": healthy_count,
            "diseased_count": diseased_count,
            "health_score": health_score,
            "average_severity": round(avg_severity, 2),
            "disease_distribution": disease_counts,
            "recent_inspections": recent
        }
