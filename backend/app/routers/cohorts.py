"""Cohorts router - CONFIGURATION DATA ONLY

NOTE: This router returns customer cohort configuration data.
Actual customer participation requires real demand response integration.
"""

from fastapi import APIRouter, HTTPException
from pathlib import Path
import json
from typing import List, Dict, Any

router = APIRouter()

DATA_DIR = Path("data/cohorts")

@router.get("/")
async def get_all_cohorts() -> List[Dict[str, Any]]:
    """Get all customer cohorts (CONFIGURATION DATA)"""
    try:
        cohorts_file = DATA_DIR / "cohorts.json"
        if not cohorts_file.exists():
            raise HTTPException(status_code=404, detail="Cohorts not found")

        with open(cohorts_file, "r") as f:
            cohorts = json.load(f)
            return [
                {
                    **cohort,
                    "DATA_TYPE": "ARTI DATA - CONFIGURATION",
                    "data_type": "CONFIGURATION",
                    "note": "This is ARTI DATA - cohort configuration. Real DR participation requires actual customer enrollment."
                }
                for cohort in cohorts
            ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary")
async def get_cohorts_summary() -> Dict[str, Any]:
    """Get cohorts summary statistics (CONFIGURATION DATA)"""
    try:
        summary_file = DATA_DIR / "summary.json"
        if not summary_file.exists():
            # Generate summary from cohorts
            cohorts = await get_all_cohorts()
            total_flex_mw = sum(
                c["num_accounts"] * c["flex_kw_per_account"] / 1000
                for c in cohorts
            )
            summary = {
                "total_cohorts": len(cohorts),
                "total_accounts": sum(c["num_accounts"] for c in cohorts),
                "total_flex_mw": round(total_flex_mw, 2),
                "by_segment": {}
            }

            # Group by segment
            for cohort in cohorts:
                segment = cohort["segment"]
                if segment not in summary["by_segment"]:
                    summary["by_segment"][segment] = {
                        "count": 0,
                        "accounts": 0,
                        "flex_mw": 0
                    }
                summary["by_segment"][segment]["count"] += 1
                summary["by_segment"][segment]["accounts"] += cohort["num_accounts"]
                summary["by_segment"][segment]["flex_mw"] += (
                    cohort["num_accounts"] * cohort["flex_kw_per_account"] / 1000
                )

            return summary

        with open(summary_file, "r") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{cohort_id}")
async def get_cohort(cohort_id: str) -> Dict[str, Any]:
    """Get specific cohort details"""
    cohorts = await get_all_cohorts()
    for cohort in cohorts:
        if cohort["id"] == cohort_id:
            return {
                **cohort,
                "data_type": "CONFIGURATION",
                "note": "This is cohort configuration. Real DR participation requires actual customer enrollment."
            }
    raise HTTPException(status_code=404, detail=f"Cohort {cohort_id} not found")

@router.get("/{cohort_id}/flexibility")
async def get_cohort_flexibility(cohort_id: str) -> Dict[str, Any]:
    """Get cohort flexibility assessment (ESTIMATED FROM CONFIG)"""
    cohort = await get_cohort(cohort_id)

    # Calculate current flexibility based on time of day
    from datetime import datetime
    hour = datetime.now().hour

    # Check if current hour is in peak hours
    in_peak = hour in cohort["peak_hours"]
    availability = 0.9 if in_peak else 0.5

    available_mw = (
        cohort["num_accounts"] *
        cohort["flex_kw_per_account"] *
        availability / 1000
    )

    return {
        "cohort_id": cohort_id,
        "available_mw": round(available_mw, 2),
        "confidence": 0.85 if in_peak else 0.65,
        "constraints": [
            f"Max {cohort['max_events_per_week']} events per week",
            f"Min {cohort['min_notice_hours']} hours notice",
            f"Comfort limit {cohort['comfort_limit_f']}°F" if cohort['comfort_limit_f'] > 0 else None
        ],
        "participation_estimate": cohort["baseline_acceptance_rate"] * availability,
        "data_type": "CONFIGURATION_BASED_ESTIMATE",
        "note": "Flexibility estimate based on configuration. Real availability requires actual customer signals."
    }