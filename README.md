# MCP Server Practices

An MCP server that provides tools and resources for development practices.

## Features

### Versioning

The Practices MCP server follows [Semantic Versioning 2.0.0](https://semver.org/) with a clear process for version management:

- **MAJOR.MINOR.PATCH**: Version format (e.g., 0.2.0)
  - **MAJOR**: Incremented for incompatible API changes
  - **MINOR**: Incremented for new functionality
  - **PATCH**: Incremented for bug fixes

#### Versioning Process

When working with the Practices MCP server, follow these steps to maintain proper versioning:

1. **Feature Development**:
   - Create feature branches (never include version changes)
   - Complete feature implementation and tests
   - Merge feature branches to develop

2. **Version Updates**:
   - After completing significant features, create a release branch:
     ```bash
     git checkout develop
     git pull origin develop
     git checkout -b release/x.y.0
     ```
   - Bump the version using bump2version:
     ```bash
     # For new features (most common)
     bump2version minor
     
     # For bug fixes only
     bump2version patch
     
     # For breaking changes
     bump2version major
     ```
   - Update the CHANGELOG.md with new features and changes

3. **Merging Release Branches**:
   - After testing, merge the release branch to both develop and main
   - Delete the release branch after merging

#### Via MCP Tools

The server provides the following versioning MCP tools:

1. `validate_version`: Checks version consistency across project files
2. `bump_version`: Bumps version according to semantic versioning rules

Example:
```python
from mcp.tools import call_tool

# Validate version consistency
result = call_tool(
    "practices", 
    "validate_version",
    {}
)

# Bump version
result = call_tool(
    "practices", 
    "bump_version", 
    {"type": "minor"}
)
```

#### Via CLI

Version management is also available through the CLI:

```bash
# Check version consistency
practices version check

# Bump version (minor)
practices version bump minor

# Bump version (patch)
practices version bump patch
```

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

### Installing from Source (Development)

1. Clone the repository:
   ```bash
   git clone https://github.com/Agentience/mcp_server_practices.git
   cd mcp_server_practices
   ```
2. Create a virtual environment with `uv`:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install the package in development mode:
   ```bash
   uv pip install -e .
   ```
4. Install dependencies from the lock file:
   ```bash
   uv pip sync uv.lock
   ```

### Installing as a UV Tool

The recommended way to install the practices MCP server is as a UV tool, which makes it globally available without needing to activate a virtual environment:

#### From the local repository (for development)

```bash
# Navigate to the project directory
cd mcp_server_practices

# Install the current directory as a UV tool
uv tool install .
```

#### From PyPI (for users)

```bash
# Install as a UV tool from PyPI
uv tool install mcp_server_practices
```

Either approach will make the `practices` command available system-wide through UV's tool management system. You can verify the installation with:

```bash
# List installed UV tools
uv tool list
```

### Installing as a Standard Package (Alternative)

Alternatively, you can install it as a regular package:

```bash
# Create a virtual environment (optional but recommended)
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the package
uv pip install mcp_server_practices
```

Note: This project uses the `mcp` package with the CLI extras enabled.

## Running the Server

```bash
# Activate the virtual environment (if you created one)
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Run the MCP server
practices server
```

## Using with Claude

To use the Practices MCP server with Claude, add the appropriate configuration to your `cline_mcp_settings.json` file:

### Direct Python Module Approach (Recommended for Development)

This approach runs the module directly from the source code and doesn't require package installation:

```json
{
  "mcpServers": {
    "practices": {
      "command": "python",
      "args": [
        "-m",
        "src.mcp_server_practices.mcp_server"
      ],
      "disabled": false,
      "autoApprove": [
        "*"
      ],
      "cwd": "/path/to/mcp_server_practices",
      "env": {
        "PYTHONPATH": "/path/to/mcp_server_practices"
      }
    }
  }
}
```

### UV Tool Installation (If Available)

For systems where the `mcp-python-sdk` dependency is available:

```json
{
  "mcpServers": {
    "practices": {
      "command": "uvx",
      "args": [
        "mcp_server_practices"
      ],
      "disabled": false,
      "autoApprove": [
        "*"
      ]
    }
  }
}
```

### Standard Package Installation

For systems where the package is installed in the environment:

```json
{
  "mcpServers": {
    "practices": {
      "command": "practices",
      "args": [
        "server"
      ],
      "disabled": false,
      "autoApprove": [
        "*"
      ]
    }
  }
}
```

This configuration file is typically located at:
- MacOS: `~/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`
- Windows: `%APPDATA%\Code\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json`
- Linux: `~/.config/Code/User/globalStorage/saoudrizwan.claude-dev\settings\cline_mcp_settings.json`

**Note:** The direct Python module approach is most reliable during development. Make sure to update the `cwd` and `PYTHONPATH` paths to point to your project directory.

## Development

1. Create a virtual environment and install the package as described above
2. Install development dependencies:
   ```bash
   uv pip install -e ".[dev]"
   ```
3. Generate or update the lock file if dependencies change:
   ```bash
   uv pip compile pyproject.toml -o uv.lock
   ```
3. Run tests:
   ```bash
   # With the virtual environment activated
   PYTHONPATH=./src python -m unittest discover tests
   ```

## License

MIT
