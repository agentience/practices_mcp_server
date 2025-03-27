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
from mcp_server_practices.integrations.github import (
    get_repository_info, create_branch as github_create_branch,
    create_pull_request as github_create_pr, get_file_contents,
    update_file, GitHubAdapter
)
from mcp_server_practices.hooks.installer import install_hooks, check_git_repo_init, update_hooks
from mcp_server_practices.headers.manager import add_license_header, verify_license_header, process_files_batch
from mcp_server_practices.version.validator import validate_version as validate_version_func
from mcp_server_practices.version.validator import get_current_version
from mcp_server_practices.version.bumper import bump_version as bump_version_func
from mcp_server_practices.pr.generator import generate_pr_description as generate_pr_desc
from mcp_server_practices.pr.generator import create_pull_request as create_pr
from mcp_server_practices.pr.workflow import prepare_pr as prepare_pr_func
from mcp_server_practices.pr.workflow import submit_pr as submit_pr_func


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
        
        # GitHub integration tools
        self.server.set_request_handler(
            "callTool",
            {"name": "get_github_repository_info"},
            self.get_github_repository_info
        )
        
        self.server.set_request_handler(
            "callTool",
            {"name": "create_github_branch"},
            self.create_github_branch
        )
        
        self.server.set_request_handler(
            "callTool",
            {"name": "create_github_pull_request"},
            self.create_github_pull_request
        )
        
        self.server.set_request_handler(
            "callTool",
            {"name": "get_github_file_contents"},
            self.get_github_file_contents
        )
        
        self.server.set_request_handler(
            "callTool",
            {"name": "update_github_file"},
            self.update_github_file
        )
        
        self.server.set_request_handler(
            "callTool",
            {"name": "get_github_workflow_status"},
            self.get_github_workflow_status
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
        
        self.server.set_request_handler(
            "callTool",
            {"name": "prepare_pr"},
            self.prepare_pr
        )
        
        self.server.set_request_handler(
            "callTool",
            {"name": "submit_pr"},
            self.submit_pr
        )
        
        self.server.set_request_handler(
            "callTool",
            {"name": "create_pull_request"},
            self.create_pull_request
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
        """
        branch_name = request.get("arguments", {}).get("branch_name", "")

        # Call the PR description generator
        result = generate_pr_desc(branch_name, self.config)
        
        if result.get("success", False):
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Generated PR description for '{branch_name}':\n\n{result['description']}"
                    },
                ],
            }
        else:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error generating PR description: {result.get('error', 'Unknown error')}"
                    },
                ],
                "isError": True
            }
    
    async def prepare_pr(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare a pull request for the current or specified branch.
        """
        args = request.get("arguments", {})
        branch_name = args.get("branch_name")
        
        # Call the PR preparation function
        result = prepare_pr_func(branch_name, self.config)
        
        if result.get("success", False):
            # Format warnings and suggestions if any
            details = ""
            if result.get("warnings"):
                details += "\n\nWarnings:\n" + "\n".join([f"⚠️ {w}" for w in result["warnings"]])
            if result.get("suggestions"):
                details += "\n\nSuggestions:\n" + "\n".join([f"💡 {s}" for s in result["suggestions"]])
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"PR preparation for '{result['branch_name']}' completed.\n" +
                                f"Base branch: {result['base_branch']}\n" +
                                f"Title: {result['title']}\n" +
                                f"Ready for submission: {result['ready']}" +
                                details
                    },
                ],
            }
        else:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error preparing PR: {result.get('error', 'Unknown error')}"
                    },
                ],
                "isError": True
            }
    
    async def submit_pr(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit a pull request for the current or specified branch.
        """
        args = request.get("arguments", {})
        branch_name = args.get("branch_name")
        force = args.get("force", False)
        
        # Call the PR submission function
        result = submit_pr_func(branch_name, force, self.config)
        
        if result.get("success", False):
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"PR for '{result['branch_name']}' submitted successfully.\n" +
                                f"Title: {result['title']}\n" +
                                f"Base branch: {result['base_branch']}\n" +
                                f"Pull request details: {result.get('pull_request', 'No details available')}"
                    },
                ],
            }
        else:
            error_details = ""
            if result.get("warnings"):
                error_details += "\n\nWarnings:\n" + "\n".join([f"⚠️ {w}" for w in result["warnings"]])
            if result.get("suggestions"):
                error_details += "\n\nSuggestions:\n" + "\n".join([f"💡 {s}" for s in result["suggestions"]])
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error submitting PR: {result.get('error', 'Unknown error')}" + error_details
                    },
                ],
                "isError": True
            }
    
    async def create_pull_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a pull request on GitHub with generated description.
        """
        branch_name = request.get("arguments", {}).get("branch_name", "")
        
        # Call the create PR function
        result = create_pr(branch_name, self.config)
        
        if result.get("success", False):
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Pull request created for '{result['branch_name']}'.\n" +
                                f"Details: {result.get('pull_request', 'No details available')}"
                    },
                ],
            }
        else:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error creating pull request: {result.get('error', 'Unknown error')}"
                    },
                ],
                "isError": True
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
    
    # GitHub integration methods
    async def get_github_repository_info(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get information about a GitHub repository.
        """
        args = request.get("arguments", {})
        owner = args.get("owner", "")
        repo = args.get("repo", "")
        
        # Call the GitHub adapter function
        result = get_repository_info(owner, repo, self.config)
        
        if result.get("success", False):
            # Format the response for display
            repo_info = result.get("repository", {})
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Repository information for {owner}/{repo}:\n" +
                                f"Description: {repo_info.get('description', 'No description')}\n" +
                                f"Default branch: {repo_info.get('default_branch', 'unknown')}\n" +
                                f"Stars: {repo_info.get('stargazers_count', 0)}\n" +
                                f"Forks: {repo_info.get('forks_count', 0)}\n" +
                                f"Open issues: {repo_info.get('open_issues_count', 0)}"
                    },
                ],
            }
        else:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error getting repository information: {result.get('error', 'Unknown error')}"
                    },
                ],
                "isError": True
            }
    
    async def create_github_branch(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new branch in a GitHub repository.
        """
        args = request.get("arguments", {})
        owner = args.get("owner", "")
        repo = args.get("repo", "")
        branch_name = args.get("branch_name", "")
        base_branch = args.get("base_branch", "")
        
        # Call the GitHub adapter function
        result = github_create_branch(owner, repo, branch_name, base_branch, self.config)
        
        if result.get("success", False):
            return {
                "content": [
                    {
                        "type": "text",
                        "text": result.get("message", f"Created branch '{branch_name}' from '{base_branch}' in {owner}/{repo}")
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
    
    async def create_github_pull_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a pull request in a GitHub repository.
        """
        args = request.get("arguments", {})
        owner = args.get("owner", "")
        repo = args.get("repo", "")
        title = args.get("title", "")
        body = args.get("body", "")
        head = args.get("head", "")
        base = args.get("base", "")
        draft = args.get("draft", False)
        
        # Call the GitHub adapter function
        result = github_create_pr(owner, repo, title, body, head, base, draft, self.config)
        
        if result.get("success", False):
            return {
                "content": [
                    {
                        "type": "text",
                        "text": result.get("message", f"Created pull request in {owner}/{repo}") + 
                                f"\nPR #{result.get('pr_number', 'unknown')}: {result.get('html_url', '')}"
                    },
                ],
            }
        else:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error creating pull request: {result.get('error', 'Unknown error')}"
                    },
                ],
                "isError": True
            }
    
    async def get_github_file_contents(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get the contents of a file from a GitHub repository.
        """
        args = request.get("arguments", {})
        owner = args.get("owner", "")
        repo = args.get("repo", "")
        path = args.get("path", "")
        ref = args.get("ref")
        
        # Call the GitHub adapter function
        result = get_file_contents(owner, repo, path, ref, self.config)
        
        if result.get("success", False):
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Contents of {path} in {owner}/{repo}:\n\n{result.get('content', '')}"
                    },
                ],
            }
        else:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error getting file contents: {result.get('error', 'Unknown error')}"
                    },
                ],
                "isError": True
            }
    
    async def update_github_file(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a file in a GitHub repository.
        """
        args = request.get("arguments", {})
        owner = args.get("owner", "")
        repo = args.get("repo", "")
        path = args.get("path", "")
        message = args.get("message", "Update file")
        content = args.get("content", "")
        branch = args.get("branch", "")
        sha = args.get("sha", "")
        
        # Call the GitHub adapter function
        result = update_file(owner, repo, path, message, content, branch, sha, self.config)
        
        if result.get("success", False):
            return {
                "content": [
                    {
                        "type": "text",
                        "text": result.get("message", f"Updated file {path} on {branch} in {owner}/{repo}")
                    },
                ],
            }
        else:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error updating file: {result.get('error', 'Unknown error')}"
                    },
                ],
                "isError": True
            }
    
    async def get_github_workflow_status(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get the workflow status for a branch or repository.
        """
        args = request.get("arguments", {})
        owner = args.get("owner", "")
        repo = args.get("repo", "")
        branch = args.get("branch")
        
        # Create a GitHub adapter instance
        github_adapter = GitHubAdapter(self.config)
        
        # Call the adapter method
        result = github_adapter.get_workflow_status(owner, repo, branch)
        
        if result.get("success", False):
            # Format the response for display
            output = f"Workflow status for {owner}/{repo}"
            if branch:
                output += f", branch '{branch}'"
            
            # Add branch information if available
            if "branch" in result:
                branch_info = result["branch"]
                output += f"\n\nBranch Information:\n" + \
                          f"Name: {branch_info.get('name', branch)}\n" + \
                          f"SHA: {branch_info.get('commit', {}).get('sha', 'unknown')}"
            
            # Add PR information if available
            if "pull_requests" in result:
                prs = result["pull_requests"]
                if prs:
                    output += f"\n\nPull Requests ({len(prs)}):"
                    for pr in prs:
                        output += f"\n- #{pr.get('number', 'unknown')}: {pr.get('title', 'No title')}"
                        output += f" ({pr.get('state', 'unknown')})"
                else:
                    output += "\n\nNo open pull requests found."
            
            # Add repository information if available
            if "repository" in result:
                repo_info = result["repository"]
                output += f"\n\nRepository Information:\n" + \
                          f"Default branch: {repo_info.get('default_branch', 'unknown')}\n" + \
                          f"Open issues: {repo_info.get('open_issues_count', 0)}"
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": output
                    },
                ],
            }
        else:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error getting workflow status: {result.get('error', 'Unknown error')}"
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
