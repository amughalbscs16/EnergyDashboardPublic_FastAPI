"""Plan execution history models"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum

class ExecutionStatus(str, Enum):
    """Plan execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class PlanExecution(BaseModel):
    """Model for tracking plan execution history"""
    id: str
    plan_id: str
    execution_start: datetime
    execution_end: Optional[datetime] = None
    status: ExecutionStatus
    target_mw: float
    achieved_mw: Optional[float] = None
    participating_accounts: int
    total_accounts: int
    acceptance_rate: Optional[float] = None
    strategy: str
    operator_id: str
    notes: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None

class PlanPerformanceMetrics(BaseModel):
    """Performance metrics for executed plans"""
    plan_id: str
    execution_id: str

    # Performance metrics
    target_achievement_rate: float  # achieved_mw / target_mw
    response_time_minutes: float  # Time to reach target
    sustained_minutes: float  # How long reduction was maintained

    # Participation metrics
    initial_acceptance_rate: float
    final_participation_rate: float
    dropout_rate: float

    # Financial metrics
    cost_per_mw: float
    total_incentives_paid: float
    avoided_cost: float  # Cost avoided by DR vs peaking plants

    # Grid impact
    peak_reduction_mw: float
    frequency_improvement: float
    reserves_freed_mw: float

class HistoricalSummary(BaseModel):
    """Summary statistics for historical performance"""
    total_plans: int
    successful_plans: int
    failed_plans: int
    average_achievement_rate: float
    average_response_time: float
    total_mw_reduced: float
    total_cost_avoided: float
    best_performing_cohorts: List[Dict[str, Any]]
    peak_reduction_achieved: float