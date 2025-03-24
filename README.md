# Practices MCP Server

An MCP server for development practices, branching strategies, versioning, and PR workflows.

## Overview

The Practices MCP Server is designed to extract, standardize, and automate the development best practices currently implemented in the Tribal project. The server provides tools and resources for implementing branching strategies, versioning rules, PR workflows, and integration with services like GitHub and Jira.

### Features

- Branch management (validation, creation, information extraction)
- Version management (consistency checking, version bumping)
- PR workflows (description generation, preparation)
- Integration with GitHub and Jira MCP servers
- Customizable templates for different project types

## Installation

### Prerequisites

- Python 3.9+
- Git

### Using pip

```bash
pip install mcp-server-practices
```

### Development Installation

```bash
git clone git@github.com:agentience/practices_mcp_server.git
cd practices_mcp_server
pip install -e .
```

## Usage

### Command Line Interface

The package provides a `practices` command-line tool:

```bash
# Validate a branch name
practices branch validate feature/PMS-123-add-feature

# Create a new branch
practices branch create feature --ticket PMS-123 --description "Add new feature"

# Validate version consistency
practices version validate

# Bump version
practices version bump minor

# Prepare a PR
practices pr prepare --open-browser
```

### MCP Server

To use as an MCP server, add the following to your MCP settings file:

```json
{
  "mcpServers": {
    "practices": {
      "command": "practices-server",
      "args": [],
      "env": {}
    }
  }
}
```

## Configuration

Create a `.practices.yaml` file in your project root:

```yaml
project_type: python
branching_strategy: gitflow
main_branch: main
develop_branch: develop

version:
  files:
    - path: src/package/__init__.py
      pattern: __version__ = "(\d+\.\d+\.\d+)"
  use_bumpversion: true

branches:
  feature:
    pattern: "feature/([A-Z]+-\d+)-(.+)"
    base: develop
    version_bump: null
  # ... other branch types
```

## Development

### Setup

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## License

MIT
