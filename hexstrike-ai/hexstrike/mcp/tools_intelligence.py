"""
HexStrike AI - MCP Intelligence Tools
"""
import json
from typing import Dict, Any
from mcp.server.fastmcp import FastMCP
from hexstrike.mcp.client import HexStrikeClient
from hexstrike.core.logging import setup_mcp_logging

logger = setup_mcp_logging()


def register_tools(mcp: FastMCP, client: HexStrikeClient):

    @mcp.tool()
    def analyze_target_intelligence(target: str) -> Dict[str, Any]:
        """Analyze target using AI-powered intelligence."""
        logger.info(f"🧠 Analyzing target: {target}")
        return client.safe_post("api/intelligence/analyze-target", {"target": target})

    @mcp.tool()
    def select_optimal_tools_ai(target: str, objective: str = "comprehensive") -> Dict[str, Any]:
        """Use AI to select optimal security tools."""
        logger.info(f"🎯 Selecting tools for {target}")
        return client.safe_post("api/intelligence/select-tools",
                                {"target": target, "objective": objective})

    @mcp.tool()
    def optimize_tool_parameters_ai(target: str, tool: str,
                                    context: str = "{}") -> Dict[str, Any]:
        """Use AI to optimize tool parameters."""
        try:
            context_dict = json.loads(context) if context != "{}" else {}
        except Exception:
            context_dict = {}
        logger.info(f"⚙️ Optimizing {tool} for {target}")
        return client.safe_post("api/intelligence/optimize-parameters",
                                {"target": target, "tool": tool, "context": context_dict})

    @mcp.tool()
    def create_attack_chain_ai(target: str,
                               objective: str = "comprehensive") -> Dict[str, Any]:
        """Create an intelligent attack chain."""
        logger.info(f"⚔️ Creating attack chain for {target}")
        return client.safe_post("api/intelligence/create-attack-chain",
                                {"target": target, "objective": objective})

    @mcp.tool()
    def intelligent_smart_scan(target: str, objective: str = "comprehensive",
                               max_tools: int = 5) -> Dict[str, Any]:
        """Execute an intelligent AI-driven scan."""
        logger.info(f"🚀 Smart scan: {target}")
        return client.safe_post("api/intelligence/smart-scan",
                                {"target": target, "objective": objective, "max_tools": max_tools})

    @mcp.tool()
    def detect_technologies_ai(target: str) -> Dict[str, Any]:
        """Use AI to detect technologies."""
        logger.info(f"🔍 Detecting technologies: {target}")
        return client.safe_post("api/intelligence/technology-detection", {"target": target})