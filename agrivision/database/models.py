import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    user_id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    role = Column(String(50), default="farmer")  # "farmer", "agronomist", "researcher", "admin"
    created_at = Column(DateTime, default=datetime.utcnow)

    farms = relationship("Farm", back_populates="user", cascade="all, delete-orphan")


class Farm(Base):
    __tablename__ = "farms"

    farm_id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    name = Column(String(150), nullable=False)
    crop_type = Column(String(100), default="Tomato")
    location = Column(String(255), default="Green Valley Farm, Sector 4")
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="farms")
    inspections = relationship("Inspection", back_populates="farm", cascade="all, delete-orphan")
    weather_records = relationship("WeatherRecord", back_populates="farm")


class Inspection(Base):
    __tablename__ = "inspections"

    inspection_id = Column(String(36), primary_key=True, default=generate_uuid)
    farm_id = Column(String(36), ForeignKey("farms.farm_id"), nullable=False)
    image_url = Column(String(500), nullable=False)
    original_filename = Column(String(255), nullable=True)
    predicted_disease = Column(String(150), nullable=False)
    disease_display = Column(String(200), nullable=True)
    confidence = Column(Float, nullable=False)
    severity_estimate = Column(Float, default=0.0)  # Percentage 0-100
    severity_level = Column(String(50), default="Low")  # "Healthy", "Mild", "Moderate", "High", "Severe"
    status = Column(String(50), default="completed")  # "completed", "needs_review", "expert_verified"
    visual_evidence = Column(JSON, nullable=True)  # paths to bbox image, mask image, heatmap image, metrics
    created_at = Column(DateTime, default=datetime.utcnow)

    farm = relationship("Farm", back_populates="inspections")
    disease_predictions = relationship("DiseasePrediction", back_populates="inspection", cascade="all, delete-orphan")
    weather_record = relationship("WeatherRecord", back_populates="inspection", uselist=False)
    feedback = relationship("ExpertFeedback", back_populates="inspection", cascade="all, delete-orphan")


class DiseasePrediction(Base):
    __tablename__ = "disease_predictions"

    prediction_id = Column(String(36), primary_key=True, default=generate_uuid)
    inspection_id = Column(String(36), ForeignKey("inspections.inspection_id"), nullable=False)
    model_version = Column(String(100), default="ResNet50-PlantVillage-v1.0")
    prediction_result = Column(String(150), nullable=False)
    confidence_score = Column(Float, nullable=False)
    probabilities = Column(JSON, nullable=True)  # full softmax distribution across classes
    created_at = Column(DateTime, default=datetime.utcnow)

    inspection = relationship("Inspection", back_populates="disease_predictions")


class WeatherRecord(Base):
    __tablename__ = "weather_records"

    record_id = Column(String(36), primary_key=True, default=generate_uuid)
    farm_id = Column(String(36), ForeignKey("farms.farm_id"), nullable=True)
    inspection_id = Column(String(36), ForeignKey("inspections.inspection_id"), nullable=True)
    temperature = Column(Float, nullable=False)  # Celsius
    humidity = Column(Float, nullable=False)     # Relative humidity %
    rainfall = Column(Float, nullable=False)     # mm
    growth_stage = Column(String(50), default="Vegetative")
    risk_score = Column(Float, default=0.0)      # 0 to 100
    risk_level = Column(String(50), default="Low") # Low, Moderate, High, Critical
    favorable_conditions = Column(String(255), nullable=True)
    recorded_at = Column(DateTime, default=datetime.utcnow)

    farm = relationship("Farm", back_populates="weather_records")
    inspection = relationship("Inspection", back_populates="weather_record")


class ExpertFeedback(Base):
    __tablename__ = "expert_feedback"

    feedback_id = Column(String(36), primary_key=True, default=generate_uuid)
    inspection_id = Column(String(36), ForeignKey("inspections.inspection_id"), nullable=False)
    verified_disease = Column(String(150), nullable=False)
    agreement = Column(String(50), default="agree")  # "agree", "disagree", "uncertain"
    comments = Column(Text, nullable=True)
    expert_name = Column(String(120), default="Agricultural Officer")
    submitted_at = Column(DateTime, default=datetime.utcnow)

    inspection = relationship("Inspection", back_populates="feedback")
