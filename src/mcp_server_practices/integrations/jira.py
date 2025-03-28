#!/usr/bin/env python
"""
Jira integration for the Practices MCP Server.
"""

from typing import Dict, Any, Optional, List, Union

# Direct import from mcp client session
import asyncio
from mcp.client.session import ClientSession
from mcp.types import Tool

def call_tool(server_name: str, tool_name: str, arguments: dict):
    """
    Call an MCP tool synchronously.
    
    Args:
        server_name: Name of the MCP server
        tool_name: Name of the tool to call
        arguments: Arguments to pass to the tool
        
    Returns:
        Result of the tool execution
    """
    result = asyncio.run(_call_tool_async(server_name, tool_name, arguments))
    return result

async def _call_tool_async(server_name: str, tool_name: str, arguments: dict):
    """
    Call an MCP tool asynchronously.
    
    Args:
        server_name: Name of the MCP server
        tool_name: Name of the tool to call
        arguments: Arguments to pass to the tool
        
    Returns:
        Result of the tool execution
    """
    session = ClientSession()
    await session.initialize()
    
    # Get the tool definition
    tool = await session.list_tools(server_name)
    
    # Call the tool
    result = await session.call_tool(server_name, tool_name, arguments)
    
    # Extract content
    content = {}
    if result and result.content:
        for item in result.content:
            if hasattr(item, "text") and item.text:
                try:
                    content = eval(item.text)
                except:
                    content = item.text
    
    await session.close()
    return content


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
        self.link_types = self._get_link_types()
        
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
    def _get_link_types(self) -> Dict[str, str]:
        """
        Get available link types from Jira.
        
        Returns:
            Dictionary mapping link type names to their IDs
        """
        try:
            result = call_tool("jira-server", "list_link_types", {})
            link_types = {}
            
            for link_type in result.get("issueLinkTypes", []):
                link_types[link_type.get("name").lower()] = link_type.get("id")
                link_types[link_type.get("inward").lower()] = link_type.get("id")
                link_types[link_type.get("outward").lower()] = link_type.get("id")
                
            return link_types
        except Exception as e:
            print(f"Error fetching Jira link types: {str(e)}")
            return {}
            
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
        
    def link_issues(self, 
                  inward_issue_id: str, 
                  outward_issue_id: str, 
                  link_type: str) -> Dict[str, Any]:
        """
        Create a link between two Jira issues.
        
        Args:
            inward_issue_id: The issue ID that is affected by the link (e.g., PMS-123)
            outward_issue_id: The issue ID that affects the other issue (e.g., PMS-456)
            link_type: The type of link (e.g., "blocks", "is blocked by", "relates to")
            
        Returns:
            Result of the link operation
        """
        try:
            # Normalize link type by converting to lowercase
            link_type_lower = link_type.lower()
            
            # Get the link type ID
            link_type_id = self.link_types.get(link_type_lower)
            
            # If link_type_id is not found, refresh link types and try again
            if not link_type_id:
                self.link_types = self._get_link_types()
                link_type_id = self.link_types.get(link_type_lower)
                
            # If still not found, use the provided string as is
            if not link_type_id:
                actual_link_type = link_type
            else:
                actual_link_type = link_type_id
            
            # Call the jira-server MCP tool to create the link
            result = call_tool(
                "jira-server", 
                "create_issue_link", 
                {
                    "inwardIssueKey": inward_issue_id,
                    "outwardIssueKey": outward_issue_id,
                    "linkType": actual_link_type
                }
            )
            
            return {
                "success": True,
                "message": f"Linked {inward_issue_id} to {outward_issue_id} with link type '{link_type}'",
                "inward_issue_id": inward_issue_id,
                "outward_issue_id": outward_issue_id,
                "link_type": link_type
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "inward_issue_id": inward_issue_id,
                "outward_issue_id": outward_issue_id,
                "link_type": link_type
            }
            
    def get_issue_links(self, issue_id: str) -> List[Dict[str, Any]]:
        """
        Get links for a specific Jira issue.
        
        Args:
            issue_id: The issue ID to get links for (e.g., PMS-123)
            
        Returns:
            List of issue links
        """
        try:
            # Get the issue details with the jira-server MCP tool
            issue = self.get_issue(issue_id)
            
            if not issue:
                return []
                
            # Extract links from the issue
            links = issue.get("fields", {}).get("issuelinks", [])
            
            # Format the links in a standardized way
            formatted_links = []
            for link in links:
                link_type = link.get("type", {}).get("name", "")
                
                # Handle inward link
                if "inwardIssue" in link:
                    linked_issue = link.get("inwardIssue", {})
                    formatted_links.append({
                        "type": link_type,
                        "direction": "inward",
                        "issue_id": linked_issue.get("key"),
                        "summary": linked_issue.get("fields", {}).get("summary", ""),
                        "status": linked_issue.get("fields", {}).get("status", {}).get("name", "")
                    })
                
                # Handle outward link
                if "outwardIssue" in link:
                    linked_issue = link.get("outwardIssue", {})
                    formatted_links.append({
                        "type": link_type,
                        "direction": "outward",
                        "issue_id": linked_issue.get("key"),
                        "summary": linked_issue.get("fields", {}).get("summary", ""),
                        "status": linked_issue.get("fields", {}).get("status", {}).get("name", "")
                    })
            
            return formatted_links
        except Exception as e:
            print(f"Error fetching issue links for {issue_id}: {str(e)}")
            return []


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


def link_issues(inward_issue_id: str, outward_issue_id: str, link_type: str, 
               config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Create a link between two Jira issues.
    
    Args:
        inward_issue_id: The issue ID that is affected by the link (e.g., PMS-123)
        outward_issue_id: The issue ID that affects the other issue (e.g., PMS-456)
        link_type: The type of link (e.g., "blocks", "is blocked by", "relates to")
        config: Optional configuration dictionary
        
    Returns:
        Result of the link operation
    """
    if config is None:
        config = {}
        
    adapter = JiraAdapter(config)
    return adapter.link_issues(inward_issue_id, outward_issue_id, link_type)


def get_issue_links(issue_id: str, config: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Get links for a specific Jira issue.
    
    Args:
        issue_id: The issue ID to get links for (e.g., PMS-123)
        config: Optional configuration dictionary
        
    Returns:
        List of issue links
    """
    if config is None:
        config = {}
        
    adapter = JiraAdapter(config)
    return adapter.get_issue_links(issue_id)
