"""
HexStrike AI - Forensics Tool Endpoints
"""
from pathlib import Path
from flask import Blueprint, request, jsonify
from hexstrike.core.executor import execute_command
from hexstrike.core.logging import setup_logging

logger = setup_logging()
bp = Blueprint('tools_forensics', __name__, url_prefix='/api/tools')


@bp.route("/volatility", methods=["POST"])
def volatility():
    params = request.json
    memory_file = params.get("memory_file", "")
    plugin = params.get("plugin", "")
    if not memory_file or not plugin:
        return jsonify({"error": "memory_file and plugin are required"}), 400
    profile = params.get("profile", "")
    additional_args = params.get("additional_args", "")
    command = f"volatility -f {memory_file}"
    if profile: command += f" --profile={profile}"
    command += f" {plugin}"
    if additional_args: command += f" {additional_args}"
    return jsonify(execute_command(command))


@bp.route("/volatility3", methods=["POST"])
def volatility3():
    params = request.json
    memory_file = params.get("memory_file", "")
    plugin = params.get("plugin", "")
    if not memory_file or not plugin:
        return jsonify({"error": "memory_file and plugin are required"}), 400
    output_file = params.get("output_file", "")
    additional_args = params.get("additional_args", "")
    command = f"vol.py -f {memory_file} {plugin}"
    if output_file: command += f" -o {output_file}"
    if additional_args: command += f" {additional_args}"
    return jsonify(execute_command(command))


@bp.route("/foremost", methods=["POST"])
def foremost():
    params = request.json
    input_file = params.get("input_file", "")
    if not input_file:
        return jsonify({"error": "input_file is required"}), 400
    output_dir = params.get("output_dir", "/tmp/foremost_output")
    file_types = params.get("file_types", "")
    additional_args = params.get("additional_args", "")
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    command = f"foremost -o {output_dir}"
    if file_types: command += f" -t {file_types}"
    if additional_args: command += f" {additional_args}"
    command += f" {input_file}"
    result = execute_command(command)
    result["output_directory"] = output_dir
    return jsonify(result)


@bp.route("/steghide", methods=["POST"])
def steghide():
    params = request.json
    action = params.get("action", "extract")
    cover_file = params.get("cover_file", "")
    if not cover_file:
        return jsonify({"error": "cover_file is required"}), 400
    passphrase = params.get("passphrase", "")
    output_file = params.get("output_file", "")
    embed_file = params.get("embed_file", "")

    if action == "extract":
        command = f"steghide extract -sf {cover_file}"
        if output_file: command += f" -xf {output_file}"
    elif action == "embed":
        if not embed_file:
            return jsonify({"error": "embed_file required for embed action"}), 400
        command = f"steghide embed -cf {cover_file} -ef {embed_file}"
    elif action == "info":
        command = f"steghide info {cover_file}"
    else:
        return jsonify({"error": "Invalid action"}), 400

    command += f" -p '{passphrase}'" if passphrase else " -p ''"
    return jsonify(execute_command(command))


@bp.route("/exiftool", methods=["POST"])
def exiftool():
    params = request.json
    file_path = params.get("file_path", "")
    if not file_path:
        return jsonify({"error": "file_path is required"}), 400
    output_format = params.get("output_format", "")
    tags = params.get("tags", "")
    additional_args = params.get("additional_args", "")
    command = "exiftool"
    if output_format: command += f" -{output_format}"
    if tags: command += f" -{tags}"
    if additional_args: command += f" {additional_args}"
    command += f" {file_path}"
    return jsonify(execute_command(command))


@bp.route("/hashpump", methods=["POST"])
def hashpump():
    params = request.json
    signature = params.get("signature", "")
    data = params.get("data", "")
    key_length = params.get("key_length", "")
    append_data = params.get("append_data", "")
    if not all([signature, data, key_length, append_data]):
        return jsonify({"error": "All parameters required"}), 400
    command = f"hashpump -s {signature} -d '{data}' -k {key_length} -a '{append_data}'"
    return jsonify(execute_command(command))