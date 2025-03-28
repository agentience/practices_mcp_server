#!/usr/bin/env python
"""
Version-related tools for the MCP server.
"""

from typing import Dict, List, Optional

from mcp.server.fastmcp.server import TextContent

from mcp_server_practices.version.validator import validate_version as validate_version_func
from mcp_server_practices.version.validator import get_current_version
from mcp_server_practices.version.bumper import bump_version as bump_version_func

# Global instance of mcp will be set by the server module
mcp = None
config = {}


def register_tools(mcp_instance, config_dict):
    """
    Register version-related tools with the MCP server.
    
    Args:
        mcp_instance: FastMCP instance
        config_dict: Configuration dictionary
    """
    global mcp, config
    mcp = mcp_instance
    config = config_dict
    
    # Register tools
    _register_validate_version()
    _register_get_current_version()
    _register_bump_version()


def _register_validate_version():
    """Register the validate_version tool."""
    @mcp.tool(
        name="validate_version",
        description="Validate version consistency across files"
    )
    async def validate_version() -> List[TextContent]:
        """
        Validate version consistency across files.
        """
        # Call the version validator with our configuration
        result = validate_version_func(config)
        
        if result.get("valid", False):
            version = result.get("version", "unknown")
            return [
                TextContent(f"Version consistency validated. Current version: {version}")
            ]
        else:
            error = result.get("error", "Unknown error")
            file_results = result.get("file_results", [])
            
            # Format file results for display
            file_details = []
            for file_result in file_results:
                if file_result.get("valid", False):
                    file_details.append(f"✅ {file_result['path']}: {file_result.get('version', 'unknown')}")
                else:
                    file_details.append(f"❌ {file_result['path']}: {file_result.get('error', 'Unknown error')}")
            
            # Join file details with newlines
            file_details_text = "\n".join(file_details)
            
            return [
                TextContent(
                    f"Version validation failed: {error}\n\nFile details:\n{file_details_text}",
                    is_error=True
                )
            ]


def _register_get_current_version():
    """Register the get_current_version tool."""
    @mcp.tool(
        name="get_current_version",
        description="Get the current version of the project"
    )
    async def get_current_version_tool() -> List[TextContent]:
        """
        Get the current version of the project.
        """
        # Call the get_current_version function with our configuration
        version = get_current_version(config)
        
        if version:
            return [
                TextContent(f"Current version: {version}")
            ]
        else:
            return [
                TextContent(
                    "Could not determine current version",
                    is_error=True
                )
            ]


def _register_bump_version():
    """Register the bump_version tool."""
    @mcp.tool(
        name="bump_version",
        description="Bump the version according to semantic versioning"
    )
    async def bump_version(part: str) -> List[TextContent]:
        """
        Bump the version according to semantic versioning.
        """
        # Validate part
        if part not in ["major", "minor", "patch", "prerelease"]:
            return [
                TextContent(
                    f"Invalid version part: {part}. Must be one of: major, minor, patch, prerelease",
                    is_error=True
                )
            ]
        
        # Call the bump_version function with our configuration
        result = bump_version_func(part, config)
        
        if result.get("success", False):
            previous = result.get("previous_version", "unknown")
            new = result.get("new_version", "unknown")
            message = result.get("message", f"Bumped {part} version: {previous} → {new}")
            
            # Format updated files if available
            files_text = ""
            if "updated_files" in result:
                files = result["updated_files"]
                file_details = []
                for file in files:
                    if file.get("success", False):
                        file_details.append(f"✅ {file['path']}: {file.get('message', 'Updated')}")
                    else:
                        file_details.append(f"❌ {file['path']}: {file.get('error', 'Failed')}")
                
                if file_details:
                    files_text = "\n\nUpdated files:\n" + "\n".join(file_details)
            
            return [
                TextContent(message + files_text)
            ]
        else:
            error = result.get("error", "Unknown error")
            return [
                TextContent(
                    f"Error bumping version: {error}",
                    is_error=True
                )
            ]
