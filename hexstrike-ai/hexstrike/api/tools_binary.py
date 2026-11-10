"""
HexStrike AI - Binary Analysis Tool Endpoints
"""
from flask import Blueprint, request, jsonify
from hexstrike.core.executor import execute_command
from hexstrike.core.logging import setup_logging

logger = setup_logging()
bp = Blueprint('tools_binary', __name__, url_prefix='/api/tools')


@bp.route("/gdb", methods=["POST"])
def gdb():
    params = request.json
    binary = params.get("binary", "")
    if not binary:
        return jsonify({"error": "Binary parameter is required"}), 400
    commands = params.get("commands", "")
    command = f"gdb {binary} -batch"
    if commands:
        command = f"echo '{commands}' | gdb {binary} -batch"
    return jsonify(execute_command(command))


@bp.route("/radare2", methods=["POST"])
def radare2():
    params = request.json
    binary = params.get("binary", "")
    if not binary:
        return jsonify({"error": "Binary parameter is required"}), 400
    commands = params.get("commands", "")
    command = f"r2 -q -c '{commands}' {binary}" if commands else f"r2 -q {binary}"
    return jsonify(execute_command(command))


@bp.route("/binwalk", methods=["POST"])
def binwalk():
    params = request.json
    file_path = params.get("file_path", "")
    if not file_path:
        return jsonify({"error": "File path is required"}), 400
    extract = params.get("extract", False)
    command = f"binwalk {'-e' if extract else ''} {file_path}"
    return jsonify(execute_command(command))


@bp.route("/ropgadget", methods=["POST"])
def ropgadget():
    params = request.json
    binary = params.get("binary", "")
    if not binary:
        return jsonify({"error": "Binary parameter is required"}), 400
    gadget_type = params.get("gadget_type", "")
    command = f"ROPgadget --binary {binary}"
    if gadget_type:
        command += f" --only '{gadget_type}'"
    return jsonify(execute_command(command))


@bp.route("/checksec", methods=["POST"])
def checksec():
    params = request.json
    binary = params.get("binary", "")
    if not binary:
        return jsonify({"error": "Binary parameter is required"}), 400
    return jsonify(execute_command(f"checksec --file={binary}"))


@bp.route("/strings", methods=["POST"])
def strings():
    params = request.json
    file_path = params.get("file_path", "")
    if not file_path:
        return jsonify({"error": "File path is required"}), 400
    min_len = params.get("min_len", 4)
    return jsonify(execute_command(f"strings -n {min_len} {file_path}"))


@bp.route("/objdump", methods=["POST"])
def objdump():
    params = request.json
    binary = params.get("binary", "")
    if not binary:
        return jsonify({"error": "Binary parameter is required"}), 400
    disassemble = params.get("disassemble", True)
    flag = "-d" if disassemble else "-x"
    return jsonify(execute_command(f"objdump {flag} {binary}"))


@bp.route("/ghidra", methods=["POST"])
def ghidra():
    params = request.json
    binary = params.get("binary", "")
    if not binary:
        return jsonify({"error": "Binary parameter is required"}), 400
    project_name = params.get("project_name", "hexstrike_analysis")
    timeout = params.get("analysis_timeout", 300)
    command = f"analyzeHeadless /tmp/ghidra_projects/{project_name} {project_name} -import {binary} -deleteProject"
    return jsonify(execute_command(command))


@bp.route("/xxd", methods=["POST"])
def xxd():
    params = request.json
    file_path = params.get("file_path", "")
    if not file_path:
        return jsonify({"error": "File path is required"}), 400
    offset = params.get("offset", "0")
    length = params.get("length", "")
    command = f"xxd -s {offset}"
    if length:
        command += f" -l {length}"
    command += f" {file_path}"
    return jsonify(execute_command(command))