"""
HexStrike AI - Telemetry Collector
"""
import time
import psutil
from typing import Dict, Any


class TelemetryCollector:
    """Collect and manage system telemetry."""

    def __init__(self):
        self.stats = {
            "commands_executed": 0,
            "successful_commands": 0,
            "failed_commands": 0,
            "total_execution_time": 0.0,
            "start_time": time.time(),
        }

    def record_execution(self, success: bool, execution_time: float):
        self.stats["commands_executed"] += 1
        if success:
            self.stats["successful_commands"] += 1
        else:
            self.stats["failed_commands"] += 1
        self.stats["total_execution_time"] += execution_time

    def get_system_metrics(self) -> Dict[str, Any]:
        try:
            net = psutil.net_io_counters()
            net_dict = net._asdict() if net else {}
        except Exception:
            net_dict = {}
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "network_io": net_dict,
        }

    def get_stats(self) -> Dict[str, Any]:
        uptime = time.time() - self.stats["start_time"]
        total = self.stats["commands_executed"]
        success_rate = (self.stats["successful_commands"] / total * 100) if total > 0 else 0
        avg_time = (self.stats["total_execution_time"] / total) if total > 0 else 0
        return {
            "uptime_seconds": uptime,
            "commands_executed": total,
            "success_rate": f"{success_rate:.1f}%",
            "average_execution_time": f"{avg_time:.2f}s",
            "system_metrics": self.get_system_metrics(),
        }


# Global instance
telemetry = TelemetryCollector()