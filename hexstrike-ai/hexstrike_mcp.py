#!/usr/bin/env python3
"""
HexStrike AI MCP Client - Entry point
"""
import sys
from hexstrike.config import DEFAULT_HEXSTRIKE_SERVER, DEFAULT_REQUEST_TIMEOUT
from hexstrike.core.logging import setup_mcp_logging
from hexstrike.mcp.client import HexStrikeClient
from hexstrike.mcp.server import setup_mcp_server

logger = setup_mcp_logging()

def parse_args():
    import argparse
    parser = argparse.ArgumentParser(description="Run the HexStrike AI MCP Client")
    parser.add_argument("--server", type=str, default=DEFAULT_HEXSTRIKE_SERVER)
    parser.add_argument("--timeout", type=int, default=DEFAULT_REQUEST_TIMEOUT)
    parser.add_argument("--debug", action="store_true")
    return parser.parse_args()

def main():
    args = parse_args()
    if args.debug:
        logger.setLevel("DEBUG")

    try:
        client = HexStrikeClient(args.server, args.timeout)
        mcp = setup_mcp_server(client)
        logger.info("🚀 Starting HexStrike AI MCP server")
        mcp.run()
    except Exception as e:
        logger.error(f"💥 Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()