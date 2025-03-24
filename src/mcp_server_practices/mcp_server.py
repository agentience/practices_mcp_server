#!/usr/bin/env python
"""
MCP server implementation for development practices.
"""

import sys
from typing import Any, Dict, Optional, List

from mcp_python_sdk import Server, StdioServerTransport

from mcp_server_practices import __version__
from mcp_server_practices.branch.validator import validate_branch_name as validate_branch
from mcp_server_practices.branch.creator import create_branch as create_branch_func
from mcp_server_practices.integrations.jira import update_issue_status


class PracticesServer:
    """
    MCP server that provides tools and resources for development practices.
    """

    def __init__(self) -> None:
        self.server = Server(
            {
                "name": "practices",
                "version": __version__,
            },
            {
                "capabilities": {
                    "resources": {},
                    "tools": {},
                },
            },
        )

        # Default configuration
        self.config = {
            "workflow_mode": "solo",  # "solo" or "team"
            "main_branch": "main",
            "develop_branch": "develop",
            "branching_strategy": "gitflow",
        }
        self._register_tools()
        self._register_resources()

    def _register_tools(self) -> None:
        """Register all tools with the MCP server."""
        # Branch tools
        self.server.set_request_handler(
            "callTool",
            {"name": "validate_branch_name"},
            self.validate_branch_name
        )
        
        self.server.set_request_handler(
            "callTool",
            {"name": "create_branch"},
            self.create_branch
        )
        
        self.server.set_request_handler(
            "callTool",
            {"name": "get_branch_info"},
            self.get_branch_info
        )

        # Version tools
        self.server.set_request_handler(
            "callTool",
            {"name": "validate_version"},
            self.validate_version
        )

        # PR tools
        self.server.set_request_handler(
            "callTool",
            {"name": "generate_pr_description"},
            self.generate_pr_description
        )

    def _register_resources(self) -> None:
        """Register all resources with the MCP server."""
        # Template resources
        self.server.set_request_handler(
            "listResourceTemplates",
            {},
            self._handle_list_resource_templates
        )

    async def _handle_list_resource_templates(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the listResourceTemplates request."""
        return {
            "resourceTemplates": [
                {
                    "uriTemplate": "practices://templates/branching-strategy/{type}",
                    "name": "Branching strategy template",
                    "description": "Template for branching strategies",
                }
            ],
        }

    async def validate_branch_name(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a branch name against the configured branching strategy.
        """
        branch_name = request.get("arguments", {}).get("branch_name", "")
        
        # Call the branch validator with our configuration
        result = validate_branch(branch_name, self.config)
        
        if result["valid"]:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Branch '{branch_name}' is valid. Type: {result['branch_type']}, Base branch: {result['base_branch']}",
                    },
                ],
            }
        else:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Branch '{branch_name}' is invalid: {result['error']}. Expected patterns: {', '.join([f'{k}: {v}' for k, v in result['expected_patterns'].items()])}",
                    },
                ],
                "isError": True
            }
            
    async def create_branch(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new branch following the branching convention.
        """
        args = request.get("arguments", {})
        branch_type = args.get("branch_type", "")
        identifier = args.get("identifier", "")
        description = args.get("description", "")
        update_jira = args.get("update_jira", True)
        
        # Convert description to list of words if it's a string
        if isinstance(description, str):
            description = description.split()
        
        # Create the branch
        result = create_branch_func(branch_type, identifier, description, self.config)
        
        # If branch creation was successful and it's a feature/bugfix branch, update Jira
        if result["success"] and update_jira and branch_type in ["feature", "bugfix"]:
            jira_result = update_issue_status(identifier, "In Progress", self.config)
            result["jira_update"] = jira_result
        
        # Format the response
        if result["success"]:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": result["message"]
                    },
                ],
            }
        else:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error creating branch: {result.get('error', 'Unknown error')}"
                    },
                ],
                "isError": True
            }
            
    async def get_branch_info(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get information about a branch based on its name.
        """
        branch_name = request.get("arguments", {}).get("branch_name", "")
        
        # Validate the branch to extract its information
        result = validate_branch(branch_name, self.config)
        
        if not result["valid"]:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Invalid branch name: {result['error']}"
                    },
                ],
                "isError": True
            }
        
        # Return the branch information
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Branch information for '{branch_name}':\n" +
                            f"Type: {result['branch_type']}\n" +
                            f"Base branch: {result['base_branch']}\n" +
                            f"Components: {result['components']}"
                },
            ],
        }

    async def validate_version(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate version consistency across files.

        Placeholder implementation.
        """
        # TODO: Implement actual validation logic
        return {
            "content": [
                {
                    "type": "text",
                    "text": "Version validation not yet implemented",
                },
            ],
        }

    async def generate_pr_description(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a PR description based on branch and configuration.

        Placeholder implementation.
        """
        branch_name = request.get("arguments", {}).get("branch_name", "")

        # TODO: Implement actual PR description generation
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"PR description for branch '{branch_name}' not yet implemented",
                },
            ],
        }

    async def run(self) -> None:
        """Run the MCP server."""
        transport = StdioServerTransport()
        await self.server.connect(transport)
        print("Practices MCP server running on stdio", file=sys.stderr)
        try:
            await self.server.wait_for_disconnect()
        except KeyboardInterrupt:
            await self.server.close()


def main() -> None:
    """Run the MCP server."""
    import asyncio

    server = PracticesServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
