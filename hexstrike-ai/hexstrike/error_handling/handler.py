"""
HexStrike AI - Intelligent Error Handler
"""
import re
import traceback
from datetime import datetime
from typing import Dict, Any, Optional

import psutil

from hexstrike.error_handling.models import (
    ErrorType, RecoveryAction, ErrorContext, RecoveryStrategy
)
from hexstrike.core.logging import setup_logging
from hexstrike.core.colors import HexStrikeColors

logger = setup_logging()


class IntelligentErrorHandler:
    """Error handling dengan automatic recovery strategies."""

    def __init__(self):
        self.error_patterns = self._initialize_error_patterns()
        self.recovery_strategies = self._initialize_recovery_strategies()
        self.tool_alternatives = self._initialize_tool_alternatives()
        self.parameter_adjustments = self._initialize_parameter_adjustments()
        self.error_history: list = []
        self.max_history_size = 1000

    def _initialize_error_patterns(self) -> Dict[str, ErrorType]:
        return {
            r"timeout|timed out": ErrorType.TIMEOUT,
            r"permission denied|access denied|forbidden": ErrorType.PERMISSION_DENIED,
            r"network unreachable|host unreachable|connection refused": ErrorType.NETWORK_UNREACHABLE,
            r"rate limit|too many requests|429": ErrorType.RATE_LIMITED,
            r"command not found|no such file": ErrorType.TOOL_NOT_FOUND,
            r"invalid argument|invalid option": ErrorType.INVALID_PARAMETERS,
            r"out of memory|disk full|no space": ErrorType.RESOURCE_EXHAUSTED,
            r"authentication failed|unauthorized": ErrorType.AUTHENTICATION_FAILED,
        }

    def _initialize_recovery_strategies(self) -> Dict[ErrorType, list]:
        return {
            ErrorType.TIMEOUT: [
                RecoveryStrategy(RecoveryAction.RETRY_WITH_BACKOFF, {"initial_delay": 5, "max_delay": 60}, 3, 2.0, 0.7, 30),
                RecoveryStrategy(RecoveryAction.RETRY_WITH_REDUCED_SCOPE, {"reduce_threads": True}, 2, 1.0, 0.8, 45),
            ],
            ErrorType.TOOL_NOT_FOUND: [
                RecoveryStrategy(RecoveryAction.SWITCH_TO_ALTERNATIVE_TOOL, {"find_equivalent": True}, 1, 1.0, 0.7, 15),
                RecoveryStrategy(RecoveryAction.ESCALATE_TO_HUMAN, {"message": "Tool installation required"}, 1, 1.0, 0.9, 600),
            ],
            ErrorType.RATE_LIMITED: [
                RecoveryStrategy(RecoveryAction.RETRY_WITH_BACKOFF, {"initial_delay": 30, "max_delay": 300}, 5, 1.5, 0.9, 180),
            ],
            ErrorType.PERMISSION_DENIED: [
                RecoveryStrategy(RecoveryAction.ESCALATE_TO_HUMAN, {"message": "Privilege escalation required"}, 1, 1.0, 0.9, 300),
            ],
            # ... error types lainnya
        }

    def _initialize_tool_alternatives(self) -> Dict[str, list]:
        return {
            "nmap": ["rustscan", "masscan"],
            "gobuster": ["feroxbuster", "dirsearch", "ffuf"],
            "nuclei": ["jaeles", "nikto"],
            "sqlmap": ["sqlninja"],
            "dalfox": ["xsser"],
            "subfinder": ["amass", "assetfinder"],
            "ghidra": ["radare2"],
            "trivy": ["clair", "docker-bench-security"],
        }

    def _initialize_parameter_adjustments(self) -> Dict[str, Dict]:
        return {
            "nmap": {ErrorType.TIMEOUT: {"timing": "-T2"}},
            "gobuster": {ErrorType.TIMEOUT: {"threads": "10"}},
            "nuclei": {ErrorType.TIMEOUT: {"concurrency": "10"}},
        }

    def classify_error(self, error_message: str, exception: Exception = None) -> ErrorType:
        error_text = error_message.lower()
        if exception:
            if isinstance(exception, TimeoutError): return ErrorType.TIMEOUT
            if isinstance(exception, PermissionError): return ErrorType.PERMISSION_DENIED
            if isinstance(exception, ConnectionError): return ErrorType.NETWORK_UNREACHABLE
            if isinstance(exception, FileNotFoundError): return ErrorType.TOOL_NOT_FOUND
        for pattern, error_type in self.error_patterns.items():
            if re.search(pattern, error_text, re.IGNORECASE):
                return error_type
        return ErrorType.UNKNOWN

    def handle_tool_failure(self, tool: str, error: Exception, context: Dict[str, Any]) -> RecoveryStrategy:
        error_message = str(error)
        error_type = self.classify_error(error_message, error)
        strategies = self.recovery_strategies.get(error_type, [
            RecoveryStrategy(RecoveryAction.ESCALATE_TO_HUMAN, {}, 1, 1.0, 0.9, 300)
        ])
        return strategies[0]

    def get_alternative_tool(self, failed_tool: str) -> Optional[str]:
        alternatives = self.tool_alternatives.get(failed_tool, [])
        return alternatives[0] if alternatives else None

    def get_error_statistics(self) -> Dict[str, Any]:
        if not self.error_history:
            return {"total_errors": 0}
        return {
            "total_errors": len(self.error_history),
            "error_counts_by_type": {},
            "recent_errors_count": 0,
        }


# Global instance
error_handler = IntelligentErrorHandler()