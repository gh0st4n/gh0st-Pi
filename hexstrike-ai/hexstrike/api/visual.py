"""
HexStrike AI - Visual Output Endpoints
"""
from datetime import datetime
from flask import Blueprint, request, jsonify
from hexstrike.core.visual_engine import ModernVisualEngine
from hexstrike.core.logging import setup_logging

logger = setup_logging()
bp = Blueprint('visual', __name__, url_prefix='/api/visual')


@bp.route("/vulnerability-card", methods=["POST"])
def create_vulnerability_card():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    card = ModernVisualEngine.render_vulnerability_card(data)
    return jsonify({
        "success": True,
        "vulnerability_card": card,
        "timestamp": datetime.now().isoformat(),
    })


@bp.route("/summary-report", methods=["POST"])
def create_summary_report():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    report = ModernVisualEngine.create_summary_report(data)
    return jsonify({
        "success": True,
        "summary_report": report,
        "timestamp": datetime.now().isoformat(),
    })


@bp.route("/tool-output", methods=["POST"])
def format_tool_output():
    data = request.get_json()
    if not data or 'tool' not in data or 'output' not in data:
        return jsonify({"error": "Tool and output required"}), 400
    formatted = ModernVisualEngine.format_tool_output(
        data['tool'], data['output'], data.get('success', True)
    )
    return jsonify({
        "success": True,
        "formatted_output": formatted,
        "timestamp": datetime.now().isoformat(),
    })