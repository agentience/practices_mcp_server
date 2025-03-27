#!/usr/bin/env python
"""
PR templates functionality for the Practices MCP Server.
"""

from typing import Dict, Any, Optional

# Default templates for different branch types
DEFAULT_TEMPLATES = {
    "feature": """
# {jira_id}: {jira_summary}

## Changes
- 

## Jira
- [Link to ticket](https://agentience.atlassian.net/browse/{jira_id})

## Testing
- [ ] Unit tests 
- [ ] Integration tests
- [ ] Manual testing

## Documentation
- [ ] Updated relevant documentation
- [ ] Added comments to code where needed

## Screenshots / Videos
*If applicable, add screenshots or videos to help explain your changes.*
""",
    "bugfix": """
# {jira_id}: {jira_summary}

## Bug Description
*Describe the bug that was fixed*

## Root Cause
*What was causing the issue?*

## Solution
*How did you fix it?*

## Jira
- [Link to ticket](https://agentience.atlassian.net/browse/{jira_id})

## Testing
- [ ] Added regression tests 
- [ ] Verified fix locally

## Screenshots / Videos
*If applicable, add screenshots or videos to help explain the bug and fix.*
""",
    "hotfix": """
# HOTFIX {version}: {description}

## Critical Issue
*Describe the critical issue this hotfix addresses*

## Impact
*Who was affected and how severely?*

## Solution
*How was the issue resolved?*

## Testing
- [ ] Verified fix in production-like environment
- [ ] Added regression tests

## Deployment Plan
*Steps to safely deploy this hotfix*
""",
    "release": """
# Release {version}

## Release Notes
*Summary of this release*

## Key Features
*List the main features included in this release*

## Breaking Changes
*List any breaking changes and migration steps*

## Known Issues
*List any known issues that couldn't be resolved for this release*

## Deployment Instructions
*Any special deployment instructions for this release*
""",
    "docs": """
# Documentation Update: {description}

## Changes
*What documentation was updated or added?*

## Reason
*Why was this documentation change needed?*

## Areas Affected
*What parts of the documentation were affected?*
"""
}


class TemplateManager:
    """Manages PR description templates for different branch types."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize the template manager with configuration.

        Args:
            config: Configuration dictionary with PR template settings
        """
        self.config = config
        self.templates = self._load_templates()

    def _load_templates(self) -> Dict[str, str]:
        """
        Load templates from configuration or use defaults.

        Returns:
            Dictionary of PR templates for each branch type
        """
        # Get templates from config or use defaults
        templates = self.config.get("pr_templates", {})
        
        # Start with default templates
        result = DEFAULT_TEMPLATES.copy()
        
        # Override with custom templates from config
        for branch_type, template in templates.items():
            if template:
                result[branch_type] = template
                
        return result

    def get_template(self, branch_type: str) -> str:
        """
        Get a PR template for a specific branch type.

        Args:
            branch_type: Type of branch (feature, bugfix, etc.)

        Returns:
            PR template string
        """
        if branch_type in self.templates:
            return self.templates[branch_type]
        
        # Return a generic template if branch type not recognized
        return """
# {branch_name}

## Changes
- 

## Testing
- [ ] Tested changes
"""


def get_template(branch_type: str, config: Optional[Dict[str, Any]] = None) -> str:
    """
    Get a PR template for a specific branch type.

    Args:
        branch_type: Type of branch (feature, bugfix, etc.)
        config: Optional configuration dictionary

    Returns:
        PR template string
    """
    if config is None:
        config = {}
    
    manager = TemplateManager(config)
    return manager.get_template(branch_type)
