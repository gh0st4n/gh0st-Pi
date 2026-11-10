"""
HexStrike AI - Web Security Tool Endpoints
"""
from flask import Blueprint, jsonify, request
from hexstrike.core.executor import execute_command
from hexstrike.core.logging import setup_logging

logger = setup_logging()
bp = Blueprint('tools_web', __name__, url_prefix='/api/tools')


@bp.route("/gobuster", methods=["POST"])
def gobuster():
    params = request.json
    url = params.get("url", "")
    if not url:
        return jsonify({"error": "URL parameter is required"}), 400

    mode = params.get("mode", "dir")
    wordlist = params.get("wordlist", "/usr/share/wordlists/dirb/common.txt")
    additional_args = params.get("additional_args", "")

    command = f"gobuster {mode} -u {url} -w {wordlist}"
    if additional_args:
        command += f" {additional_args}"

    result = execute_command(command)
    return jsonify(result)


@bp.route("/nuclei", methods=["POST"])
def nuclei():
    params = request.json
    target = params.get("target", "")
    if not target:
        return jsonify({"error": "Target parameter is required"}), 400

    severity = params.get("severity", "")
    tags = params.get("tags", "")

    command = f"nuclei -u {target}"
    if severity:
        command += f" -severity {severity}"
    if tags:
        command += f" -tags {tags}"

    result = execute_command(command)
    return jsonify(result)


@bp.route("/sqlmap", methods=["POST"])
def sqlmap():
    params = request.json
    url = params.get("url", "")
    if not url:
        return jsonify({"error": "URL parameter is required"}), 400

    data = params.get("data", "")
    additional_args = params.get("additional_args", "")

    command = f"sqlmap -u {url} --batch"
    if data:
        command += f' --data="{data}"'
    if additional_args:
        command += f" {additional_args}"

    result = execute_command(command)
    return jsonify(result)


# ... endpoint web lainnya: ffuf, feroxbuster, dirsearch, katana,
#     gau, waybackurls, arjun, paramspider, x8, jaeles, dalfox,
#     httpx, wafw00f, nikto, wpscan, dirb, wfuzz, xsser, dotdotpwn