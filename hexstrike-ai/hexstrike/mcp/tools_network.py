"""
HexStrike AI - MCP Network Scanning Tools
"""
from typing import Dict, Any
from mcp.server.fastmcp import FastMCP
from hexstrike.mcp.client import HexStrikeClient
from hexstrike.core.colors import HexStrikeColors as C
from hexstrike.core.logging import setup_mcp_logging

logger = setup_mcp_logging()


def register_tools(mcp: FastMCP, client: HexStrikeClient):
    """Register semua network scanning tools."""

    @mcp.tool()
    def nmap_scan(target: str, scan_type: str = "-sV", ports: str = "", additional_args: str = "") -> Dict[str, Any]:
        """Execute Nmap scan terhadap target."""
        data = {"target": target, "scan_type": scan_type, "ports": ports, "additional_args": additional_args, "use_recovery": True}
        logger.info(f"{C.FIRE_RED}🔍 Nmap scan: {target}{C.RESET}")
        result = client.safe_post("api/tools/nmap", data)
        if result.get("success"):
            logger.info(f"{C.SUCCESS}✅ Nmap completed: {target}{C.RESET}")
        else:
            logger.error(f"{C.ERROR}❌ Nmap failed: {target}{C.RESET}")
        return result

    @mcp.tool()
    def masscan_high_speed(target: str, ports: str = "1-65535", rate: int = 1000) -> Dict[str, Any]:
        """Execute Masscan high-speed port scanning."""
        data = {"target": target, "ports": ports, "rate": rate}
        logger.info(f"🚀 Masscan: {target}")
        return client.safe_post("api/tools/masscan", data)

    @mcp.tool()
    def rustscan_fast_scan(target: str, ports: str = "", ulimit: int = 5000) -> Dict[str, Any]:
        """Execute Rustscan ultra-fast port scanning."""
        data = {"target": target, "ports": ports, "ulimit": ulimit}
        logger.info(f"⚡ Rustscan: {target}")
        return client.safe_post("api/tools/rustscan", data)

    # ... tool lainnya: autorecon, enum4linux_ng, nbtscan, arp_scan, responder