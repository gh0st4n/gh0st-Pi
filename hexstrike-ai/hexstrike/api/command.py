"""
HexStrike AI - Command Execution Endpoint
"""
import traceback
from flask import Blueprint, request, jsonify
from hexstrike.core.executor import execute_command
from hexstrike.core.logging import setup_logging

logger = setup_logging()
bp = Blueprint('command', __name__)


@bp.route("/api/command", methods=["POST"])
def generic_command():
    try:
        params = request.json
        command = params.get("command", "")
        use_cache = params.get("use_cache", True)
        if not command:
            return jsonify({"error": "Command parameter is required"}), 400
        result = execute_command(command, use_cache=use_cache)
        return jsonify(result)
    except Exception as e:
        logger.error(f"💥 Error in command endpoint: {e}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500