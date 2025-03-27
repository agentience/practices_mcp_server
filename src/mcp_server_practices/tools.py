#!/usr/bin/env python
"""
Tool definitions for the Practices MCP Server.

This module defines the input schemas and documentation for the MCP tools.

Copyright (c) 2025 Agentience.ai
Author: Troy Molander
License: MIT License - See LICENSE file for details

Version: 0.1.0
"""

from typing import Dict, Any, List


def get_tool_definitions() -> List[Dict[str, Any]]:
    """
    Get the tool definitions for the Practices MCP Server.
    
    Returns:
        List of tool definitions
    """
    return [
        # Branch tools
        {
            "name": "validate_branch_name",
            "description": "Validate a branch name against the configured branching strategy",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "branch_name": {
                        "type": "string",
                        "description": "Name of the branch to validate"
                    }
                },
                "required": ["branch_name"]
            }
        },
        {
            "name": "create_branch",
            "description": "Create a new branch following the branching convention",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "branch_type": {
                        "type": "string",
                        "description": "Type of branch to create (feature, bugfix, hotfix, release, docs)",
                        "enum": ["feature", "bugfix", "hotfix", "release", "docs"]
                    },
                    "identifier": {
                        "type": "string",
                        "description": "For feature/bugfix: Jira issue ID (e.g., PMS-123). For hotfix/release: version (e.g., 1.0.1). For docs: brief description."
                    },
                    "description": {
                        "type": ["array", "string", "null"],
                        "description": "Brief description for the branch. Can be a string or list of words.",
                        "items": {
                            "type": "string"
                        }
                    },
                    "update_jira": {
                        "type": "boolean",
                        "description": "Whether to update Jira issue status to 'In Progress'",
                        "default": True
                    }
                },
                "required": ["branch_type", "identifier"]
            }
        },
        {
            "name": "get_branch_info",
            "description": "Get information about a branch based on its name",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "branch_name": {
                        "type": "string",
                        "description": "Name of the branch to analyze"
                    }
                },
                "required": ["branch_name"]
            }
        },
        
        # Version tools
        {
            "name": "validate_version",
            "description": "Validate version consistency across files",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "get_current_version",
            "description": "Get the current version of the project",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "bump_version",
            "description": "Bump the version according to semantic versioning",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "part": {
                        "type": "string",
                        "description": "Part of the version to bump",
                        "enum": ["major", "minor", "patch", "prerelease"]
                    }
                },
                "required": ["part"]
            }
        },
        
        # PR tools
        {
            "name": "generate_pr_description",
            "description": "Generate a PR description based on branch and configuration",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "branch_name": {
                        "type": "string",
                        "description": "Name of the branch for the PR"
                    }
                },
                "required": ["branch_name"]
            }
        },
        {
            "name": "prepare_pr",
            "description": "Prepare a pull request for the current or specified branch",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "branch_name": {
                        "type": "string",
                        "description": "Name of the branch for the PR (defaults to current branch)"
                    }
                }
            }
        },
        {
            "name": "submit_pr",
            "description": "Submit a pull request for the current or specified branch",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "branch_name": {
                        "type": "string",
                        "description": "Name of the branch for the PR (defaults to current branch)"
                    },
                    "force": {
                        "type": "boolean",
                        "description": "Force submission even if there are warnings",
                        "default": false
                    }
                }
            }
        },
        {
            "name": "create_pull_request",
            "description": "Create a pull request on GitHub with generated description",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "branch_name": {
                        "type": "string",
                        "description": "Name of the branch for the PR"
                    }
                },
                "required": ["branch_name"]
            }
        },
        
        # Pre-commit hooks tools
        {
            "name": "install_pre_commit_hooks",
            "description": "Install pre-commit hooks in a Git repository",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "repo_path": {
                        "type": "string",
                        "description": "Path to the Git repository",
                        "default": "."
                    }
                }
            }
        },
        {
            "name": "check_git_repo_init",
            "description": "Check if a Git repository was recently initialized",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "repo_path": {
                        "type": "string",
                        "description": "Path to check for Git repository",
                        "default": "."
                    }
                }
            }
        },
        {
            "name": "update_pre_commit_hooks",
            "description": "Update pre-commit hooks in a Git repository",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "repo_path": {
                        "type": "string",
                        "description": "Path to the Git repository",
                        "default": "."
                    }
                }
            }
        },
        
        # License header tools
        {
            "name": "add_license_header",
            "description": "Add a license header to a file",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Path to the file"
                    },
                    "description": {
                        "type": "string",
                        "description": "Description of the file's purpose",
                        "default": ""
                    }
                },
                "required": ["filename"]
            }
        },
        {
            "name": "verify_license_header",
            "description": "Check if a file has a proper license header",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Path to the file"
                    }
                },
                "required": ["filename"]
            }
        },
        {
            "name": "process_license_headers_batch",
            "description": "Process multiple files to add or check license headers",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Path to the directory"
                    },
                    "pattern": {
                        "type": "string",
                        "description": "File pattern to match (e.g., '*.py')",
                        "default": "*.*"
                    },
                    "check_only": {
                        "type": "boolean",
                        "description": "Only check for headers without adding them",
                        "default": False
                    },
                    "description": {
                        "type": "string",
                        "description": "Description to use for headers",
                        "default": ""
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "Process subdirectories recursively",
                        "default": False
                    }
                },
                "required": ["directory"]
            }
        }
    ]
