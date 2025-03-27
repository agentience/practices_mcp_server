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


def install_hooks_command(arg_list: List[str]) -> int:
    """
    Install pre-commit hooks in a Git repository.
    
    Args:
        arg_list: Command-line arguments
        
    Returns:
        Exit code
    """
    parser = argparse.ArgumentParser(
        description="Install pre-commit hooks in a Git repository"
    )
    
    # Repository path argument
    parser.add_argument(
        "--path",
        default=".",
        help="Path to the Git repository (default: current directory)",
    )
    
    # Project type
    parser.add_argument(
        "--project-type",
        choices=["python", "javascript", "typescript"],
        help="Type of project for specialized hooks",
    )
    
    # Parse arguments
    args = parser.parse_args(arg_list)
    
    # Load configuration from .practices.yaml (not implemented yet)
    config = {
        "project_type": args.project_type or "",
    }
    
    # Install hooks
    from mcp_server_practices.hooks.installer import install_hooks
    result = install_hooks(args.path, config)
    
    if result["success"]:
        print(result["message"])
        if "output" in result:
            print(result["output"])
        return 0
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
        return 1


def update_hooks_command(arg_list: List[str]) -> int:
    """
    Update pre-commit hooks in a Git repository.
    
    Args:
        arg_list: Command-line arguments
        
    Returns:
        Exit code
    """
    parser = argparse.ArgumentParser(
        description="Update pre-commit hooks in a Git repository"
    )
    
    # Repository path argument
    parser.add_argument(
        "--path",
        default=".",
        help="Path to the Git repository (default: current directory)",
    )
    
    # Parse arguments
    args = parser.parse_args(arg_list)
    
    # Update hooks
    from mcp_server_practices.hooks.installer import update_hooks
    result = update_hooks(args.path)
    
    if result["success"]:
        print(result["message"])
        if "output" in result:
            print(result["output"])
        return 0
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
        return 1


def add_header_command(arg_list: List[str]) -> int:
    """
    Add a license header to a file.
    
    Args:
        arg_list: Command-line arguments
        
    Returns:
        Exit code
    """
    parser = argparse.ArgumentParser(
        description="Add a license header to a file"
    )
    
    # File path argument
    parser.add_argument(
        "filename",
        help="Path to the file",
    )
    
    # Description
    parser.add_argument(
        "--description",
        default="",
        help="Description of the file's purpose",
    )
    
    # Parse arguments
    args = parser.parse_args(arg_list)
    
    # Add header
    from mcp_server_practices.headers.manager import add_license_header
    result = add_license_header(args.filename, args.description)
    
    if result["success"]:
        print(result["message"])
        return 0
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
        return 1


def verify_header_command(arg_list: List[str]) -> int:
    """
    Check if a file has a proper license header.
    
    Args:
        arg_list: Command-line arguments
        
    Returns:
        Exit code
    """
    parser = argparse.ArgumentParser(
        description="Check if a file has a proper license header"
    )
    
    # File path argument
    parser.add_argument(
        "filename",
        help="Path to the file",
    )
    
    # Parse arguments
    args = parser.parse_args(arg_list)
    
    # Verify header
    from mcp_server_practices.headers.manager import verify_license_header
    result = verify_license_header(args.filename)
    
    print(result["message"])
    return 0 if result.get("has_header", False) else 1


def batch_headers_command(arg_list: List[str]) -> int:
    """
    Process multiple files to add or check license headers.
    
    Args:
        arg_list: Command-line arguments
        
    Returns:
        Exit code
    """
    parser = argparse.ArgumentParser(
        description="Process multiple files to add or check license headers"
    )
    
    # Directory path argument
    parser.add_argument(
        "directory",
        help="Path to the directory",
    )
    
    # File pattern
    parser.add_argument(
        "--pattern",
        default="*.py",
        help="File pattern to match (default: *.py)",
    )
    
    # Check only
    parser.add_argument(
        "--check",
        action="store_true",
        help="Only check for headers without adding them",
    )
    
    # Description
    parser.add_argument(
        "--description",
        default="",
        help="Description to use for headers",
    )
    
    # Recursive
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Process subdirectories recursively",
    )
    
    # Parse arguments
    args = parser.parse_args(arg_list)
    
    # Process files
    from mcp_server_practices.headers.manager import process_files_batch
    result = process_files_batch(
        args.directory,
        args.pattern,
        args.check,
        args.description,
        args.recursive
    )
    
    if result["success"]:
        action = "Checked" if args.check else "Processed"
        print(f"{action} {result['total_files']} files.")
        print(f"Missing headers: {result['missing_headers']}")
        
        if not args.check:
            print(f"Modified files: {result['modified_files']}")
            
        print(f"Errors: {result['errors']}")
        
        # Return non-zero if any files are missing headers
        return 1 if args.check and result["missing_headers"] > 0 else 0
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
        return 1


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


