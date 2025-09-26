"""Weather data models"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class WeatherData(BaseModel):
    """Current weather conditions"""
    timestamp: datetime
    zip_code: str
    temperature_f: float
    humidity_pct: float
    cloud_cover_pct: float
    wind_speed_mph: float
    conditions: str
    heat_index_f: Optional[float] = None

class WeatherForecast(BaseModel):
    """Weather forecast for planning"""
    timestamp: datetime
    zip_code: str
    forecast_hours: List[int]
    temperatures_f: List[float]
    conditions: List[str]
    cloud_cover_pct: List[float]
    peak_temp_f: float
    peak_temp_hour: int