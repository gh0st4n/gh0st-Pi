"""
HexStrike AI - Process Management Endpoints
"""
import psutil
from datetime import datetime
from flask import Blueprint, request, jsonify
from hexstrike.core.process_manager import ProcessManager
from hexstrike.core.visual_engine import ModernVisualEngine
from hexstrike.infrastructure.enhanced_manager import enhanced_process_manager
from hexstrike.core.logging import setup_logging

logger = setup_logging()
bp = Blueprint('process_mgmt', __name__, url_prefix='/api/processes')


@bp.route("/list", methods=["GET"])
def list_processes():
    processes = ProcessManager.list_active_processes()
    for pid, info in processes.items():
        runtime = info.get("runtime", 0)
        info["runtime_formatted"] = f"{runtime:.1f}s"
    return jsonify({
        "success": True,
        "active_processes": processes,
        "total_count": len(processes),
    })


@bp.route("/status/<int:pid>", methods=["GET"])
def get_process_status(pid):
    info = ProcessManager.get_process_status(pid)
    if info:
        return jsonify({"success": True, "process": info})
    return jsonify({"success": False, "error": f"Process {pid} not found"}), 404


@bp.route("/terminate/<int:pid>", methods=["POST"])
def terminate_process(pid):
    success = ProcessManager.terminate_process(pid)
    if success:
        return jsonify({"success": True, "message": f"Process {pid} terminated"})
    return jsonify({"success": False, "error": f"Failed to terminate {pid}"}), 404


@bp.route("/pause/<int:pid>", methods=["POST"])
def pause_process(pid):
    success = ProcessManager.pause_process(pid)
    if success:
        return jsonify({"success": True, "message": f"Process {pid} paused"})
    return jsonify({"success": False, "error": f"Failed to pause {pid}"}), 404


@bp.route("/resume/<int:pid>", methods=["POST"])
def resume_process(pid):
    success = ProcessManager.resume_process(pid)
    if success:
        return jsonify({"success": True, "message": f"Process {pid} resumed"})
    return jsonify({"success": False, "error": f"Failed to resume {pid}"}), 404


@bp.route("/dashboard", methods=["GET"])
def process_dashboard():
    processes = ProcessManager.list_active_processes()
    dashboard_visual = ModernVisualEngine.create_live_dashboard(processes)
    dashboard = {
        "timestamp": datetime.now().isoformat(),
        "total_processes": len(processes),
        "visual_dashboard": dashboard_visual,
        "processes": [],
        "system_load": {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
        },
    }
    for pid, info in processes.items():
        progress = info.get("progress", 0)
        progress_bar = ModernVisualEngine.render_progress_bar(progress, width=25, style='cyber')
        dashboard["processes"].append({
            "pid": pid,
            "command": info["command"][:60],
            "status": info["status"],
            "progress_percent": f"{progress * 100:.1f}%",
            "progress_bar": progress_bar,
        })
    return jsonify(dashboard)


@bp.route("/pool-stats", methods=["GET"])
def get_pool_stats():
    stats = enhanced_process_manager.get_comprehensive_stats()
    return jsonify({"success": True, "stats": stats, "timestamp": datetime.now().isoformat()})