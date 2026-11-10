"""
HexStrike AI - Process Manager
"""
import os
import signal
import threading
import time
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

active_processes: Dict[int, Dict[str, Any]] = {}
process_lock = threading.Lock()


class ProcessManager:
    """Enhanced process manager for command termination and monitoring."""

    @staticmethod
    def register_process(pid: int, command: str, process_obj):
        with process_lock:
            active_processes[pid] = {
                "pid": pid, "command": command, "process": process_obj,
                "start_time": time.time(), "status": "running",
                "progress": 0.0, "last_output": "", "bytes_processed": 0,
            }
        logger.info(f"🆔 REGISTERED: Process {pid} - {command[:50]}...")

    @staticmethod
    def update_process_progress(pid: int, progress: float,
                                last_output: str = "", bytes_processed: int = 0):
        with process_lock:
            if pid in active_processes:
                active_processes[pid]["progress"] = progress
                active_processes[pid]["last_output"] = last_output
                active_processes[pid]["bytes_processed"] = bytes_processed
                runtime = time.time() - active_processes[pid]["start_time"]
                eta = 0
                if progress > 0:
                    eta = (runtime / progress) * (1.0 - progress)
                active_processes[pid]["runtime"] = runtime
                active_processes[pid]["eta"] = eta

    @staticmethod
    def terminate_process(pid: int) -> bool:
        with process_lock:
            if pid in active_processes:
                info = active_processes[pid]
                try:
                    proc = info["process"]
                    if proc and proc.poll() is None:
                        proc.terminate()
                        time.sleep(1)
                        if proc.poll() is None:
                            proc.kill()
                    active_processes[pid]["status"] = "terminated"
                    logger.warning(f"🛑 TERMINATED: Process {pid}")
                    return True
                except Exception as e:
                    logger.error(f"💥 Error terminating process {pid}: {e}")
                    return False
            return False

    @staticmethod
    def cleanup_process(pid: int) -> Optional[Dict]:
        with process_lock:
            if pid in active_processes:
                info = active_processes.pop(pid)
                logger.info(f"🧹 CLEANUP: Process {pid} removed")
                return info
            return None

    @staticmethod
    def get_process_status(pid: int) -> Optional[Dict]:
        with process_lock:
            return active_processes.get(pid)

    @staticmethod
    def list_active_processes() -> Dict[int, Dict]:
        with process_lock:
            return dict(active_processes)

    @staticmethod
    def pause_process(pid: int) -> bool:
        with process_lock:
            if pid in active_processes:
                try:
                    proc = active_processes[pid]["process"]
                    if proc and proc.poll() is None:
                        os.kill(pid, signal.SIGSTOP)
                        active_processes[pid]["status"] = "paused"
                        return True
                except Exception as e:
                    logger.error(f"💥 Error pausing process {pid}: {e}")
            return False

    @staticmethod
    def resume_process(pid: int) -> bool:
        with process_lock:
            if pid in active_processes:
                try:
                    proc = active_processes[pid]["process"]
                    if proc and proc.poll() is None:
                        os.kill(pid, signal.SIGCONT)
                        active_processes[pid]["status"] = "running"
                        return True
                except Exception as e:
                    logger.error(f"💥 Error resuming process {pid}: {e}")
            return False