# MCP Server Practices

A Model Context Protocol server that provides tools for enforcing development practices.

## Overview

This MCP server provides tools to help enforce and automate development practices like:

- Branch name validation
- Version management
- PR preparation
- License header management
- Pre-commit hook installation

## Installation

```bash
pip install mcp-server-practices
```

For development installation:

```bash
pip install -e .
```

## Usage

### As an MCP Server

The server can be invoked through the following method:

```bash
# Run server using the --from parameter
uvx --from mcp-server-practices practices [options]

# Show version
uvx --from mcp-server-practices practices --version
```

> **Note:** Support for direct invocation via `uvx mcp-server-practices` is planned for a future release.

#### Server Options

- `--log-level`: Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `--project-root`: Specify the project root directory
- `--log-file`: Enable logging to a file (default)
- `--no-log-file`: Disable logging to a file
- `--log-file-path`: Specify a custom log file path

### As a CLI Tool

```bash
# Access CLI functionality
uvx --from mcp-server-practices practices cli [command] [options]
```

> **Note:** Support for direct invocation via `uvx mcp-server-practices cli` is planned for a future release.

#### Branch Commands

```bash
# Validate a branch name
uvx --from mcp-server-practices practices cli branch validate feature/ABC-123-description

# Create a branch
uvx --from mcp-server-practices practices cli branch create feature/ABC-123-description
```

#### Jira Commands

```bash
# Get issue details
uvx --from mcp-server-practices practices cli jira issue ABC-123

# Update issue status
uvx --from mcp-server-practices practices cli jira update ABC-123 "In Progress"
```

## MCP Configuration

```json
"practices": {
  "command": "practices",
  "args": [
    "--log-level",
    "ERROR"
  ],
  "disabled": false,
  "autoApprove": [
    "validate_branch_name",
    "get_branch_info",
    "validate_version"
  ]
}
```

## Development

### Testing

```bash
python -m pytest
```

### License Headers

```bash
uvx --from mcp-server-practices practices cli headers add /path/to/your/source/directory
```

## License

[MIT](LICENSE)
