#!/usr/bin/env python
"""
PR description generation functionality for the Practices MCP Server.
"""

from typing import Dict, Any, Optional
import re
import datetime

from ..branch.validator import validate_branch_name
from ..integrations.jira import get_issue
from .templates import get_template


class PRGenerator:
    """Generates PR descriptions from branch information."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize the PR generator with configuration.

        Args:
            config: Configuration dictionary with PR and project settings
        """
        self.config = config

    def generate_description(self, branch_name: str) -> Dict[str, Any]:
        """
        Generate a PR description for a branch.

        Args:
            branch_name: The name of the branch to generate a PR description for

        Returns:
            Dictionary with PR description and metadata
        """
        # Validate the branch name
        branch_info = validate_branch_name(branch_name, self.config)
        if not branch_info["valid"]:
            return {
                "success": False,
                "error": branch_info["error"],
                "description": "",
                "branch_name": branch_name,
            }
        
        # Get the branch type and components
        branch_type = branch_info["branch_type"]
        components = branch_info["components"]
        
        # Get the template for the branch type
        template = get_template(branch_type, self.config)
        
        # Format data based on branch type
        format_data = {
            "branch_name": branch_name,
            "description": components.get("description", ""),
        }
        
        # Add Jira information for feature and bugfix branches
        if branch_type in ["feature", "bugfix"] and "identifier" in components:
            jira_id = components["identifier"]
            format_data["jira_id"] = jira_id
            
            # Try to get Jira issue details
            issue = get_issue(jira_id, self.config)
            if issue:
                format_data["jira_summary"] = issue.get("fields", {}).get("summary", "")
                format_data["jira_description"] = self._extract_text_from_jira_description(
                    issue.get("fields", {}).get("description", {})
                )
                format_data["jira_status"] = issue.get("fields", {}).get("status", {}).get("name", "")
            else:
                format_data["jira_summary"] = f"Unknown issue {jira_id}"
        
        # Add version for hotfix and release branches
        if branch_type in ["hotfix", "release"] and "version" in components:
            format_data["version"] = components["version"]
        
        # Format the template with data
        description = template.format(**format_data)
        
        # Set up PR metadata
        base_branch = branch_info["base_branch"]
        title = self._generate_title(branch_type, components, format_data)
        
        return {
            "success": True,
            "description": description,
            "title": title,
            "base_branch": base_branch,
            "branch_name": branch_name,
            "branch_type": branch_type,
            "components": components,
            "jira_id": format_data.get("jira_id"),
            "timestamp": datetime.datetime.now().isoformat(),
        }

    def _generate_title(self, branch_type: str, components: Dict[str, Any], format_data: Dict[str, Any]) -> str:
        """
        Generate a PR title from branch information.

        Args:
            branch_type: Type of branch (feature, bugfix, etc.)
            components: Branch components from validation
            format_data: Formatted data for template

        Returns:
            PR title string
        """
        if branch_type in ["feature", "bugfix"]:
            jira_id = components.get("identifier", "")
            description = format_data.get("jira_summary", components.get("description", ""))
            return f"{jira_id}: {description}"
        
        elif branch_type == "hotfix":
            version = components.get("version", "")
            description = components.get("description", "")
            return f"HOTFIX {version}: {description}"
        
        elif branch_type == "release":
            version = components.get("version", "")
            return f"Release {version}"
        
        elif branch_type == "docs":
            description = components.get("description", "")
            return f"Docs: {description}"
        
        # Generic fallback
        return components.get("description", branch_type)

    def _extract_text_from_jira_description(self, description: Dict[str, Any]) -> str:
        """
        Extract plain text from a Jira description object.

        Args:
            description: Jira description object

        Returns:
            Plain text description
        """
        # Simple extraction for now - this could be improved to handle more complex Jira formats
        if not description or not isinstance(description, dict):
            return ""
        
        # Try to handle basic Jira Atlassian Document Format (ADF)
        if description.get("type") == "doc" and "content" in description:
            text_parts = []
            for content in description.get("content", []):
                if content.get("type") == "paragraph" and "content" in content:
                    for text_content in content.get("content", []):
                        if text_content.get("type") == "text":
                            text_parts.append(text_content.get("text", ""))
            return " ".join(text_parts)
        
        return str(description)


def generate_pr_description(branch_name: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Generate a PR description for a branch.

    Args:
        branch_name: The name of the branch to generate a PR description for
        config: Optional configuration dictionary

    Returns:
        Dictionary with PR description and metadata
    """
    if config is None:
        config = {}
    
    generator = PRGenerator(config)
    return generator.generate_description(branch_name)


def create_pull_request(branch_name: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Create a pull request for a branch.

    Args:
        branch_name: The name of the branch to create a PR for
        config: Optional configuration dictionary

    Returns:
        Dictionary with PR creation results
    """
    if config is None:
        config = {}
    
    # Generate the PR description first
    pr_data = generate_pr_description(branch_name, config)
    if not pr_data["success"]:
        return pr_data
    
    # Import GitHub integration if available
    try:
        # Import directly
        from mcp.tools import call_tool
        
        # Get repository information from config
        repo_owner = config.get("github", {}).get("owner", "")
        repo_name = config.get("github", {}).get("repo", "")
        
        if not repo_owner or not repo_name:
            return {
                "success": False,
                "error": "Missing GitHub repository configuration",
                "description": pr_data["description"],
                "pull_request": None,
            }
        
        # Create the PR using the GitHub MCP server
        result = call_tool(
            "github",
            "create_pull_request",
            {
                "owner": repo_owner,
                "repo": repo_name,
                "title": pr_data["title"],
                "body": pr_data["description"],
                "head": branch_name,
                "base": pr_data["base_branch"],
                "draft": config.get("pull_requests", {}).get("create_as_draft", True),
            }
        )
        
        # Update Jira status if PR was created and option is enabled
        if result and pr_data.get("jira_id") and config.get("jira", {}).get("update_on_pr", True):
            from ..integrations.jira import update_issue_status
            update_issue_status(
                pr_data["jira_id"],
                config.get("jira", {}).get("pr_submitted_status", "In Review")
            )
        
        return {
            "success": True,
            "pull_request": result,
            "description": pr_data["description"],
            "title": pr_data["title"],
            "base_branch": pr_data["base_branch"],
            "branch_name": branch_name,
        }
        
    except ImportError:
        # If GitHub integration is not available, just return the PR data
        return {
            "success": False,
            "error": "GitHub integration is not available",
            "description": pr_data["description"],
            "pull_request": None,
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to create pull request: {str(e)}",
            "description": pr_data["description"],
            "pull_request": None,
        }
