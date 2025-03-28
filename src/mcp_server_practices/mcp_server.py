#!/usr/bin/env python
"""
MCP server implementation for development practices using modern decorator pattern.
"""

import asyncio
import sys
from typing import Any, Dict, List, Optional

# Import directly from mcp package
from mcp.server.fastmcp import FastMCP
from mcp.content import TextContent

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

# Register resources
mcp.resources.add_template(
    "practices://templates/branching-strategy/{type}",
    "Branching strategy template",
    "Template for branching strategies"
)

# Define tools using decorators
@mcp.tool(
    name="validate_branch_name",
    description="Validate a branch name against the configured branching strategy",
    schema={
        "type": "object",
        "properties": {
            "branch_name": {
                "type": "string",
                "description": "The branch name to validate"
            }
        },
        "required": ["branch_name"]
    }
)
async def validate_branch_name(branch_name: str) -> List[TextContent]:
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

@mcp.tool(
    name="create_branch",
    description="Create a new branch following the branching convention",
    schema={
        "type": "object",
        "properties": {
            "branch_type": {
                "type": "string",
                "description": "Type of branch (feature, bugfix, hotfix, release, docs)"
            },
            "identifier": {
                "type": "string",
                "description": "Jira issue ID or version number"
            },
            "description": {
                "type": ["string", "array"],
                "description": "Description words or string"
            },
            "update_jira": {
                "type": "boolean",
                "description": "Whether to update Jira issue status"
            }
        },
        "required": ["branch_type", "identifier"]
    }
)
async def create_branch(branch_type: str, identifier: str, description: Any = None, update_jira: bool = True) -> List[TextContent]:
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

@mcp.tool(
    name="get_branch_info",
    description="Get information about a branch based on its name",
    schema={
        "type": "object",
        "properties": {
            "branch_name": {
                "type": "string",
                "description": "Name of the branch"
            }
        },
        "required": ["branch_name"]
    }
)
async def get_branch_info(branch_name: str) -> List[TextContent]:
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

