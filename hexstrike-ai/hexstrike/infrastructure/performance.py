"""
HexStrike AI - Performance Dashboard
"""
import time
import threading
from typing import Dict, Any


class PerformanceDashboard:
    """Real-time performance monitoring dashboard."""

    def __init__(self):
        self.execution_history = []
        self.system_metrics = []
        self.dashboard_lock = threading.Lock()
        self.max_history = 1000

    def record_execution(self, command: str, result: Dict[str, Any]):
        with self.dashboard_lock:
            self.execution_history.append({
                "command": command[:100],
                "success": result.get("success", False),
                "execution_time": result.get("execution_time", 0),
                "return_code": result.get("return_code", -1),
                "timestamp": time.time(),
            })
            if len(self.execution_history) > self.max_history:
                self.execution_history.pop(0)

    def update_system_metrics(self, metrics: Dict[str, Any]):
        with self.dashboard_lock:
            self.system_metrics.append(metrics)
            if len(self.system_metrics) > self.max_history:
                self.system_metrics.pop(0)

    def get_summary(self) -> Dict[str, Any]:
        with self.dashboard_lock:
            if not self.execution_history:
                return {"executions": 0}
            recent = self.execution_history[-100:]
            total = len(recent)
            successful = sum(1 for e in recent if e["success"])
            avg_time = sum(e["execution_time"] for e in recent) / total
            return {
                "total_executions": len(self.execution_history),
                "recent_executions": total,
                "success_rate": (successful / total * 100) if total > 0 else 0,
                "avg_execution_time": avg_time,
                "system_metrics_count": len(self.system_metrics),
            }