import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    user_id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(30), nullable=True)
    hashed_password = Column(String(255), nullable=True)
    role = Column(String(50), default="farmer")  # "farmer", "agronomist", "admin"
    created_at = Column(DateTime, default=datetime.utcnow)

    farms = relationship("Farm", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    chat_logs = relationship("ChatHistory", back_populates="user", cascade="all, delete-orphan")


class Farm(Base):
    __tablename__ = "farms"

    farm_id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    name = Column(String(150), nullable=False)
    location = Column(String(255), default="Green Valley Farm, Sector 4")
    latitude = Column(Float, default=19.9975)
    longitude = Column(Float, default=73.7898)
    area_hectares = Column(Float, default=4.5)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="farms")
    fields = relationship("Field", back_populates="farm", cascade="all, delete-orphan")
    crop_cycles = relationship("CropCycle", back_populates="farm", cascade="all, delete-orphan")
    inspections = relationship("Inspection", back_populates="farm", cascade="all, delete-orphan")
    weather_records = relationship("WeatherRecord", back_populates="farm")


class Field(Base):
    __tablename__ = "fields"

    field_id = Column(String(36), primary_key=True, default=generate_uuid)
    farm_id = Column(String(36), ForeignKey("farms.farm_id"), nullable=False)
    name = Column(String(120), nullable=False)
    boundaries_geojson = Column(JSON, nullable=True)
    soil_type = Column(String(100), default="Loamy Sand")

    farm = relationship("Farm", back_populates="fields")


class Crop(Base):
    __tablename__ = "crops"

    crop_id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), unique=True, nullable=False)
    scientific_name = Column(String(150), nullable=True)
    variety = Column(String(100), default="High-Yield Hybrid")
    category = Column(String(80), default="Vegetable")

    cycles = relationship("CropCycle", back_populates="crop")


class CropCycle(Base):
    __tablename__ = "crop_cycles"

    cycle_id = Column(String(36), primary_key=True, default=generate_uuid)
    farm_id = Column(String(36), ForeignKey("farms.farm_id"), nullable=False)
    crop_id = Column(String(36), ForeignKey("crops.crop_id"), nullable=False)
    planting_date = Column(DateTime, default=datetime.utcnow)
    expected_harvest = Column(DateTime, nullable=True)
    status = Column(String(50), default="Active")  # Active, Harvested, Terminated

    farm = relationship("Farm", back_populates="crop_cycles")
    crop = relationship("Crop", back_populates="cycles")


class Inspection(Base):
    __tablename__ = "inspections"

    inspection_id = Column(String(36), primary_key=True, default=generate_uuid)
    farm_id = Column(String(36), ForeignKey("farms.farm_id"), nullable=False)
    crop = Column(String(80), default="Tomato")
    image_url = Column(String(500), nullable=False)
    predicted_disease = Column(String(150), nullable=False)
    disease_display = Column(String(200), nullable=True)
    disease_display_ta = Column(String(200), nullable=True)
    confidence = Column(Float, nullable=False)
    severity_estimate = Column(Float, default=0.0)
    severity_level = Column(String(50), default="Low")
    status = Column(String(50), default="completed")  # "completed", "needs_review", "expert_verified"
    inspection_type = Column(String(50), default="mobile_camera")  # "live_stream", "photo_upload", "mobile_camera"
    visual_evidence = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    farm = relationship("Farm", back_populates="inspections")
    predictions = relationship("DiseasePrediction", back_populates="inspection", cascade="all, delete-orphan")
    images = relationship("InspectionImage", back_populates="inspection", cascade="all, delete-orphan")
    weather = relationship("WeatherRecord", back_populates="inspection", uselist=False)
    feedback = relationship("ExpertFeedback", back_populates="inspection", cascade="all, delete-orphan")


class DiseasePrediction(Base):
    __tablename__ = "disease_predictions"

    prediction_id = Column(String(36), primary_key=True, default=generate_uuid)
    inspection_id = Column(String(36), ForeignKey("inspections.inspection_id"), nullable=False)
    crop_identified = Column(String(80), default="Tomato")
    disease_name = Column(String(150), nullable=False)
    confidence = Column(Float, nullable=False)
    model_version = Column(String(100), default="AgriVision-Hybrid-v2.0")
    probabilities = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    inspection = relationship("Inspection", back_populates="predictions")


class InspectionImage(Base):
    __tablename__ = "inspection_images"

    image_id = Column(String(36), primary_key=True, default=generate_uuid)
    inspection_id = Column(String(36), ForeignKey("inspections.inspection_id"), nullable=False)
    original_url = Column(String(500), nullable=False)
    bbox_overlay_url = Column(String(500), nullable=True)
    mask_url = Column(String(500), nullable=True)
    heatmap_url = Column(String(500), nullable=True)

    inspection = relationship("Inspection", back_populates="images")


class WeatherRecord(Base):
    __tablename__ = "weather_records"

    record_id = Column(String(36), primary_key=True, default=generate_uuid)
    farm_id = Column(String(36), ForeignKey("farms.farm_id"), nullable=True)
    inspection_id = Column(String(36), ForeignKey("inspections.inspection_id"), nullable=True)
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    rainfall = Column(Float, nullable=False)
    wind_speed = Column(Float, default=5.0)
    risk_score = Column(Float, default=0.0)
    risk_level = Column(String(50), default="Low")
    recorded_at = Column(DateTime, default=datetime.utcnow)

    farm = relationship("Farm", back_populates="weather_records")
    inspection = relationship("Inspection", back_populates="weather")


class Notification(Base):
    __tablename__ = "notifications"

    notification_id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    title = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    alert_type = Column(String(50), default="disease_alert")  # "disease_alert", "weather_warning", "system"
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")


class ExpertFeedback(Base):
    __tablename__ = "expert_feedback"

    feedback_id = Column(String(36), primary_key=True, default=generate_uuid)
    inspection_id = Column(String(36), ForeignKey("inspections.inspection_id"), nullable=False)
    verified_disease = Column(String(150), nullable=False)
    agreement = Column(String(50), default="agree")
    comments = Column(Text, nullable=True)
    expert_name = Column(String(120), default="Agricultural Officer")
    submitted_at = Column(DateTime, default=datetime.utcnow)

    inspection = relationship("Inspection", back_populates="feedback")


class ModelVersion(Base):
    __tablename__ = "model_versions"

    model_id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(120), nullable=False)
    version = Column(String(50), nullable=False)
    framework = Column(String(80), default="PyTorch 2.0")
    metrics = Column(JSON, nullable=True)
    status = Column(String(50), default="production")


class ChatHistory(Base):
    __tablename__ = "chat_history"

    message_id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    language = Column(String(10), default="en")
    context_crop = Column(String(80), default="Tomato")
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="chat_logs")
