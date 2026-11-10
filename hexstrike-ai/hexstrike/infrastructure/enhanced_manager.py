"""
HexStrike AI - Enhanced Process Manager
"""
import os
import subprocess
import threading
import time
import logging
from typing import Dict, Any

from hexstrike.infrastructure.process_pool import ProcessPool
from hexstrike.core.cache import AdvancedCache
from hexstrike.infrastructure.resource_monitor import ResourceMonitor
from hexstrike.infrastructure.performance import PerformanceDashboard

logger = logging.getLogger(__name__)


class EnhancedProcessManager:
    """Advanced process management with intelligent resource allocation."""

    def __init__(self):
        self.process_pool = ProcessPool(min_workers=4, max_workers=32)
        self.cache = AdvancedCache(max_size=2000, default_ttl=1800)
        self.resource_monitor = ResourceMonitor()
        self.process_registry = {}
        self.registry_lock = threading.RLock()
        self.performance_dashboard = PerformanceDashboard()
        self.auto_scaling_enabled = True
        self.resource_thresholds = {
            "cpu_high": 85.0, "memory_high": 90.0,
            "disk_high": 95.0, "load_high": 0.8,
        }
        self.monitor_thread = threading.Thread(target=self._monitor_system, daemon=True)
        self.monitor_thread.start()

    def execute_command_async(self, command: str, context: Dict[str, Any] = None) -> str:
        task_id = f"cmd_{int(time.time() * 1000)}_{hash(command) % 10000}"
        cache_key = f"cmd_result_{hash(command)}"
        cached = self.cache.get(cache_key)
        if cached and context and context.get("use_cache", True):
            return cached
        self.process_pool.submit_task(task_id, self._execute_command_internal, command, context or {})
        return task_id

    def _execute_command_internal(self, command: str, context: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        try:
            process = subprocess.Popen(
                command, shell=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, preexec_fn=os.setsid if os.name != 'nt' else None,
            )
            stdout, stderr = process.communicate()
            execution_time = time.time() - start_time
            result = {
                "success": process.returncode == 0,
                "stdout": stdout, "stderr": stderr,
                "return_code": process.returncode,
                "execution_time": execution_time,
                "pid": process.pid,
            }
            if result["success"] and context.get("cache_result", True):
                self.cache.set(f"cmd_result_{hash(command)}", result, context.get("cache_ttl", 1800))
            self.performance_dashboard.record_execution(command, result)
            return result
        except Exception as e:
            return {
                "success": False, "stdout": "", "stderr": str(e),
                "return_code": -1, "execution_time": time.time() - start_time,
                "error": str(e),
            }

    def get_task_result(self, task_id: str) -> Dict[str, Any]:
        return self.process_pool.get_task_result(task_id)

    def terminate_process_gracefully(self, pid: int, timeout: int = 30) -> bool:
        try:
            with self.registry_lock:
                if pid not in self.process_registry:
                    return False
                proc = self.process_registry[pid]["process"]
                proc.terminate()
                try:
                    proc.wait(timeout=timeout)
                    return True
                except subprocess.TimeoutExpired:
                    proc.kill()
                    return True
        except Exception as e:
            logger.error(f"💥 Error terminating process {pid}: {e}")
            return False

    def _monitor_system(self):
        while True:
            try:
                time.sleep(15)
                usage = self.resource_monitor.get_current_usage()
                if self.auto_scaling_enabled:
                    self._auto_scale(usage)
                self.performance_dashboard.update_system_metrics(usage)
            except Exception as e:
                logger.error(f"💥 Monitor error: {e}")

    def _auto_scale(self, usage: Dict[str, float]):
        stats = self.process_pool.get_pool_stats()
        workers = stats["active_workers"]
        if (usage["cpu_percent"] > self.resource_thresholds["cpu_high"] or
                usage["memory_percent"] > self.resource_thresholds["memory_high"]):
            if workers > self.process_pool.min_workers:
                self.process_pool._scale_down(1)
        elif (usage["cpu_percent"] < 60 and usage["memory_percent"] < 70 and
              stats["queue_size"] > 2):
            if workers < self.process_pool.max_workers:
                self.process_pool._scale_up(1)

    def get_comprehensive_stats(self) -> Dict[str, Any]:
        return {
            "process_pool": self.process_pool.get_pool_stats(),
            "cache": self.cache.get_stats(),
            "resource_usage": self.resource_monitor.get_current_usage(),
            "active_processes": len(self.process_registry),
            "performance_dashboard": self.performance_dashboard.get_summary(),
            "auto_scaling_enabled": self.auto_scaling_enabled,
            "resource_thresholds": self.resource_thresholds,
        }


# Global instance
enhanced_process_manager = EnhancedProcessManager()