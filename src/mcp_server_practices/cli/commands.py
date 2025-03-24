#!/usr/bin/env python
"""
CLI commands for the Practices MCP Server.
"""

import argparse
import re
import subprocess
import sys
from typing import List, Optional, Dict, Any

from mcp_server_practices import __version__
from mcp_server_practices.branch.creator import create_branch
from mcp_server_practices.branch.validator import validate_branch_name
from mcp_server_practices.integrations.jira import get_issue, update_issue_status


def run_mcp_server(arg_list: List[str]) -> int:
    """
    Run the MCP server, forwarding all arguments.
    
    Args:
        arg_list: Command-line arguments
        
    Returns:
        Exit code
    """
    from mcp_server_practices.mcp_server import main
    return main()


def create_branch_command(arg_list: List[str]) -> int:
    """
    Create a new branch following the configured branching convention.
    
    The following branch types are supported:
    - feature/PMS-123-brief-description (from develop)
    - bugfix/PMS-123-brief-description (from develop)
    - hotfix/1.0.1-brief-description (from main)
    - release/1.1.0 (from develop)
    - docs/update-readme (from develop)
    
    Args:
        arg_list: Command-line arguments
        
    Returns:
        Exit code
    """
    parser = argparse.ArgumentParser(
        description="Create a new branch following the configured branching convention"
    )
    
    # Branch type argument
    parser.add_argument(
        "branch_type",
        choices=["feature", "bugfix", "hotfix", "release", "docs"],
        help="Type of branch to create",
    )
    
    # Issue ID or version argument - required for feature, bugfix, hotfix, release
    parser.add_argument(
        "identifier",
        help="For feature/bugfix: Jira issue ID (e.g., PMS-123). For hotfix/release: version (e.g., 1.0.1). For docs: brief description.",
    )
    
    # Description - required for feature, bugfix, hotfix, docs, optional for release
    parser.add_argument(
        "description",
        nargs="*",
        help="Brief description for the branch (use hyphens for spaces). Optional for release branches.",
    )
    
    # Option to fetch issue details from Jira
    parser.add_argument(
        "--fetch-jira",
        action="store_true",
        help="Fetch issue details from Jira to use in branch name",
    )
    
    # Option to update Jira status
    parser.add_argument(
        "--update-jira",
        action="store_true",
        help="Update Jira issue status to 'In Progress'",
    )
    
    # Load configuration from .practices.yaml (not implemented yet)
    config = {
        "project_key": "PMS",
        "main_branch": "main",
        "develop_branch": "develop",
        "branching_strategy": "gitflow",
        "workflow_mode": "solo",
    }
    
    # Parse arguments
    args = parser.parse_args(arg_list)
    
    # Get issue details from Jira if requested
    issue_description = ""
    if args.fetch_jira and args.branch_type in ["feature", "bugfix"]:
        issue = get_issue(args.identifier, config)
        if issue:
            from mcp_server_practices.integrations.jira import JiraAdapter
            jira_adapter = JiraAdapter(config)
            issue_description = jira_adapter.format_issue_summary(issue)
            print(f"Using description from Jira: {issue_description}")
    
    # Use Jira description or provided description
    description = None
    if issue_description:
        description = [issue_description]
    elif args.description:
        description = args.description
    
    # Create the branch
    result = create_branch(args.branch_type, args.identifier, description, config)
    
    if not result["success"]:
        print(f"Error creating branch: {result.get('error', 'Unknown error')}")
        return 1
    
    print(result["message"])
    
    # Update Jira if requested
    if args.update_jira and args.branch_type in ["feature", "bugfix"]:
        jira_result = update_issue_status(args.identifier, "In Progress", config)
        if jira_result["success"]:
            print(jira_result["message"])
        else:
            print(f"Error updating Jira: {jira_result.get('error', 'Unknown error')}")
    
    # Print reminder about Jira status
    if args.branch_type in ["feature", "bugfix"] and not args.update_jira:
        print(f"\nDon't forget to update the status of {args.identifier} in Jira to 'In Progress'")
    
    return 0


def validate_branch_command(arg_list: List[str]) -> int:
    """
    Validate a branch name against the configured branching convention.
    
    Args:
        arg_list: Command-line arguments
        
    Returns:
        Exit code
    """
    parser = argparse.ArgumentParser(
        description="Validate a branch name against the configured branching convention"
    )
    
    # Branch name argument
    parser.add_argument(
        "branch_name",
        help="Name of the branch to validate",
    )
    
    # Parse arguments
    args = parser.parse_args(arg_list)
    
    # Load configuration from .practices.yaml (not implemented yet)
    config = {
        "project_key": "PMS",
        "main_branch": "main",
        "develop_branch": "develop",
        "branching_strategy": "gitflow",
        "workflow_mode": "solo",
    }
    
    # Validate the branch
    result = validate_branch_name(args.branch_name, config)
    
    if result["valid"]:
        print(f"Branch '{args.branch_name}' is valid.")
        print(f"Type: {result['branch_type']}")
        print(f"Base branch: {result['base_branch']}")
        print(f"Components: {result['components']}")
        return 0
    else:
        print(f"Branch '{args.branch_name}' is invalid: {result['error']}")
        print("Expected patterns:")
        for branch_type, pattern in result["expected_patterns"].items():
            print(f"  {branch_type}: {pattern}")
        return 1


def print_version() -> None:
    """Print version information for the package."""
    print(f"Practices MCP Server version: {__version__}")
    print("A server implementing development practices for Git, GitHub, and Jira")
    print("License: MIT")
    print("\nBranching strategy: GitFlow")
    print("Default project key: PMS")


def practices_main() -> int:
    """
    Entry point for the 'practices' command.
    
    Returns:
        Exit code
    """
    parser = argparse.ArgumentParser(
        description="Practices MCP server CLI"
    )
    parser.add_argument("command", help="Command to run")
    
    # First, handle the case where no arguments are provided
    if len(sys.argv) == 1:
        parser.print_help()
        return 0
    
    args, remaining = parser.parse_known_args()
    
    # Handle different commands
    if args.command == "server":
        return run_mcp_server(remaining)
    elif args.command == "branch":
        if not remaining:
            print("Error: subcommand required")
            print("Available subcommands: create, validate")
            return 1
        
        subcommand = remaining[0]
        if subcommand == "create":
            return create_branch_command(remaining[1:])
        elif subcommand == "validate":
            return validate_branch_command(remaining[1:])
        else:
            print(f"Unknown subcommand: {subcommand}")
            print("Available subcommands: create, validate")
            return 1
    elif args.command == "version":
        print_version()
        return 0
    elif args.command == "help":
        parser.print_help()
        return 0
    else:
        print(f"Unknown command: {args.command}")
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(practices_main())
