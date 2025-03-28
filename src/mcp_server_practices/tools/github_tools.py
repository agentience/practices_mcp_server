#!/usr/bin/env python
"""
GitHub integration tools for the MCP server.
"""

from typing import Dict, List, Optional

from mcp.server.fastmcp.server import TextContent

from mcp_server_practices.integrations.github import (
    get_repository_info,
    create_branch as github_create_branch,
    create_pull_request as github_create_pr,
    get_file_contents,
    update_file
)

# Global instance of mcp will be set by the server module
mcp = None
config = {}


def register_tools(mcp_instance, config_dict):
    """
    Register GitHub-related tools with the MCP server.
    
    Args:
        mcp_instance: FastMCP instance
        config_dict: Configuration dictionary
    """
    global mcp, config
    mcp = mcp_instance
    config = config_dict
    
    # Register tools
    _register_get_repository_info()
    _register_create_github_branch()
    _register_create_github_pr()
    _register_get_file_contents()
    _register_update_file()


def _register_get_repository_info():
    """Register the get_repository_info tool."""
    @mcp.tool(
        name="get_repository_info",
        description="Get information about a GitHub repository"
    )
    async def get_repo_info(owner: str, repo: str) -> List[TextContent]:
        """
        Get information about a GitHub repository.
        """
        result = get_repository_info(owner, repo, config)
        
        if result.get("success", False):
            repo_info = result.get("repository", {})
            return [
                TextContent(f"Repository information for {owner}/{repo}:\n{repo_info}")
            ]
        else:
            return [
                TextContent(
                    f"Error getting repository information: {result.get('error', 'Unknown error')}",
                    is_error=True
                )
            ]


def _register_create_github_branch():
    """Register the create_github_branch tool."""
    @mcp.tool(
        name="create_github_branch",
        description="Create a new branch in a GitHub repository"
    )
    async def create_github_branch_tool(owner: str, repo: str, branch_name: str, base_branch: str) -> List[TextContent]:
        """
        Create a new branch in a GitHub repository.
        """
        result = github_create_branch(owner, repo, branch_name, base_branch, config)
        
        if result.get("success", False):
            return [
                TextContent(f"Branch created: {branch_name} (based on {base_branch})")
            ]
        else:
            return [
                TextContent(
                    f"Error creating branch: {result.get('error', 'Unknown error')}",
                    is_error=True
                )
            ]


def _register_create_github_pr():
    """Register the create_github_pr tool."""
    @mcp.tool(
        name="create_github_pr",
        description="Create a pull request in a GitHub repository"
    )
    async def create_github_pr_tool(owner: str, repo: str, title: str, body: str, 
                             head: str, base: str, draft: bool = False) -> List[TextContent]:
        """
        Create a pull request in a GitHub repository.
        """
        result = github_create_pr(owner, repo, title, body, head, base, draft, config)
        
        if result.get("success", False):
            pr_number = result.get("pr_number")
            html_url = result.get("html_url")
            return [
                TextContent(f"Pull request created: #{pr_number}\nTitle: {title}\nURL: {html_url}")
            ]
        else:
            return [
                TextContent(
                    f"Error creating pull request: {result.get('error', 'Unknown error')}",
                    is_error=True
                )
            ]


def _register_get_file_contents():
    """Register the get_file_contents tool."""
    @mcp.tool(
        name="get_file_contents",
        description="Get the contents of a file from a GitHub repository"
    )
    async def get_github_file(owner: str, repo: str, path: str, 
                            ref: Optional[str] = None) -> List[TextContent]:
        """
        Get the contents of a file from a GitHub repository.
        """
        result = get_file_contents(owner, repo, path, ref, config)
        
        if result.get("success", False):
            content = result.get("content", "")
            return [
                TextContent(f"Contents of {path} in {owner}/{repo}:\n\n{content}")
            ]
        else:
            return [
                TextContent(
                    f"Error getting file contents: {result.get('error', 'Unknown error')}",
                    is_error=True
                )
            ]


def _register_update_file():
    """Register the update_file tool."""
    @mcp.tool(
        name="update_file",
        description="Update a file in a GitHub repository"
    )
    async def update_github_file(owner: str, repo: str, path: str, message: str, 
                              content: str, branch: str, sha: str) -> List[TextContent]:
        """
        Update a file in a GitHub repository.
        """
        result = update_file(owner, repo, path, message, content, branch, sha, config)
        
        if result.get("success", False):
            return [
                TextContent(f"File updated: {path} in {owner}/{repo} on branch {branch}")
            ]
        else:
            return [
                TextContent(
                    f"Error updating file: {result.get('error', 'Unknown error')}",
                    is_error=True
                )
            ]
