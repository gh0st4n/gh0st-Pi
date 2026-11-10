"""
HexStrike AI - Bug Bounty Workflow Endpoints
"""
from datetime import datetime
from flask import Blueprint, request, jsonify
from hexstrike.workflows.bugbounty import BugBountyTarget, bugbounty_manager
from hexstrike.core.logging import setup_logging

logger = setup_logging()
bp = Blueprint('bugbounty', __name__, url_prefix='/api/bugbounty')


@bp.route("/reconnaissance-workflow", methods=["POST"])
def create_reconnaissance_workflow():
    data = request.get_json()
    if not data or 'domain' not in data:
        return jsonify({"error": "Domain is required"}), 400
    target = BugBountyTarget(
        domain=data['domain'],
        scope=data.get('scope', []),
        out_of_scope=data.get('out_of_scope', []),
        program_type=data.get('program_type', 'web'),
    )
    workflow = bugbounty_manager.create_reconnaissance_workflow(target)
    return jsonify({"success": True, "workflow": workflow, "timestamp": datetime.now().isoformat()})


@bp.route("/vulnerability-hunting-workflow", methods=["POST"])
def create_vulnerability_hunting_workflow():
    data = request.get_json()
    if not data or 'domain' not in data:
        return jsonify({"error": "Domain is required"}), 400
    target = BugBountyTarget(
        domain=data['domain'],
        priority_vulns=data.get('priority_vulns', ["rce", "sqli", "xss", "idor", "ssrf"]),
        bounty_range=data.get('bounty_range', 'unknown'),
    )
    workflow = bugbounty_manager.create_vulnerability_hunting_workflow(target)
    return jsonify({"success": True, "workflow": workflow, "timestamp": datetime.now().isoformat()})


@bp.route("/comprehensive-assessment", methods=["POST"])
def create_comprehensive_assessment():
    data = request.get_json()
    if not data or 'domain' not in data:
        return jsonify({"error": "Domain is required"}), 400
    target = BugBountyTarget(
        domain=data['domain'],
        scope=data.get('scope', []),
        priority_vulns=data.get('priority_vulns', ["rce", "sqli", "xss", "idor", "ssrf"]),
    )
    assessment = {
        "target": data['domain'],
        "reconnaissance": bugbounty_manager.create_reconnaissance_workflow(target),
        "vulnerability_hunting": bugbounty_manager.create_vulnerability_hunting_workflow(target),
    }
    total_time = sum(w.get("estimated_time", 0) for w in assessment.values() if isinstance(w, dict))
    assessment["summary"] = {
        "total_estimated_time": total_time,
        "workflow_count": len([k for k in assessment if k != "target"]),
    }
    return jsonify({"success": True, "assessment": assessment, "timestamp": datetime.now().isoformat()})