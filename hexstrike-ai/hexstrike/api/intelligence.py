"""
HexStrike AI - Intelligence Engine Endpoints
"""
from datetime import datetime
from flask import Blueprint, request, jsonify
from hexstrike.intelligence.decision_engine import decision_engine
from hexstrike.core.logging import setup_logging

logger = setup_logging()
bp = Blueprint('intelligence', __name__, url_prefix='/api/intelligence')


@bp.route("/analyze-target", methods=["POST"])
def analyze_target():
    data = request.get_json()
    if not data or 'target' not in data:
        return jsonify({"error": "Target is required"}), 400
    target = data['target']
    profile = decision_engine.analyze_target(target)
    return jsonify({
        "success": True,
        "target_profile": profile.to_dict(),
        "timestamp": datetime.now().isoformat(),
    })


@bp.route("/select-tools", methods=["POST"])
def select_optimal_tools():
    data = request.get_json()
    if not data or 'target' not in data:
        return jsonify({"error": "Target is required"}), 400
    target = data['target']
    objective = data.get('objective', 'comprehensive')
    profile = decision_engine.analyze_target(target)
    tools = decision_engine.select_optimal_tools(profile, objective)
    return jsonify({
        "success": True,
        "target": target,
        "objective": objective,
        "target_profile": profile.to_dict(),
        "selected_tools": tools,
        "tool_count": len(tools),
        "timestamp": datetime.now().isoformat(),
    })


@bp.route("/optimize-parameters", methods=["POST"])
def optimize_tool_parameters():
    data = request.get_json()
    if not data or 'target' not in data or 'tool' not in data:
        return jsonify({"error": "Target and tool are required"}), 400
    target = data['target']
    tool = data['tool']
    context = data.get('context', {})
    profile = decision_engine.analyze_target(target)
    params = decision_engine.optimize_parameters(tool, profile, context)
    return jsonify({
        "success": True,
        "target": target,
        "tool": tool,
        "optimized_parameters": params,
        "timestamp": datetime.now().isoformat(),
    })


@bp.route("/create-attack-chain", methods=["POST"])
def create_attack_chain():
    data = request.get_json()
    if not data or 'target' not in data:
        return jsonify({"error": "Target is required"}), 400
    target = data['target']
    objective = data.get('objective', 'comprehensive')
    profile = decision_engine.analyze_target(target)
    chain = decision_engine.create_attack_chain(profile, objective)
    return jsonify({
        "success": True,
        "target": target,
        "attack_chain": chain.to_dict(),
        "timestamp": datetime.now().isoformat(),
    })


@bp.route("/smart-scan", methods=["POST"])
def intelligent_smart_scan():
    from concurrent.futures import ThreadPoolExecutor

    data = request.get_json()
    if not data or 'target' not in data:
        return jsonify({"error": "Target is required"}), 400

    target = data['target']
    objective = data.get('objective', 'comprehensive')
    max_tools = data.get('max_tools', 5)

    profile = decision_engine.analyze_target(target)
    selected_tools = decision_engine.select_optimal_tools(profile, objective)[:max_tools]

    scan_results = {
        "target": target,
        "target_profile": profile.to_dict(),
        "tools_executed": [],
        "total_vulnerabilities": 0,
        "execution_summary": {},
        "combined_output": "",
    }

    from hexstrike.core.executor import execute_command

    def execute_single_tool(tool_name):
        try:
            params = decision_engine.optimize_parameters(tool_name, profile)
            tool_map = {
                'nmap': lambda: execute_command(f"nmap -sV {target}"),
                'gobuster': lambda: execute_command(f"gobuster dir -u {target} -w /usr/share/wordlists/dirb/common.txt"),
                'nuclei': lambda: execute_command(f"nuclei -u {target} -severity critical,high"),
                'nikto': lambda: execute_command(f"nikto -h {target}"),
                'sqlmap': lambda: execute_command(f"sqlmap -u {target} --batch"),
                'ffuf': lambda: execute_command(f"ffuf -u {target}/FUZZ -w /usr/share/wordlists/dirb/common.txt"),
            }
            if tool_name in tool_map:
                result = tool_map[tool_name]()
                vuln_count = 0
                if result.get('success') and result.get('stdout'):
                    output = result.get('stdout', '')
                    indicators = ['CRITICAL', 'HIGH', 'MEDIUM', 'VULNERABILITY']
                    vuln_count = sum(1 for i in indicators if i.lower() in output.lower())
                return {
                    "tool": tool_name,
                    "status": "success" if result.get('success') else "failed",
                    "execution_time": result.get('execution_time', 0),
                    "stdout": result.get('stdout', ''),
                    "vulnerabilities_found": vuln_count,
                    "success": result.get('success', False),
                }
            return {"tool": tool_name, "status": "skipped", "success": False}
        except Exception as e:
            return {"tool": tool_name, "status": "failed", "error": str(e), "success": False}

    with ThreadPoolExecutor(max_workers=min(len(selected_tools), 5)) as executor:
        futures = {executor.submit(execute_single_tool, t): t for t in selected_tools}
        for future in futures:
            tool_result = future.result()
            scan_results["tools_executed"].append(tool_result)
            if tool_result.get("vulnerabilities_found"):
                scan_results["total_vulnerabilities"] += tool_result["vulnerabilities_found"]
            if tool_result.get("stdout"):
                scan_results["combined_output"] += f"\n=== {tool_result['tool'].upper()} ===\n"
                scan_results["combined_output"] += tool_result["stdout"] + "\n"

    successful = [t for t in scan_results["tools_executed"] if t.get("success")]
    scan_results["execution_summary"] = {
        "total_tools": len(selected_tools),
        "successful_tools": len(successful),
        "failed_tools": len(selected_tools) - len(successful),
        "success_rate": len(successful) / len(selected_tools) * 100 if selected_tools else 0,
        "total_execution_time": sum(t.get("execution_time", 0) for t in scan_results["tools_executed"]),
    }

    return jsonify({
        "success": True,
        "scan_results": scan_results,
        "timestamp": datetime.now().isoformat(),
    })


@bp.route("/technology-detection", methods=["POST"])
def detect_technologies():
    data = request.get_json()
    if not data or 'target' not in data:
        return jsonify({"error": "Target is required"}), 400
    target = data['target']
    profile = decision_engine.analyze_target(target)
    return jsonify({
        "success": True,
        "target": target,
        "detected_technologies": [t.value for t in profile.technologies],
        "cms_type": profile.cms_type,
        "target_profile": profile.to_dict(),
        "timestamp": datetime.now().isoformat(),
    })