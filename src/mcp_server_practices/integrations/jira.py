#!/usr/bin/env python
"""
Jira integration for the Practices MCP Server.
"""

from typing import Dict, Any, Optional, List

# Direct import from mcp package
from mcp.tools import call_tool


class JiraAdapter:
    """
    Adapter for interacting with the Jira MCP server.
    """
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize the Jira adapter with configuration.
        
        Args:
            config: Configuration dictionary with Jira settings
        """
        self.config = config
        
    def get_issue(self, issue_id: str) -> Optional[Dict[str, Any]]:
        """
        Get issue details from Jira.
        
        Args:
            issue_id: The issue ID to fetch (e.g., PMS-123)
            
        Returns:
            Issue details or None if not found or error
        """
        try:
            project_key = issue_id.split("-")[0]
            issue_number = int(issue_id.split("-")[1])
            
            # Call the jira-server MCP tool
            result = call_tool(
                "jira-server", 
                "get_issues", 
                {
                    "projectKey": project_key,
                    "jql": f"key = {issue_id}"
                }
            )
            
            # Find the issue in the result
            issues = result.get("issues", [])
            for issue in issues:
                if issue.get("key") == issue_id:
                    return issue
                    
            return None
        except Exception as e:
            print(f"Error fetching Jira issue {issue_id}: {str(e)}")
            return None
            
    def update_issue_status(self, issue_id: str, status: str) -> Dict[str, Any]:
        """
        Update the status of a Jira issue.
        
        Args:
            issue_id: The issue ID to update (e.g., PMS-123)
            status: The new status (e.g., "In Progress")
            
        Returns:
            Result of the update operation
        """
        try:
            # Call the jira-server MCP tool to update the issue
            result = call_tool(
                "jira-server", 
                "update_issue", 
                {
                    "issueKey": issue_id,
                    "status": status
                }
            )
            
            return {
                "success": True,
                "message": f"Updated {issue_id} status to '{status}'",
                "issue_id": issue_id,
                "status": status
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "issue_id": issue_id,
                "status": status
            }
            
    def format_issue_summary(self, issue: Dict[str, Any]) -> str:
        """
        Format issue summary for use in branch names.
        
        Args:
            issue: Issue details from Jira
            
        Returns:
            Formatted summary
        """
        summary = issue.get("fields", {}).get("summary", "")
        
        # Convert to lowercase
        result = summary.lower()
        
        # Replace spaces and special characters with hyphens
        import re
        result = re.sub(r"[^a-z0-9]+", "-", result)
        
        # Remove leading and trailing hyphens
        result = result.strip("-")
        
        # Limit length to 50 characters
        if len(result) > 50:
            result = result[:50]
            
        return result


def get_issue(issue_id: str, config: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """
    Get issue details from Jira.
    
    Args:
        issue_id: The issue ID to fetch (e.g., PMS-123)
        config: Optional configuration dictionary
        
    Returns:
        Issue details or None if not found or error
    """
    if config is None:
        config = {}
        
    adapter = JiraAdapter(config)
    return adapter.get_issue(issue_id)
    
    
def update_issue_status(issue_id: str, status: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Update the status of a Jira issue.
    
    Args:
        issue_id: The issue ID to update (e.g., PMS-123)
        status: The new status (e.g., "In Progress")
        config: Optional configuration dictionary
        
    Returns:
        Result of the update operation
    """
    if config is None:
        config = {}
        
    adapter = JiraAdapter(config)
    return adapter.update_issue_status(issue_id, status)
