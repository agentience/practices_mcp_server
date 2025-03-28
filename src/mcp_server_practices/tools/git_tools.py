#!/usr/bin/env python
"""
Git-related tools for the MCP server.
"""

from typing import Dict, List, Optional

from mcp.server.fastmcp.server import TextContent

from mcp_server_practices.hooks.installer import install_hooks, check_git_repo_init, update_hooks

# Global instance of mcp will be set by the server module
mcp = None
config = {}


def register_tools(mcp_instance, config_dict):
    """
    Register Git-related tools with the MCP server.
    
    Args:
        mcp_instance: FastMCP instance
        config_dict: Configuration dictionary
    """
    global mcp, config
    mcp = mcp_instance
    config = config_dict
    
    # Register tools
    _register_install_pre_commit_hooks()
    _register_check_git_repo_init()
    _register_update_pre_commit_hooks()


def _register_install_pre_commit_hooks():
    """Register the install_pre_commit_hooks tool."""
    @mcp.tool(
        name="install_pre_commit_hooks",
        description="Install pre-commit hooks in a Git repository"
    )
    async def install_pre_commit_hooks(repo_path: str = "") -> List[TextContent]:
        """
        Install pre-commit hooks in a Git repository.
        """
        result = install_hooks(repo_path, config)
        
        if result.get("success", False):
            return [
                TextContent(result.get("message", "Pre-commit hooks installed successfully"))
            ]
        else:
            return [
                TextContent(
                    f"Error installing pre-commit hooks: {result.get('error', 'Unknown error')}",
                    is_error=True
                )
            ]


def _register_check_git_repo_init():
    """Register the check_git_repo_init tool."""
    @mcp.tool(
        name="check_git_repo_init",
        description="Check if a Git repository was recently initialized"
    )
    async def check_git_repo_initialized(repo_path: str = "") -> List[TextContent]:
        """
        Check if a Git repository was recently initialized.
        """
        result = check_git_repo_init(repo_path)
        
        return [
            TextContent(
                f"Repository check result:\n" +
                f"Initialized: {result.get('initialized', False)}\n" +
                f"Newly initialized: {result.get('is_newly_initialized', False)}\n" +
                f"Default branch: {result.get('default_branch', 'unknown')}"
            )
        ]


def _register_update_pre_commit_hooks():
    """Register the update_pre_commit_hooks tool."""
    @mcp.tool(
        name="update_pre_commit_hooks",
        description="Update pre-commit hooks in a Git repository"
    )
    async def update_pre_commit_hooks(repo_path: str = "") -> List[TextContent]:
        """
        Update pre-commit hooks in a Git repository.
        """
        result = update_hooks(repo_path)
        
        if result.get("success", False):
            return [
                TextContent(result.get("message", "Pre-commit hooks updated successfully"))
            ]
        else:
            return [
                TextContent(
                    f"Error updating pre-commit hooks: {result.get('error', 'Unknown error')}",
                    is_error=True
                )
            ]
