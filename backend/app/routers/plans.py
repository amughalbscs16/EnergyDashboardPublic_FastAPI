"""DR Plans router"""

from fastapi import APIRouter, HTTPException, Body
from pathlib import Path
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.models.plan import DRPlanProposal, DRStrategy, PlanStatus
from app.agents.planner import DRPlanningAgent

router = APIRouter()

DATA_DIR = Path("data/plans")
DATA_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/propose")
async def propose_plan(proposal: DRPlanProposal) -> Dict[str, Any]:
    """Create a new DR plan proposal"""
    try:
        agent = DRPlanningAgent()

        # Create the plan
        plan = agent.create_plan(
            window_start=proposal.window_start,
            window_end=proposal.window_end,
            strategy=proposal.strategy,
            target_mw=proposal.target_mw,
            selected_cohorts=proposal.selected_cohorts
        )

        # Save plan
        plan_file = DATA_DIR / f"{plan['id']}.json"
        with open(plan_file, "w") as f:
            json.dump(plan, f, indent=2)

        return plan

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{plan_id}/approve")
async def approve_plan(
    plan_id: str,
    operator_id: str = Body(..., embed=True),
    notes: Optional[str] = Body(None, embed=True)
) -> Dict[str, Any]:
    """Approve a DR plan (HITL approval)"""
    try:
        plan_file = DATA_DIR / f"{plan_id}.json"
        if not plan_file.exists():
            raise HTTPException(status_code=404, detail="Plan not found")

        with open(plan_file, "r") as f:
            plan = json.load(f)

        # Update plan status
        plan["status"] = "approved"
        plan["approved_by"] = operator_id
        plan["approved_at"] = datetime.now().isoformat()
        if notes:
            plan["operator_notes"] = notes

        # Save updated plan
        with open(plan_file, "w") as f:
            json.dump(plan, f, indent=2)

        # In a real system, this would trigger signal dispatch
        # For demo, we'll simulate signal creation
        _create_signals(plan)

        return {
            "plan_id": plan_id,
            "status": "approved",
            "message": "Plan approved and signals dispatched",
            "predicted_mw": plan["predicted_mw_total"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{plan_id}/reject")
async def reject_plan(
    plan_id: str,
    operator_id: str = Body(..., embed=True),
    reason: str = Body(..., embed=True)
) -> Dict[str, Any]:
    """Reject a DR plan"""
    try:
        plan_file = DATA_DIR / f"{plan_id}.json"
        if not plan_file.exists():
            raise HTTPException(status_code=404, detail="Plan not found")

        with open(plan_file, "r") as f:
            plan = json.load(f)

        # Update plan status
        plan["status"] = "rejected"
        plan["rejected_by"] = operator_id
        plan["rejected_at"] = datetime.now().isoformat()
        plan["rejection_reason"] = reason

        # Save updated plan
        with open(plan_file, "w") as f:
            json.dump(plan, f, indent=2)

        return {
            "plan_id": plan_id,
            "status": "rejected",
            "message": "Plan rejected"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{plan_id}")
async def get_plan(plan_id: str) -> Dict[str, Any]:
    """Get specific plan details"""
    try:
        plan_file = DATA_DIR / f"{plan_id}.json"
        if not plan_file.exists():
            raise HTTPException(status_code=404, detail="Plan not found")

        with open(plan_file, "r") as f:
            return json.load(f)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def get_all_plans(
    status: Optional[str] = None,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """Get all plans with optional filtering"""
    try:
        plans = []

        # Read all plan files
        for plan_file in DATA_DIR.glob("*.json"):
            with open(plan_file, "r") as f:
                plan = json.load(f)

                # Filter by status if specified
                if status and plan.get("status") != status:
                    continue

                plans.append(plan)

        # Sort by creation time (newest first)
        plans.sort(key=lambda x: x.get("created_at", ""), reverse=True)

        return plans[:limit]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{plan_id}/status")
async def get_plan_status(plan_id: str) -> Dict[str, Any]:
    """Get plan execution status"""
    try:
        plan = await get_plan(plan_id)

        # Check signal responses
        signals_dir = Path("data/signals")
        responses = []

        if signals_dir.exists():
            for signal_file in signals_dir.glob(f"{plan_id}_*.json"):
                with open(signal_file, "r") as f:
                    signal = json.load(f)
                    if "response" in signal:
                        responses.append(signal["response"])

        # Calculate realized MW
        realized_mw = sum(r.get("committed_kw", 0) / 1000 for r in responses)

        return {
            "plan_id": plan_id,
            "status": plan["status"],
            "target_mw": plan["target_mw_total"],
            "predicted_mw": plan["predicted_mw_total"],
            "realized_mw": round(realized_mw, 2),
            "num_signals_sent": len(plan.get("cohort_allocations", [])),
            "num_responses": len(responses),
            "acceptance_rate": len([r for r in responses if r.get("accepted")]) / len(responses) if responses else 0
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def _create_signals(plan: Dict) -> None:
    """Create signals for approved plan (simulation)"""
    signals_dir = Path("data/signals")
    signals_dir.mkdir(parents=True, exist_ok=True)

    for allocation in plan.get("cohort_allocations", []):
        signal = {
            "id": f"SIG_{plan['id']}_{allocation['cohort_id']}",
            "plan_id": plan["id"],
            "cohort_id": allocation["cohort_id"],
            "signal_type": "dr_event",
            "created_at": datetime.now().isoformat(),
            "sent_at": datetime.now().isoformat(),
            "event_start": plan["window_start"],
            "event_end": plan["window_end"],
            "target_reduction_kw": allocation["target_mw"] * 1000,
            "message": allocation.get("message_template", "DR Event"),
            "status": "sent"
        }

        signal_file = signals_dir / f"{signal['id']}.json"
        with open(signal_file, "w") as f:
            json.dump(signal, f, indent=2)