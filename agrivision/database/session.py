from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from agrivision.config import DATABASE_URL
from agrivision.database.models import Base, User, Farm

# SQLite compatibility check
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
        # Check if default user exists
        user = db.query(User).first()
        if not user:
            user = User(
                user_id="default-user-001",
                name="Ramesh Patel (Lead Farmer)",
                email="ramesh.patel@agrivision.ai",
                role="farmer"
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # Check if default farms exist
        farm1 = db.query(Farm).filter(Farm.farm_id == "farm-north-block").first()
        if not farm1:
            farm1 = Farm(
                farm_id="farm-north-block",
                user_id=user.user_id,
                name="North Greenhouse Block A",
                crop_type="Tomato (Solanum lycopersicum)",
                location="Sector 4B, Nashik Agro Belt",
                latitude=19.9975,
                longitude=73.7898
            )
            farm2 = Farm(
                farm_id="farm-south-openfield",
                user_id=user.user_id,
                name="South Open Horizon Fields",
                crop_type="Tomato (Heirloom & Roma)",
                location="Plot 12, Pune Agritech Zone",
                latitude=18.5204,
                longitude=73.8567
            )
            db.add_all([farm1, farm2])
            db.commit()
    finally:
        db.close()
