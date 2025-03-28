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
    Run the MCP server forwarding all arguments.

    Args:
        arg_list: Command-line arguments

    Returns:
        Exit code
    """
    from mcp_server_practices.mcp_server import main as server_main
    return server_main()


def main() -> int:
    """
    Main entry point for the practices CLI.

    Returns:
        Exit code
    """
    parser = argparse.ArgumentParser(description="MCP Server Practices CLI")
    parser.add_argument("--version", action="store_true", help="Show version and exit")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Server command
    server_parser = subparsers.add_parser("server", help="Run the MCP server")
    
    # Branch commands
    branch_parser = subparsers.add_parser("branch", help="Branch management commands")
    branch_subparsers = branch_parser.add_subparsers(dest="branch_command", help="Branch command to run")
    
    create_parser = branch_subparsers.add_parser("create", help="Create a new branch")
    create_parser.add_argument("name", help="Name of the branch")
    
    validate_parser = branch_subparsers.add_parser("validate", help="Validate branch name")
    validate_parser.add_argument("name", help="Name of the branch to validate")
    
    # Jira commands
    jira_parser = subparsers.add_parser("jira", help="Jira integration commands")
    jira_subparsers = jira_parser.add_subparsers(dest="jira_command", help="Jira command to run")
    
    issue_parser = jira_subparsers.add_parser("issue", help="Get issue details")
    issue_parser.add_argument("key", help="Jira issue key")
    
    update_parser = jira_subparsers.add_parser("update", help="Update issue status")
    update_parser.add_argument("key", help="Jira issue key")
    update_parser.add_argument("status", help="New status")

    args = parser.parse_args()

    if args.version:
        print(f"mcp-server-practices version {__version__}")
        return 0

    if args.command == "server":
        return run_mcp_server(sys.argv[2:])
    elif args.command == "branch":
        if args.branch_command == "create":
            create_branch(args.name)
            return 0
        elif args.branch_command == "validate":
            is_valid = validate_branch_name(args.name)
            if is_valid:
                print(f"Branch name '{args.name}' is valid")
                return 0
            else:
                print(f"Branch name '{args.name}' is invalid")
                return 1
    elif args.command == "jira":
        if args.jira_command == "issue":
            issue = get_issue(args.key)
            if issue:
                print(f"Issue {args.key}: {issue.get('summary', 'No summary')}")
                print(f"Status: {issue.get('status', 'Unknown')}")
                print(f"Description: {issue.get('description', 'No description')}")
                return 0
            else:
                print(f"Issue {args.key} not found")
                return 1
        elif args.jira_command == "update":
            success = update_issue_status(args.key, args.status)
            if success:
                print(f"Updated issue {args.key} to status {args.status}")
                return 0
            else:
                print(f"Failed to update issue {args.key}")
                return 1

    # No command or unknown command
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
