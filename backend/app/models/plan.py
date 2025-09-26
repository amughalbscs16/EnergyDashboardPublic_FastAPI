"""DR Plan models"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict
from enum import Enum

class DRStrategy(str, Enum):
    COST_MINIMIZE = "cost_minimize"
    RELIABILITY = "reliability"
    BALANCED = "balanced"
    EMERGENCY = "emergency"

class PlanStatus(str, Enum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class CohortAllocation(BaseModel):
    """MW allocation for a cohort"""
    cohort_id: str
    target_mw: float
    predicted_mw: float
    acceptance_probability: float
    message_template: Optional[str] = None

class DRPlan(BaseModel):
    """Demand Response Plan"""
    id: str
    created_at: datetime
    window_start: datetime
    window_end: datetime
    strategy: DRStrategy
    status: PlanStatus
    target_mw_total: float
    predicted_mw_total: float
    cohort_allocations: List[CohortAllocation]
    operator_notes: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    confidence_score: float = Field(..., ge=0, le=1)
    constraints_applied: List[str] = Field(default_factory=list)

class DRPlanProposal(BaseModel):
    """Request to create a DR plan"""
    window_start: datetime
    window_end: datetime
    strategy: DRStrategy
    target_mw: Optional[float] = None
    selected_cohorts: Optional[List[str]] = None
    operator_id: str