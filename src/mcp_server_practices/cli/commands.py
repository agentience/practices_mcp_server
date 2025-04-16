#!/usr/bin/env python

"""
CLI commands for the Practices MCP Server.
By default, runs the MCP server unless 'cli' subcommand is specified.
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


def main() -> int:
    """
    Main entry point for the practices CLI.
    By default, runs the MCP server unless 'cli' subcommand is specified.
    
    Returns:
        Exit code
    """
    parser = argparse.ArgumentParser(description="Practices MCP Server")
    parser.add_argument("--version", action="store_true", help="Show version and exit")
    
    # Add server-specific arguments to the main parser
    parser.add_argument(
        '--log-level', 
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='ERROR',
        help='Set the logging level (default: ERROR)'
    )
    parser.add_argument(
        '--project-root',
        help='Specify the project root directory'
    )
    parser.add_argument(
        '--log-file',
        action='store_true',
        default=True,
        help='Enable logging to a file (default: enabled)'
    )
    parser.add_argument(
        '--no-log-file',
        action='store_false',
        dest='log_file',
        help='Disable logging to a file'
    )
    parser.add_argument(
        '--log-file-path',
        help='Specify a custom log file path'
    )
    
    # Create CLI subparser for command-line operations
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # CLI command for all non-server operations
    cli_parser = subparsers.add_parser("cli", help="Command-line interface operations")
    cli_subparsers = cli_parser.add_subparsers(dest="cli_command", help="CLI command to run")
    
    # Branch commands - under the cli subcommand
    branch_parser = cli_subparsers.add_parser("branch", help="Branch management commands")
    branch_subparsers = branch_parser.add_subparsers(dest="branch_command", help="Branch command to run")
    
    create_parser = branch_subparsers.add_parser("create", help="Create a new branch")
    create_parser.add_argument("name", help="Name of the branch")
    
    validate_parser = branch_subparsers.add_parser("validate", help="Validate branch name")
    validate_parser.add_argument("name", help="Name of the branch to validate")
    
    # Jira commands - under the cli subcommand
    jira_parser = cli_subparsers.add_parser("jira", help="Jira integration commands")
    jira_subparsers = jira_parser.add_subparsers(dest="jira_command", help="Jira command to run")
    
    issue_parser = jira_subparsers.add_parser("issue", help="Get issue details")
    issue_parser.add_argument("key", help="Jira issue key")
    
    update_parser = jira_subparsers.add_parser("update", help="Update issue status")
    update_parser.add_argument("key", help="Jira issue key")
    update_parser.add_argument("status", help="New status")

    # Parse known args to handle --version and determine if CLI mode is requested
    args, unknown_args = parser.parse_known_args()

    if args.version:
        print(f"mcp-server-practices version {__version__}")
        return 0

    # Check if running in CLI mode
    if args.command == "cli":
        # Re-parse with the full parser to validate CLI args
        args = parser.parse_args()
        
        # Handle CLI commands
        if args.cli_command == "branch":
            if args.branch_command == "create":
                # Extract branch type, ID, and description from name
                parts = args.name.split('/')
                if len(parts) == 2 and '-' in parts[1]:
                    branch_type = parts[0]
                    id_desc_parts = parts[1].split('-', 1)
                    identifier = id_desc_parts[0]
                    description = id_desc_parts[1] if len(id_desc_parts) > 1 else None
                    result = create_branch(branch_type, identifier, description)
                    if result.get("success", False):
                        print(f"Branch '{args.name}' created successfully")
                        return 0
                    else:
                        print(f"Error creating branch: {result.get('error', 'Unknown error')}")
                        return 1
                else:
                    print(f"Invalid branch name format. Expected: <type>/<id>-<description>")
                    return 1
            elif args.branch_command == "validate":
                is_valid = validate_branch_name(args.name)
                if is_valid:
                    print(f"Branch name '{args.name}' is valid")
                    return 0
                else:
                    print(f"Branch name '{args.name}' is invalid")
                    return 1
        elif args.cli_command == "jira":
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
                    
        # No valid CLI command specified
        cli_parser.print_help()
        return 1
    
    # Default: Run the MCP server
    from mcp_server_practices.mcp_server import main as server_main
    
    # Transfer arguments to the server
    old_argv = sys.argv
    try:
        sys.argv = [sys.argv[0]] + unknown_args
        return server_main()
    finally:
        sys.argv = old_argv


if __name__ == "__main__":
    sys.exit(main())
