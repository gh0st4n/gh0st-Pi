"""
HexStrike AI - Error Handling Endpoints
"""
from datetime import datetime
from flask import Blueprint, request, jsonify
from hexstrike.error_handling.handler import error_handler
from hexstrike.error_handling.degradation import degradation_manager
from hexstrike.error_handling.models import ErrorType
from hexstrike.core.logging import setup_logging

logger = setup_logging()
bp = Blueprint('error_handling', __name__, url_prefix='/api/error-handling')


@bp.route("/statistics", methods=["GET"])
def get_error_statistics():
    stats = error_handler.get_error_statistics()
    return jsonify({
        "success": True,
        "statistics": stats,
        "timestamp": datetime.now().isoformat(),
    })


@bp.route("/test-recovery", methods=["POST"])
def test_error_recovery():
    data = request.get_json()
    tool_name = data.get("tool_name", "nmap")
    error_type = data.get("error_type", "timeout")
    target = data.get("target", "example.com")

    exceptions = {
        "timeout": TimeoutError("Simulated timeout"),
        "permission_denied": PermissionError("Simulated permission error"),
        "network_unreachable": ConnectionError("Simulated network error"),
    }
    exception = exceptions.get(error_type, Exception(f"Simulated {error_type}"))

    context = {"target": target, "parameters": data.get("parameters", {}), "attempt_count": 1}
    strategy = error_handler.handle_tool_failure(tool_name, exception, context)

    return jsonify({
        "success": True,
        "recovery_strategy": {
            "action": strategy.action.value,
            "parameters": strategy.parameters,
            "max_attempts": strategy.max_attempts,
            "success_probability": strategy.success_probability,
            "estimated_time": strategy.estimated_time,
        },
        "error_classification": error_handler.classify_error(str(exception), exception).value,
        "alternative_tools": error_handler.tool_alternatives.get(tool_name, []),
        "timestamp": datetime.now().isoformat(),
    })


@bp.route("/fallback-chains", methods=["GET"])
def get_fallback_chains():
    operation = request.args.get("operation", "")
    failed_tools = request.args.getlist("failed_tools")
    if operation:
        chain = degradation_manager.create_fallback_chain(operation, failed_tools)
        return jsonify({
            "success": True,
            "operation": operation,
            "fallback_chain": chain,
            "is_critical": degradation_manager.is_critical_operation(operation),
            "timestamp": datetime.now().isoformat(),
        })
    return jsonify({
        "success": True,
        "available_operations": list(degradation_manager.fallback_chains.keys()),
        "critical_operations": list(degradation_manager.critical_operations),
        "timestamp": datetime.now().isoformat(),
    })


@bp.route("/alternative-tools", methods=["GET"])
def get_alternative_tools():
    tool_name = request.args.get("tool_name", "")
    if not tool_name:
        return jsonify({"error": "tool_name required"}), 400
    alternatives = error_handler.tool_alternatives.get(tool_name, [])
    return jsonify({
        "success": True,
        "tool_name": tool_name,
        "alternatives": alternatives,
        "has_alternatives": len(alternatives) > 0,
        "timestamp": datetime.now().isoformat(),
    })