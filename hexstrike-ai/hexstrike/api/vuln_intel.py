"""
HexStrike AI - Vulnerability Intelligence Endpoints
"""
from datetime import datetime
from flask import Blueprint, request, jsonify
from hexstrike.vuln_intel.cve_manager import cve_intelligence
from hexstrike.vuln_intel.exploit_generator import exploit_generator
from hexstrike.vuln_intel.correlator import vulnerability_correlator
from hexstrike.core.logging import setup_logging

logger = setup_logging()
bp = Blueprint('vuln_intel', __name__, url_prefix='/api/vuln-intel')


@bp.route("/cve-monitor", methods=["POST"])
def cve_monitor():
    params = request.json
    hours = params.get("hours", 24)
    severity_filter = params.get("severity_filter", "HIGH,CRITICAL")
    keywords = params.get("keywords", "")

    cve_results = cve_intelligence.fetch_latest_cves(hours, severity_filter)

    if keywords and cve_results.get("success"):
        keyword_list = [k.strip().lower() for k in keywords.split(",")]
        filtered = [c for c in cve_results.get("cves", [])
                    if any(k in c.get("description", "").lower() for k in keyword_list)]
        cve_results["cves"] = filtered
        cve_results["total_after_filter"] = len(filtered)

    exploitability_analysis = []
    for cve in cve_results.get("cves", [])[:5]:
        cve_id = cve.get("cve_id", "")
        if cve_id:
            analysis = cve_intelligence.analyze_cve_exploitability(cve_id)
            if analysis.get("success"):
                exploitability_analysis.append(analysis)

    return jsonify({
        "success": True,
        "cve_monitoring": cve_results,
        "exploitability_analysis": exploitability_analysis,
        "timestamp": datetime.now().isoformat(),
    })


@bp.route("/exploit-generate", methods=["POST"])
def exploit_generate():
    params = request.json
    cve_id = params.get("cve_id", "")
    if not cve_id:
        return jsonify({"success": False, "error": "CVE ID is required"}), 400

    target_info = {
        "target_os": params.get("target_os", ""),
        "target_arch": params.get("target_arch", "x64"),
        "exploit_type": params.get("exploit_type", "poc"),
        "evasion_level": params.get("evasion_level", "none"),
    }

    cve_analysis = cve_intelligence.analyze_cve_exploitability(cve_id)
    if not cve_analysis.get("success"):
        return jsonify({"success": False, "error": f"Failed to analyze CVE {cve_id}"}), 400

    cve_data = {
        "cve_id": cve_id,
        "description": f"Vulnerability analysis for {cve_id}",
        "exploitability_level": cve_analysis.get("exploitability_level", "UNKNOWN"),
    }

    exploit_result = exploit_generator.generate_exploit_from_cve(cve_data, target_info)
    existing_exploits = cve_intelligence.search_existing_exploits(cve_id)

    return jsonify({
        "success": True,
        "cve_analysis": cve_analysis,
        "exploit_generation": exploit_result,
        "existing_exploits": existing_exploits,
        "timestamp": datetime.now().isoformat(),
    })


@bp.route("/attack-chains", methods=["POST"])
def discover_attack_chains():
    params = request.json
    target_software = params.get("target_software", "")
    if not target_software:
        return jsonify({"success": False, "error": "Target software is required"}), 400
    attack_depth = params.get("attack_depth", 3)
    chain_results = vulnerability_correlator.find_attack_chains(target_software, attack_depth)
    return jsonify({
        "success": True,
        "attack_chain_discovery": chain_results,
        "timestamp": datetime.now().isoformat(),
    })


@bp.route("/threat-feeds", methods=["POST"])
def threat_intelligence_feeds():
    params = request.json
    indicators = params.get("indicators", [])
    if isinstance(indicators, str):
        indicators = [i.strip() for i in indicators.split(",")]
    if not indicators:
        return jsonify({"success": False, "error": "Indicators required"}), 400

    correlations = []
    threat_score = 0

    for ind in indicators:
        if ind.startswith("CVE-"):
            analysis = cve_intelligence.analyze_cve_exploitability(ind)
            if analysis.get("success"):
                correlations.append({
                    "indicator": ind, "type": "cve",
                    "analysis": analysis,
                    "threat_level": analysis.get("exploitability_level", "UNKNOWN"),
                })
                threat_score += min(analysis.get("exploitability_score", 0) * 100, 100)

    total = len(indicators)
    avg_score = threat_score / total if total > 0 else 0

    return jsonify({
        "success": True,
        "threat_intelligence": {
            "indicators_analyzed": indicators,
            "correlations": correlations,
            "threat_score": avg_score,
        },
        "timestamp": datetime.now().isoformat(),
    })