@mcp.tool(
    name="validate_version",
    description="Validate version consistency across files",
    schema={
        "type": "object",
        "properties": {},
        "required": []
    }
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

@mcp.tool(
    name="get_current_version",
    description="Get the current version of the project",
    schema={
        "type": "object",
        "properties": {},
        "required": []
    }
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

@mcp.tool(
    name="bump_version",
    description="Bump the version according to semantic versioning",
    schema={
        "type": "object",
        "properties": {
            "part": {
                "type": "string",
                "description": "Version part to bump (major, minor, patch, prerelease)",
                "enum": ["major", "minor", "patch", "prerelease"]
            }
        },
        "required": ["part"]
    }
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

@mcp.tool(
    name="generate_pr_description",
    description="Generate a PR description based on branch and configuration",
    schema={
        "type": "object",
        "properties": {
            "branch_name": {
                "type": "string",
                "description": "Branch name to generate description for"
            }
        },
        "required": ["branch_name"]
    }
)
async def generate_pr_description(branch_name: str) -> List[TextContent]:
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

@mcp.tool(
    name="create_pull_request",
    description="Create a pull request on GitHub with generated description",
    schema={
        "type": "object",
        "properties": {
            "branch_name": {
                "type": "string",
                "description": "Branch name to create PR for"
            }
        },
        "required": ["branch_name"]
    }
)
async def create_pull_request(branch_name: str) -> List[TextContent]:
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

@mcp.tool(
    name="prepare_pr",
    description="Prepare a pull request for the current or specified branch",
    schema={
        "type": "object",
        "properties": {
            "branch_name": {
                "type": "string",
                "description": "Branch name to prepare PR for"
            }
        },
        "required": []
    }
)
async def prepare_pr(branch_name: Optional[str] = None) -> List[TextContent]:
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

@mcp.tool(
    name="submit_pr",
    description="Submit a pull request for the current or specified branch",
    schema={
        "type": "object",
        "properties": {
            "branch_name": {
                "type": "string",
                "description": "Branch name to submit PR for"
            },
            "force": {
                "type": "boolean",
                "description": "Force submission even if checks fail"
            }
        },
        "required": []
    }
)
async def submit_pr(branch_name: Optional[str] = None, force: bool = False) -> List[TextContent]:
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

@mcp.tool(
    name="install_pre_commit_hooks",
    description="Install pre-commit hooks in a Git repository",
    schema={
        "type": "object",
        "properties": {
            "repo_path": {
                "type": "string",
                "description": "Path to Git repository"
            }
        },
        "required": []
    }
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

@mcp.tool(
    name="check_git_repo_init",
    description="Check if a Git repository was recently initialized",
    schema={
        "type": "object",
        "properties": {
            "repo_path": {
                "type": "string",
                "description": "Path to Git repository"
            }
        },
        "required": []
    }
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

@mcp.tool(
    name="update_pre_commit_hooks",
    description="Update pre-commit hooks in a Git repository",
    schema={
        "type": "object",
        "properties": {
            "repo_path": {
                "type": "string",
                "description": "Path to Git repository"
            }
        },
        "required": []
    }
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

@mcp.tool(
    name="add_license_header",
    description="Add a license header to a file",
    schema={
        "type": "object",
        "properties": {
            "filename": {
                "type": "string",
                "description": "Path to the file"
            },
            "description": {
                "type": "string",
                "description": "File description to include in header"
            }
        },
        "required": ["filename"]
    }
)
async def add_license_header_tool(filename: str, description: str = "") -> List[TextContent]:
    """
    Add a license header to a file.
    """
    result = add_license_header(filename, description, config)
    
    if result.get("success", False):
        return [
            TextContent(result.get("message", f"License header added to {filename}"))
        ]
    else:
        return [
            TextContent(
                f"Error adding license header: {result.get('error', 'Unknown error')}",
                is_error=True
            )
        ]

@mcp.tool(
    name="verify_license_header",
    description="Check if a file has a proper license header",
    schema={
        "type": "object",
        "properties": {
            "filename": {
                "type": "string",
                "description": "Path to the file"
            }
        },
        "required": ["filename"]
    }
)
async def verify_license_header_tool(filename: str) -> List[TextContent]:
    """
    Check if a file has a proper license header.
    """
    result = verify_license_header(filename)
    
    return [
        TextContent(result.get("message", f"License header check for {filename}"))
    ]

@mcp.tool(
    name="process_license_headers_batch",
    description="Process multiple files to add or check license headers",
    schema={
        "type": "object",
        "properties": {
            "directory": {
                "type": "string",
                "description": "Directory to process"
            },
            "pattern": {
                "type": "string",
                "description": "File pattern to match"
            },
            "check_only": {
                "type": "boolean",
                "description": "Only check, don't modify files"
            },
            "description": {
                "type": "string",
                "description": "Default file description"
            },
            "recursive": {
                "type": "boolean",
                "description": "Process subdirectories"
            }
        },
        "required": ["directory"]
    }
)
async def process_license_headers_batch_tool(directory: str, pattern: str = "*.*", check_only: bool = False, description: str = "", recursive: bool = False) -> List[TextContent]:
    """
    Process multiple files to add or check license headers.
    """
    result = process_files_batch(directory, pattern, check_only, description, recursive)
    
    if result.get("success", False):
        action = "Checked" if check_only else "Processed"
        return [
            TextContent(
                f"{action} {result.get('total_files', 0)} files.\n" +
                f"Missing headers: {result.get('missing_headers', 0)}\n" +
                f"Modified files: {result.get('modified_files', 0)}\n" +
                f"Errors: {result.get('errors', 0)}"
            )
        ]
    else:
        return [
            TextContent(
                f"Error processing license headers: {result.get('error', 'Unknown error')}",
                is_error=True
            )
        ]

# Register GitHub-related tools
@mcp.tool(
    name="get_github_repository_info",
    description="Get information about a GitHub repository",
    schema={
        "type": "object",
        "properties": {
            "owner": {
                "type": "string",
                "description": "Repository owner (username or organization)"
            },
            "repo": {
                "type": "string",
                "description": "Repository name"
            }
        },
        "required": ["owner", "repo"]
    }
)
async def get_github_repository_info(owner: str, repo: str) -> List[TextContent]:
    """
    Get information about a GitHub repository.
    """
    # Call the GitHub adapter function
    result = get_repository_info(owner, repo, config)
    
    if result.get("success", False):
        # Format the response for display
        repo_info = result.get("repository", {})
        return [
            TextContent(
                f"Repository information for {owner}/{repo}:\n" +
                f"Description: {repo_info.get('description', 'No description')}\n" +
                f"Default branch: {repo_info.get('default_branch', 'unknown')}\n" +
                f"Stars: {repo_info.get('stargazers_count', 0)}\n" +
                f"Forks: {repo_info.get('forks_count', 0)}\n" +
                f"Open issues: {repo_info.get('open_issues_count', 0)}"
            )
        ]
    else:
        return [
            TextContent(
                f"Error getting repository information: {result.get('error', 'Unknown error')}",
                is_error=True
            )
        ]

@mcp.tool(
    name="create_github_branch",
    description="Create a new branch in a GitHub repository",
    schema={
        "type": "object",
        "properties": {
            "owner": {
                "type": "string",
                "description": "Repository owner (username or organization)"
            },
            "repo": {
                "type": "string",
                "description": "Repository name"
            },
            "branch_name": {
                "type": "string",
                "description": "Name for the new branch"
            },
            "base_branch": {
                "type": "string",
                "description": "Base branch to create from"
            }
        },
        "required": ["owner", "repo", "branch_name"]
    }
)
async def create_github_branch(owner: str, repo: str, branch_name: str, base_branch: Optional[str] = None) -> List[TextContent]:
    """
    Create a new branch in a GitHub repository.
    """
    # Call the GitHub adapter function
    result = github_create_branch(owner, repo, branch_name, base_branch, config)
    
    if result.get("success", False):
        return [
            TextContent(
                f"Branch '{branch_name}' created in {owner}/{repo} " +
                f"from {result.get('base', 'default branch')}."
            )
        ]
    else:
        return [
            TextContent(
                f"Error creating branch: {result.get('error', 'Unknown error')}",
                is_error=True
            )
        ]

@mcp.tool(
    name="create_github_pull_request",
    description="Create a pull request in a GitHub repository",
    schema={
        "type": "object",
        "properties": {
            "owner": {
                "type": "string",
                "description": "Repository owner (username or organization)"
            },
            "repo": {
                "type": "string",
                "description": "Repository name"
            },
            "title": {
                "type": "string",
                "description": "Pull request title"
            },
            "body": {
                "type": "string",
                "description": "Pull request description"
            },
            "head": {
                "type": "string",
                "description": "Head branch (branch with changes)"
            },
            "base": {
                "type": "string",
                "description": "Base branch (target branch)"
            },
            "draft": {
                "type": "boolean",
                "description": "Create as draft PR"
            }
        },
        "required": ["owner", "repo", "title", "head", "base"]
    }
)
async def create_github_pull_request(owner: str, repo: str, title: str, head: str, base: str, body: str = "", draft: bool = False) -> List[TextContent]:
    """
    Create a pull request in a GitHub repository.
    """
    # Call the GitHub adapter function
    result = github_create_pr(owner, repo, title, body, head, base, draft, config)
    
    if result.get("success", False):
        return [
            TextContent(
                f"Pull request created in {owner}/{repo}:\n" +
                f"Title: {title}\n" +
                f"From: {head} → {base}\n" +
                f"URL: {result.get('html_url', 'unknown')}"
            )
        ]
    else:
        return [
            TextContent(
                f"Error creating pull request: {result.get('error', 'Unknown error')}",
                is_error=True
            )
        ]

@mcp.tool(
    name="get_github_file_contents",
    description="Get the contents of a file from a GitHub repository",
    schema={
        "type": "object",
        "properties": {
            "owner": {
                "type": "string",
                "description": "Repository owner (username or organization)"
            },
            "repo": {
                "type": "string",
                "description": "Repository name"
            },
            "path": {
                "type": "string",
                "description": "Path to the file"
            },
            "ref": {
                "type": "string",
                "description": "Branch, tag, or commit SHA"
            }
        },
        "required": ["owner", "repo", "path"]
    }
)
async def get_github_file_contents(owner: str, repo: str, path: str, ref: Optional[str] = None) -> List[TextContent]:
    """
    Get the contents of a file from a GitHub repository.
    """
    # Call the GitHub adapter function
    result = get_file_contents(owner, repo, path, ref, config)
    
    if result.get("success", False):
        return [
            TextContent(
                f"Contents of {path} in {owner}/{repo}" +
                (f" (ref: {ref})" if ref else "") + 
                f":\n\n{result.get('content', '')}"
            )
        ]
    else:
        return [
            TextContent(
                f"Error getting file contents: {result.get('error', 'Unknown error')}",
                is_error=True
            )
        ]

@mcp.tool(
    name="update_github_file",
    description="Update a file in a GitHub repository",
    schema={
        "type": "object",
        "properties": {
            "owner": {
                "type": "string",
                "description": "Repository owner (username or organization)"
            },
            "repo": {
                "type": "string",
                "description": "Repository name"
            },
            "path": {
                "type": "string",
                "description": "Path to the file"
            },
            "message": {
                "type": "string",
                "description": "Commit message"
            },
            "content": {
                "type": "string",
                "description": "New file content"
            },
            "branch": {
                "type": "string",
                "description": "Branch to commit to"
            },
            "sha": {
                "type": "string",
                "description": "SHA of the file being replaced"
            }
        },
        "required": ["owner", "repo", "path", "message", "content"]
    }
)
async def update_github_file(owner: str, repo: str, path: str, message: str, content: str, branch: str = "", sha: str = "") -> List[TextContent]:
    """
    Update a file in a GitHub repository.
    """
    # Call the GitHub adapter function
    result = update_file(owner, repo, path, message, content, branch, sha, config)
    
    if result.get("success", False):
        return [
            TextContent(
                f"File {path} updated in {owner}/{repo}" +
                (f" on branch {branch}" if branch else "") +
                f".\nCommit message: {message}"
            )
        ]
    else:
        return [
            TextContent(
                f"Error updating file: {result.get('error', 'Unknown error')}",
                is_error=True
            )
        ]

@mcp.tool(
    name="get_github_workflow_status",
    description="Get the workflow status for a branch or repository",
    schema={
        "type": "object",
        "properties": {
            "owner": {
                "type": "string",
                "description": "Repository owner (username or organization)"
            },
            "repo": {
                "type": "string",
                "description": "Repository name"
            },
            "branch": {
                "type": "string",
                "description": "Branch to check status for (optional)"
            }
        },
        "required": ["owner", "repo"]
    }
)
async def get_github_workflow_status(owner: str, repo: str, branch: Optional[str] = None) -> List[TextContent]:
    """
    Get the workflow status for a branch or repository.
    """
    # Create a GitHub adapter instance
    github_adapter = GitHubAdapter(config)
    
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
        
        return [
            TextContent(output)
        ]
    else:
        return [
            TextContent(
                f"Error getting workflow status: {result.get('error', 'Unknown error')}",
                is_error=True
            )
        ]

def main() -> None:
    """Run the MCP server."""
    # Use mcp.run() for modern implementation
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
