# Configuration System Guide for LLMs

This guide helps AI assistants understand the configuration system in the Practices MCP Server, enabling better assistance with configuration-related tasks.

## Conceptual Overview

The configuration system serves as the central control mechanism for the Practices MCP Server, allowing customization of:

1. **Development workflows**: Solo vs. team development approaches
2. **Branching strategies**: GitFlow, GitHub Flow, or Trunk-based development
3. **Project-specific settings**: Different configurations for Python, JavaScript, etc.
4. **Integration points**: Connections to external services like Jira and GitHub
5. **Code quality tools**: Pre-commit hooks, license headers, etc.

The system follows these key principles:
- **Sensible defaults**: Works out-of-the-box with smart defaults
- **Progressive configuration**: Start simple, add complexity as needed
- **Validated schemas**: Prevent configuration errors through validation
- **Project detection**: Adapt to different project types automatically
- **Tool-driven interaction**: Exposed through MCP tools API

## Core Components

### Configuration Schema (`src/mcp_server_practices/config/schema.py`)

- Defines the structure and validation rules using Pydantic models
- Provides type safety and runtime validation
- Includes versioned schema to handle migrations
- Key models: `ConfigurationSchema`, `BranchConfig`, `VersionConfig`

### Configuration Loader (`src/mcp_server_practices/config/loader.py`)

- Locates configuration files in project directories
- Loads YAML into typed objects
- Creates default configurations when none exist
- Files supported: `.practices.yaml`, `.practices.yml`

### Project Type Detection (`src/mcp_server_practices/config/detector.py`)

- Analyzes project files to determine language/framework
- Creates appropriate default configurations
- Indicators: file extensions, config files, etc.
- Supports Python, JavaScript, TypeScript, and more

### Configuration Validator (`src/mcp_server_practices/config/validator.py`)

- Validates configurations against schema
- Checks file existence and permissions
- Ensures consistency across configuration
- Provides clear error messages for issues

### Configuration Templates (`src/mcp_server_practices/config/templates.py`)

- Defines default templates for different project types
- Includes branch patterns, version file configs, etc.
- Adaptable to project requirements

### Configuration Tools (`src/mcp_server_practices/tools/config_tools.py`)

- Exposes configuration functionality as MCP tools
- Provides user-facing API for configuration management
- Handles errors and returns helpful messages

## Tool Usage Patterns

When helping users with configuration, follow these patterns:

1. **Check Existing Configuration**:
   ```python
   config = await call_tool("practices", "get_config", {})
   ```

2. **Create Default Configuration** (only if one doesn't exist):
   ```python
   result = await call_tool("practices", "create_config", {})
   ```

3. **Validate Configuration**:
   ```python
   validation = await call_tool("practices", "validate_config", {})
   ```

4. **Detect Project Type**:
   ```python
   project_info = await call_tool("practices", "detect_project_type", {})
   ```

5. **Modify and Save Configuration**:
   ```python
   config = await call_tool("practices", "get_config", {})
   config["config"]["workflow_mode"] = "team"
   await call_tool("practices", "save_config", {"config": config["config"]})
   ```

## Common User Requests and Responses

### "How do I change my branching strategy?"

Provide instructions to:
1. Check current configuration to see current strategy
2. Modify the branching_strategy field
3. Update branch configurations to match the new strategy
4. Save the configuration

Example:
```python
config = await call_tool("practices", "get_config", {})
config["config"]["branching_strategy"] = "github-flow"
config["config"]["develop_branch"] = None  # Not needed for GitHub Flow
# Update branch configurations...
await call_tool("practices", "save_config", {"config": config["config"]})
```

### "How do I add custom PR templates?"

Provide instructions to:
1. Check if pull_requests.templates exists in configuration
2. Create it if not
3. Add template for specific branch type
4. Save the configuration

Example:
```python
config = await call_tool("practices", "get_config", {})
if "pull_requests" not in config["config"]:
    config["config"]["pull_requests"] = {"templates": {}}
elif "templates" not in config["config"]["pull_requests"]:
    config["config"]["pull_requests"]["templates"] = {}

config["config"]["pull_requests"]["templates"]["feature"] = """
# {ticket_id}: {description}

## Changes
- 

## Testing
1. 
"""
await call_tool("practices", "save_config", {"config": config["config"]})
```

### "What's my current configuration?"

Provide the configuration in an easy-to-read format from:
```python
config = await call_tool("practices", "get_config", {})
```

### "How do I set up version tracking?"

Provide instructions to:
1. Check if version configuration exists
2. Add version information with appropriate file paths and patterns
3. Save configuration

Example:
```python
config = await call_tool("practices", "get_config", {})
config["config"]["version"] = {
    "files": [
        {
            "path": "src/package/__init__.py",
            "pattern": "__version__ = \"(\\d+\\.\\d+\\.\\d+)\""
        },
        {
            "path": "pyproject.toml",
            "pattern": "version = \"(\\d+\\.\\d+\\.\\d+)\""
        }
    ],
    "use_bumpversion": True,
    "bumpversion_config": ".bumpversion.cfg",
    "changelog": "CHANGELOG.md"
}
await call_tool("practices", "save_config", {"config": config["config"]})
```

## Error Handling Best Practices

When users encounter configuration errors:

1. **Validation Errors**: Use `validate_config` to pinpoint issues
2. **Missing Configuration**: Suggest creating a default configuration
3. **Project Type Mismatch**: Check project type detection and suggest manual override
4. **Invalid Regex Patterns**: Help debug and fix regular expressions
5. **File Path Issues**: Verify file paths exist and are accessible

Always prioritize providing clear, actionable solutions rather than just identifying problems.

## Advanced Configuration Scenarios

### Multi-repo Projects

For users working with multiple repositories:
- Explain that configuration is per-repository
- Suggest shared templates across repositories
- Recommend consistent branch and version patterns

### Custom Branch Types

For users needing custom branch types:
- Show how to add new branch types to the branches dictionary
- Ensure pattern includes capture groups for ticket IDs
- Set appropriate base and target branches
- Add version bump settings if needed

### Complex Version Management

For projects with complex versioning:
- Configure multiple version files
- Create patterns to capture version components
- Set up appropriate version bump rules
- Configure changelog management

## Schema Evolution Notes

The configuration schema may evolve over time. Key points:

- New fields are generally optional with sensible defaults
- Default configurations are updated with schema changes
- Loading older configurations will populate new fields with defaults
- Schema validation helps identify missing required fields

Always refer to the latest documentation for the most current schema definition.
