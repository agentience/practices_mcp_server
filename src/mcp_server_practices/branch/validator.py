#!/usr/bin/env python
"""
Branch validation functionality for the Practices MCP Server.
"""

import re
from typing import Dict, Optional, Any, Tuple, Pattern


class BranchValidator:
    """Validates branch names according to configured branching strategy."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize the branch validator with configuration.

        Args:
            config: Configuration dictionary containing branch patterns and settings
        """
        self.config = config
        self.branch_patterns = self._get_branch_patterns()

    def _get_branch_patterns(self) -> Dict[str, Pattern]:
        """
        Get regex patterns for different branch types based on configuration.

        Returns:
            Dictionary of compiled regex patterns for each branch type
        """
        # Get project key from config or use default
        project_key = self.config.get("project_key", "PMS")
        
        # Create patterns based on branching strategy
        if self.config.get("branching_strategy", "gitflow") == "gitflow":
            return {
                "feature": re.compile(fr"^feature/({project_key}-\d+)-(.+)$"),
                "bugfix": re.compile(fr"^bugfix/({project_key}-\d+)-(.+)$"),
                "hotfix": re.compile(r"^hotfix/(\d+\.\d+\.\d+(?:-[a-zA-Z0-9.]+)?)-(.+)$"),
                "release": re.compile(r"^release/(\d+\.\d+\.\d+(?:-[a-zA-Z0-9.]+)?)(?:-(.+))?$"),
                "docs": re.compile(r"^docs/(.+)$"),
            }
        else:
            # Default to gitflow patterns
            return {
                "feature": re.compile(fr"^feature/({project_key}-\d+)-(.+)$"),
                "bugfix": re.compile(fr"^bugfix/({project_key}-\d+)-(.+)$"),
                "hotfix": re.compile(r"^hotfix/(\d+\.\d+\.\d+(?:-[a-zA-Z0-9.]+)?)-(.+)$"),
                "release": re.compile(r"^release/(\d+\.\d+\.\d+(?:-[a-zA-Z0-9.]+)?)(?:-(.+))?$"),
                "docs": re.compile(r"^docs/(.+)$"),
            }

    def validate(self, branch_name: str) -> Dict[str, Any]:
        """
        Validate a branch name against configured patterns.

        Args:
            branch_name: The branch name to validate

        Returns:
            Dictionary with validation results
        """
        branch_type = self._get_branch_type(branch_name)
        
        if not branch_type:
            return {
                "valid": False,
                "error": "Branch name does not match any supported branch type pattern",
                "branch_type": None,
                "expected_patterns": {
                    "feature": "feature/PMS-123-brief-description",
                    "bugfix": "bugfix/PMS-123-brief-description",
                    "hotfix": "hotfix/1.0.1-brief-description",
                    "release": "release/1.1.0",
                    "docs": "docs/update-readme",
                },
            }
        
        # Parse the branch components
        components = self._parse_branch_components(branch_name, branch_type)
        
        return {
            "valid": True,
            "branch_type": branch_type,
            "components": components,
            "base_branch": self._get_base_branch(branch_type),
        }

    def _get_branch_type(self, branch_name: str) -> Optional[str]:
        """
        Determine the branch type from the branch name.

        Args:
            branch_name: The branch name to check

        Returns:
            Branch type or None if not recognized
        """
        for branch_type, pattern in self.branch_patterns.items():
            if pattern.match(branch_name):
                return branch_type
        return None

    def _parse_branch_components(self, branch_name: str, branch_type: str) -> Dict[str, Any]:
        """
        Parse the components from a branch name.

        Args:
            branch_name: The branch name to parse
            branch_type: The type of branch (feature, bugfix, etc.)

        Returns:
            Dictionary with parsed components
        """
        match = self.branch_patterns[branch_type].match(branch_name)
        if not match:
            return {}
        
        result = {}
        
        if branch_type in ["feature", "bugfix"]:
            result["identifier"] = match.group(1)  # Jira ID
            result["description"] = match.group(2)  # Description
        elif branch_type == "hotfix":
            result["version"] = match.group(1)  # Version
            result["description"] = match.group(2)  # Description
        elif branch_type == "release":
            result["version"] = match.group(1)  # Version
            # Description is optional for release branches
            result["description"] = match.group(2) if match.group(2) else None
        elif branch_type == "docs":
            result["description"] = match.group(1)  # Description
            
        return result

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


def validate_branch_name(branch_name: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Validate a branch name against configured patterns.

    Args:
        branch_name: The branch name to validate
        config: Optional configuration dictionary

    Returns:
        Dictionary with validation results
    """
    if config is None:
        config = {}
    
    validator = BranchValidator(config)
    return validator.validate(branch_name)
