#!/usr/bin/env python
"""
MCP server implementation for development practices using modern decorator pattern.
"""

import asyncio
import os
import sys
from pathlib import Path
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

async def get_system_instructions(project_root=None) -> str:
    """
    Get system instructions from .practices/system_instructions.md
    Falls back to default instructions if not found.
    
    Args:
        project_root: Optional project root path, defaults to current directory
        
    Returns:
        str: System instructions content
    """
    # Determine project root if not provided
    if project_root is None:
        project_root = os.getcwd()
    
    # Define paths
    practices_dir = os.path.join(project_root, ".practices")
    system_instructions_path = os.path.join(practices_dir, "system_instructions.md")
    
    # Create directory and copy default if needed
    if not os.path.exists(system_instructions_path):
        if not os.path.exists(practices_dir):
            os.makedirs(practices_dir, exist_ok=True)
            
        # Get default template path
        default_instructions = Path(__file__).parent / "templates" / "system_instructions.md"
        
        # Copy default if it exists
        if default_instructions.exists():
            import shutil
            shutil.copy(default_instructions, system_instructions_path)
        else:
            # If template doesn't exist yet, create basic instructions
            with open(system_instructions_path, 'w') as f:
                f.write("# Practices MCP Server - System Instructions\n\n"
                        "This file contains instructions for AI assistants on how to use "
                        "the development practices tools and follow established conventions.\n")
    
    # Load and return instructions
    try:
        with open(system_instructions_path, 'r') as f:
            return f.read()
    except Exception as e:
        print(f"Warning: Could not read system instructions: {e}", file=sys.stderr)
        return "# Practices MCP Server\n\nError loading system instructions."

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
    
    # Register system instructions resource
    @mcp.resource_uri("practices://system-instructions")
    async def system_instructions_resource():
        instructions = await get_system_instructions()
        return TextContent(
            content=instructions,
            mime_type="text/markdown"
        )

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
