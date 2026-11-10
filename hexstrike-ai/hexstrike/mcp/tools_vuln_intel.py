"""
HexStrike AI - MCP Vulnerability Intelligence Tools
"""
from typing import Dict, Any
from mcp.server.fastmcp import FastMCP
from hexstrike.mcp.client import HexStrikeClient
from hexstrike.core.logging import setup_mcp_logging

logger = setup_mcp_logging()


def register_tools(mcp: FastMCP, client: HexStrikeClient):

    @mcp.tool()
    def monitor_cve_feeds(hours: int = 24, severity_filter: str = "HIGH,CRITICAL",
                          keywords: str = "") -> Dict[str, Any]:
        """Monitor CVE databases for new vulnerabilities."""
        data = {"hours": hours, "severity_filter": severity_filter, "keywords": keywords}
        logger.info(f"🔍 CVE monitoring: last {hours}h | {severity_filter}")
        return client.safe_post("api/vuln-intel/cve-monitor", data)

    @mcp.tool()
    def generate_exploit_from_cve(cve_id: str, target_os: str = "",
                                  target_arch: str = "x64",
                                  exploit_type: str = "poc") -> Dict[str, Any]:
        """Generate exploits from CVE information."""
        data = {
            "cve_id": cve_id, "target_os": target_os,
            "target_arch": target_arch, "exploit_type": exploit_type,
        }
        logger.info(f"🤖 Generating exploit for {cve_id}")
        return client.safe_post("api/vuln-intel/exploit-generate", data)

    @mcp.tool()
    def discover_attack_chains(target_software: str,
                               attack_depth: int = 3) -> Dict[str, Any]:
        """Discover multi-stage attack chains."""
        data = {"target_software": target_software, "attack_depth": min(max(attack_depth, 1), 5)}
        logger.info(f"🔗 Attack chains: {target_software}")
        return client.safe_post("api/vuln-intel/attack-chains", data)

    @mcp.tool()
    def correlate_threat_intelligence(indicators: str,
                                      timeframe: str = "30d") -> Dict[str, Any]:
        """Correlate threat intelligence across sources."""
        indicator_list = [i.strip() for i in indicators.split(",") if i.strip()]
        if not indicator_list:
            return {"success": False, "error": "No valid indicators provided"}
        valid_timeframes = ["7d", "30d", "90d", "1y"]
        if timeframe not in valid_timeframes:
            timeframe = "30d"
        data = {"indicators": indicator_list, "timeframe": timeframe, "sources": "all"}
        logger.info(f"🧠 Threat intel: {len(indicator_list)} indicators")
        return client.safe_post("api/vuln-intel/threat-feeds", data)