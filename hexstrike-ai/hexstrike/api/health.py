"""
HexStrike AI - Health Check Endpoint
"""
from flask import Blueprint, jsonify
from hexstrike.core.executor import execute_command
from hexstrike.core.cache import cache
from hexstrike.core.telemetry import telemetry
import time

bp = Blueprint('health', __name__)

ESSENTIAL_TOOLS = ["nmap", "gobuster", "dirb", "nikto", "sqlmap", "hydra", "john", "hashcat"]


@bp.route("/health", methods=["GET"])
def health_check():
    tools_status = {}
    for tool in ESSENTIAL_TOOLS:
        result = execute_command(f"which {tool}", use_cache=True)
        tools_status[tool] = result["success"]

    return jsonify({
        "status": "healthy",
        "version": "6.0.0",
        "tools_status": tools_status,
        "all_essential_tools_available": all(tools_status.values()),
        "total_tools_available": sum(1 for v in tools_status.values() if v),
        "cache_stats": cache.get_stats(),
        "telemetry": telemetry.get_stats(),
        "uptime": time.time() - telemetry.stats["start_time"],
    })