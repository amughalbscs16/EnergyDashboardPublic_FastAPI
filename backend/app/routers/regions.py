"""Regional data router for Texas cities"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from ..config.regions import get_region_by_name, get_all_regions, TEXAS_REGIONS
from ..services.real_weather_service import RealWeatherService
from ..services.real_ercot_service import RealERCOTService

router = APIRouter()

# Initialize services
weather_service = RealWeatherService()
ercot_service = RealERCOTService()

@router.get("/")
async def get_all_regions_data() -> List[str]:
    """Get list of all available regions"""
    return get_all_regions()

@router.get("/compare/weather")
async def compare_all_regions_weather() -> Dict[str, Any]:
    """Get weather comparison across all major Texas cities"""
    all_weather = {}

    for region_key, region_data in TEXAS_REGIONS.items():
        try:
            weather_data = await weather_service.get_weather(region_data["primary_zip"])
            all_weather[region_key] = {
                "city": region_data["name"],
                "weather": weather_data
            }
        except Exception as e:
            all_weather[region_key] = {
                "city": region_data["name"],
                "error": str(e)
            }

    return {
        "regions": all_weather,
        "grid_data": await ercot_service.get_current_conditions()
    }

@router.get("/{region_name}")
async def get_region_data(region_name: str) -> Dict[str, Any]:
    """Get comprehensive data for a specific region"""
    region = get_region_by_name(region_name)
    if not region:
        raise HTTPException(status_code=404, detail=f"Region '{region_name}' not found")

    try:
        # Get weather data for this region
        weather_data = await weather_service.get_weather(region["primary_zip"])

        # ERCOT data is grid-wide for now (no regional breakdown available)
        ercot_data = await ercot_service.get_current_conditions()

        return {
            "region": region,
            "weather": weather_data,
            "grid_data": ercot_data,
            "last_updated": weather_data.get("timestamp", "unknown")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{region_name}/weather")
async def get_region_weather(region_name: str) -> Dict[str, Any]:
    """Get weather data for a specific region"""
    region = get_region_by_name(region_name)
    if not region:
        raise HTTPException(status_code=404, detail=f"Region '{region_name}' not found")

    try:
        weather_data = await weather_service.get_weather(region["primary_zip"])
        return {
            "region_name": region["name"],
            "weather": weather_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))