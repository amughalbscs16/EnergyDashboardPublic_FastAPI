"""Signal models for OpenADR-style messaging"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict
from enum import Enum

class SignalType(str, Enum):
    DR_EVENT = "dr_event"
    PRICE_SIGNAL = "price_signal"
    EMERGENCY = "emergency"
    TEST = "test"

class SignalStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    ACKNOWLEDGED = "acknowledged"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    COMPLETED = "completed"

class DRSignal(BaseModel):
    """OpenADR-style demand response signal"""
    id: str
    plan_id: str
    cohort_id: str
    signal_type: SignalType
    created_at: datetime
    sent_at: Optional[datetime] = None
    event_start: datetime
    event_end: datetime
    target_reduction_kw: float
    message: str
    status: SignalStatus
    metadata: Dict = Field(default_factory=dict)

class SignalResponse(BaseModel):
    """Response from simulated endpoint"""
    signal_id: str
    cohort_id: str
    responded_at: datetime
    accepted: bool
    participating_accounts: int
    committed_kw: float
    reason: Optional[str] = None