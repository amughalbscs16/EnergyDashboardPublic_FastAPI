"""DER management router"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from ..services.der_service import DERService
from ..services.real_ercot_service import RealERCOTService
from ..services.real_weather_service import RealWeatherService

router = APIRouter()
der_service = DERService()
ercot_service = RealERCOTService()
weather_service = RealWeatherService()

@router.get("/portfolio")
async def get_der_portfolio() -> Dict[str, Any]:
    """Get current DER portfolio status"""
    try:
        return await der_service.get_der_portfolio()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/solar/forecast")
async def get_solar_forecast() -> Dict[str, Any]:
    """Get solar generation forecast based on weather"""
    try:
        # Get real weather data
        weather_data = await weather_service.get_weather("78701")
        return await der_service.predict_solar_generation(weather_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/grid/stress")
async def get_grid_stress() -> Dict[str, Any]:
    """Analyze current grid stress level"""
    try:
        # Get real ERCOT data
        ercot_data = await ercot_service.get_current_conditions()
        return await der_service.analyze_grid_stress(ercot_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dispatch/schedule")
async def get_dispatch_schedule(hours: int = 24) -> Dict[str, Any]:
    """Get optimal DER dispatch schedule"""
    try:
        return await der_service.generate_dispatch_schedule(hours)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics")
async def get_der_metrics(period: str = "today") -> Dict[str, Any]:
    """Get DER performance metrics"""
    try:
        return await der_service.calculate_der_metrics(period)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ml/features")
async def get_ml_features() -> Dict[str, Any]:
    """Get current features for ML models"""
    try:
        # Combine all data sources for ML
        ercot_data = await ercot_service.get_current_conditions()
        weather_data = await weather_service.get_weather("78701")
        portfolio = await der_service.get_der_portfolio()
        stress = await der_service.analyze_grid_stress(ercot_data)
        solar = await der_service.predict_solar_generation(weather_data)

        return {
            "features": {
                "grid": {
                    "load_mw": ercot_data.get("system_load_mw"),
                    "price_per_mwh": ercot_data.get("price_per_mwh"),
                    "reserves_mw": ercot_data.get("reserves_mw"),
                    "stress_score": stress.get("stress_score")
                },
                "weather": {
                    "temperature_f": weather_data.get("temperature_f"),
                    "humidity": weather_data.get("humidity"),
                    "wind_speed": weather_data.get("wind_speed", 10),
                    "cloud_cover": weather_data.get("cloud_cover", 30)
                },
                "der": {
                    "total_capacity_mw": portfolio.get("total_der_capacity_mw"),
                    "available_capacity_mw": portfolio.get("available_capacity_mw"),
                    "solar_output_mw": solar.get("current_prediction_mw")
                }
            },
            "target_variables": {
                "optimal_dispatch_mw": stress.get("recommended_der_activation_mw"),
                "stress_level": stress.get("stress_level")
            },
            "timestamp": ercot_data.get("timestamp")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))