"""
HexStrike AI - MCP Process Management Tools
"""
from typing import Dict, Any
from mcp.server.fastmcp import FastMCP
from hexstrike.mcp.client import HexStrikeClient
from hexstrike.core.logging import setup_mcp_logging

logger = setup_mcp_logging()


def register_tools(mcp: FastMCP, client: HexStrikeClient):

    @mcp.tool()
    def list_active_processes() -> Dict[str, Any]:
        """List all active processes."""
        logger.info("📊 Listing processes")
        return client.safe_get("api/processes/list")

    @mcp.tool()
    def get_process_status(pid: int) -> Dict[str, Any]:
        """Get status of a specific process."""
        logger.info(f"🔍 Process status: {pid}")
        return client.safe_get(f"api/processes/status/{pid}")

    @mcp.tool()
    def terminate_process(pid: int) -> Dict[str, Any]:
        """Terminate a running process."""
        logger.info(f"🛑 Terminating process {pid}")
        return client.safe_post(f"api/processes/terminate/{pid}", {})

    @mcp.tool()
    def pause_process(pid: int) -> Dict[str, Any]:
        """Pause a running process."""
        logger.info(f"⏸️ Pausing process {pid}")
        return client.safe_post(f"api/processes/pause/{pid}", {})

    @mcp.tool()
    def resume_process(pid: int) -> Dict[str, Any]:
        """Resume a paused process."""
        logger.info(f"▶️ Resuming process {pid}")
        return client.safe_post(f"api/processes/resume/{pid}", {})

    @mcp.tool()
    def get_process_dashboard() -> Dict[str, Any]:
        """Get enhanced process dashboard."""
        logger.info("📊 Process dashboard")
        return client.safe_get("api/processes/dashboard")

    @mcp.tool()
    def execute_command(command: str, use_cache: bool = True) -> Dict[str, Any]:
        """Execute an arbitrary command on the server."""
        logger.info(f"⚡ Executing: {command}")
        try:
            result = client.execute_command(command, use_cache)
            if "error" in result:
                return {"success": False, "error": result["error"]}
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    @mcp.tool()
    def server_health() -> Dict[str, Any]:
        """Check server health status."""
        logger.info("🏥 Checking server health")
        return client.check_health()

    @mcp.tool()
    def get_cache_stats() -> Dict[str, Any]:
        """Get cache statistics."""
        logger.info("💾 Cache stats")
        return client.safe_get("api/cache/stats")

    @mcp.tool()
    def clear_cache() -> Dict[str, Any]:
        """Clear the server cache."""
        logger.info("🧹 Clearing cache")
        return client.safe_post("api/cache/clear", {})

    @mcp.tool()
    def get_telemetry() -> Dict[str, Any]:
        """Get system telemetry."""
        logger.info("📈 Telemetry")
        return client.safe_get("api/telemetry")