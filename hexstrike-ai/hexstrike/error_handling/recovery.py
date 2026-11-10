"""
HexStrike AI - Command Execution with Recovery
"""
import time
import traceback
import logging
from datetime import datetime
from typing import Dict, Any

from hexstrike.error_handling.models import ErrorType, RecoveryAction, ErrorContext
from hexstrike.error_handling.handler import error_handler
from hexstrike.error_handling.degradation import degradation_manager
from hexstrike.core.executor import execute_command
from hexstrike.core.visual_engine import ModernVisualEngine

logger = logging.getLogger(__name__)


def execute_command_with_recovery(tool_name: str, command: str,
                                  parameters: Dict[str, Any] = None,
                                  use_cache: bool = True,
                                  max_attempts: int = 3) -> Dict[str, Any]:
    """Execute a command with intelligent error handling and recovery."""
    if parameters is None:
        parameters = {}

    attempt_count = 0
    last_error = None
    recovery_history = []

    while attempt_count < max_attempts:
        attempt_count += 1
        try:
            result = execute_command(command, use_cache)

            if result.get("success", False):
                result["recovery_info"] = {
                    "attempts_made": attempt_count,
                    "recovery_applied": len(recovery_history) > 0,
                    "recovery_history": recovery_history,
                }
                return result

            error_message = result.get("stderr", "Unknown error")
            exception = Exception(error_message)

            context = {
                "target": parameters.get("target", "unknown"),
                "parameters": parameters,
                "attempt_count": attempt_count,
                "command": command,
            }

            recovery_strategy = error_handler.handle_tool_failure(tool_name, exception, context)
            recovery_history.append({
                "attempt": attempt_count,
                "error": error_message,
                "recovery_action": recovery_strategy.action.value,
                "timestamp": datetime.now().isoformat(),
            })

            if recovery_strategy.action == RecoveryAction.RETRY_WITH_BACKOFF:
                delay = recovery_strategy.parameters.get("initial_delay", 5)
                backoff = recovery_strategy.parameters.get("max_delay", 60)
                actual_delay = min(delay * (recovery_strategy.backoff_multiplier ** (attempt_count - 1)), backoff)
                logger.info(f"🔄 Retrying {tool_name} in {actual_delay}s (attempt {attempt_count}/{max_attempts})")
                time.sleep(actual_delay)
                continue

            elif recovery_strategy.action == RecoveryAction.RETRY_WITH_REDUCED_SCOPE:
                adjusted = error_handler.auto_adjust_parameters(
                    tool_name, error_handler.classify_error(error_message, exception), parameters
                )
                command = _rebuild_command_with_params(tool_name, command, adjusted)
                continue

            elif recovery_strategy.action == RecoveryAction.SWITCH_TO_ALTERNATIVE_TOOL:
                alt = error_handler.get_alternative_tool(tool_name, recovery_strategy.parameters)
                if alt:
                    result["alternative_tool_suggested"] = alt
                    result["recovery_info"] = {
                        "attempts_made": attempt_count, "recovery_applied": True,
                        "recovery_history": recovery_history, "final_action": "tool_switch_suggested",
                    }
                    return result

            elif recovery_strategy.action == RecoveryAction.ADJUST_PARAMETERS:
                error_type = error_handler.classify_error(error_message, exception)
                adjusted = error_handler.auto_adjust_parameters(tool_name, error_type, parameters)
                command = _rebuild_command_with_params(tool_name, command, adjusted)
                continue

            elif recovery_strategy.action == RecoveryAction.ESCALATE_TO_HUMAN:
                error_context = ErrorContext(
                    tool_name=tool_name, target=parameters.get("target", "unknown"),
                    parameters=parameters,
                    error_type=error_handler.classify_error(error_message, exception),
                    error_message=error_message, attempt_count=attempt_count,
                    timestamp=datetime.now(), stack_trace="",
                    system_resources=error_handler._get_system_resources(),
                )
                escalation = error_handler.escalate_to_human(
                    error_context, recovery_strategy.parameters.get("urgency", "medium")
                )
                result["human_escalation"] = escalation
                result["recovery_info"] = {
                    "attempts_made": attempt_count, "recovery_applied": True,
                    "recovery_history": recovery_history, "final_action": "human_escalation",
                }
                return result

            elif recovery_strategy.action == RecoveryAction.GRACEFUL_DEGRADATION:
                operation = _determine_operation_type(tool_name)
                degraded = degradation_manager.handle_partial_failure(operation, result, [tool_name])
                degraded["recovery_info"] = {
                    "attempts_made": attempt_count, "recovery_applied": True,
                    "recovery_history": recovery_history, "final_action": "graceful_degradation",
                }
                return degraded

            elif recovery_strategy.action == RecoveryAction.ABORT_OPERATION:
                result["recovery_info"] = {
                    "attempts_made": attempt_count, "recovery_applied": True,
                    "recovery_history": recovery_history, "final_action": "operation_aborted",
                }
                return result

            last_error = exception

        except Exception as e:
            last_error = e
            logger.error(f"💥 Unexpected error in recovery attempt {attempt_count}: {e}")

    logger.error(f"🚫 All recovery attempts exhausted for {tool_name}")
    return {
        "success": False,
        "error": f"All recovery attempts exhausted: {str(last_error)}",
        "recovery_info": {
            "attempts_made": attempt_count, "recovery_applied": True,
            "recovery_history": recovery_history, "final_action": "all_attempts_exhausted",
        },
    }


def _rebuild_command_with_params(tool_name: str, original_command: str,
                                 new_params: Dict[str, Any]) -> str:
    additional_args = []
    for key, value in new_params.items():
        if key == "timeout" and tool_name in ["nmap", "gobuster", "nuclei"]:
            additional_args.append(f"--timeout {value}")
        elif key == "threads" and tool_name in ["gobuster", "feroxbuster", "ffuf"]:
            additional_args.append(f"-t {value}")
        elif key == "delay" and tool_name in ["gobuster", "feroxbuster"]:
            additional_args.append(f"--delay {value}")
        elif key == "timing" and tool_name == "nmap":
            additional_args.append(f"{value}")
        elif key == "concurrency" and tool_name == "nuclei":
            additional_args.append(f"-c {value}")
    if additional_args:
        return f"{original_command} {' '.join(additional_args)}"
    return original_command


def _determine_operation_type(tool_name: str) -> str:
    mapping = {
        "nmap": "network_discovery", "rustscan": "network_discovery",
        "masscan": "network_discovery", "gobuster": "web_discovery",
        "feroxbuster": "web_discovery", "dirsearch": "web_discovery",
        "ffuf": "web_discovery", "nuclei": "vulnerability_scanning",
        "jaeles": "vulnerability_scanning", "nikto": "vulnerability_scanning",
        "subfinder": "subdomain_enumeration", "amass": "subdomain_enumeration",
        "arjun": "parameter_discovery", "paramspider": "parameter_discovery",
    }
    return mapping.get(tool_name, "unknown_operation")