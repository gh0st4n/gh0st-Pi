"""
HexStrike AI - File Operations Endpoints
"""
import time
from flask import Blueprint, request, jsonify
from hexstrike.utils.file_ops import file_manager
from hexstrike.core.logging import setup_logging

logger = setup_logging()
bp = Blueprint('files', __name__)


@bp.route("/api/files/create", methods=["POST"])
def create_file():
    try:
        params = request.json
        filename = params.get("filename", "")
        content = params.get("content", "")
        binary = params.get("binary", False)
        if not filename:
            return jsonify({"error": "Filename is required"}), 400
        return jsonify(file_manager.create_file(filename, content, binary))
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@bp.route("/api/files/modify", methods=["POST"])
def modify_file():
    try:
        params = request.json
        filename = params.get("filename", "")
        content = params.get("content", "")
        append = params.get("append", False)
        if not filename:
            return jsonify({"error": "Filename is required"}), 400
        return jsonify(file_manager.modify_file(filename, content, append))
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@bp.route("/api/files/delete", methods=["POST", "DELETE"])
def delete_file():
    try:
        params = request.json
        filename = params.get("filename", "")
        if not filename:
            return jsonify({"error": "Filename is required"}), 400
        return jsonify(file_manager.delete_file(filename))
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@bp.route("/api/files/list", methods=["GET"])
def list_files():
    try:
        directory = request.args.get("directory", ".")
        return jsonify(file_manager.list_files(directory))
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@bp.route("/api/payloads/generate", methods=["POST"])
def generate_payload():
    try:
        params = request.json
        payload_type = params.get("type", "buffer")
        size = params.get("size", 1024)
        pattern = params.get("pattern", "A")
        filename = params.get("filename", f"payload_{int(time.time())}")

        if size > 100 * 1024 * 1024:
            return jsonify({"error": "Payload size too large (max 100MB)"}), 400

        if payload_type == "buffer":
            content = pattern * (size // len(pattern))
        elif payload_type == "cyclic":
            alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            content = "".join(alphabet[i % len(alphabet)] for i in range(size))
        elif payload_type == "random":
            import random, string
            content = ''.join(random.choices(string.ascii_letters + string.digits, k=size))
        else:
            return jsonify({"error": "Invalid payload type"}), 400

        result = file_manager.create_file(filename, content)
        result["payload_info"] = {"type": payload_type, "size": size, "pattern": pattern}
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500