"""
HexStrike AI - Network Security Tool Endpoints
"""
from flask import Blueprint, jsonify, request
from hexstrike.core.executor import execute_command
from hexstrike.core.logging import setup_logging
from hexstrike.error_handling.recovery import execute_command_with_recovery

logger = setup_logging()
bp = Blueprint('tools_network', __name__, url_prefix='/api/tools')


@bp.route("/nmap", methods=["POST"])
def nmap():
    params = request.json
    target = params.get("target", "")
    if not target:
        return jsonify({"error": "Target parameter is required"}), 400

    scan_type = params.get("scan_type", "-sCV")
    ports = params.get("ports", "")
    additional_args = params.get("additional_args", "-T4 -Pn")

    command = f"nmap {scan_type}"
    if ports:
        command += f" -p {ports}"
    if additional_args:
        command += f" {additional_args}"
    command += f" {target}"

    logger.info(f"🔍 Starting Nmap scan: {target}")
    result = execute_command_with_recovery("nmap", command, {"target": target})
    return jsonify(result)


@bp.route("/masscan", methods=["POST"])
def masscan():
    params = request.json
    target = params.get("target", "")
    if not target:
        return jsonify({"error": "Target parameter is required"}), 400

    ports = params.get("ports", "1-65535")
    rate = params.get("rate", 1000)
    command = f"masscan {target} -p{ports} --rate={rate}"

    result = execute_command(command)
    return jsonify(result)


@bp.route("/rustscan", methods=["POST"])
def rustscan():
    params = request.json
    target = params.get("target", "")
    if not target:
        return jsonify({"error": "Target parameter is required"}), 400

    ulimit = params.get("ulimit", 5000)
    batch_size = params.get("batch_size", 4500)
    command = f"rustscan -a {target} --ulimit {ulimit} -b {batch_size}"

    result = execute_command(command)
    return jsonify(result)


# ... endpoint network lainnya: autorecon, enum4linux-ng, rpcclient, nbtscan, arp-scan, responder