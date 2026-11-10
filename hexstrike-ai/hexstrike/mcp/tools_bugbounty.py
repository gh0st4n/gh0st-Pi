"""
HexStrike AI - MCP Bug Bounty Tools
"""
from typing import Dict, Any
from mcp.server.fastmcp import FastMCP
from hexstrike.mcp.client import HexStrikeClient
from hexstrike.core.logging import setup_mcp_logging

logger = setup_mcp_logging()


def register_tools(mcp: FastMCP, client: HexStrikeClient):

    @mcp.tool()
    def bugbounty_reconnaissance_workflow(domain: str, scope: str = "",
                                          out_of_scope: str = "") -> Dict[str, Any]:
        """Create reconnaissance workflow for bug bounty."""
        data = {
            "domain": domain,
            "scope": scope.split(",") if scope else [],
            "out_of_scope": out_of_scope.split(",") if out_of_scope else [],
        }
        logger.info(f"🎯 Recon workflow: {domain}")
        return client.safe_post("api/bugbounty/reconnaissance-workflow", data)

    @mcp.tool()
    def bugbounty_vulnerability_hunting(domain: str,
                                        priority_vulns: str = "rce,sqli,xss,idor,ssrf") -> Dict[str, Any]:
        """Create vulnerability hunting workflow."""
        data = {
            "domain": domain,
            "priority_vulns": priority_vulns.split(",") if priority_vulns else [],
        }
        logger.info(f"🎯 Vuln hunting: {domain}")
        return client.safe_post("api/bugbounty/vulnerability-hunting-workflow", data)

    @mcp.tool()
    def bugbounty_comprehensive_assessment(domain: str, scope: str = "") -> Dict[str, Any]:
        """Create comprehensive bug bounty assessment."""
        data = {
            "domain": domain,
            "scope": scope.split(",") if scope else [],
        }
        logger.info(f"🎯 Comprehensive assessment: {domain}")
        return client.safe_post("api/bugbounty/comprehensive-assessment", data)