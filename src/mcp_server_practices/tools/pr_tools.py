#!/usr/bin/env python
"""
Pull request related tools for the MCP server.
"""

from typing import Dict, List, Optional

from mcp.server.fastmcp.server import TextContent

from mcp_server_practices.pr.generator import generate_pr_description as generate_pr_desc
from mcp_server_practices.pr.generator import create_pull_request as create_pr
from mcp_server_practices.pr.workflow import prepare_pr as prepare_pr_func
from mcp_server_practices.pr.workflow import submit_pr as submit_pr_func

# Global instance of mcp will be set by the server module
mcp = None
config = {}


def register_tools(mcp_instance, config_dict):
    """
    Register PR-related tools with the MCP server.
    
    Args:
        mcp_instance: FastMCP instance
        config_dict: Configuration dictionary
    """
    global mcp, config
    mcp = mcp_instance
    config = config_dict
    
    # Register tools
    _register_generate_pr_description()
    _register_create_pull_request()
    _register_prepare_pr()
    _register_submit_pr()


def _register_generate_pr_description():
    """Register the generate_pr_description tool."""
    @mcp.tool(
        name="generate_pr_description",
        description="Generate a PR description based on branch and configuration"
    )
    async def generate_pr_description(*, branch_name: str) -> List[TextContent]:
        """
        Generate a PR description based on branch and configuration.
        """
        # Call the PR description generator
        result = generate_pr_desc(branch_name, config)
        
        if result.get("success", False):
            return [
                TextContent(f"Generated PR description for '{branch_name}':\n\n{result['description']}")
            ]
        else:
            return [
                TextContent(
                    f"Error generating PR description: {result.get('error', 'Unknown error')}",
                    is_error=True
                )
            ]


def _register_create_pull_request():
    """Register the create_pull_request tool."""
    @mcp.tool(
        name="create_pull_request",
        description="Create a pull request on GitHub with generated description"
    )
    async def create_pull_request(*, branch_name: str) -> List[TextContent]:
        """
        Create a pull request on GitHub with generated description.
        """
        # Call the create PR function
        result = create_pr(branch_name, config)
        
        if result.get("success", False):
            return [
                TextContent(
                    f"Pull request created for '{result['branch_name']}'.\n" +
                    f"Details: {result.get('pull_request', 'No details available')}"
                )
            ]
        else:
            return [
                TextContent(
                    f"Error creating pull request: {result.get('error', 'Unknown error')}",
                    is_error=True
                )
            ]


def _register_prepare_pr():
    """Register the prepare_pr tool."""
    @mcp.tool(
        name="prepare_pr",
        description="Prepare a pull request for the current or specified branch"
    )
    async def prepare_pr(*, branch_name: Optional[str] = None) -> List[TextContent]:
        """
        Prepare a pull request for the current or specified branch.
        """
        # Call the PR preparation function
        result = prepare_pr_func(branch_name, config)
        
        if result.get("success", False):
            # Format warnings and suggestions if any
            details = ""
            if result.get("warnings"):
                details += "\n\nWarnings:\n" + "\n".join([f"⚠️ {w}" for w in result["warnings"]])
            if result.get("suggestions"):
                details += "\n\nSuggestions:\n" + "\n".join([f"💡 {s}" for s in result["suggestions"]])
            
            return [
                TextContent(
                    f"PR preparation for '{result['branch_name']}' completed.\n" +
                    f"Base branch: {result['base_branch']}\n" +
                    f"Title: {result['title']}\n" +
                    f"Ready for submission: {result['ready']}" +
                    details
                )
            ]
        else:
            return [
                TextContent(
                    f"Error preparing PR: {result.get('error', 'Unknown error')}",
                    is_error=True
                )
            ]


def _register_submit_pr():
    """Register the submit_pr tool."""
    @mcp.tool(
        name="submit_pr",
        description="Submit a pull request for the current or specified branch"
    )
    async def submit_pr(*, branch_name: Optional[str] = None, force: bool = False) -> List[TextContent]:
        """
        Submit a pull request for the current or specified branch.
        """
        # Call the PR submission function
        result = submit_pr_func(branch_name, force, config)
        
        if result.get("success", False):
            return [
                TextContent(
                    f"PR for '{result['branch_name']}' submitted successfully.\n" +
                    f"Title: {result['title']}\n" +
                    f"Base branch: {result['base_branch']}\n" +
                    f"Pull request details: {result.get('pull_request', 'No details available')}"
                )
            ]
        else:
            error_details = ""
            if result.get("warnings"):
                error_details += "\n\nWarnings:\n" + "\n".join([f"⚠️ {w}" for w in result["warnings"]])
            if result.get("suggestions"):
                error_details += "\n\nSuggestions:\n" + "\n".join([f"💡 {s}" for s in result["suggestions"]])
            
            return [
                TextContent(
                    f"Error submitting PR: {result.get('error', 'Unknown error')}" + error_details,
                    is_error=True
                )
            ]
