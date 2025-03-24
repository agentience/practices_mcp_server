"""Command-line interface for the practices server."""

import argparse
import sys
from typing import List, Optional

from mcp_server_practices import __version__


def create_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Development practices CLI",
        prog="practices",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    subparsers = parser.add_subparsers(dest="entity", help="Entity to operate on")

    # Branch commands
    branch_parser = subparsers.add_parser("branch", help="Branch operations")
    branch_subparsers = branch_parser.add_subparsers(dest="action", help="Action to perform")

    validate_branch_parser = branch_subparsers.add_parser(
        "validate", help="Validate a branch name"
    )
    validate_branch_parser.add_argument(
        "branch_name", help="Name of the branch to validate"
    )

    create_branch_parser = branch_subparsers.add_parser(
        "create", help="Create a new branch"
    )
    create_branch_parser.add_argument(
        "branch_type", choices=["feature", "bugfix", "release", "hotfix", "docs"],
        help="Type of branch to create"
    )
    create_branch_parser.add_argument(
        "--ticket", "-t", help="Ticket ID (e.g., PMS-123)"
    )
    create_branch_parser.add_argument(
        "--description", "-d", help="Short description for the branch"
    )

    merge_branch_parser = branch_subparsers.add_parser(
        "merge", help="Merge a branch to its base branch"
    )
    merge_branch_parser.add_argument(
        "branch_name", nargs="?", help="Name of the branch to merge (defaults to current branch)"
    )
    merge_branch_parser.add_argument(
        "--no-delete", action="store_true", help="Don't delete the branch after merging"
    )
    merge_branch_parser.add_argument(
        "--mode", choices=["solo", "team"], help="Workflow mode (defaults to configuration)"
    )

    cleanup_branch_parser = branch_subparsers.add_parser(
        "cleanup", help="Delete a branch locally and remotely"
    )
    cleanup_branch_parser.add_argument(
        "branch_name", help="Name of the branch to delete"
    )
    cleanup_branch_parser.add_argument(
        "--force", "-f", action="store_true", help="Force deletion even if unmerged"
    )

    # Version commands
    version_parser = subparsers.add_parser("version", help="Version operations")
    version_subparsers = version_parser.add_subparsers(dest="action", help="Action to perform")

    validate_version_parser = version_subparsers.add_parser(
        "validate", help="Validate version consistency"
    )

    bump_version_parser = version_subparsers.add_parser(
        "bump", help="Bump version numbers"
    )
    bump_version_parser.add_argument(
        "part", choices=["major", "minor", "patch"],
        help="Version part to bump"
    )

    # PR commands
    pr_parser = subparsers.add_parser("pr", help="PR operations")
    pr_subparsers = pr_parser.add_subparsers(dest="action", help="Action to perform")

    pr_prepare_parser = pr_subparsers.add_parser(
        "prepare", help="Prepare a PR"
    )
    pr_prepare_parser.add_argument(
        "--branch", "-b", help="Branch name (defaults to current branch)"
    )
    pr_prepare_parser.add_argument(
        "--open-browser", "-o", action="store_true", help="Open browser with PR"
    )

    return parser


def main(args: Optional[List[str]] = None) -> int:
    """Run the CLI with the given arguments."""
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    if not parsed_args.entity:
        parser.print_help()
        return 0

    if parsed_args.entity == "branch":
        if not parsed_args.action:
            parser.parse_args([parsed_args.entity, "--help"])
            return 0

        if parsed_args.action == "validate":
            print(f"Validating branch name: {parsed_args.branch_name}")
            # TODO: Implement branch validation
            return 0

        elif parsed_args.action == "create":
            ticket = parsed_args.ticket or ""
            description = parsed_args.description or ""
            print(f"Creating {parsed_args.branch_type} branch for {ticket}: {description}")
            # TODO: Implement branch creation
            return 0

        elif parsed_args.action == "merge":
            branch_name = parsed_args.branch_name or "current branch"
            delete_after = not parsed_args.no_delete
            mode = parsed_args.mode or "from config"
            print(f"Merging branch {branch_name} (mode: {mode})")
            if delete_after:
                print(f"Will delete branch {branch_name} after successful merge")
            # TODO: Implement branch merging
            return 0

        elif parsed_args.action == "cleanup":
            force = parsed_args.force
            print(f"Cleaning up branch {parsed_args.branch_name}" + (" (forced)" if force else ""))
            # TODO: Implement branch cleanup
            return 0

    elif parsed_args.entity == "version":
        if not parsed_args.action:
            parser.parse_args([parsed_args.entity, "--help"])
            return 0

        if parsed_args.action == "validate":
            print("Validating version consistency")
            # TODO: Implement version validation
            return 0

        elif parsed_args.action == "bump":
            print(f"Bumping {parsed_args.part} version")
            # TODO: Implement version bumping
            return 0

    elif parsed_args.entity == "pr":
        if not parsed_args.action:
            parser.parse_args([parsed_args.entity, "--help"])
            return 0

        if parsed_args.action == "prepare":
            branch = parsed_args.branch or "current branch"
            print(f"Preparing PR for {branch}")
            if parsed_args.open_browser:
                print("Will open browser with PR")
            # TODO: Implement PR preparation
            return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
