#!/usr/bin/env python
"""
GitHub integration for the Practices MCP Server.
"""

from typing import Dict, Any, Optional, List, Union
import json
import re

from mcp.tools import call_tool


class GitHubAdapter:
    """
    Adapter for interacting with the GitHub MCP server.
    """
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize the GitHub adapter with configuration.
        
        Args:
            config: Configuration dictionary with GitHub settings
        """
        self.config = config
        
        # Extract default repository information if available
        self.default_owner = config.get("github", {}).get("repository", {}).get("owner")
        self.default_repo = config.get("github", {}).get("repository", {}).get("name")
        
        # Feature flags
        self.create_pr_enabled = config.get("github", {}).get("features", {}).get("create_pr", True)
        self.auto_merge_enabled = config.get("github", {}).get("features", {}).get("auto_merge", False)
        
        # CI settings
        self.required_checks = config.get("github", {}).get("ci", {}).get("required_checks", [])
        self.wait_for_checks = config.get("github", {}).get("ci", {}).get("wait_for_checks", True)
    
    def get_repository_info(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        Get information about a GitHub repository.
        
        Args:
            owner: Repository owner (username or organization)
            repo: Repository name
            
        Returns:
            Repository information
        """
        try:
            # Call the github MCP tool
            result = call_tool(
                "github", 
                "get_repository", 
                {
                    "owner": owner,
                    "repo": repo
                }
            )
            
            return {
                "success": True,
                "repository": result,
                "owner": owner,
                "repo": repo
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "owner": owner,
                "repo": repo
            }
    
    def list_branches(self, owner: str, repo: str, pattern: Optional[str] = None) -> Dict[str, Any]:
        """
        List branches in a GitHub repository.
        
        Args:
            owner: Repository owner (username or organization)
            repo: Repository name
            pattern: Optional regex pattern to filter branches
            
        Returns:
            List of branches
        """
        try:
            # Call the github MCP tool
            result = call_tool(
                "github", 
                "list_branches", 
                {
                    "owner": owner,
                    "repo": repo
                }
            )
            
            branches = result.get("branches", [])
            
            # Filter branches by pattern if provided
            if pattern:
                pattern_regex = re.compile(pattern)
                branches = [b for b in branches if pattern_regex.match(b.get("name", ""))]
            
            return {
                "success": True,
                "branches": branches,
                "count": len(branches),
                "owner": owner,
                "repo": repo
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "branches": [],
                "owner": owner,
                "repo": repo
            }
    
    def branch_exists(self, owner: str, repo: str, branch_name: str) -> Dict[str, Any]:
        """
        Check if a branch exists in a GitHub repository.
        
        Args:
            owner: Repository owner (username or organization)
            repo: Repository name
            branch_name: Name of the branch to check
            
        Returns:
            Result with exists flag
        """
        try:
            # Call the github MCP tool
            result = call_tool(
                "github", 
                "get_branch", 
                {
                    "owner": owner,
                    "repo": repo,
                    "branch": branch_name
                }
            )
            
            return {
                "success": True,
                "exists": True,
                "branch": result,
                "branch_name": branch_name,
                "owner": owner,
                "repo": repo
            }
        except Exception as e:
            # Check if the error is a 404 (branch doesn't exist)
            if "Not Found" in str(e):
                return {
                    "success": True,
                    "exists": False,
                    "branch_name": branch_name,
                    "owner": owner,
                    "repo": repo
                }
            
            return {
                "success": False,
                "error": str(e),
                "exists": False,
                "branch_name": branch_name,
                "owner": owner,
                "repo": repo
            }
    
    def create_branch(self, owner: str, repo: str, branch_name: str, base_branch: str) -> Dict[str, Any]:
        """
        Create a new branch in a GitHub repository.
        
        Args:
            owner: Repository owner (username or organization)
            repo: Repository name
            branch_name: Name of the branch to create
            base_branch: Base branch to create from
            
        Returns:
            Result of branch creation
        """
        try:
            # First check if branch already exists
            branch_check = self.branch_exists(owner, repo, branch_name)
            
            if branch_check.get("exists", False):
                return {
                    "success": False,
                    "error": f"Branch '{branch_name}' already exists",
                    "branch_name": branch_name,
                    "owner": owner,
                    "repo": repo
                }
            
            # Call the github MCP tool
            result = call_tool(
                "github", 
                "create_branch", 
                {
                    "owner": owner,
                    "repo": repo,
                    "branch": branch_name,
                    "from_branch": base_branch
                }
            )
            
            return {
                "success": True,
                "message": f"Created branch '{branch_name}' from '{base_branch}'",
                "branch_name": branch_name,
                "base_branch": base_branch,
                "owner": owner,
                "repo": repo
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "branch_name": branch_name,
                "base_branch": base_branch,
                "owner": owner,
                "repo": repo
            }
    
    def delete_branch(self, owner: str, repo: str, branch_name: str) -> Dict[str, Any]:
        """
        Delete a branch in a GitHub repository.
        
        Args:
            owner: Repository owner (username or organization)
            repo: Repository name
            branch_name: Name of the branch to delete
            
        Returns:
            Result of branch deletion
        """
        try:
            # Call the github MCP tool (note: this is a placeholder as the direct delete_branch
            # tool may not exist, but we can use other GitHub API endpoints)
            # This would typically use an endpoint like DELETE /repos/{owner}/{repo}/git/refs/heads/{branch}
            
            # For now, we'll use a more generic approach with the github MCP tool
            # This is pseudocode that would need to be adjusted based on the actual github MCP server capabilities
            result = call_tool(
                "github", 
                "delete_ref", 
                {
                    "owner": owner,
                    "repo": repo,
                    "ref": f"heads/{branch_name}"
                }
            )
            
            return {
                "success": True,
                "message": f"Deleted branch '{branch_name}'",
                "branch_name": branch_name,
                "owner": owner,
                "repo": repo
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "branch_name": branch_name,
                "owner": owner,
                "repo": repo
            }
    
    def list_pull_requests(self, owner: str, repo: str, state: str = "open") -> Dict[str, Any]:
        """
        List pull requests in a GitHub repository.
        
        Args:
            owner: Repository owner (username or organization)
            repo: Repository name
            state: PR state to filter by (open, closed, all)
            
        Returns:
            List of pull requests
        """
        try:
            # Call the github MCP tool
            result = call_tool(
                "github", 
                "list_pull_requests", 
                {
                    "owner": owner,
                    "repo": repo,
                    "state": state
                }
            )
            
            return {
                "success": True,
                "pull_requests": result,
                "count": len(result),
                "state": state,
                "owner": owner,
                "repo": repo
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "pull_requests": [],
                "state": state,
                "owner": owner,
                "repo": repo
            }
    
    def get_pull_request(self, owner: str, repo: str, pr_number: int) -> Dict[str, Any]:
        """
        Get details about a specific pull request.
        
        Args:
            owner: Repository owner (username or organization)
            repo: Repository name
            pr_number: Pull request number
            
        Returns:
            Pull request details
        """
        try:
            # Call the github MCP tool
            result = call_tool(
                "github", 
                "get_pull_request", 
                {
                    "owner": owner,
                    "repo": repo,
                    "pull_number": pr_number
                }
            )
            
            return {
                "success": True,
                "pull_request": result,
                "pr_number": pr_number,
                "owner": owner,
                "repo": repo
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "pr_number": pr_number,
                "owner": owner,
                "repo": repo
            }
    
    def create_pull_request(self, owner: str, repo: str, title: str, body: str, 
                           head: str, base: str, draft: bool = False) -> Dict[str, Any]:
        """
        Create a pull request in a GitHub repository.
        
        Args:
            owner: Repository owner (username or organization)
            repo: Repository name
            title: PR title
            body: PR description
            head: Head branch (source)
            base: Base branch (target)
            draft: Whether to create as a draft PR
            
        Returns:
            Result of PR creation
        """
        if not self.create_pr_enabled:
            return {
                "success": False,
                "error": "PR creation is disabled in configuration",
                "owner": owner,
                "repo": repo
            }
        
        try:
            # Call the github MCP tool
            result = call_tool(
                "github", 
                "create_pull_request", 
                {
                    "owner": owner,
                    "repo": repo,
                    "title": title,
                    "body": body,
                    "head": head,
                    "base": base,
                    "draft": draft
                }
            )
            
            return {
                "success": True,
                "pull_request": result,
                "pr_number": result.get("number"),
                "html_url": result.get("html_url"),
                "message": f"Created PR #{result.get('number')}: {title}",
                "owner": owner,
                "repo": repo
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "title": title,
                "head": head,
                "base": base,
                "owner": owner,
                "repo": repo
            }
    
    def merge_pull_request(self, owner: str, repo: str, pr_number: int, 
                          method: str = "merge") -> Dict[str, Any]:
        """
        Merge a pull request.
        
        Args:
            owner: Repository owner (username or organization)
            repo: Repository name
            pr_number: Pull request number
            method: Merge method (merge, squash, rebase)
            
        Returns:
            Result of PR merge
        """
        if not self.auto_merge_enabled:
            return {
                "success": False,
                "error": "Auto-merge is disabled in configuration",
                "pr_number": pr_number,
                "owner": owner,
                "repo": repo
            }
        
        try:
            # Call the github MCP tool
            result = call_tool(
                "github", 
                "merge_pull_request", 
                {
                    "owner": owner,
                    "repo": repo,
                    "pull_number": pr_number,
                    "merge_method": method
                }
            )
            
            return {
                "success": True,
                "message": f"Merged PR #{pr_number}",
                "merge_commit_sha": result.get("sha"),
                "pr_number": pr_number,
                "owner": owner,
                "repo": repo
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "pr_number": pr_number,
                "owner": owner,
                "repo": repo
            }
    
    def get_file_contents(self, owner: str, repo: str, path: str, 
                         ref: Optional[str] = None) -> Dict[str, Any]:
        """
        Get the contents of a file from a GitHub repository.
        
        Args:
            owner: Repository owner (username or organization)
            repo: Repository name
            path: Path to the file
            ref: Branch, tag, or commit SHA (optional)
            
        Returns:
            File contents
        """
        try:
            params = {
                "owner": owner,
                "repo": repo,
                "path": path
            }
            
            if ref:
                params["ref"] = ref
            
            # Call the github MCP tool
            result = call_tool(
                "github", 
                "get_file_contents", 
                params
            )
            
            return {
                "success": True,
                "content": result.get("content"),
                "sha": result.get("sha"),
                "path": path,
                "owner": owner,
                "repo": repo
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "path": path,
                "owner": owner,
                "repo": repo
            }
    
    def update_file(self, owner: str, repo: str, path: str, message: str, 
                   content: str, branch: str, sha: str) -> Dict[str, Any]:
        """
        Update a file in a GitHub repository.
        
        Args:
            owner: Repository owner (username or organization)
            repo: Repository name
            path: Path to the file
            message: Commit message
            content: New file content
            branch: Branch to update
            sha: SHA of the file being replaced
            
        Returns:
            Result of file update
        """
        try:
            # Call the github MCP tool
            result = call_tool(
                "github", 
                "create_or_update_file", 
                {
                    "owner": owner,
                    "repo": repo,
                    "path": path,
                    "message": message,
                    "content": content,
                    "branch": branch,
                    "sha": sha
                }
            )
            
            return {
                "success": True,
                "message": f"Updated file {path} on {branch}",
                "commit": result.get("commit"),
                "path": path,
                "branch": branch,
                "owner": owner,
                "repo": repo
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "path": path,
                "branch": branch,
                "owner": owner,
                "repo": repo
            }
    
    def get_workflow_status(self, owner: str, repo: str, 
                           branch: Optional[str] = None) -> Dict[str, Any]:
        """
        Get the workflow status for a branch or repository.
        
        Args:
            owner: Repository owner (username or organization)
            repo: Repository name
            branch: Branch name (optional)
            
        Returns:
            Workflow status information
        """
        try:
            # This would typically check CI status, PR status, etc.
            # For now, we'll return some basic information about the branch and PRs
            
            result = {
                "success": True,
                "owner": owner,
                "repo": repo
            }
            
            if branch:
                # Get branch information
                branch_result = call_tool(
                    "github", 
                    "get_branch", 
                    {
                        "owner": owner,
                        "repo": repo,
                        "branch": branch
                    }
                )
                
                result["branch"] = branch_result
                
                # Get PRs for this branch
                prs = call_tool(
                    "github", 
                    "list_pull_requests", 
                    {
                        "owner": owner,
                        "repo": repo,
                        "head": f"{owner}:{branch}"
                    }
                )
                
                result["pull_requests"] = prs
                
                # Get check runs for the branch
                # (This would depend on the actual GitHub MCP server capabilities)
                
            else:
                # Get repository information
                repo_info = self.get_repository_info(owner, repo)
                result["repository"] = repo_info.get("repository", {})
                
                # Get open PRs
                prs = self.list_pull_requests(owner, repo, "open")
                result["open_pull_requests"] = prs.get("pull_requests", [])
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "owner": owner,
                "repo": repo
            }


