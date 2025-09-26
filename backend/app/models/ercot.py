"""ERCOT data models"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class ERCOTSnapshot(BaseModel):
    """Current ERCOT system conditions"""
    timestamp: datetime
    system_load_mw: float = Field(..., description="Current system load in MW")
    capacity_mw: float = Field(..., description="Available capacity in MW")
    reserves_mw: float = Field(..., description="Operating reserves in MW")
    price_per_mwh: float = Field(..., description="Current price per MWh")
    frequency_hz: float = Field(default=60.0, description="System frequency")
    generation_mix: dict = Field(default_factory=dict, description="Generation by fuel type")
    congestion_zones: List[str] = Field(default_factory=list, description="Congested zones")

class ERCOTForecast(BaseModel):
    """ERCOT load forecast"""
    timestamp: datetime
    forecast_hours: List[int]
    load_forecast_mw: List[float]
    price_forecast_mwh: List[float]
    peak_hour: int
    peak_load_mw: float
    confidence: float = Field(default=0.95, ge=0, le=1)