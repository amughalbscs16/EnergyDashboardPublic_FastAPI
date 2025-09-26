"""DR Planning Agent"""

from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
import json
import random
from pathlib import Path
from app.models.plan import DRStrategy

class DRPlanningAgent:
    """Intelligent agent for DR plan creation"""

    def __init__(self):
        self.data_dir = Path("data")

    def create_plan(
        self,
        window_start: datetime,
        window_end: datetime,
        strategy: DRStrategy,
        target_mw: Optional[float] = None,
        selected_cohorts: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create an optimized DR plan"""

        # Load current conditions
        ercot_data = self._load_ercot_data()
        cohorts = self._load_cohorts()

        # Filter cohorts if specified
        if selected_cohorts:
            cohorts = [c for c in cohorts if c["id"] in selected_cohorts]

        # Analyze situation
        situation = self._analyze_situation(ercot_data, window_start, window_end)

        # Determine target MW if not specified
        if not target_mw:
            target_mw = self._calculate_target_mw(situation, strategy)

        # Score and rank cohorts
        scored_cohorts = self._score_cohorts(
            cohorts, window_start, window_end, strategy, situation
        )

        # Allocate MW to cohorts
        allocations = self._allocate_mw(scored_cohorts, target_mw, strategy)

        # Calculate confidence
        confidence = self._calculate_confidence(allocations, situation)

        # Generate plan
        plan = {
            "id": f"DR_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "window_start": window_start.isoformat(),
            "window_end": window_end.isoformat(),
            "strategy": strategy,
            "status": "proposed",
            "target_mw_total": target_mw,
            "predicted_mw_total": sum(a["predicted_mw"] for a in allocations),
            "cohort_allocations": allocations,
            "confidence_score": confidence,
            "constraints_applied": self._get_applied_constraints(window_start),
            "explanation": self._generate_explanation(
                strategy, allocations, situation, confidence
            ),
            "situation_summary": situation
        }

        return plan

    def _load_ercot_data(self) -> Dict[str, Any]:
        """Load current ERCOT data"""
        try:
            with open(self.data_dir / "ercot" / "current_snapshot.json", "r") as f:
                snapshot = json.load(f)
            with open(self.data_dir / "ercot" / "forecast_24h.json", "r") as f:
                forecast = json.load(f)
            return {"snapshot": snapshot, "forecast": forecast}
        except:
            # Return error - real ERCOT data required
            return {
                "error": "ERCOT data not available",
                "note": "Real ERCOT data files not found. Integration with ERCOT API required."
            }

    def _load_cohorts(self) -> List[Dict[str, Any]]:
        """Load cohort data"""
        try:
            with open(self.data_dir / "cohorts" / "cohorts.json", "r") as f:
                return json.load(f)
        except:
            return []

    def _analyze_situation(
        self, ercot_data: Dict, window_start: datetime, window_end: datetime
    ) -> Dict[str, Any]:
        """Analyze grid situation for the window"""
        snapshot = ercot_data["snapshot"]
        forecast = ercot_data["forecast"]

        window_hour = window_start.hour

        return {
            "current_load_mw": snapshot.get("system_load_mw", 65000),
            "current_price": snapshot.get("price_per_mwh", 45),
            "reserves_mw": snapshot.get("reserves_mw", 15000),
            "forecast_peak_mw": forecast.get("peak_load_mw", 72000),
            "forecast_peak_hour": forecast.get("peak_hour", 17),
            "window_overlaps_peak": (
                forecast.get("peak_hour", 17) >= window_start.hour and
                forecast.get("peak_hour", 17) <= window_end.hour
            ),
            "stress_level": self._calculate_stress_level(snapshot, forecast)
        }

    def _calculate_stress_level(self, snapshot: Dict, forecast: Dict) -> str:
        """Calculate system stress level"""
        load = snapshot.get("system_load_mw", 65000)
        reserves = snapshot.get("reserves_mw", 15000)

        if reserves < 5000 or load > 75000:
            return "critical"
        elif reserves < 10000 or load > 70000:
            return "high"
        elif reserves < 15000 or load > 65000:
            return "moderate"
        else:
            return "low"

    def _calculate_target_mw(self, situation: Dict, strategy: DRStrategy) -> float:
        """Calculate target MW based on strategy"""
        base_target = 50.0  # Base MW target

        if strategy == DRStrategy.EMERGENCY:
            # Maximum available reduction
            return base_target * 3

        elif strategy == DRStrategy.RELIABILITY:
            # Based on reserve needs
            if situation["stress_level"] == "critical":
                return base_target * 2.5
            elif situation["stress_level"] == "high":
                return base_target * 2
            else:
                return base_target * 1.5

        elif strategy == DRStrategy.COST_MINIMIZE:
            # Based on price signals
            price = situation["current_price"]
            if price > 100:
                return base_target * 2
            elif price > 50:
                return base_target * 1.5
            else:
                return base_target

        else:  # BALANCED
            return base_target * 1.5

    def _score_cohorts(
        self,
        cohorts: List[Dict],
        window_start: datetime,
        window_end: datetime,
        strategy: DRStrategy,
        situation: Dict
    ) -> List[Dict[str, Any]]:
        """Score and rank cohorts for participation"""
        scored = []

        for cohort in cohorts:
            score = 0
            factors = {}

            # Check notice time
            hours_notice = (window_start - datetime.now(timezone.utc)).total_seconds() / 3600
            if hours_notice < cohort["min_notice_hours"]:
                continue  # Skip this cohort

            # Peak hours alignment
            window_hours = list(range(window_start.hour, window_end.hour + 1))
            peak_overlap = len(set(window_hours) & set(cohort["peak_hours"]))
            factors["peak_alignment"] = peak_overlap / len(window_hours) if window_hours else 0
            score += factors["peak_alignment"] * 30

            # Acceptance rate
            factors["acceptance"] = cohort["baseline_acceptance_rate"]
            score += factors["acceptance"] * 25

            # Flexibility magnitude
            flex_mw = cohort["num_accounts"] * cohort["flex_kw_per_account"] / 1000
            factors["flex_mw"] = flex_mw
            score += min(flex_mw / 10, 20)  # Cap at 20 points

            # Strategy-specific scoring
            if strategy == DRStrategy.COST_MINIMIZE:
                # Prefer commercial/industrial for cost
                if "commercial" in cohort["segment"] or "industrial" in cohort["segment"]:
                    score += 15
            elif strategy == DRStrategy.RELIABILITY:
                # Prefer reliable responders
                score += factors["acceptance"] * 15
            elif strategy == DRStrategy.EMERGENCY:
                # Prefer large, fast-responding
                if cohort["min_notice_hours"] <= 1:
                    score += 20

            scored.append({
                "cohort": cohort,
                "score": score,
                "factors": factors,
                "available_mw": flex_mw * factors["peak_alignment"] * factors["acceptance"]
            })

        # Sort by score
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored

    def _allocate_mw(
        self,
        scored_cohorts: List[Dict],
        target_mw: float,
        strategy: DRStrategy
    ) -> List[Dict[str, Any]]:
        """Allocate MW to cohorts"""
        allocations = []
        allocated_mw = 0

        for sc in scored_cohorts:
            if allocated_mw >= target_mw:
                break

            cohort = sc["cohort"]
            available = sc["available_mw"]

            # Determine allocation
            needed = target_mw - allocated_mw
            allocate = min(available, needed)

            # Apply strategy-specific adjustments
            if strategy == DRStrategy.BALANCED:
                # Don't over-burden any single cohort
                max_per_cohort = target_mw * 0.3
                allocate = min(allocate, max_per_cohort)

            # Predict actual response
            predicted = allocate * cohort["baseline_acceptance_rate"]  # Use actual acceptance rate

            allocations.append({
                "cohort_id": cohort["id"],
                "cohort_name": cohort["name"],
                "target_mw": round(allocate, 2),
                "predicted_mw": round(predicted, 2),
                "acceptance_probability": round(
                    cohort["baseline_acceptance_rate"] * sc["factors"]["peak_alignment"],
                    3
                ),
                "num_accounts": cohort["num_accounts"],
                "message_template": self._generate_message(cohort, allocate)
            })

            allocated_mw += allocate

        return allocations

    def _calculate_confidence(
        self, allocations: List[Dict], situation: Dict
    ) -> float:
        """Calculate overall plan confidence"""
        if not allocations:
            return 0.0

        # Base confidence
        confidence = 0.7

        # Adjust based on situation
        if situation["stress_level"] == "low":
            confidence += 0.1
        elif situation["stress_level"] == "critical":
            confidence -= 0.1

        # Adjust based on acceptance probabilities
        avg_acceptance = sum(a["acceptance_probability"] for a in allocations) / len(allocations)
        confidence = confidence * 0.7 + avg_acceptance * 0.3

        return round(min(max(confidence, 0.0), 1.0), 3)

    def _get_applied_constraints(self, window_start: datetime) -> List[str]:
        """Get list of constraints applied"""
        constraints = []

        hours_notice = (window_start - datetime.now(timezone.utc)).total_seconds() / 3600
        if hours_notice < 4:
            constraints.append("Short notice period")

        if window_start.hour >= 17 and window_start.hour <= 20:
            constraints.append("Peak hour window")

        constraints.append("Customer comfort limits enforced")
        constraints.append("Max weekly events checked")

        return constraints

    def _generate_message(self, cohort: Dict, target_mw: float) -> str:
        """Generate message template for cohort"""
        messages = {
            "residential_ev": f"Help balance the grid! Delay EV charging for 2 hours and earn rewards. Target: {target_mw:.1f} MW reduction.",
            "residential_solar": f"Grid needs your help! Export stored energy during peak hours. Target: {target_mw:.1f} MW support.",
            "commercial_hvac": f"Demand Response Event: Adjust HVAC setpoints by {cohort['comfort_limit_f']}°F. Target: {target_mw:.1f} MW reduction.",
            "industrial": f"Load reduction requested: {target_mw:.1f} MW needed. Shift non-critical operations to earn incentives."
        }

        segment = cohort["segment"]
        for key in messages:
            if key in segment:
                return messages[key]

        return f"Demand response event: {target_mw:.1f} MW reduction requested. Participate to earn rewards."

    def _generate_explanation(
        self,
        strategy: DRStrategy,
        allocations: List[Dict],
        situation: Dict,
        confidence: float
    ) -> str:
        """Generate human-readable explanation"""
        total_mw = sum(a["predicted_mw"] for a in allocations)
        num_accounts = sum(a["num_accounts"] for a in allocations)

        explanation = f"Strategy: {strategy.value.replace('_', ' ').title()}\n"
        explanation += f"System stress level: {situation['stress_level']}\n"
        explanation += f"Targeting {total_mw:.1f} MW reduction across {num_accounts:,} accounts\n"

        if situation["window_overlaps_peak"]:
            explanation += "Window overlaps with forecasted peak demand\n"

        explanation += f"Confidence level: {confidence:.1%}\n"

        if strategy == DRStrategy.COST_MINIMIZE:
            explanation += f"Current price: ${situation['current_price']:.2f}/MWh - targeting high-cost periods"
        elif strategy == DRStrategy.RELIABILITY:
            explanation += f"Reserve margin: {situation['reserves_mw']:.0f} MW - enhancing grid stability"
        elif strategy == DRStrategy.EMERGENCY:
            explanation += "EMERGENCY MODE - Maximum reduction requested"

        return explanation