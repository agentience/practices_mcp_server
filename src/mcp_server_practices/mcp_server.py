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
from mcp_server_practices.hooks.installer import install_hooks, check_git_repo_init, update_hooks
from mcp_server_practices.headers.manager import add_license_header, verify_license_header, process_files_batch
from mcp_server_practices.version.validator import validate_version as validate_version_func
from mcp_server_practices.version.validator import get_current_version
from mcp_server_practices.version.bumper import bump_version as bump_version_func


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
        from mcp_server_practices.tools import get_tool_definitions
        
        # Set up handler for listTools request
        self.server.set_request_handler(
            "listTools",
            {},
            self._handle_list_tools
        )
        
        # Register each tool's handler
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
        
        self.server.set_request_handler(
            "callTool",
            {"name": "get_current_version"},
            self.get_current_version
        )
        
        self.server.set_request_handler(
            "callTool",
            {"name": "bump_version"},
            self.bump_version
        )

        # PR tools
        self.server.set_request_handler(
            "callTool",
            {"name": "generate_pr_description"},
            self.generate_pr_description
        )
        
        # Pre-commit hooks tools
        self.server.set_request_handler(
            "callTool",
            {"name": "install_pre_commit_hooks"},
            self.install_pre_commit_hooks
        )
        
        self.server.set_request_handler(
            "callTool",
            {"name": "check_git_repo_init"},
            self.check_git_repo_init
        )
        
        self.server.set_request_handler(
            "callTool",
            {"name": "update_pre_commit_hooks"},
            self.update_pre_commit_hooks
        )
        
        # License header tools
        self.server.set_request_handler(
            "callTool",
            {"name": "add_license_header"},
            self.add_license_header
        )
        
        self.server.set_request_handler(
            "callTool",
            {"name": "verify_license_header"},
            self.verify_license_header
        )
        
        self.server.set_request_handler(
            "callTool",
            {"name": "process_license_headers_batch"},
            self.process_license_headers_batch
        )

    async def _handle_list_tools(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the listTools request."""
        from mcp_server_practices.tools import get_tool_definitions
        return {
            "tools": get_tool_definitions(),
        }
    
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
        """
        # Call the version validator with our configuration
        result = validate_version_func(self.config)
        
        if result.get("valid", False):
            version = result.get("version", "unknown")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Version consistency validated. Current version: {version}"
                    },
                ],
            }
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
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Version validation failed: {error}\n\nFile details:\n{file_details_text}"
                    },
                ],
                "isError": True
            }
    
    async def get_current_version(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get the current version of the project.
        """
        # Call the get_current_version function with our configuration
        version = get_current_version(self.config)
        
        if version:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Current version: {version}"
                    },
                ],
            }
        else:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": "Could not determine current version"
                    },
                ],
                "isError": True
            }
    
    async def bump_version(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Bump the version according to semantic versioning.
        """
        args = request.get("arguments", {})
        part = args.get("part", "")
        
        # Validate part
        if part not in ["major", "minor", "patch", "prerelease"]:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Invalid version part: {part}. Must be one of: major, minor, patch, prerelease"
                    },
                ],
                "isError": True
            }
        
        # Call the bump_version function with our configuration
        result = bump_version_func(part, self.config)
        
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
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": message + files_text
                    },
                ],
            }
        else:
            error = result.get("error", "Unknown error")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error bumping version: {error}"
                    },
                ],
                "isError": True
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
        
    async def install_pre_commit_hooks(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Install pre-commit hooks in a Git repository.
        """
        args = request.get("arguments", {})
        repo_path = args.get("repo_path", "")
        
        result = install_hooks(repo_path, self.config)
        
        if result.get("success", False):
            return {
                "content": [
                    {
                        "type": "text",
                        "text": result.get("message", "Pre-commit hooks installed successfully")
                    },
                ],
            }
        else:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error installing pre-commit hooks: {result.get('error', 'Unknown error')}"
                    },
                ],
                "isError": True
            }
    
    async def check_git_repo_init(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if a Git repository was recently initialized.
        """
        args = request.get("arguments", {})
        repo_path = args.get("repo_path", "")
        
        result = check_git_repo_init(repo_path)
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Repository check result:\n" +
                            f"Initialized: {result.get('initialized', False)}\n" +
                            f"Newly initialized: {result.get('is_newly_initialized', False)}\n" +
                            f"Default branch: {result.get('default_branch', 'unknown')}"
                },
            ],
        }
    
    async def update_pre_commit_hooks(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update pre-commit hooks in a Git repository.
        """
        args = request.get("arguments", {})
        repo_path = args.get("repo_path", "")
        
        result = update_hooks(repo_path)
        
        if result.get("success", False):
            return {
                "content": [
                    {
                        "type": "text",
                        "text": result.get("message", "Pre-commit hooks updated successfully")
                    },
                ],
            }
        else:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error updating pre-commit hooks: {result.get('error', 'Unknown error')}"
                    },
                ],
                "isError": True
            }
    
    async def add_license_header(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a license header to a file.
        """
        args = request.get("arguments", {})
        filename = args.get("filename", "")
        description = args.get("description", "")
        
        result = add_license_header(filename, description, self.config)
        
        if result.get("success", False):
            return {
                "content": [
                    {
                        "type": "text",
                        "text": result.get("message", f"License header added to {filename}")
                    },
                ],
            }
        else:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error adding license header: {result.get('error', 'Unknown error')}"
                    },
                ],
                "isError": True
            }
    
    async def verify_license_header(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if a file has a proper license header.
        """
        args = request.get("arguments", {})
        filename = args.get("filename", "")
        
        result = verify_license_header(filename)
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": result.get("message", f"License header check for {filename}")
                },
            ],
        }
    
    async def process_license_headers_batch(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process multiple files to add or check license headers.
        """
        args = request.get("arguments", {})
        directory = args.get("directory", "")
        pattern = args.get("pattern", "*.*")
        check_only = args.get("check_only", False)
        description = args.get("description", "")
        recursive = args.get("recursive", False)
        
        result = process_files_batch(directory, pattern, check_only, description, recursive)
        
        if result.get("success", False):
            action = "Checked" if check_only else "Processed"
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"{action} {result.get('total_files', 0)} files.\n" +
                                f"Missing headers: {result.get('missing_headers', 0)}\n" +
                                f"Modified files: {result.get('modified_files', 0)}\n" +
                                f"Errors: {result.get('errors', 0)}"
                    },
                ],
            }
        else:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error processing license headers: {result.get('error', 'Unknown error')}"
                    },
                ],
                "isError": True
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
