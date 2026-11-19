import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
BACKEND_DIR = BASE_DIR / "backend"
UPLOAD_DIR = BACKEND_DIR / "uploads"
ARTIFACTS_DIR = BACKEND_DIR / "artifacts"
STATIC_DIR = BACKEND_DIR / "app" / "static"

for d in [UPLOAD_DIR, ARTIFACTS_DIR, STATIC_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Database
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/agrivision_2.db")

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "agrivision-enterprise-secure-jwt-key-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# Supported Crops
SUPPORTED_CROPS = ["Tomato", "Potato", "Rice", "Cotton", "Maize", "Pepper", "Apple"]
