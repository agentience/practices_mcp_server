#!/usr/bin/env python
"""
MCP server implementation for development practices using modern decorator pattern.
"""

import asyncio
import sys
from typing import Any, Dict, List, Optional

# Import directly from mcp package
from mcp.server import FastMCP
from mcp.server.fastmcp.server import TextContent

from mcp_server_practices import __version__
from mcp_server_practices.tools import (
    branch_tools, 
    version_tools, 
    pr_tools, 
    git_tools, 
    license_tools, 
    github_tools
)

def create_server():
    """
    Create and configure the MCP server.
    
    Returns:
        FastMCP: Configured MCP server instance
    """
    # Initialize FastMCP with decorator pattern
    mcp = FastMCP(
        name="practices",
        description="Development practices tools and resources",
        version=__version__,
    )

    # Default configuration
    config = {
        "workflow_mode": "solo",  # "solo" or "team"
        "main_branch": "main",
        "develop_branch": "develop",
        "branching_strategy": "gitflow",
    }

    # Register tools from modules
    branch_tools.register_tools(mcp, config)
    version_tools.register_tools(mcp, config)
    pr_tools.register_tools(mcp, config)
    git_tools.register_tools(mcp, config)
    license_tools.register_tools(mcp, config)
    github_tools.register_tools(mcp, config)

    return mcp

# Create a main function to make it compatible with project.scripts
def main():
    # Create server and set up error handling
    mcp = create_server()
    mcp.onerror = lambda error: print(f"[MCP Error] {error}", file=sys.stderr)
    
    # Run the server
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(mcp.run())
    except KeyboardInterrupt:
        print("Server stopped", file=sys.stderr)

# This allows running the server directly or importing it as a module
if __name__ == "__main__":
    main()
