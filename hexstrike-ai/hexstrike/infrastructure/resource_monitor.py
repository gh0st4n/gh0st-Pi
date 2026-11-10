"""
HexStrike AI - Resource Monitor
"""
import time
import threading
import logging
from typing import Dict, Any

import psutil

logger = logging.getLogger(__name__)


class ResourceMonitor:
    """Advanced resource monitoring with historical tracking."""

    def __init__(self, history_size: int = 100):
        self.history_size = history_size
        self.usage_history = []
        self.history_lock = threading.Lock()

    def get_current_usage(self) -> Dict[str, float]:
        try:
            cpu = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            net = psutil.net_io_counters()
            usage = {
                "cpu_percent": cpu,
                "memory_percent": mem.percent,
                "memory_available_gb": mem.available / (1024 ** 3),
                "disk_percent": disk.percent,
                "disk_free_gb": disk.free / (1024 ** 3),
                "network_bytes_sent": net.bytes_sent,
                "network_bytes_recv": net.bytes_recv,
                "timestamp": time.time(),
            }
            with self.history_lock:
                self.usage_history.append(usage)
                if len(self.usage_history) > self.history_size:
                    self.usage_history.pop(0)
            return usage
        except Exception as e:
            logger.error(f"💥 Error getting resource usage: {e}")
            return {
                "cpu_percent": 0, "memory_percent": 0, "memory_available_gb": 0,
                "disk_percent": 0, "disk_free_gb": 0,
                "network_bytes_sent": 0, "network_bytes_recv": 0,
                "timestamp": time.time(),
            }

    def get_process_usage(self, pid: int) -> Dict[str, Any]:
        try:
            proc = psutil.Process(pid)
            return {
                "cpu_percent": proc.cpu_percent(),
                "memory_percent": proc.memory_percent(),
                "memory_rss_mb": proc.memory_info().rss / (1024 ** 2),
                "num_threads": proc.num_threads(),
                "status": proc.status(),
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return {}

    def get_usage_trends(self) -> Dict[str, Any]:
        with self.history_lock:
            if len(self.usage_history) < 2:
                return {}
            recent = self.usage_history[-10:]
            return {
                "cpu_avg_10": sum(u["cpu_percent"] for u in recent) / len(recent),
                "memory_avg_10": sum(u["memory_percent"] for u in recent) / len(recent),
                "measurements": len(self.usage_history),
            }