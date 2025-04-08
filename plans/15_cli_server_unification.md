# CLI and Server Unification Implementation Plan

## Overview

This document outlines the implementation plan for unifying the `practices` CLI and `practices-server` commands into a single `practices` command with default server mode behavior, following the "No Installation Required" pattern used by other MCP servers.

## Jira Ticket

```
Project: PMS
Type: Task
Summary: Unify practices CLI and server into single command
Description: 
Consolidate the 'practices' and 'practices-server' commands into a single 'practices' 
command with server as the default mode. Enable direct execution via 'uvx' without 
requiring installation.

Acceptance Criteria:
1. Single 'practices' command that runs the MCP server by default
2. CLI functionality accessible via 'practices cli' subcommand
3. Tool can be run via 'uvx mcp-server-practices' without pre-installation
4. MCP configuration updated to reflect the new structure
5. All existing functionality maintained with backward compatibility
6. All tests pass for the modified functionality
```

## Implementation Details

### 1. Branch Creation

```
branch_type: feature
ticket_id: PMS-27
description: unify-cli-server-command
```

This will create: `feature/PMS-27-unify-cli-server-command`

### 2. Package Entry Points Modification

Update `pyproject.toml` to have a single entry point:

```toml
[project.scripts]
practices = "mcp_server_practices.cli:main"
# Remove the practices-server entry point
```

### 3. CLI Command Structure Overhaul

Modify `src/mcp_server_practices/cli/commands.py` to make server mode the default:

```python
def main() -> int:
    """
    Main entry point for the practices CLI.
    By default, runs the MCP server unless 'cli' subcommand is specified.
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
```

### 4. Unit Tests Update

Create/update unit tests in `tests/unit/test_cli_commands.py` to test:

1. Default server behavior
2. CLI subcommand functionality
3. Argument passing between CLI and server

### 5. MCP Configuration

The MCP configuration will be simplified to:

```json
"practices": {
  "command": "uvx",
  "args": [
    "mcp-server-practices",
    "--log-level",
    "ERROR"
  ],
  "disabled": false,
  "autoApprove": [
    "create_branch",
    "set_working_directory"
  ]
}
```

This enables:
- No installation required (runs directly via `uvx`)
- Server mode by default
- Proper logging level configuration
- Auto-approval for necessary tools

### 6. Documentation Updates

#### README.md Updates

Update the README.md to reflect the new unified command structure:

```markdown
## Usage

### MCP Server Configuration

Add the following to your MCP settings:

```json
"practices": {
  "command": "uvx",
  "args": [
    "mcp-server-practices",
    "--log-level",
    "ERROR"
  ],
  "disabled": false,
  "autoApprove": [
    "create_branch",
    "set_working_directory"
  ]
}
```

### CLI Usage

For command-line operations:

```bash
# Show version
uvx mcp-server-practices --version

# Branch operations
uvx mcp-server-practices cli branch create feature/PMS-123-new-feature
uvx mcp-server-practices cli branch validate feature/PMS-123-new-feature

# Jira operations
uvx mcp-server-practices cli jira issue PMS-123
uvx mcp-server-practices cli jira update PMS-123 "In Progress"
```

### Server Options

When running the server (default mode):

```bash
# Run with custom log level
uvx mcp-server-practices --log-level DEBUG

# Run with custom project root
uvx mcp-server-practices --project-root /path/to/project

# Disable file logging
uvx mcp-server-practices --no-log-file
```
```

## Implementation Steps

### Phase 1: Code Modifications

1. Update `pyproject.toml` to consolidate entry points
2. Modify `cli/commands.py` to make server the default mode
3. Create/update unit tests for the new structure

### Phase 2: Testing

1. Test running the server directly: `practices`
2. Test CLI functionality: `practices cli branch create test-branch`
3. Test argument passing between CLI and server
4. Verify `uvx mcp-server-practices` works without installation
5. Test the MCP configuration using `uvx`

### Phase 3: Documentation

1. Update README.md with new command structure
2. Update any usage examples in documentation
3. Document MCP configuration options

## Verification & Release

1. Verify all tests pass
2. Ensure backward compatibility is maintained
3. Update the version number following semantic versioning
4. Publish to PyPI for public availability

## New Usage Patterns

### Default (Server) Mode

```bash
# Run with defaults
uvx mcp-server-practices

# Run with custom log level
uvx mcp-server-practices --log-level DEBUG

# Run with custom project root
uvx mcp-server-practices --project-root /path/to/project
```

### CLI Mode

```bash
# Branch management
uvx mcp-server-practices cli branch create feature/PMS-123-new-feature
uvx mcp-server-practices cli branch validate feature/PMS-123-new-feature

# Jira integration
uvx mcp-server-practices cli jira issue PMS-123
uvx mcp-server-practices cli jira update PMS-123 "In Progress"
```

## Benefits

1. **Simplified User Experience**: Single command with logical default behavior
2. **No Installation Required**: Direct execution via `uvx`
3. **Streamlined MCP Configuration**: Simpler configuration without server subcommand
4. **Better Alignment**: Follows patterns used by other MCP servers
5. **Backward Compatibility**: All previous functionality maintained with new structure
