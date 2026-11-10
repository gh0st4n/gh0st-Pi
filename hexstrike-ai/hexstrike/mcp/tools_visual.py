"""
HexStrike AI - MCP Visual Output Tools
"""
import json
from typing import Dict, Any
from mcp.server.fastmcp import FastMCP
from hexstrike.mcp.client import HexStrikeClient
from hexstrike.core.logging import setup_mcp_logging

logger = setup_mcp_logging()


def register_tools(mcp: FastMCP, client: HexStrikeClient):

    @mcp.tool()
    def get_live_dashboard() -> Dict[str, Any]:
        """Get live process dashboard."""
        logger.info("📊 Live dashboard")
        return client.safe_get("api/processes/dashboard")

    @mcp.tool()
    def create_vulnerability_report(vulnerabilities: str, target: str = "",
                                    scan_type: str = "comprehensive") -> Dict[str, Any]:
        """Create a vulnerability report with visual styling."""
        try:
            vuln_data = json.loads(vulnerabilities) if isinstance(vulnerabilities, str) else vulnerabilities
            cards = []
            for vuln in vuln_data:
                card_result = client.safe_post("api/visual/vulnerability-card", vuln)
                if card_result.get("success"):
                    cards.append(card_result.get("vulnerability_card", ""))
            summary_data = {
                "target": target,
                "vulnerabilities": vuln_data,
                "tools_used": [scan_type],
                "execution_time": 0,
            }
            summary_result = client.safe_post("api/visual/summary-report", summary_data)
            return {
                "success": True,
                "vulnerability_cards": cards,
                "summary_report": summary_result.get("summary_report", ""),
                "total_vulnerabilities": len(vuln_data),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @mcp.tool()
    def format_tool_output_visual(tool_name: str, output: str,
                                  success: bool = True) -> Dict[str, Any]:
        """Format tool output with visual styling."""
        logger.info(f"🎨 Formatting output: {tool_name}")
        return client.safe_post("api/visual/tool-output",
                                {"tool": tool_name, "output": output, "success": success})

    @mcp.tool()
    def create_scan_summary(target: str, tools_used: str,
                            vulnerabilities_found: int = 0,
                            execution_time: float = 0.0) -> Dict[str, Any]:
        """Create a scan summary report."""
        tools_list = [t.strip() for t in tools_used.split(",")]
        summary_data = {
            "target": target,
            "tools_used": tools_list,
            "execution_time": execution_time,
            "vulnerabilities": [{"severity": "info"}] * vulnerabilities_found,
        }
        return client.safe_post("api/visual/summary-report", summary_data)