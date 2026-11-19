import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
APP_DIR = BASE_DIR / "agrivision"
UPLOAD_DIR = BASE_DIR / "uploads"
SAMPLES_DIR = BASE_DIR / "samples"
STATIC_DIR = APP_DIR / "static"
WEIGHTS_DIR = BASE_DIR / "weights"

# Create required directories
for directory in [UPLOAD_DIR, SAMPLES_DIR, STATIC_DIR, WEIGHTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Database
# Default to SQLite for zero-config local run, supports PostgreSQL via env
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/agrivision.db")

# Classification Classes (Standard PlantVillage Tomato Categories)
DISEASE_CLASSES = [
    "Tomato___healthy",
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___Bacterial_spot",
    "Tomato___Septoria_leaf_spot",
    "Tomato___Leaf_Mold",
    "Tomato___Spider_mites_Two_spotted_spider_mite",
    "Tomato___Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato___Tomato_mosaic_virus"
]

DISEASE_DISPLAY_NAMES = {
    "Tomato___healthy": "Healthy Tomato Leaf",
    "Tomato___Early_blight": "Early Blight (Alternaria solani)",
    "Tomato___Late_blight": "Late Blight (Phytophthora infestans)",
    "Tomato___Bacterial_spot": "Bacterial Spot (Xanthomonas)",
    "Tomato___Septoria_leaf_spot": "Septoria Leaf Spot",
    "Tomato___Leaf_Mold": "Leaf Mold (Passalora fulva)",
    "Tomato___Spider_mites_Two_spotted_spider_mite": "Spider Mites Infestation",
    "Tomato___Target_Spot": "Target Spot (Corynespora cassiicola)",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": "Tomato Yellow Leaf Curl Virus (TYLCV)",
    "Tomato___Tomato_mosaic_virus": "Tomato Mosaic Virus (ToMV)",
    "Unknown___needs_expert_review": "Uncertain / Needs Agricultural Expert Review"
}

# Thresholds
CONFIDENCE_THRESHOLD = 0.60  # Below this, flag as "needs expert review"
IMAGE_SIZE = (224, 224)
UNET_INPUT_SIZE = (256, 256)

# NASA POWER API Endpoint
NASA_POWER_API_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
