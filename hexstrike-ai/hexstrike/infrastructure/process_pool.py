"""
HexStrike AI - Intelligent Process Pool dengan Auto-Scaling
"""
import queue
import threading
import time
from typing import Dict, Any

import psutil

from hexstrike.config import POOL_MIN_WORKERS, POOL_MAX_WORKERS
from hexstrike.core.logging import setup_logging

logger = setup_logging()


class ProcessPool:
    """Thread pool dengan auto-scaling."""

    def __init__(self, min_workers=POOL_MIN_WORKERS, max_workers=POOL_MAX_WORKERS, scale_threshold=0.8):
        self.min_workers = min_workers
        self.max_workers = max_workers
        self.scale_threshold = scale_threshold
        self.workers = []
        self.task_queue = queue.Queue()
        self.results: Dict[str, Any] = {}
        self.pool_lock = threading.Lock()
        self.active_tasks: Dict[str, Any] = {}
        self.performance_metrics = {"tasks_completed": 0, "tasks_failed": 0, "avg_task_time": 0.0}

        self._scale_up(self.min_workers)
        self.monitor_thread = threading.Thread(target=self._monitor_performance, daemon=True)
        self.monitor_thread.start()

    def submit_task(self, task_id: str, func, *args, **kwargs) -> str:
        task = {"id": task_id, "func": func, "args": args, "kwargs": kwargs, "status": "queued"}
        with self.pool_lock:
            self.active_tasks[task_id] = task
            self.task_queue.put(task)
        return task_id

    def get_task_result(self, task_id: str) -> Dict[str, Any]:
        with self.pool_lock:
            if task_id in self.results:
                return self.results[task_id]
            if task_id in self.active_tasks:
                return {"status": self.active_tasks[task_id]["status"], "result": None}
            return {"status": "not_found", "result": None}

    def _worker_thread(self, worker_id: int):
        while True:
            try:
                task = self.task_queue.get(timeout=30)
                if task is None:
                    break
                task_id = task["id"]
                start = time.time()
                try:
                    result = task["func"](*task["args"], **task["kwargs"])
                    exec_time = time.time() - start
                    with self.pool_lock:
                        self.results[task_id] = {"status": "completed", "result": result, "execution_time": exec_time}
                        self.performance_metrics["tasks_completed"] += 1
                        self.active_tasks.pop(task_id, None)
                except Exception as e:
                    with self.pool_lock:
                        self.results[task_id] = {"status": "failed", "error": str(e)}
                        self.performance_metrics["tasks_failed"] += 1
                        self.active_tasks.pop(task_id, None)
                self.task_queue.task_done()
            except queue.Empty:
                continue

    def _monitor_performance(self):
        while True:
            time.sleep(10)
            with self.pool_lock:
                active = len([w for w in self.workers if w.is_alive()])
                load = (len(self.active_tasks) + self.task_queue.qsize()) / max(active, 1)
                if load > self.scale_threshold and active < self.max_workers:
                    self._scale_up(1)
                elif load < 0.3 and active > self.min_workers:
                    self._scale_down(1)

    def _scale_up(self, count: int):
        with self.pool_lock:
            for _ in range(count):
                wid = len(self.workers)
                w = threading.Thread(target=self._worker_thread, args=(wid,), daemon=True)
                w.start()
                self.workers.append(w)

    def _scale_down(self, count: int):
        with self.pool_lock:
            for _ in range(count):
                if len(self.workers) > self.min_workers:
                    self.task_queue.put(None)
                    self.workers.pop()

    def get_pool_stats(self) -> Dict[str, Any]:
        with self.pool_lock:
            return {
                "active_workers": len([w for w in self.workers if w.is_alive()]),
                "queue_size": self.task_queue.qsize(),
                "active_tasks": len(self.active_tasks),
                "performance_metrics": self.performance_metrics.copy(),
            }