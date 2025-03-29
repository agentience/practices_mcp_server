# Practices MCP Server - User Guide

This guide provides instructions for using the Practices MCP Server with AI assistants like Claude.

## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Configuring Claude](#configuring-claude)
- [Natural Language Interaction](#natural-language-interaction)
- [Common Use Cases](#common-use-cases)
- [Configuration](#configuration)
- [CLI Reference](#cli-reference)
- [Troubleshooting](#troubleshooting)

## Introduction

The Practices MCP Server enables AI assistants like Claude to help you implement consistent development practices across your projects. Through natural language conversations, Claude can assist with branch management, version control, pull request workflows, and integration with tools like GitHub and Jira.

## Installation

### Using UV (Recommended)

The recommended way to install the Practices MCP Server is using UV:

```bash
# Install as a UV tool
uv tool install mcp_server_practices
```

This makes the `practices` command available system-wide without activating a virtual environment.

### Using PIP

You can also install using pip:

```bash
# Install with pip
pip install mcp_server_practices
```

### Verifying Installation

To verify the installation:

```bash
# Check if the command is available
practices --version

# Or check installed UV tools
uv tool list
```

## Configuring Claude

To use the Practices MCP Server with Claude, you need to add it to your Claude configuration:

### Claude Desktop App

Add the following to your `claude_desktop_config.json` file (typically located at `~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "practices": {
      "command": "practices",
      "args": ["server"],
      "disabled": false,
      "autoApprove": [
        "validate_branch_name",
        "get_branch_info",
        "validate_version"
      ]
    }
  }
}
```

### Cline Extension for VS Code

Add the following to your Cline MCP settings (typically located at `~/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json` on macOS):

```json
{
  "mcpServers": {
    "practices": {
      "command": "practices",
      "args": ["server"],
      "disabled": false,
      "autoApprove": [
        "validate_branch_name",
        "get_branch_info",
        "validate_version"
      ]
    }
  }
}
```

## Natural Language Interaction

Once configured, you can interact with Claude naturally to handle development workflow tasks. The MCP server provides Claude with the tools and context to understand your project's practices.

### How It Works

1. **You ask Claude in natural language** - Ask for help with branch creation, version checking, PR preparation, etc.
2. **Claude interprets your request** - The AI understands your intent and identifies which development practice you need help with
3. **Claude uses appropriate MCP tools** - Behind the scenes, Claude calls the right tools from the Practices MCP Server
4. **You get helpful results** - Claude presents the results and next steps in a friendly, context-aware way

## Common Use Cases

Here are common tasks and how to ask Claude to perform them:

### Branch Management

**Create a new feature branch:**
> "Create a feature branch for ticket PMS-123 about user authentication"

**Validate a branch name:**
> "Is the branch name 'feature/PMS-123-add-user-auth' valid according to our conventions?"

**Get information about a branch:**
> "What type of branch is 'feature/PMS-123-add-user-auth' and what ticket is it related to?"

### Version Management

**Check version consistency:**
> "Are our version numbers consistent across all files in the project?"

**Bump the version:**
> "We've added new features and need to bump the minor version number"
>
> "Prepare a patch version bump for our hotfix"

### Pull Request Workflows

**Prepare a pull request:**
> "Prepare a pull request for my current branch"
>
> "Generate a standardized PR description for branch 'feature/PMS-123-add-user-auth'"

**Submit a pull request:**
> "Submit a PR for my current branch to GitHub"

### Jira Integration

**Update a ticket status:**
> "Update the status of PMS-123 to 'In Progress'"

**Create issue links:**
> "Create a link between PMS-123 and PMS-124 to show they're related"

### GitHub Integration

**Create a GitHub PR:**
> "Create a pull request on GitHub from my current branch to develop"

### License Headers

**Add license headers:**
> "Add our standard license headers to all source files in the src directory"

**Check for missing headers:**
> "Check which files are missing license headers in our project"

### Pre-commit Hooks

**Install hooks:**
> "Set up pre-commit hooks for our project"

## Configuration

The Practices MCP Server is configured through a `.practices.yaml` file in your project root. You can ask Claude to help you set this up:

> "Create a default practices configuration file for our Python project"
>
> "Update our practices configuration to use GitHub Flow instead of GitFlow"
>
> "Add a new version file pattern for our package.json"

See the [Configuration Guide](configuration_guide.md) for detailed configuration options.

## CLI Reference

While natural language interaction with Claude is the primary way to use the Practices MCP Server, you can also use the command-line interface directly for scripting or automation purposes.

### Branch Management

```bash
# Create a feature branch
practices branch create feature PMS-123 add-user-authentication

# Create a bugfix branch
practices branch create bugfix PMS-124 fix-login-issue

# Create a hotfix branch
practices branch create hotfix 1.0.1 critical-security-fix

# Create a release branch
practices branch create release 1.1.0

# Validate a branch name
practices branch validate feature/PMS-123-add-authentication

# Get branch info
practices branch info feature/PMS-123-add-authentication
```

### Version Management

```bash
# Check version consistency
practices version check

# Bump minor version
practices version bump minor

# Bump patch version
practices version bump patch

# Bump major version
practices version bump major
```

### Pull Request Workflows

```bash
# Prepare a PR
practices pr prepare

# Prepare a PR and open in browser
practices pr prepare --open-browser

# Submit a PR
practices pr submit

# Generate PR description
practices pr generate-description
```

### Jira Integration

```bash
# Update ticket status
practices jira update-status PMS-123 "In Progress"

# Create issue links
practices jira link-issues PMS-123 PMS-124 "relates to"
```

### GitHub Integration

```bash
# Create a branch on GitHub
practices github create-branch feature/PMS-123-add-authentication

# Create a PR on GitHub
practices github create-pr \
  --title "PMS-123: Add user authentication" \
  --body "This PR implements user authentication functionality" \
  --head feature/PMS-123-add-authentication \
  --base develop
```

### License Headers

```bash
# Add license headers
practices license add-headers src/

# Check for missing headers
practices license check-headers src/
```

### Pre-commit Hooks

```bash
# Install hooks
practices hooks install

# Update hooks
practices hooks update
```

### Working Directory

```bash
# Set working directory
practices set-working-directory .
```

## Troubleshooting

### Common Issues

**Issue**: Claude doesn't recognize the practices MCP server commands

**Solution**: Ensure the server is properly configured in your Claude settings. Try restarting Claude/VS Code, or check if the server is running with:
```bash
# Start the server manually to check for errors
practices server --log-level DEBUG
```

**Issue**: "Error in tool use: MCP server not connected" message

**Solution**: The server may not be starting correctly. Check that the command path is correct in your MCP settings and that the package is properly installed.

**Issue**: Jira integration not working

**Solution**: Check that you have the Jira MCP server configured with valid credentials. See the [Jira MCP Server documentation](https://github.com/modelcontextprotocol/servers/tree/main/src/jira) for details.

**Issue**: GitHub integration not working

**Solution**: Verify that you have the GitHub MCP server configured with a valid personal access token. See the [GitHub MCP Server documentation](https://github.com/modelcontextprotocol/servers/tree/main/src/github) for details.

**Issue**: Version bump failing

**Solution**: Ensure that all version files are consistent before bumping. Ask Claude to "Check if our version numbers are consistent" first.

### Logs and Debugging

Logs are stored in the `.practices/logs` directory in your project. Check these logs for detailed information about errors.

For more verbose server output:

```bash
# Run server with increased logging verbosity
practices server --log-level DEBUG
```

### Getting Help

Ask Claude for help with specific features:

> "What practices MCP tools are available?"
>
> "How do I configure Jira integration with the practices MCP server?"
>
> "What branch naming conventions does the practices server support?"
