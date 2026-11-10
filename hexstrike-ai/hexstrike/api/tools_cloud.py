"""
HexStrike AI - Cloud Security Tool Endpoints
"""
from pathlib import Path
from flask import Blueprint, request, jsonify
from hexstrike.core.executor import execute_command
from hexstrike.core.logging import setup_logging

logger = setup_logging()
bp = Blueprint('tools_cloud', __name__, url_prefix='/api/tools')


@bp.route("/prowler", methods=["POST"])
def prowler():
    params = request.json
    provider = params.get("provider", "aws")
    profile = params.get("profile", "default")
    region = params.get("region", "")
    checks = params.get("checks", "")
    output_dir = params.get("output_dir", "/tmp/prowler_output")
    output_format = params.get("output_format", "json")
    additional_args = params.get("additional_args", "")

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    command = f"prowler {provider}"
    if profile: command += f" --profile {profile}"
    if region: command += f" --region {region}"
    if checks: command += f" --checks {checks}"
    command += f" --output-directory {output_dir} --output-format {output_format}"
    if additional_args: command += f" {additional_args}"

    result = execute_command(command)
    result["output_directory"] = output_dir
    return jsonify(result)


@bp.route("/trivy", methods=["POST"])
def trivy():
    params = request.json
    scan_type = params.get("scan_type", "image")
    target = params.get("target", "")
    if not target:
        return jsonify({"error": "Target parameter is required"}), 400
    output_format = params.get("output_format", "json")
    severity = params.get("severity", "")
    output_file = params.get("output_file", "")
    additional_args = params.get("additional_args", "")

    command = f"trivy {scan_type} {target}"
    if output_format: command += f" --format {output_format}"
    if severity: command += f" --severity {severity}"
    if output_file: command += f" --output {output_file}"
    if additional_args: command += f" {additional_args}"

    result = execute_command(command)
    if output_file: result["output_file"] = output_file
    return jsonify(result)


@bp.route("/scout-suite", methods=["POST"])
def scout_suite():
    params = request.json
    provider = params.get("provider", "aws")
    profile = params.get("profile", "default")
    report_dir = params.get("report_dir", "/tmp/scout-suite")
    services = params.get("services", "")
    additional_args = params.get("additional_args", "")

    Path(report_dir).mkdir(parents=True, exist_ok=True)
    command = f"scout {provider}"
    if profile and provider == "aws": command += f" --profile {profile}"
    if services: command += f" --services {services}"
    command += f" --report-dir {report_dir}"
    if additional_args: command += f" {additional_args}"

    result = execute_command(command)
    result["report_directory"] = report_dir
    return jsonify(result)


@bp.route("/kube-hunter", methods=["POST"])
def kube_hunter():
    params = request.json
    target = params.get("target", "")
    active = params.get("active", False)
    report = params.get("report", "json")
    additional_args = params.get("additional_args", "")

    command = "kube-hunter"
    if target: command += f" --remote {target}"
    else: command += " --pod"
    if active: command += " --active"
    if report: command += f" --report {report}"
    if additional_args: command += f" {additional_args}"
    return jsonify(execute_command(command))


@bp.route("/kube-bench", methods=["POST"])
def kube_bench():
    params = request.json
    targets = params.get("targets", "")
    output_format = params.get("output_format", "json")
    additional_args = params.get("additional_args", "")

    command = "kube-bench"
    if targets: command += f" --targets {targets}"
    if output_format: command += f" --outputfile /tmp/kube-bench-results.{output_format} --json"
    if additional_args: command += f" {additional_args}"
    return jsonify(execute_command(command))


@bp.route("/docker-bench-security", methods=["POST"])
def docker_bench():
    params = request.json
    checks = params.get("checks", "")
    exclude = params.get("exclude", "")
    output_file = params.get("output_file", "/tmp/docker-bench-results.json")
    additional_args = params.get("additional_args", "")

    command = "docker-bench-security"
    if checks: command += f" -c {checks}"
    if exclude: command += f" -e {exclude}"
    if output_file: command += f" -l {output_file}"
    if additional_args: command += f" {additional_args}"

    result = execute_command(command)
    result["output_file"] = output_file
    return jsonify(result)


@bp.route("/checkov", methods=["POST"])
def checkov():
    params = request.json
    directory = params.get("directory", ".")
    framework = params.get("framework", "")
    output_format = params.get("output_format", "json")
    additional_args = params.get("additional_args", "")

    command = f"checkov -d {directory}"
    if framework: command += f" --framework {framework}"
    if output_format: command += f" --output {output_format}"
    if additional_args: command += f" {additional_args}"
    return jsonify(execute_command(command))


@bp.route("/terrascan", methods=["POST"])
def terrascan():
    params = request.json
    scan_type = params.get("scan_type", "all")
    iac_dir = params.get("iac_dir", ".")
    output_format = params.get("output_format", "json")
    severity = params.get("severity", "")
    additional_args = params.get("additional_args", "")

    command = f"terrascan scan -t {scan_type} -d {iac_dir}"
    if output_format: command += f" -o {output_format}"
    if severity: command += f" --severity {severity}"
    if additional_args: command += f" {additional_args}"
    return jsonify(execute_command(command))


@bp.route("/clair", methods=["POST"])
def clair():
    params = request.json
    image = params.get("image", "")
    if not image:
        return jsonify({"error": "Image parameter is required"}), 400
    output_format = params.get("output_format", "json")
    additional_args = params.get("additional_args", "")

    command = f"clairctl analyze {image}"
    if output_format: command += f" --format {output_format}"
    if additional_args: command += f" {additional_args}"
    return jsonify(execute_command(command))


@bp.route("/falco", methods=["POST"])
def falco():
    params = request.json
    config_file = params.get("config_file", "/etc/falco/falco.yaml")
    duration = params.get("duration", 60)
    output_format = params.get("output_format", "json")
    additional_args = params.get("additional_args", "")

    command = f"timeout {duration} falco"
    if config_file: command += f" --config {config_file}"
    if output_format == "json": command += " --json"
    if additional_args: command += f" {additional_args}"
    return jsonify(execute_command(command))