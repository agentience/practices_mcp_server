#!/usr/bin/env python
"""
License header management tools for the MCP server.
"""

from typing import Dict, List, Optional

from mcp.server.fastmcp.server import TextContent

from mcp_server_practices.headers.manager import process_files_batch, verify_license_header

# Global instance of mcp will be set by the server module
mcp = None
config = {}


def register_tools(mcp_instance, config_dict):
    """
    Register license header management tools with the MCP server.
    
    Args:
        mcp_instance: FastMCP instance
        config_dict: Configuration dictionary
    """
    global mcp, config
    mcp = mcp_instance
    config = config_dict
    
    # Register tools
    _register_add_license_headers()
    _register_check_license_headers()


def _register_add_license_headers():
    """Register the add_license_headers tool."""
    @mcp.tool(
        name="add_license_headers",
        description="Add license headers to source files in a directory"
    )
    async def add_license_headers_tool(directory: str, recursive: bool = True) -> List[TextContent]:
        """
        Add license headers to source files in a directory.
        """
        # Use process_files_batch with check_only=False to add headers
        result = process_files_batch(directory, pattern="*.py", check_only=False, recursive=recursive)
        
        if result.get("success", False):
            files_added = result.get("modified_files", 0)
            if files_added > 0:
                message = f"License headers added to {files_added} file(s) out of {result.get('total_files', 0)} total files"
            else:
                message = "No files needed license headers"
            
            return [TextContent(message)]
        else:
            return [
                TextContent(
                    f"Error adding license headers: {result.get('error', 'Unknown error')}",
                    is_error=True
                )
            ]


def _register_check_license_headers():
    """Register the check_license_headers tool."""
    @mcp.tool(
        name="check_license_headers",
        description="Check for missing license headers in source files"
    )
    async def check_license_headers_tool(directory: str, recursive: bool = True) -> List[TextContent]:
        """
        Check for missing license headers in source files.
        """
        # Use process_files_batch with check_only=True to just check headers
        result = process_files_batch(directory, pattern="*.py", check_only=True, recursive=recursive)
        
        if result.get("success", False):
            missing_headers = result.get("missing_headers", 0)
            if missing_headers > 0:
                message = f"Found {missing_headers} file(s) with missing license headers out of {result.get('total_files', 0)} total files"
            else:
                message = "All files have appropriate license headers"
            
            return [TextContent(message)]
        else:
            return [
                TextContent(
                    f"Error checking license headers: {result.get('error', 'Unknown error')}",
                    is_error=True
                )
            ]
