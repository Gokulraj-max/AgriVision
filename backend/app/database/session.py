from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.core.config import DATABASE_URL
from backend.app.database.models import Base, User, Farm, Crop, CropCycle

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Seed default user
        user = db.query(User).first()
        if not user:
            user = User(
                user_id="farmer-patel-001",
                name="Ramesh Patel",
                email="ramesh.patel@agrivision.ai",
                phone="+91-9876543210",
                role="farmer"
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # Seed standard crops
        standard_crops = [
            ("Tomato", "Solanum lycopersicum", "Roma & Cherry Hybrid", "Vegetable"),
            ("Potato", "Solanum tuberosum", "Kufri Jyoti", "Tuber"),
            ("Rice", "Oryza sativa", "Basmati & IR64", "Cereal"),
            ("Cotton", "Gossypium hirsutum", "Bt Cotton Hybrid", "Cash Crop"),
            ("Maize", "Zea mays", "Single Cross Sweet Corn", "Cereal"),
            ("Pepper", "Capsicum annuum", "Bell & Chili Hybrid", "Spice"),
            ("Apple", "Malus domestica", "Red Delicious", "Fruit")
        ]
        for name, sci, var, cat in standard_crops:
            existing = db.query(Crop).filter(Crop.name == name).first()
            if not existing:
                db.add(Crop(name=name, scientific_name=sci, variety=var, category=cat))
        db.commit()

        # Seed default farms
        farm1 = db.query(Farm).filter(Farm.farm_id == "farm-north-block").first()
        if not farm1:
            farm1 = Farm(
                farm_id="farm-north-block",
                user_id=user.user_id,
                name="North Green Belt Polyhouse",
                location="Plot 4B, Nashik Agritech Zone, Maharashtra",
                latitude=19.9975,
                longitude=73.7898,
                area_hectares=6.2
            )
            farm2 = Farm(
                farm_id="farm-south-openfield",
                user_id=user.user_id,
                name="Cauvery Delta Paddy & Cotton Fields",
                location="Thanjavur Agro District, Tamil Nadu",
                latitude=10.7870,
                longitude=79.1378,
                area_hectares=14.0
            )
            db.add_all([farm1, farm2])
            db.commit()
    finally:
        db.close()
