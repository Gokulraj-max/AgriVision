from typing import Optional
from fastapi import APIRouter, Query
from agrivision.services.weather_service import WeatherService

router = APIRouter(prefix="/api/v1/weather", tags=["Weather Risk"])

weather_svc = WeatherService()

@router.get("/risk")
def calculate_weather_risk(
    latitude: Optional[float] = Query(19.9975, description="Farm Latitude"),
    longitude: Optional[float] = Query(73.7898, description="Farm Longitude"),
    temperature: Optional[float] = Query(None, description="Custom Temperature in C"),
    humidity: Optional[float] = Query(None, description="Custom Humidity %"),
    rainfall: Optional[float] = Query(None, description="Custom Rainfall in mm"),
    growth_stage: Optional[str] = Query("Vegetative", description="Crop Growth Stage")
):
    """
    Retrieves meteorological observations (NASA POWER API)
    and computes disease risk probability and favorable conditions.
    """
    if temperature is None or humidity is None or rainfall is None:
        obs = weather_svc.fetch_nasa_power_weather(latitude, longitude)
        t = obs["temperature"]
        h = obs["humidity"]
        r = obs["rainfall"]
        source = obs["source"]
    else:
        t = temperature
        h = humidity
        r = rainfall
        source = "User_Microclimate_Input"

    risk_analysis = weather_svc.assess_risk(t, h, r, growth_stage)

    return {
        "source": source,
        "parameters": {
            "latitude": latitude,
            "longitude": longitude,
            "temperature": t,
            "humidity": h,
            "rainfall": r,
            "growth_stage": growth_stage
        },
        **risk_analysis
    }
