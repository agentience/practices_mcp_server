# Configuration Guide

This guide provides comprehensive documentation for the configuration system in the Practices MCP Server.

## Table of Contents

- [Overview](#overview)
- [Configuration File Format](#configuration-file-format)
- [Configuration Schema](#configuration-schema)
- [Project Type Detection](#project-type-detection)
- [Default Configurations](#default-configurations)
- [MCP Tools](#mcp-tools)
- [Working with Configuration Files](#working-with-configuration-files)
- [Common Scenarios](#common-scenarios)
- [Troubleshooting](#troubleshooting)

## Overview

The configuration system enables development teams to customize the behavior of the Practices MCP Server based on project requirements. It provides sensible defaults while allowing flexibility for different project types, branching strategies, and development workflows.

Key features of the configuration system:

- **Project type detection**: Automatically identifies project types (Python, JavaScript, etc.)
- **Branching strategy support**: Compatible with GitFlow, GitHub Flow, and Trunk-based development
- **Extensible schema**: Rich configuration options for integrations, PR templates, etc.
- **Validation**: Ensures configuration is valid and consistent
- **Simple YAML format**: Easy to read and edit
- **MCP tools**: Provides tools for configuration management

## Configuration File Format

Configuration is stored in a YAML file named `.practices.yaml` in the project root directory. Here's an example of a minimal configuration file:

```yaml
# Project type (python, javascript, typescript, java, csharp, go, rust, generic)
project_type: python

# Branching strategy (gitflow, github-flow, trunk)
branching_strategy: gitflow

# Development workflow mode (solo, team)
workflow_mode: solo 

# Main branch name
main_branch: main

# Develop branch name (required for GitFlow)
develop_branch: develop

# Branch configurations
branches:
  feature:
    pattern: ^feature/([A-Z]+-\d+)-(.+)$
    base: develop
  bugfix:
    pattern: ^bugfix/([A-Z]+-\d+)-(.+)$
    base: develop
  hotfix:
    pattern: ^hotfix/(\d+\.\d+\.\d+(?:-[a-zA-Z0-9.]+)?)-(.+)$
    base: main
    target: [main, develop]
    version_bump: patch
  release:
    pattern: ^release/(\d+\.\d+\.\d+(?:-[a-zA-Z0-9.]+)?)(?:-(.+))?$
    base: develop
    target: [main, develop]
    version_bump: minor
  docs:
    pattern: ^docs/(.+)$
    base: develop
```

## Configuration Schema

The configuration schema is defined using Pydantic models and provides validation for all configuration options. Below is a detailed list of available settings:

### Root Configuration

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `project_type` | String | `python` | Project language or framework |
| `branching_strategy` | String | `gitflow` | Branching strategy to use |
| `workflow_mode` | String | `solo` | Development workflow mode |
| `main_branch` | String | `main` | Name of the main/production branch |
| `develop_branch` | String | `develop` | Name of the development branch (required for GitFlow) |
| `branches` | Dict | | Configuration for branch types |
| `version` | Dict | Optional | Configuration for version management |
| `pull_requests` | Dict | Optional | Configuration for pull requests |
| `jira` | Dict | Optional | Configuration for Jira integration |
| `github` | Dict | Optional | Configuration for GitHub integration |
| `pre_commit` | Dict | Optional | Configuration for pre-commit hooks |
| `license_headers` | Dict | Optional | Configuration for license headers |

### Branch Configuration

Each branch type (feature, bugfix, hotfix, release, docs) can have the following configuration:

| Field | Type | Description |
|-------|------|-------------|
| `pattern` | String | Regex pattern for branch names |
| `base` | String | Base branch to create from and merge to |
| `target` | List | List of branches to merge to (for release and hotfix branches) |
| `version_bump` | String | Type of version bump to perform (major, minor, patch, none) |

### Version Configuration

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `files` | List | | List of files containing version strings |
| `use_bumpversion` | Boolean | `true` | Whether to use bump2version for version management |
| `bumpversion_config` | String | `.bumpversion.cfg` | Path to the bump2version configuration file |
| `changelog` | String | `CHANGELOG.md` | Path to the changelog file |

Each version file configuration requires:
- `path`: Path to the file containing version
- `pattern`: Regex pattern to match version string (must include a capture group)

### PR Configuration

| Field | Type | Description |
|-------|------|-------------|
| `templates` | Dict | Templates for PR descriptions |
| `checks` | Dict | Checks to run before PR creation |

PR templates include:
- `feature`: Template for feature PR descriptions
- `bugfix`: Template for bugfix PR descriptions
- `release`: Template for release PR descriptions
- `hotfix`: Template for hotfix PR descriptions
- `docs`: Template for documentation PR descriptions

PR checks include:
- `run_tests`: Whether to run tests before allowing PR creation
- `run_linting`: Whether to run linting before allowing PR creation

### Jira Configuration

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enabled` | Boolean | `true` | Whether Jira integration is enabled |
| `project_key` | String | | Jira project key |
| `transition_to_in_progress` | Boolean | `true` | Whether to transition tickets to In Progress when creating branches |
| `update_on_pr_creation` | Boolean | `true` | Whether to update Jira tickets when PRs are created |

### GitHub Configuration

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enabled` | Boolean | `true` | Whether GitHub integration is enabled |
| `owner` | String | Optional | GitHub repository owner |
| `repo` | String | Optional | GitHub repository name |
| `create_pr` | Boolean | `true` | Whether to automatically create PRs |
| `required_checks` | List | Optional | List of required checks for PRs |

### Pre-Commit Configuration

| Field | Type | Description |
|-------|------|-------------|
| `hooks` | List | List of pre-commit hooks to install |

### License Header Configuration

| Field | Type | Description |
|-------|------|-------------|
| `template` | String | License header template text |
| `file_types` | List | Configuration for different file types |

## Project Type Detection

The configuration system can automatically detect the project type based on files in the project directory. This detection is used when creating default configurations.

Detection rules:

- **Python**: Presence of `pyproject.toml`, `setup.py`, or multiple `.py` files
- **JavaScript**: Presence of `package.json`, `node_modules`, or multiple `.js` files
- **TypeScript**: Presence of `tsconfig.json` or multiple `.ts` files
- **Java**: Presence of `pom.xml`, `build.gradle`, or multiple `.java` files
- **C#**: Presence of `.sln`, `.csproj`, or multiple `.cs` files
- **Go**: Presence of `go.mod`, `go.sum`, or multiple `.go` files
- **Rust**: Presence of `Cargo.toml`, `Cargo.lock`, or multiple `.rs` files
- **Generic**: Used when no specific project type is detected

## Default Configurations

The system provides default configurations for different project types and branching strategies. These defaults are used when creating a new configuration file or when no configuration file exists.

Default configurations include:

- Branch patterns appropriate for the project
- Version file paths specific to the project type
- Appropriate pre-commit hooks for the language
- License header templates for the project's file types

## MCP Tools

The configuration system exposes the following MCP tools:

### `get_config`

Gets the current project configuration.

**Output Schema:**
- `config`: Project configuration
- `is_default`: Whether this is a default configuration
- `path`: Path to the configuration file, or null if default

Example:
```python
result = await call_tool("practices", "get_config", {})
print(f"Configuration loaded from: {result['path']}")
```

### `create_config`

Creates a default configuration file in the project root.

**Input Schema:**
- `project_type`: Project type (optional, auto-detected if not provided)
- `overwrite`: Whether to overwrite existing configuration (default: false)

**Output Schema:**
- `success`: Whether the configuration was created successfully
- `path`: Path to the created configuration file
- `error`: Error message if the creation failed

Example:
```python
result = await call_tool("practices", "create_config", {
    "project_type": "typescript",
    "overwrite": True
})
if result["success"]:
    print(f"Created configuration at: {result['path']}")
else:
    print(f"Failed to create configuration: {result['error']}")
```

### `validate_config`

Validates the current project configuration.

**Output Schema:**
- `valid`: Whether the configuration is valid
- `errors`: List of validation errors
- `missing_files`: List of missing files referenced in configuration

Example:
```python
result = await call_tool("practices", "validate_config", {})
if result["valid"]:
    print("Configuration is valid")
else:
    print("Configuration errors:")
    for error in result["errors"]:
        print(f"- {error}")
    
    if result["missing_files"]:
        print("Missing files:")
        for file in result["missing_files"]:
            print(f"- {file}")
```

### `detect_project_type`

Detects the project type based on files in the directory.

**Output Schema:**
- `project_type`: Detected project type
- `confidence`: Confidence level (high, medium, low)
- `details`: Details about the detection

Example:
```python
result = await call_tool("practices", "detect_project_type", {})
print(f"Detected project type: {result['project_type']} (confidence: {result['confidence']})")
```

### `save_config`

Saves a configuration to a file.

**Input Schema:**
- `config`: Configuration to save
- `path`: Path to save the configuration to (optional)

**Output Schema:**
- `success`: Whether the configuration was saved successfully
- `path`: Path to the saved configuration file
- `error`: Error message if the save failed

Example:
```python
config = await call_tool("practices", "get_config", {})
config["config"]["workflow_mode"] = "team"

result = await call_tool("practices", "save_config", {
    "config": config["config"]
})
if result["success"]:
    print(f"Saved configuration to: {result['path']}")
else:
    print(f"Failed to save configuration: {result['error']}")
```

## Working with Configuration Files

### Creating a New Configuration

To create a new configuration file:

1. Use the `create_config` tool:
   ```python
   await call_tool("practices", "create_config", {})
   ```

2. Or create the file manually:
   ```python
   config = {
       "project_type": "python",
       "branching_strategy": "gitflow",
       "workflow_mode": "solo",
       "main_branch": "main",
       "develop_branch": "develop",
       "branches": {
           "feature": {
               "pattern": "^feature/([A-Z]+-\\d+)-(.+)$",
               "base": "develop"
           },
           "bugfix": {
               "pattern": "^bugfix/([A-Z]+-\\d+)-(.+)$",
               "base": "develop"
           }
       }
   }
   
   await call_tool("practices", "save_config", {"config": config})
   ```

### Modifying Configuration

To modify an existing configuration:

1. Load the current configuration:
   ```python
   config_result = await call_tool("practices", "get_config", {})
   config = config_result["config"]
   ```

2. Modify the configuration:
   ```python
   config["workflow_mode"] = "team"
   config["branches"]["feature"]["pattern"] = "^feature/([A-Z]+-\\d+)_(.+)$"
   ```

3. Save the updated configuration:
   ```python
   await call_tool("practices", "save_config", {"config": config})
   ```

## Common Scenarios

### Switching Branching Strategies

To switch from GitFlow to GitHub Flow:

```python
config_result = await call_tool("practices", "get_config", {})
config = config_result["config"]

# Change to GitHub Flow
config["branching_strategy"] = "github-flow"
config["develop_branch"] = None  # Not needed for GitHub Flow

# Update branch configurations
for branch_type in ["feature", "bugfix", "docs", "hotfix"]:
    if branch_type in config["branches"]:
        config["branches"][branch_type]["base"] = "main"

# Remove release branch (not typically used in GitHub Flow)
if "release" in config["branches"]:
    del config["branches"]["release"]

await call_tool("practices", "save_config", {"config": config})
```

### Adding Jira Integration

To add or update Jira integration:

```python
config_result = await call_tool("practices", "get_config", {})
config = config_result["config"]

# Configure Jira integration
config["jira"] = {
    "enabled": True,
    "project_key": "PMS",
    "transition_to_in_progress": True,
    "update_on_pr_creation": True
}

await call_tool("practices", "save_config", {"config": config})
```

### Customizing PR Templates

To customize PR templates:

```python
config_result = await call_tool("practices", "get_config", {})
config = config_result["config"]

# Ensure the PR section exists
if "pull_requests" not in config:
    config["pull_requests"] = {}

# Ensure the templates section exists
if "templates" not in config["pull_requests"]:
    config["pull_requests"]["templates"] = {}

# Set up a custom feature PR template
config["pull_requests"]["templates"]["feature"] = """
# {ticket_id}: {description}

## Summary
This PR implements {description} functionality ({ticket_id}).

## Changes
- 

## How to Test
1. 
2. 

## Screenshots
(Add screenshots here)

## Related Issues
- {ticket_id}: {ticket_description}
"""

await call_tool("practices", "save_config", {"config": config})
```

## Troubleshooting

### Configuration Validation Errors

If you receive validation errors, check the following:

1. **Missing required fields**: Ensure all required fields are present in your configuration.
2. **Invalid branching strategy**: For GitFlow, ensure `develop_branch` is specified.
3. **Invalid regex patterns**: Ensure all branch patterns are valid regular expressions.
4. **Invalid version patterns**: Version patterns must include a capture group.
5. **Missing base branches**: Base branches must be defined in the configuration.

### Project Type Detection Issues

If project type detection is not working as expected:

1. Ensure you have the appropriate files for your project type (e.g., `package.json` for JavaScript).
2. Use the `detect_project_type` tool to see what's being detected and why.
3. Manually specify the project type when creating a configuration:
   ```python
   await call_tool("practices", "create_config", {"project_type": "typescript"})
   ```

### File Path Issues

If you see messages about missing files:

1. Use the `validate_config` tool to see which files are missing.
2. Update the configuration with the correct file paths.
3. Create any missing files that are required by the configuration.
