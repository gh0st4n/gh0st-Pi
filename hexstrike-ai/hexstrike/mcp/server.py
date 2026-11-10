"""
HexStrike AI - MCP Server Setup
"""
from mcp.server.fastmcp import FastMCP
from hexstrike.mcp.client import HexStrikeClient
from hexstrike.core.logging import setup_mcp_logging

logger = setup_mcp_logging()


def setup_mcp_server(client: HexStrikeClient) -> FastMCP:
    mcp = FastMCP("hexstrike-ai-mcp")

    from hexstrike.mcp.tools_network import register_tools as reg_network
    from hexstrike.mcp.tools_web import register_tools as reg_web
    from hexstrike.mcp.tools_binary import register_tools as reg_binary
    from hexstrike.mcp.tools_cloud import register_tools as reg_cloud
    from hexstrike.mcp.tools_forensics import register_tools as reg_forensics
    from hexstrike.mcp.tools_intelligence import register_tools as reg_intelligence
    from hexstrike.mcp.tools_bugbounty import register_tools as reg_bugbounty
    from hexstrike.mcp.tools_process import register_tools as reg_process
    from hexstrike.mcp.tools_visual import register_tools as reg_visual
    from hexstrike.mcp.tools_vuln_intel import register_tools as reg_vuln_intel

    reg_network(mcp, client)
    reg_web(mcp, client)
    reg_binary(mcp, client)
    reg_cloud(mcp, client)
    reg_forensics(mcp, client)
    reg_intelligence(mcp, client)
    reg_bugbounty(mcp, client)
    reg_process(mcp, client)
    reg_visual(mcp, client)
    reg_vuln_intel(mcp, client)

    logger.info("📦 All MCP tools registered")
    return mcp