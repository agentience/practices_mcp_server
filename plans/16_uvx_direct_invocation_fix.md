# uvx Direct Invocation Fix Implementation Plan

## Overview

This document outlines the implementation plan for fixing the direct invocation of the package via the `uvx` command. Currently, the package can only be invoked using `uvx --from mcp-server-practices practices` but not directly with `uvx mcp-server-practices` as intended in the CLI and Server Unification plan.

## Jira Ticket

```
Project: PMS
Type: Bug
Summary: Fix direct execution via uvx command
Description: 
Currently, the package can only be invoked using 'uvx --from mcp-server-practices practices' 
but not directly with 'uvx mcp-server-practices' as intended in the CLI and Server Unification plan.
Fix the package configuration to support direct invocation.

Acceptance Criteria:
1. Package can be invoked directly via 'uvx mcp-server-practices'
2. All existing functionality maintained with backward compatibility
3. MCP configuration works with the direct invocation pattern
4. Documentation updated to demonstrate both invocation methods
```

## Root Cause Analysis

Based on testing, the package has successfully unified the CLI and server functionality as intended, but the direct invocation via `uvx mcp-server-practices` is failing. The error message specifically indicates:

```
The executable `mcp-server-practices` was not found.
warning: An executable named `mcp-server-practices` is not provided by package `mcp-server-practices`.
The following executables are provided by `mcp-server-practices`:
- practices
```

This occurs because while we've created a `practices` entry point in the package, we haven't created an entry point that matches the package name itself, which is what `uvx` looks for by default when invoked without the `--from` parameter.

## Implementation Plan

### Phase 1: Add Package-Named Entry Point

1. Update `pyproject.toml` to add a second entry point that matches the package name:

```toml
[project.scripts]
practices = "mcp_server_practices.cli:main"
mcp-server-practices = "mcp_server_practices.cli:main"  # Add this line
```

This creates a command-line entry point with the same name as the package, allowing direct invocation.

### Phase 2: Handle Hyphenated Package Name

Hyphenated package names require special handling because Python identifiers can't contain hyphens. Make the entry point robust:

1. Create a symbolic module alias in `__init__.py` to handle potential naming issues:

```python
# src/mcp_server_practices/__init__.py
"""MCP Server for Development Practices."""

__version__ = "0.3.0"

# Add alias for hyphenated command name
mcp_server_practices_main = lambda: __import__('mcp_server_practices.cli').cli.main()
```

2. Update the `pyproject.toml` entry point to use this alias:

```toml
[project.scripts]
practices = "mcp_server_practices.cli:main"
mcp-server-practices = "mcp_server_practices:mcp_server_practices_main"
```

### Phase 3: Testing

1. Rebuild and reinstall the package:
```bash
pip install -e .
```

2. Test direct invocation:
```bash
uvx mcp-server-practices --version
```

3. Test server functionality:
```bash
uvx mcp-server-practices
```

4. Test CLI functionality:
```bash
uvx mcp-server-practices cli branch validate feature/PMS-123-test
```

5. Test backwards compatibility:
```bash
uvx --from mcp-server-practices practices --version
```

### Phase 4: Documentation Updates

1. Update README.md to show both invocation patterns:

```markdown
## Usage

### Direct Invocation (Recommended)

```bash
# Show version
uvx mcp-server-practices --version

# Run server (default)
uvx mcp-server-practices

# CLI operations
uvx mcp-server-practices cli branch validate feature/PMS-123-test
```

### Alternative Invocation

```bash
# Using --from parameter
uvx --from mcp-server-practices practices --version
```
```

2. Update MCP configuration example to show the direct invocation pattern:

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

## Version Bump

Since this is a bug fix that doesn't change functionality but improves usability, create a patch version:

```bash
bump2version patch
```

## Implementation Timeline

- Code changes and testing: ~1 hour
- Documentation updates: ~30 minutes
- Version bump and publishing: ~15 minutes

Total estimated time: ~2 hours

## Backward Compatibility Notes

This change is purely additive and maintains full backward compatibility:
- All existing `practices` entry points continue to work
- All existing `uvx --from mcp-server-practices practices` invocations continue to work
- New direct `uvx mcp-server-practices` invocations will now work as originally intended
