#!/usr/bin/env python
"""
Branch-related tools for the MCP server.
"""

from typing import Any, Dict, List, Optional

from mcp.server.fastmcp.server import TextContent

from mcp_server_practices.branch.validator import validate_branch_name as validate_branch
from mcp_server_practices.branch.creator import create_branch as create_branch_func
from mcp_server_practices.integrations.jira import update_issue_status

# Global instance of mcp will be set by the server module
mcp = None
config = {}


def register_tools(mcp_instance, config_dict):
    """
    Register branch-related tools with the MCP server.
    
    Args:
        mcp_instance: FastMCP instance
        config_dict: Configuration dictionary
    """
    global mcp, config
    mcp = mcp_instance
    config = config_dict
    
    # Register tools
    _register_validate_branch_name()
    _register_create_branch()
    _register_get_branch_info()


def _register_validate_branch_name():
    """Register the validate_branch_name tool."""
    @mcp.tool(
        name="validate_branch_name",
        description="Validate a branch name against the configured branching strategy"
    )
    async def validate_branch_name(*, branch_name: str) -> List[TextContent]:
        """
        Validate a branch name against the configured branching strategy.
        """
        # Call the branch validator with our configuration
        result = validate_branch(branch_name, config)
        
        if result["valid"]:
            return [
                TextContent(f"Branch '{branch_name}' is valid. Type: {result['branch_type']}, Base branch: {result['base_branch']}")
            ]
        else:
            return [
                TextContent(
                    f"Branch '{branch_name}' is invalid: {result['error']}. Expected patterns: {', '.join([f'{k}: {v}' for k, v in result['expected_patterns'].items()])}",
                    is_error=True
                )
            ]


def _register_create_branch():
    """Register the create_branch tool."""
    @mcp.tool(
        name="create_branch",
        description="Create a new branch following the branching convention"
    )
    async def create_branch(*, branch_type: str, identifier: str, description: Any = None, update_jira: bool = True) -> List[TextContent]:
        """
        Create a new branch following the branching convention.
        """
        # Convert description to list of words if it's a string
        if isinstance(description, str):
            description = description.split()
        
        # Create the branch
        result = create_branch_func(branch_type, identifier, description, config)
        
        # If branch creation was successful and it's a feature/bugfix branch, update Jira
        if result["success"] and update_jira and branch_type in ["feature", "bugfix"]:
            jira_result = update_issue_status(identifier, "In Progress", config)
            result["jira_update"] = jira_result
        
        # Format the response
        if result["success"]:
            return [
                TextContent(result["message"])
            ]
        else:
            return [
                TextContent(
                    f"Error creating branch: {result.get('error', 'Unknown error')}",
                    is_error=True
                )
            ]


def _register_get_branch_info():
    """Register the get_branch_info tool."""
    @mcp.tool(
        name="get_branch_info",
        description="Get information about a branch based on its name"
    )
    async def get_branch_info(*, branch_name: str) -> List[TextContent]:
        """
        Get information about a branch based on its name.
        """
        # Validate the branch to extract its information
        result = validate_branch(branch_name, config)
        
        if not result["valid"]:
            return [
                TextContent(
                    f"Invalid branch name: {result['error']}",
                    is_error=True
                )
            ]
        
        # Return the branch information
        return [
            TextContent(
                f"Branch information for '{branch_name}':\n" +
                f"Type: {result['branch_type']}\n" +
                f"Base branch: {result['base_branch']}\n" +
                f"Components: {result['components']}"
            )
        ]
