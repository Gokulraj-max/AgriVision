from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from agrivision.config import UPLOAD_DIR, SAMPLES_DIR, STATIC_DIR
from agrivision.database.session import init_db
from agrivision.api import (
    routes_inspection,
    routes_farm,
    routes_feedback,
    routes_models,
    routes_weather,
    routes_samples
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="AgriVision AI — Intelligent Crop Diagnostic & Health Platform",
    description="Multi-model AI for plant disease classification, YOLO symptom localization, U-Net segmentation, and meteorological risk assessment.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static and media mountings
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
app.mount("/samples", StaticFiles(directory=str(SAMPLES_DIR)), name="samples")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Include Routers
app.include_router(routes_inspection.router)
app.include_router(routes_farm.router)
app.include_router(routes_feedback.router)
app.include_router(routes_models.router)
app.include_router(routes_weather.router)
app.include_router(routes_samples.router)

@app.get("/")
def serve_dashboard():
    return FileResponse(STATIC_DIR / "index.html")

@app.get("/health")
def healthcheck():
    return {"status": "healthy", "service": "AgriVision AI", "version": "1.0.0"}
