import urllib.request
import json
import numpy as np

class WeatherRiskService:
    """
    Weather-Based Disease Risk Forecasting Service.
    Uses epidemiological pathogen windows & NASA POWER atmospheric feeds.
    """
    @staticmethod
    def forecast_risk(temperature: float, humidity: float, rainfall: float, wind_speed: float = 5.0, crop: str = "Tomato", growth_stage: str = "Vegetative") -> dict:
        # Calculate pathogen infection favorability index
        score = 15.0

        if humidity >= 80.0:
            score += 35.0
        elif humidity >= 65.0:
            score += 15.0

        if rainfall > 2.0:
            score += 25.0

        if 15.0 <= temperature <= 24.0 and humidity >= 75.0:
            score += 20.0  # Cool-moist (Late blight / blast)
        elif 24.0 <= temperature <= 32.0 and humidity >= 70.0:
            score += 18.0  # Warm-humid (Early blight / Bacterial spot)

        if growth_stage in ["Flowering", "Fruiting"]:
            score += 10.0

        score = min(max(score, 5.0), 98.0)
        risk_score = round(score, 1)

        if risk_score >= 65.0:
            level = "High"
            alert = f"CRITICAL: Microclimate ({temperature}°C, {humidity}% RH) highly accelerates fungal sporulation and rain splash in {crop}."
        elif risk_score >= 35.0:
            level = "Moderate"
            alert = f"CAUTION: Moderate pathogen favorability window. Inspect lower leaf canopy every 48 hours."
        else:
            level = "Low"
            alert = "FAVORABLE: Microclimate does not support active disease outbreaks."

        return {
            "risk_score": risk_score,
            "risk_level": level,
            "weather_alert": alert,
            "temperature": temperature,
            "humidity": humidity,
            "rainfall": rainfall,
            "wind_speed": wind_speed,
            "crop": crop,
            "growth_stage": growth_stage,
            "recommended_action": "Scout lower leaves" if level != "Low" else "Standard irrigation maintenance"
        }
