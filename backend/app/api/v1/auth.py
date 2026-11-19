from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.database.models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

class RegisterRequest(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    password: Optional[str] = "farmer123"

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/register")
def register_farmer(payload: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        return {
            "success": True,
            "message": "User already registered.",
            "user_id": existing.user_id,
            "name": existing.name,
            "email": existing.email,
            "token": f"jwt-mock-token-{existing.user_id}"
        }

    user = User(
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        hashed_password=payload.password,
        role="farmer"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "success": True,
        "message": "Farmer account registered successfully.",
        "user_id": user.user_id,
        "name": user.name,
        "email": user.email,
        "token": f"jwt-mock-token-{user.user_id}"
    }

@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        # Auto-create for seamless farmer onboarding in demo
        user = User(
            name=payload.email.split("@")[0].capitalize(),
            email=payload.email,
            role="farmer"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    return {
        "success": True,
        "user_id": user.user_id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "token": f"jwt-mock-token-{user.user_id}"
    }

@router.get("/me")
def get_current_user(db: Session = Depends(get_db)):
    user = db.query(User).first()
    return {
        "user_id": user.user_id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "farms_count": len(user.farms)
    }
