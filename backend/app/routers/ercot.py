"""ERCOT data router with real data integration"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional
from ..services.simple_ercot_service import SimpleERCOTService

# Initialize simple ERCOT service for REAL DATA
ercot_service = SimpleERCOTService()

router = APIRouter()

@router.get("/current")
async def get_current_conditions() -> Dict[str, Any]:
    """Get current ERCOT system conditions"""
    try:
        return await ercot_service.get_current_conditions()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/forecast")
async def get_forecast(hours: int = Query(default=24, ge=1, le=168)) -> Dict[str, Any]:
    """Get ERCOT load forecast"""
    try:
        return await ercot_service.get_forecast()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/real-time-prices")
async def get_real_time_prices() -> Dict[str, Any]:
    """Get real-time LMP prices"""
    try:
        return await ercot_service.get_real_time_prices()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))