def version_validate_command(arg_list: List[str]) -> int:
    """
    Validate version consistency across files.
    
    Args:
        arg_list: Command-line arguments
        
    Returns:
        Exit code
    """
    parser = argparse.ArgumentParser(
        description="Validate version consistency across files"
    )
    
    # Parse arguments
    args = parser.parse_args(arg_list)
    
    # Load configuration from .practices.yaml (not implemented yet)
    config = {}
    
    # Import the version validator
    from mcp_server_practices.version.validator import validate_version
    result = validate_version(config)
    
    if result["valid"]:
        print(f"Version consistency validated. Current version: {result['version']}")
        return 0
    else:
        print(f"Version validation failed: {result.get('error', 'Unknown error')}")
        print("\nFile details:")
        for file_result in result.get("file_results", []):
            if file_result.get("valid", False):
                print(f"✅ {file_result['path']}: {file_result.get('version', 'unknown')}")
            else:
                print(f"❌ {file_result['path']}: {file_result.get('error', 'Unknown error')}")
        return 1


def version_get_command(arg_list: List[str]) -> int:
    """
    Get the current version of the project.
    
    Args:
        arg_list: Command-line arguments
        
    Returns:
        Exit code
    """
    parser = argparse.ArgumentParser(
        description="Get the current version of the project"
    )
    
    # Parse arguments
    args = parser.parse_args(arg_list)
    
    # Load configuration from .practices.yaml (not implemented yet)
    config = {}
    
    # Import the version getter
    from mcp_server_practices.version.validator import get_current_version
    version = get_current_version(config)
    
    if version:
        print(f"Current version: {version}")
        return 0
    else:
        print("Could not determine current version")
        return 1


def version_bump_command(arg_list: List[str]) -> int:
    """
    Bump the version according to semantic versioning.
    
    Args:
        arg_list: Command-line arguments
        
    Returns:
        Exit code
    """
    parser = argparse.ArgumentParser(
        description="Bump the version according to semantic versioning"
    )
    
    # Part argument
    parser.add_argument(
        "part",
        choices=["major", "minor", "patch", "prerelease"],
        help="Part of the version to bump",
    )
    
    # Option to use bump2version
    parser.add_argument(
        "--use-bumpversion",
        action="store_true",
        help="Use bump2version tool instead of manual file updates",
    )
    
    # Parse arguments
    args = parser.parse_args(arg_list)
    
    # Load configuration from .practices.yaml (not implemented yet)
    config = {
        "version": {
            "use_bumpversion": args.use_bumpversion
        }
    }
    
    # Import the version bumper
    from mcp_server_practices.version.bumper import bump_version
    result = bump_version(args.part, config)
    
    if result["success"]:
        print(result["message"])
        
        # Print updated files if available
        if "updated_files" in result:
            print("\nUpdated files:")
            for file in result["updated_files"]:
                if file["success"]:
                    print(f"✅ {file['path']}")
                else:
                    print(f"❌ {file['path']}: {file.get('error', 'Failed')}")
        
        return 0
    else:
        print(f"Error bumping version: {result.get('error', 'Unknown error')}")
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
    elif args.command == "hooks":
        if not remaining:
            print("Error: subcommand required")
            print("Available subcommands: install, update")
            return 1
        
        subcommand = remaining[0]
        if subcommand == "install":
            return install_hooks_command(remaining[1:])
        elif subcommand == "update":
            return update_hooks_command(remaining[1:])
        else:
            print(f"Unknown subcommand: {subcommand}")
            print("Available subcommands: install, update")
            return 1
    elif args.command == "header":
        if not remaining:
            print("Error: subcommand required")
            print("Available subcommands: add, verify, batch")
            return 1
        
        subcommand = remaining[0]
        if subcommand == "add":
            return add_header_command(remaining[1:])
        elif subcommand == "verify":
            return verify_header_command(remaining[1:])
        elif subcommand == "batch":
            return batch_headers_command(remaining[1:])
        else:
            print(f"Unknown subcommand: {subcommand}")
            print("Available subcommands: add, verify, batch")
            return 1
    elif args.command == "version":
        if not remaining:
            print_version()
            return 0
        
        subcommand = remaining[0]
        if subcommand == "validate":
            return version_validate_command(remaining[1:])
        elif subcommand == "get":
            return version_get_command(remaining[1:])
        elif subcommand == "bump":
            return version_bump_command(remaining[1:])
        elif subcommand == "info":
            print_version()
            return 0
        else:
            print(f"Unknown subcommand: {subcommand}")
            print("Available subcommands: validate, get, bump, info")
            return 1
    elif args.command == "help":
        parser.print_help()
        print("\nAvailable commands:")
        print("  server           - Run the MCP server")
        print("  branch           - Branch management commands")
        print("  hooks            - Pre-commit hooks management")
        print("  header           - License header management")
        print("  version          - Version management commands")
        print("  help             - Show this help message")
        return 0
    else:
        print(f"Unknown command: {args.command}")
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(practices_main())
