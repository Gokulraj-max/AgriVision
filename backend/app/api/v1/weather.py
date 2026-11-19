from fastapi import APIRouter, Query
from typing import Optional
from backend.app.services.weather_risk import WeatherRiskService

router = APIRouter(prefix="/weather", tags=["Weather Intelligence"])

@router.get("/risk")
def calculate_weather_risk(
    temperature: Optional[float] = Query(24.5, description="Temperature in C"),
    humidity: Optional[float] = Query(88.0, description="Relative Humidity %"),
    rainfall: Optional[float] = Query(12.4, description="Rainfall in mm"),
    wind_speed: Optional[float] = Query(8.5, description="Wind speed in km/h"),
    crop: Optional[str] = Query("Tomato", description="Crop species"),
    growth_stage: Optional[str] = Query("Fruiting", description="Crop growth stage"),
    lat: Optional[float] = Query(11.0168, description="Latitude"),
    lon: Optional[float] = Query(76.9558, description="Longitude")
):
    base_risk = WeatherRiskService.forecast_risk(
        temperature=temperature,
        humidity=humidity,
        rainfall=rainfall,
        wind_speed=wind_speed,
        crop=crop,
        growth_stage=growth_stage
    )
    
    current_data = {
        "temperature_c": temperature,
        "relative_humidity_pct": humidity,
        "precipitation_mm": rainfall,
        "wind_speed_kmh": wind_speed,
        "leaf_wetness_hours": round(humidity * 0.08, 1),
        "solar_radiation_mj": 14.2,
        "disease_risk_index": int(base_risk["risk_score"]),
        "risk_level": base_risk["risk_level"].upper(),
        "pathogen_alerts": [
            {
                "disease": f"{crop} Foliar Pathogen Pressure",
                "pathogen": "Fungus / Oomycete",
                "risk_level": base_risk["risk_level"].upper(),
                "favorable_factors": [
                    f"Relative Humidity ({humidity}%)",
                    f"Rainfall ({rainfall} mm)",
                    f"Temperature ({temperature}°C)"
                ]
            }
        ]
    }
    
    forecast_days = [
        {"date": "2026-11-15", "day_name": "Today", "temp_min": 20, "temp_max": 27, "humidity_pct": int(humidity), "rain_probability_pct": 75, "overall_risk": "HIGH", "alert_summary": "Prolonged leaf wetness window."},
        {"date": "2026-11-16", "day_name": "Tomorrow", "temp_min": 21, "temp_max": 28, "humidity_pct": 78, "rain_probability_pct": 40, "overall_risk": "MEDIUM", "alert_summary": "Afternoon drying window."},
        {"date": "2026-11-17", "day_name": "Wednesday", "temp_min": 22, "temp_max": 29, "humidity_pct": 68, "rain_probability_pct": 15, "overall_risk": "LOW", "alert_summary": "Optimal field scouting conditions."},
        {"date": "2026-11-18", "day_name": "Thursday", "temp_min": 21, "temp_max": 30, "humidity_pct": 65, "rain_probability_pct": 10, "overall_risk": "LOW", "alert_summary": "Dry canopy conditions."},
        {"date": "2026-11-19", "day_name": "Friday", "temp_min": 20, "temp_max": 28, "humidity_pct": 82, "rain_probability_pct": 60, "overall_risk": "MEDIUM", "alert_summary": "Evening precipitation expected."}
    ]

    return {
        **base_risk,
        "current": current_data,
        "forecast": forecast_days
    }

@router.get("/forecast")
def get_weather_forecast(farm_id: Optional[str] = None):
    """5-Day Agro-Meteorological Forecast with Optimal Scouting Windows."""
    return {
        "location": "Central Regional Agricultural Station",
        "days": [
            {"day": "Today", "temp": "28°C / 21°C", "humidity": "82%", "rain": "3.5 mm", "risk": "High", "scout_recommendation": "Inspect lower leaves today"},
            {"day": "Tomorrow", "temp": "29°C / 22°C", "humidity": "76%", "rain": "0.0 mm", "risk": "Moderate", "scout_recommendation": "Morning spraying window"},
            {"day": "Day 3", "temp": "31°C / 23°C", "humidity": "68%", "rain": "0.0 mm", "risk": "Low", "scout_recommendation": "Favorable condition"},
            {"day": "Day 4", "temp": "27°C / 20°C", "humidity": "88%", "rain": "12.0 mm", "risk": "Critical", "scout_recommendation": "High rain-splash risk; check drainage"},
            {"day": "Day 5", "temp": "26°C / 19°C", "humidity": "85%", "rain": "5.0 mm", "risk": "High", "scout_recommendation": "Immediate post-rain disease scouting"}
        ]
    }
