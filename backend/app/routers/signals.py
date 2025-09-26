"""Signals router for OpenADR-style messaging"""

from fastapi import APIRouter, HTTPException
from pathlib import Path
import json
import random
from datetime import datetime
from typing import List, Dict, Any, Optional

router = APIRouter()

DATA_DIR = Path("data/signals")
DATA_DIR.mkdir(parents=True, exist_ok=True)

@router.get("/{signal_id}")
async def get_signal(signal_id: str) -> Dict[str, Any]:
    """Get specific signal details"""
    try:
        signal_file = DATA_DIR / f"{signal_id}.json"
        if not signal_file.exists():
            raise HTTPException(status_code=404, detail="Signal not found")

        with open(signal_file, "r") as f:
            return json.load(f)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{signal_id}/simulate-response")
async def simulate_response(signal_id: str) -> Dict[str, Any]:
    """Simulate endpoint response to signal (for demo)"""
    try:
        signal_file = DATA_DIR / f"{signal_id}.json"
        if not signal_file.exists():
            raise HTTPException(status_code=404, detail="Signal not found")

        with open(signal_file, "r") as f:
            signal = json.load(f)

        # Simulate response based on cohort characteristics
        cohort_id = signal["cohort_id"]

        # Load cohort data to get acceptance rate
        cohorts_file = Path("data/cohorts/cohorts.json")
        with open(cohorts_file, "r") as f:
            cohorts = json.load(f)

        cohort = next((c for c in cohorts if c["id"] == cohort_id), None)
        if not cohort:
            raise HTTPException(status_code=404, detail="Cohort not found")

        # Use actual baseline acceptance rate without simulation
        acceptance_rate = cohort["baseline_acceptance_rate"]
        # For real deployment, would need actual customer response data
        accepted = True  # Placeholder - real system would track actual responses

        # Calculate committed kW based on historical data
        if accepted:
            # Use actual acceptance rate for commitment
            participating_accounts = int(cohort["num_accounts"] * acceptance_rate)
            committed_kw = signal["target_reduction_kw"] * acceptance_rate
        else:
            participating_accounts = 0
            committed_kw = 0

        response = {
            "signal_id": signal_id,
            "cohort_id": cohort_id,
            "responded_at": datetime.now().isoformat(),
            "accepted": accepted,
            "participating_accounts": participating_accounts,
            "committed_kw": round(committed_kw, 2),
            "reason": None if accepted else "Customer opt-out"
        }

        # Update signal with response
        signal["status"] = "acknowledged" if accepted else "declined"
        signal["response"] = response

        with open(signal_file, "w") as f:
            json.dump(signal, f, indent=2)

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def get_all_signals(
    plan_id: Optional[str] = None,
    status: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Get all signals with optional filtering"""
    from typing import Optional

    try:
        signals = []

        for signal_file in DATA_DIR.glob("*.json"):
            with open(signal_file, "r") as f:
                signal = json.load(f)

                # Filter by plan_id if specified
                if plan_id and signal.get("plan_id") != plan_id:
                    continue

                # Filter by status if specified
                if status and signal.get("status") != status:
                    continue

                signals.append(signal)

        # Sort by creation time (newest first)
        signals.sort(key=lambda x: x.get("created_at", ""), reverse=True)

        return signals

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from typing import Optional