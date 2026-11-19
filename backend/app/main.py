from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import UPLOAD_DIR, STATIC_DIR
from backend.app.database.session import init_db
from backend.app.api.v1 import (
    auth,
    farms,
    crops,
    ai,
    live,
    inspections,
    weather,
    assistant,
    feedback,
    reports
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="AgriVision AI 2.0 — Real-Time Smart Agriculture Platform",
    description="Multi-Crop Disease Detection, Live Camera Scanner, Tamil/English Voice Assistant & Decision Support.",
    version="2.0.0",
    lifespan=lifespan
)

# CORS (Development enabled for React Native mobile client & browser)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static and media mountings
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Mount API v1 Routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(farms.router, prefix="/api/v1")
app.include_router(crops.router, prefix="/api/v1")
app.include_router(ai.router, prefix="/api/v1")
app.include_router(live.router, prefix="/api/v1")
app.include_router(inspections.router, prefix="/api/v1")
app.include_router(weather.router, prefix="/api/v1")
app.include_router(assistant.router, prefix="/api/v1")
app.include_router(feedback.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")

@app.api_route("/", methods=["GET", "HEAD"])
def serve_dashboard():
    return FileResponse(STATIC_DIR / "index.html")

@app.api_route("/mobile", methods=["GET", "HEAD"])
def serve_mobile_simulator():
    return FileResponse(STATIC_DIR / "index.html")

@app.api_route("/health", methods=["GET", "HEAD"])
def healthcheck():
    return {
        "status": "healthy",
        "platform": "AgriVision AI 2.0",
        "version": "2.0.0",
        "supported_crops": ["Tomato", "Potato", "Rice", "Cotton", "Maize", "Pepper", "Apple"],
        "multilingual_voice": ["en", "ta"]
    }
