"""Customer cohort models"""

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class CustomerSegment(str, Enum):
    RESIDENTIAL_EV = "residential_ev"
    RESIDENTIAL_SOLAR = "residential_solar"
    RESIDENTIAL_STANDARD = "residential_standard"
    COMMERCIAL_HVAC = "commercial_hvac"
    COMMERCIAL_LIGHTING = "commercial_lighting"
    INDUSTRIAL = "industrial"

class Cohort(BaseModel):
    """Customer cohort definition"""
    id: str
    name: str
    segment: CustomerSegment
    zip_codes: List[str]
    num_accounts: int
    avg_consumption_kwh: float
    flex_kw_per_account: float = Field(..., description="Flexible load per account")
    peak_hours: List[int] = Field(..., description="Typical peak usage hours")
    baseline_acceptance_rate: float = Field(..., ge=0, le=1)
    comfort_limit_f: float = Field(default=2.0, description="Max HVAC adjustment")
    max_events_per_week: int = Field(default=3)
    min_notice_hours: float = Field(default=1.0)

class CohortFlexibility(BaseModel):
    """Cohort flexibility assessment"""
    cohort_id: str
    available_mw: float
    confidence: float = Field(..., ge=0, le=1)
    constraints: List[str] = Field(default_factory=list)
    participation_estimate: float = Field(..., ge=0, le=1)