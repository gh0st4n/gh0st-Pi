"""
HexStrike AI - CTF Endpoints
"""
from datetime import datetime
from flask import Blueprint, request, jsonify
from hexstrike.workflows.ctf_manager import CTFChallenge, ctf_manager
from hexstrike.workflows.ctf_automation import ctf_automator
from hexstrike.workflows.ctf_team import ctf_coordinator
from hexstrike.workflows.ctf_tools import ctf_tools
from hexstrike.core.logging import setup_logging

logger = setup_logging()
bp = Blueprint('ctf', __name__, url_prefix='/api/ctf')


@bp.route("/create-challenge-workflow", methods=["POST"])
def create_ctf_challenge_workflow():
    params = request.json
    challenge_name = params.get("name", "")
    if not challenge_name:
        return jsonify({"error": "Challenge name is required"}), 400
    challenge = CTFChallenge(
        name=challenge_name,
        category=params.get("category", "misc"),
        difficulty=params.get("difficulty", "unknown"),
        points=params.get("points", 100),
        description=params.get("description", ""),
        target=params.get("target", ""),
    )
    workflow = ctf_manager.create_ctf_challenge_workflow(challenge)
    return jsonify({
        "success": True,
        "workflow": workflow,
        "challenge": challenge.to_dict(),
        "timestamp": datetime.now().isoformat(),
    })


@bp.route("/auto-solve-challenge", methods=["POST"])
def auto_solve_challenge():
    params = request.json
    challenge_name = params.get("name", "")
    if not challenge_name:
        return jsonify({"error": "Challenge name is required"}), 400
    challenge = CTFChallenge(
        name=challenge_name,
        category=params.get("category", "misc"),
        difficulty=params.get("difficulty", "unknown"),
        points=params.get("points", 100),
        description=params.get("description", ""),
        target=params.get("target", ""),
    )
    result = ctf_automator.auto_solve_challenge(challenge)
    return jsonify({
        "success": True,
        "solve_result": result,
        "challenge": challenge.to_dict(),
        "timestamp": datetime.now().isoformat(),
    })


@bp.route("/suggest-tools", methods=["POST"])
def suggest_ctf_tools():
    params = request.json
    description = params.get("description", "")
    category = params.get("category", "misc")
    if not description:
        return jsonify({"error": "Challenge description is required"}), 400
    suggested = ctf_tools.suggest_tools_for_challenge(description, category)
    category_tools = ctf_tools.get_category_tools(f"{category}_recon")
    tool_commands = {}
    for tool in suggested:
        try:
            tool_commands[tool] = ctf_tools.get_tool_command(tool, "TARGET")
        except Exception:
            tool_commands[tool] = f"{tool} TARGET"
    return jsonify({
        "success": True,
        "suggested_tools": suggested,
        "category_tools": category_tools,
        "tool_commands": tool_commands,
        "category": category,
        "timestamp": datetime.now().isoformat(),
    })


@bp.route("/team-strategy", methods=["POST"])
def create_team_strategy():
    params = request.json
    challenges_data = params.get("challenges", [])
    team_skills = params.get("team_skills", {})
    if not challenges_data:
        return jsonify({"error": "Challenges data is required"}), 400
    challenges = []
    for cd in challenges_data:
        challenges.append(CTFChallenge(
            name=cd.get("name", ""),
            category=cd.get("category", "misc"),
            difficulty=cd.get("difficulty", "unknown"),
            points=cd.get("points", 100),
            description=cd.get("description", ""),
            target=cd.get("target", ""),
        ))
    strategy = ctf_coordinator.optimize_team_strategy(challenges, team_skills)
    return jsonify({
        "success": True,
        "strategy": strategy,
        "challenges_count": len(challenges),
        "team_size": len(team_skills),
        "timestamp": datetime.now().isoformat(),
    })