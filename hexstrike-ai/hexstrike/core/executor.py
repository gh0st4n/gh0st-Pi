"""
HexStrike AI - Enhanced Command Executor
"""
import subprocess
import threading
import time
import traceback
from datetime import datetime
from typing import Dict, Any

from hexstrike.config import COMMAND_TIMEOUT
from hexstrike.core.logging import setup_logging
from hexstrike.core.visual_engine import ModernVisualEngine

logger = setup_logging()


class EnhancedCommandExecutor:
    """Execute commands dengan progress tracking dan output handling."""

    def __init__(self, command: str, timeout: int = COMMAND_TIMEOUT):
        self.command = command
        self.timeout = timeout
        self.process = None
        self.stdout_data = ""
        self.stderr_data = ""
        self.return_code = None
        self.timed_out = False
        self.start_time = None
        self.end_time = None

    def _read_stdout(self):
        try:
            for line in iter(self.process.stdout.readline, ''):
                if line:
                    self.stdout_data += line
                    logger.info(f"📤 STDOUT: {line.strip()}")
        except Exception:
            pass

    def _read_stderr(self):
        try:
            for line in iter(self.process.stderr.readline, ''):
                if line:
                    self.stderr_data += line
                    logger.warning(f"📥 STDERR: {line.strip()}")
        except Exception:
            pass

    def execute(self) -> Dict[str, Any]:
        """Execute command dengan monitoring penuh."""
        from hexstrike.core.process_manager import ProcessManager
        from hexstrike.core.telemetry import telemetry

        self.start_time = time.time()
        logger.info(f"🚀 EXECUTING: {self.command}")

        try:
            self.process = subprocess.Popen(
                self.command, shell=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, bufsize=1
            )
            pid = self.process.pid
            ProcessManager.register_process(pid, self.command, self.process)

            self.stdout_thread = threading.Thread(target=self._read_stdout, daemon=True)
            self.stderr_thread = threading.Thread(target=self._read_stderr, daemon=True)
            self.stdout_thread.start()
            self.stderr_thread.start()

            try:
                self.return_code = self.process.wait(timeout=self.timeout)
                self.end_time = time.time()
                self.stdout_thread.join(timeout=1)
                self.stderr_thread.join(timeout=1)
            except subprocess.TimeoutExpired:
                self.end_time = time.time()
                self.timed_out = True
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                self.return_code = -1

            ProcessManager.cleanup_process(pid)
            execution_time = self.end_time - self.start_time
            success = (self.return_code == 0) or (self.timed_out and self.stdout_data)
            telemetry.record_execution(success, execution_time)

            return {
                "stdout": self.stdout_data,
                "stderr": self.stderr_data,
                "return_code": self.return_code,
                "success": success,
                "timed_out": self.timed_out,
                "partial_results": self.timed_out and bool(self.stdout_data or self.stderr_data),
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            self.end_time = time.time()
            logger.error(f"💥 Command failed: {str(e)}")
            return {
                "stdout": self.stdout_data,
                "stderr": f"Error: {str(e)}\n{self.stderr_data}",
                "return_code": -1,
                "success": False,
                "timed_out": False,
                "partial_results": bool(self.stdout_data or self.stderr_data),
                "execution_time": self.end_time - self.start_time,
                "timestamp": datetime.now().isoformat(),
            }


def execute_command(command: str, use_cache: bool = True) -> Dict[str, Any]:
    """Interface utama untuk execute command."""
    from hexstrike.core.cache import cache

    if use_cache:
        cached = cache.get(command, {})
        if cached:
            return cached

    executor = EnhancedCommandExecutor(command)
    result = executor.execute()

    if use_cache and result.get("success"):
        cache.set(command, {}, result)

    return result