#!/usr/bin/env python
"""
Branch creation functionality for the Practices MCP Server.
"""

import re
import subprocess
from typing import Dict, Optional, Any, List

from mcp_server_practices.branch.validator import BranchValidator


class BranchCreator:
    """Creates branches according to configured branching strategy."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize the branch creator with configuration.

        Args:
            config: Configuration dictionary containing branching settings
        """
        self.config = config
        self.validator = BranchValidator(config)

    def create_branch(self, branch_type: str, identifier: str, description: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Create a new branch following the configured branching convention.

        Args:
            branch_type: Type of branch to create (feature, bugfix, hotfix, release, docs)
            identifier: Jira ID for feature/bugfix, version for release/hotfix, description for docs
            description: Description for the branch (optional for release branches)

        Returns:
            Dictionary with creation results
        """
        # Format description if provided
        formatted_description = None
        if description:
            formatted_description = "-".join(description)

        # Validate and construct branch name
        branch_name = self._construct_branch_name(branch_type, identifier, formatted_description)
        if not branch_name:
            return {
                "success": False,
                "error": "Failed to construct valid branch name",
                "branch_name": None,
            }

        # Determine base branch
        base_branch = self._get_base_branch(branch_type)

        # Create the branch
        try:
            # Ensure we have the latest base branch
            self._run_command(["git", "fetch", "origin", base_branch])
            self._run_command(["git", "checkout", base_branch])
            self._run_command(["git", "pull", "origin", base_branch])

            # Create and checkout the new branch
            self._run_command(["git", "checkout", "-b", branch_name])

            return {
                "success": True,
                "branch_name": branch_name,
                "base_branch": base_branch,
                "message": f"Successfully created branch: {branch_name} from {base_branch}",
            }
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Error creating branch: {str(e)}",
                "branch_name": branch_name,
                "base_branch": base_branch,
            }

    def _construct_branch_name(self, branch_type: str, identifier: str, description: Optional[str]) -> Optional[str]:
        """
        Construct a branch name following the conventions.

        Args:
            branch_type: Type of branch (feature, bugfix, hotfix, release, docs)
            identifier: Jira ID, version, or description
            description: Additional description (optional for release branches)

        Returns:
            Constructed branch name or None if validation fails
        """
        project_key = self.config.get("project_key", "PMS")

        # Construct branch name based on type
        if branch_type in ["feature", "bugfix"]:
            # Validate Jira issue ID format
            if not re.match(fr"^{project_key}-\d+$", identifier):
                return None

            if not description:
                return None

            return f"{branch_type}/{identifier}-{description}"

        elif branch_type == "hotfix":
            # Validate version format
            if not re.match(r"^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?$", identifier):
                return None

            if not description:
                return None

            return f"hotfix/{identifier}-{description}"

        elif branch_type == "release":
            # Validate version format
            if not re.match(r"^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?$", identifier):
                return None

            branch_name = f"release/{identifier}"
            if description:
                branch_name += f"-{description}"
            return branch_name

        elif branch_type == "docs":
            description_text = description if description else identifier
            return f"docs/{description_text}"

        return None

    def _get_base_branch(self, branch_type: str) -> str:
        """
        Determine the base branch for a given branch type.

        Args:
            branch_type: The type of branch (feature, bugfix, etc.)

        Returns:
            Name of the base branch
        """
        main_branch = self.config.get("main_branch", "main")
        develop_branch = self.config.get("develop_branch", "develop")
        
        if branch_type in ["feature", "bugfix", "docs", "release"]:
            return develop_branch
        elif branch_type == "hotfix":
            return main_branch
        else:
            return develop_branch

    def _run_command(self, command: List[str]) -> str:
        """
        Run a shell command and return its output.

        Args:
            command: Command to run as a list of strings

        Returns:
            Command output as string

        Raises:
            subprocess.CalledProcessError: If the command fails
        """
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()


def create_branch(branch_type: str, identifier: str, description: Optional[List[str]] = None, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Create a new branch following the configured branching convention.

    Args:
        branch_type: Type of branch to create (feature, bugfix, hotfix, release, docs)
        identifier: Jira ID for feature/bugfix, version for release/hotfix, description for docs
        description: Description for the branch (optional for release branches)
        config: Optional configuration dictionary

    Returns:
        Dictionary with creation results
    """
    if config is None:
        config = {}
    
    creator = BranchCreator(config)
    return creator.create_branch(branch_type, identifier, description)
