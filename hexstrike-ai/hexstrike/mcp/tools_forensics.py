"""
HexStrike AI - MCP Forensics Tools
"""
from typing import Dict, Any
from mcp.server.fastmcp import FastMCP
from hexstrike.mcp.client import HexStrikeClient
from hexstrike.core.logging import setup_mcp_logging

logger = setup_mcp_logging()


def register_tools(mcp: FastMCP, client: HexStrikeClient):

    @mcp.tool()
    def volatility_analyze(memory_file: str, plugin: str,
                           profile: str = "") -> Dict[str, Any]:
        """Execute Volatility for memory forensics."""
        data = {"memory_file": memory_file, "plugin": plugin, "profile": profile}
        logger.info(f"🧠 Volatility: {plugin}")
        return client.safe_post("api/tools/volatility", data)

    @mcp.tool()
    def volatility3_analyze(memory_file: str, plugin: str) -> Dict[str, Any]:
        """Execute Volatility3 for advanced memory forensics."""
        data = {"memory_file": memory_file, "plugin": plugin}
        logger.info(f"🧠 Volatility3: {plugin}")
        return client.safe_post("api/tools/volatility3", data)

    @mcp.tool()
    def foremost_carving(input_file: str, file_types: str = "") -> Dict[str, Any]:
        """Execute Foremost for file carving."""
        data = {"input_file": input_file, "file_types": file_types}
        logger.info(f"📁 Foremost: {input_file}")
        return client.safe_post("api/tools/foremost", data)

    @mcp.tool()
    def steghide_analysis(action: str, cover_file: str,
                          passphrase: str = "") -> Dict[str, Any]:
        """Execute Steghide for steganography analysis."""
        data = {"action": action, "cover_file": cover_file, "passphrase": passphrase}
        logger.info(f"🖼️ Steghide {action}: {cover_file}")
        return client.safe_post("api/tools/steghide", data)

    @mcp.tool()
    def exiftool_extract(file_path: str) -> Dict[str, Any]:
        """Execute ExifTool for metadata extraction."""
        data = {"file_path": file_path}
        logger.info(f"📷 ExifTool: {file_path}")
        return client.safe_post("api/tools/exiftool", data)

    @mcp.tool()
    def hashpump_attack(signature: str, data: str, key_length: str,
                        append_data: str) -> Dict[str, Any]:
        """Execute HashPump for hash length extension attacks."""
        data = {"signature": signature, "data": data,
                "key_length": key_length, "append_data": append_data}
        logger.info("🔐 HashPump attack")
        return client.safe_post("api/tools/hashpump", data)