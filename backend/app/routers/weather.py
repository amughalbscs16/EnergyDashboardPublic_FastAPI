"""Weather data router with real NWS integration"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from ..services.real_weather_service import RealWeatherService

# Initialize real weather service
weather_service = RealWeatherService()

router = APIRouter()

@router.get("/{zip_code}")
async def get_weather(zip_code: str) -> Dict[str, Any]:
    """Get weather data for a ZIP code"""
    try:
        return await weather_service.get_weather(zip_code)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alerts/{state}")
async def get_weather_alerts(state: str = "TX") -> Dict[str, Any]:
    """Get weather alerts for Texas"""
    try:
        return await weather_service.get_weather_alerts(state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

