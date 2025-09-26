"""Service for tracking and analyzing plan execution history"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
from pathlib import Path
import uuid
from app.models.history import (
    PlanExecution, PlanPerformanceMetrics,
    ExecutionStatus, HistoricalSummary
)

class HistoryService:
    """Service for managing plan execution history"""

    def __init__(self):
        self.history_dir = Path("data/history")
        self.history_dir.mkdir(parents=True, exist_ok=True)
        self.executions_file = self.history_dir / "executions.json"
        self.metrics_file = self.history_dir / "metrics.json"

        # Load existing history
        self.executions = self._load_executions()
        self.metrics = self._load_metrics()

    def _load_executions(self) -> List[PlanExecution]:
        """Load execution history from file"""
        if self.executions_file.exists():
            with open(self.executions_file, "r") as f:
                data = json.load(f)
                return [PlanExecution(**e) for e in data]
        return []

    def _load_metrics(self) -> List[PlanPerformanceMetrics]:
        """Load performance metrics from file"""
        if self.metrics_file.exists():
            with open(self.metrics_file, "r") as f:
                data = json.load(f)
                return [PlanPerformanceMetrics(**m) for m in data]
        return []

    def _save_executions(self):
        """Save executions to file"""
        data = [e.dict() for e in self.executions]
        # Convert datetime to ISO format
        for d in data:
            d['execution_start'] = d['execution_start'].isoformat()
            if d['execution_end']:
                d['execution_end'] = d['execution_end'].isoformat()

        with open(self.executions_file, "w") as f:
            json.dump(data, f, indent=2)

    def _save_metrics(self):
        """Save metrics to file"""
        data = [m.dict() for m in self.metrics]
        with open(self.metrics_file, "w") as f:
            json.dump(data, f, indent=2)

    def start_execution(self, plan: Dict[str, Any], operator_id: str) -> PlanExecution:
        """Start tracking a plan execution"""
        execution = PlanExecution(
            id=f"EXEC_{uuid.uuid4().hex[:8]}",
            plan_id=plan['id'],
            execution_start=datetime.now(),
            status=ExecutionStatus.IN_PROGRESS,
            target_mw=plan['target_mw_total'],
            participating_accounts=sum(
                c['num_accounts'] for c in plan['cohort_allocations']
            ),
            total_accounts=sum(
                c['num_accounts'] for c in plan['cohort_allocations']
            ),
            strategy=plan['strategy'],
            operator_id=operator_id
        )

        self.executions.append(execution)
        self._save_executions()
        return execution

    def complete_execution(
        self,
        execution_id: str,
        achieved_mw: float,
        acceptance_rate: float,
        notes: Optional[str] = None
    ) -> PlanExecution:
        """Mark execution as complete"""
        execution = next((e for e in self.executions if e.id == execution_id), None)
        if not execution:
            raise ValueError(f"Execution {execution_id} not found")

        execution.execution_end = datetime.now()
        execution.status = ExecutionStatus.COMPLETED
        execution.achieved_mw = achieved_mw
        execution.acceptance_rate = acceptance_rate
        execution.notes = notes

        self._save_executions()

        # Calculate and save metrics
        self._calculate_metrics(execution)

        return execution

    def _calculate_metrics(self, execution: PlanExecution):
        """Calculate performance metrics for completed execution"""
        if execution.status != ExecutionStatus.COMPLETED:
            return

        duration = (execution.execution_end - execution.execution_start).total_seconds() / 60

        metrics = PlanPerformanceMetrics(
            plan_id=execution.plan_id,
            execution_id=execution.id,
            target_achievement_rate=execution.achieved_mw / execution.target_mw,
            response_time_minutes=duration * 0.2,  # Simulated quick response
            sustained_minutes=duration * 0.8,
            initial_acceptance_rate=0.6,
            final_participation_rate=execution.acceptance_rate,
            dropout_rate=0.1,
            cost_per_mw=15.5,  # $15.50 per MW
            total_incentives_paid=execution.achieved_mw * 15.5,
            avoided_cost=execution.achieved_mw * 150,  # $150/MW avoided
            peak_reduction_mw=execution.achieved_mw,
            frequency_improvement=0.002,  # 0.002 Hz improvement
            reserves_freed_mw=execution.achieved_mw * 0.3
        )

        self.metrics.append(metrics)
        self._save_metrics()

    def get_historical_summary(self, days: int = 30) -> HistoricalSummary:
        """Get summary statistics for historical performance"""
        cutoff = datetime.now() - timedelta(days=days)
        recent_executions = [
            e for e in self.executions
            if e.execution_start >= cutoff
        ]

        if not recent_executions:
            return HistoricalSummary(
                total_plans=0,
                successful_plans=0,
                failed_plans=0,
                average_achievement_rate=0,
                average_response_time=0,
                total_mw_reduced=0,
                total_cost_avoided=0,
                best_performing_cohorts=[],
                peak_reduction_achieved=0
            )

        successful = [e for e in recent_executions if e.status == ExecutionStatus.COMPLETED]
        failed = [e for e in recent_executions if e.status == ExecutionStatus.FAILED]

        total_mw = sum(e.achieved_mw or 0 for e in successful)
        avg_achievement = sum(
            (e.achieved_mw or 0) / e.target_mw for e in successful
        ) / len(successful) if successful else 0

        # Calculate cohort performance
        cohort_stats = {}
        for e in successful:
            if e.metrics and 'cohorts' in e.metrics:
                for cohort in e.metrics['cohorts']:
                    cid = cohort['id']
                    if cid not in cohort_stats:
                        cohort_stats[cid] = {
                            'name': cohort['name'],
                            'total_mw': 0,
                            'count': 0
                        }
                    cohort_stats[cid]['total_mw'] += cohort.get('achieved_mw', 0)
                    cohort_stats[cid]['count'] += 1

        best_cohorts = sorted(
            [
                {
                    'id': k,
                    'name': v['name'],
                    'average_mw': v['total_mw'] / v['count']
                }
                for k, v in cohort_stats.items()
            ],
            key=lambda x: x['average_mw'],
            reverse=True
        )[:3]

        return HistoricalSummary(
            total_plans=len(recent_executions),
            successful_plans=len(successful),
            failed_plans=len(failed),
            average_achievement_rate=avg_achievement,
            average_response_time=15.5,  # minutes
            total_mw_reduced=total_mw,
            total_cost_avoided=total_mw * 150,
            best_performing_cohorts=best_cohorts,
            peak_reduction_achieved=max(
                (e.achieved_mw or 0 for e in successful), default=0
            )
        )

    def get_execution_history(
        self,
        limit: int = 100,
        status: Optional[ExecutionStatus] = None
    ) -> List[PlanExecution]:
        """Get execution history with optional filtering"""
        executions = self.executions

        if status:
            executions = [e for e in executions if e.status == status]

        # Sort by start time, most recent first
        executions.sort(key=lambda e: e.execution_start, reverse=True)

        return executions[:limit]