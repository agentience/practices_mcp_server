# MCP Server Practices

An MCP server that provides tools and resources for development practices.

## Features

### Branch Management

The Practices MCP server provides tools for managing Git branches according to a standardized convention:

- **feature/PMS-123-brief-description**: Feature branches for new features (from develop)
- **bugfix/PMS-123-brief-description**: Bug fix branches (from develop)
- **hotfix/1.0.1-brief-description**: Hot fix branches for urgent fixes (from main)
- **release/1.1.0**: Release branches for preparing releases (from develop)
- **docs/update-readme**: Documentation branches (from develop)

#### Via MCP Tools

The server provides the following MCP tools:

1. `validate_branch_name`: Validates a branch name against the configured convention
2. `create_branch`: Creates a new branch following the convention
3. `get_branch_info`: Gets information about a branch

Example:
```python
from mcp.tools import call_tool

# Validate a branch name
result = call_tool(
    "practices", 
    "validate_branch_name", 
    {"branch_name": "feature/PMS-123-add-authentication"}
)

# Create a branch
result = call_tool(
    "practices", 
    "create_branch", 
    {
        "branch_type": "feature",
        "identifier": "PMS-123",
        "description": "add-authentication",
        "update_jira": True
    }
)

# Get branch info
result = call_tool(
    "practices", 
    "get_branch_info", 
    {"branch_name": "feature/PMS-123-add-authentication"}
)
```

#### Via CLI

The package also provides a command-line interface:

```bash
# Validate a branch name
practices branch validate feature/PMS-123-add-authentication

# Create a branch
practices branch create feature PMS-123 add authentication

# Create a branch and update Jira status
practices branch create feature PMS-123 add authentication --update-jira

# Create a branch using Jira summary as description
practices branch create feature PMS-123 --fetch-jira
```

### Integration with Jira

The server integrates with Jira to:

1. Fetch issue summaries for use in branch names
2. Update issue status when creating branches

## Installation

1. Clone the repository
2. Install with pip: `pip install -e .`

## Running the Server

```bash
# Run the MCP server
practices server
```

## Development

1. Install development dependencies: `pip install -e ".[dev]"`
2. Run tests: `python -m unittest discover tests`

## License

MIT