def get_repository_info(owner: str, repo: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Get information about a GitHub repository.
    
    Args:
        owner: Repository owner (username or organization)
        repo: Repository name
        config: Optional configuration dictionary
        
    Returns:
        Repository information
    """
    if config is None:
        config = {}
        
    adapter = GitHubAdapter(config)
    return adapter.get_repository_info(owner, repo)


def create_branch(owner: str, repo: str, branch_name: str, base_branch: str, 
                 config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Create a new branch in a GitHub repository.
    
    Args:
        owner: Repository owner (username or organization)
        repo: Repository name
        branch_name: Name of the branch to create
        base_branch: Base branch to create from
        config: Optional configuration dictionary
        
    Returns:
        Result of branch creation
    """
    if config is None:
        config = {}
        
    adapter = GitHubAdapter(config)
    return adapter.create_branch(owner, repo, branch_name, base_branch)


def create_pull_request(owner: str, repo: str, title: str, body: str, 
                      head: str, base: str, draft: bool = False,
                      config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Create a pull request in a GitHub repository.
    
    Args:
        owner: Repository owner (username or organization)
        repo: Repository name
        title: PR title
        body: PR description
        head: Head branch (source)
        base: Base branch (target)
        draft: Whether to create as a draft PR
        config: Optional configuration dictionary
        
    Returns:
        Result of PR creation
    """
    if config is None:
        config = {}
        
    adapter = GitHubAdapter(config)
    return adapter.create_pull_request(owner, repo, title, body, head, base, draft)


def get_file_contents(owner: str, repo: str, path: str, 
                     ref: Optional[str] = None,
                     config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Get the contents of a file from a GitHub repository.
    
    Args:
        owner: Repository owner (username or organization)
        repo: Repository name
        path: Path to the file
        ref: Branch, tag, or commit SHA (optional)
        config: Optional configuration dictionary
        
    Returns:
        File contents
    """
    if config is None:
        config = {}
        
    adapter = GitHubAdapter(config)
    return adapter.get_file_contents(owner, repo, path, ref)


def update_file(owner: str, repo: str, path: str, message: str, 
               content: str, branch: str, sha: str,
               config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Update a file in a GitHub repository.
    
    Args:
        owner: Repository owner (username or organization)
        repo: Repository name
        path: Path to the file
        message: Commit message
        content: New file content
        branch: Branch to update
        sha: SHA of the file being replaced
        config: Optional configuration dictionary
        
    Returns:
        Result of file update
    """
    if config is None:
        config = {}
        
    adapter = GitHubAdapter(config)
    return adapter.update_file(owner, repo, path, message, content, branch, sha)
