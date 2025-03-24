# Practices MCP Server - Tool Specifications

## Overview

The Practices MCP server provides a set of tools that enable AI assistants and developers to implement and enforce development best practices. This document outlines the specifications for each tool, including input parameters, output formats, and usage examples.

## Core Tools

### Branch Management Tools

#### `validate_branch_name`

Validates a branch name against the configured branch naming conventions.

**Input Schema:**
```json
{
  "branch_name": "String",
  "config_path": "String (optional)"
}
```

**Output Schema:**
```json
{
  "valid": "Boolean",
  "branch_type": "String (feature, bugfix, release, etc.)",
  "errors": ["String (error messages if not valid)"],
  "suggestions": ["String (suggested fixes if not valid)"]
}
```

**Example:**
```python
# Valid branch name
result = validate_branch_name({
  "branch_name": "feature/PMS-3-add-branch-validation"
})
# Result: {"valid": true, "branch_type": "feature", "errors": [], "suggestions": []}

# Invalid branch name
result = validate_branch_name({
  "branch_name": "add-feature"
})
# Result: {"valid": false, "branch_type": null, "errors": ["Branch name does not follow convention"], "suggestions": ["feature/TICKET-add-feature"]}
```

#### `get_branch_info`

Extracts information from a branch name according to configured patterns.

**Input Schema:**
```json
{
  "branch_name": "String",
  "config_path": "String (optional)"
}
```

**Output Schema:**
```json
{
  "type": "String (feature, bugfix, release, etc.)",
  "ticket_id": "String (optional)",
  "description": "String",
  "version": "String (for release/hotfix branches)",
  "base_branch": "String",
  "target_branches": ["String"],
  "version_bump": "String (major, minor, patch, or null)"
}
```

**Example:**
```python
result = get_branch_info({
  "branch_name": "feature/PMS-3-add-branch-validation"
})
# Result: {"type": "feature", "ticket_id": "PMS-3", "description": "add branch validation", "base_branch": "develop", "target_branches": ["develop"], "version_bump": null}
```

#### `create_branch`

Creates a properly formatted branch based on the provided information.

**Input Schema:**
```json
{
  "type": "String (feature, bugfix, release, etc.)",
  "ticket_id": "String (optional)",
  "description": "String",
  "version": "String (for release/hotfix branches, optional)",
  "config_path": "String (optional)"
}
```

**Output Schema:**
```json
{
  "branch_name": "String",
  "created": "Boolean",
  "base_branch": "String",
  "command_used": "String"
}
```

**Example:**
```python
result = create_branch({
  "type": "feature",
  "ticket_id": "PMS-4",
  "description": "implement version management"
})
# Result: {"branch_name": "feature/PMS-4-implement-version-management", "created": true, "base_branch": "develop", "command_used": "git checkout -b feature/PMS-4-implement-version-management develop"}
```

### Version Management Tools

#### `validate_version`

Checks version consistency across files according to the configured patterns.

**Input Schema:**
```json
{
  "files": [
    {
      "path": "String",
      "pattern": "String (regex)"
    }
  ],
  "config_path": "String (optional)"
}
```

**Output Schema:**
```json
{
  "consistent": "Boolean",
  "version": "String",
  "files": [
    {
      "path": "String",
      "version": "String",
      "consistent": "Boolean"
    }
  ],
  "errors": ["String"]
}
```

**Example:**
```python
result = validate_version({
  "files": [
    {"path": "src/package/__init__.py", "pattern": "__version__ = \"(\\d+\\.\\d+\\.\\d+)\""},
    {"path": "pyproject.toml", "pattern": "version = \"(\\d+\\.\\d+\\.\\d+)\""}
  ]
})
# Result: {"consistent": true, "version": "0.1.0", "files": [{"path": "src/package/__init__.py", "version": "0.1.0", "consistent": true}, {"path": "pyproject.toml", "version": "0.1.0", "consistent": true}], "errors": []}
```

#### `bump_version`

Bumps the version in all configured files according to semantic versioning rules.

**Input Schema:**
```json
{
  "part": "String (major, minor, patch)",
  "files": [
    {
      "path": "String",
      "pattern": "String (regex)"
    }
  ],
  "dry_run": "Boolean (optional)",
  "config_path": "String (optional)"
}
```

**Output Schema:**
```json
{
  "previous_version": "String",
  "new_version": "String",
  "files_updated": ["String (file paths)"],
  "changes": [
    {
      "path": "String",
      "previous": "String",
      "new": "String"
    }
  ]
}
```

**Example:**
```python
result = bump_version({
  "part": "minor",
  "files": [
    {"path": "src/package/__init__.py", "pattern": "__version__ = \"(\\d+\\.\\d+\\.\\d+)\""},
    {"path": "pyproject.toml", "pattern": "version = \"(\\d+\\.\\d+\\.\\d+)\""}
  ]
})
# Result: {"previous_version": "0.1.0", "new_version": "0.2.0", "files_updated": ["src/package/__init__.py", "pyproject.toml"], "changes": [{"path": "src/package/__init__.py", "previous": "__version__ = \"0.1.0\"", "new": "__version__ = \"0.2.0\""}, {"path": "pyproject.toml", "previous": "version = \"0.1.0\"", "new": "version = \"0.2.0\""}]}
```

### PR Management Tools

#### `generate_pr_description`

Generates a Pull Request description based on branch information and templates.

**Input Schema:**
```json
{
  "branch_name": "String",
  "template_type": "String (optional)",
  "template_variables": {
    "key": "value (optional)"
  },
  "config_path": "String (optional)"
}
```

**Output Schema:**
```json
{
  "title": "String",
  "description": "String",
  "template_used": "String",
  "ticket_id": "String (optional)",
  "variables_used": {
    "key": "value"
  }
}
```

**Example:**
```python
result = generate_pr_description({
  "branch_name": "feature/PMS-3-add-branch-validation"
})
# Result: {"title": "PMS-3: Add branch validation", "description": "# PMS-3: Add branch validation\n\n## Summary\nThis PR implements branch validation functionality (PMS-3).\n\n...", "template_used": "feature", "ticket_id": "PMS-3", "variables_used": {"ticket_id": "PMS-3", "description": "add branch validation"}}
```

#### `prepare_pr`

Prepares a Pull Request by running checks, generating a description, and optionally creating the PR on GitHub.

**Input Schema:**
```json
{
  "branch_name": "String",
  "base_branch": "String (optional)",
  "run_checks": "Boolean (optional)",
  "create_pr": "Boolean (optional)",
  "pr_file_path": "String (optional)",
  "config_path": "String (optional)"
}
```

**Output Schema:**
```json
{
  "title": "String",
  "description": "String",
  "base_branch": "String",
  "checks": {
    "passed": "Boolean",
    "results": [
      {
        "name": "String",
        "passed": "Boolean",
        "output": "String (optional)"
      }
    ]
  },
  "pr_file": "String (path to PR description file, if created)",
  "pr_url": "String (if PR was created on GitHub)"
}
```

**Example:**
```python
result = prepare_pr({
  "branch_name": "feature/PMS-3-add-branch-validation",
  "run_checks": true
})
# Result: {"title": "PMS-3: Add branch validation", "description": "...", "base_branch": "develop", "checks": {"passed": true, "results": [{"name": "tests", "passed": true}, {"name": "lint", "passed": true}]}, "pr_file": "pr_description_PMS-3.md", "pr_url": null}
```

### Workflow Tools

#### `get_workflow_status`

Gets the current workflow status and provides guidance on next steps.

**Input Schema:**
```json
{
  "config_path": "String (optional)"
}
```

**Output Schema:**
```json
{
  "current_branch": "String",
  "branch_type": "String",
  "workflow_stage": "String (development, release, hotfix, etc.)",
  "current_version": "String",
  "jira_status": {
    "ticket_id": "String",
    "status": "String"
  },
  "next_steps": [
    {
      "step": "String",
      "description": "String",
      "command": "String (optional)"
    }
  ]
}
```

**Example:**
```python
result = get_workflow_status({})
# Result: {"current_branch": "feature/PMS-3-add-branch-validation", "branch_type": "feature", "workflow_stage": "development", "current_version": "0.1.0", "jira_status": {"ticket_id": "PMS-3", "status": "In Progress"}, "next_steps": [{"step": "Complete development", "description": "Finish implementing the feature"}, {"step": "Run tests", "description": "Ensure all tests pass", "command": "pytest"}, {"step": "Prepare PR", "description": "Create a PR to merge to develop", "command": "practices pr prepare"}]}
```

## Integration Tools

### Jira Integration

#### `update_jira_status`

Updates the status of a Jira issue using the jira-server MCP.

**Input Schema:**
```json
{
  "ticket_id": "String",
  "status": "String",
  "comment": "String (optional)"
}
```

**Output Schema:**
```json
{
  "updated": "Boolean",
  "ticket_id": "String",
  "previous_status": "String",
  "new_status": "String",
  "url": "String"
}
```

**Example:**
```python
result = update_jira_status({
  "ticket_id": "PMS-3",
  "status": "In Progress",
  "comment": "Starting implementation"
})
# Result: {"updated": true, "ticket_id": "PMS-3", "previous_status": "To Do", "new_status": "In Progress", "url": "https://jira.example.com/browse/PMS-3"}
```

#### `get_jira_ticket_info`

Gets information about a Jira ticket using the jira-server MCP.

**Input Schema:**
```json
{
  "ticket_id": "String"
}
```

**Output Schema:**
```json
{
  "ticket_id": "String",
  "summary": "String",
  "description": "String",
  "status": "String",
  "assignee": "String",
  "reporter": "String",
  "created": "String (date)",
  "updated": "String (date)",
  "priority": "String",
  "url": "String"
}
```

**Example:**
```python
result = get_jira_ticket_info({
  "ticket_id": "PMS-3"
})
# Result: {"ticket_id": "PMS-3", "summary": "Add branch validation", "description": "Implement branch name validation against configured patterns", "status": "In Progress", "assignee": "User", "reporter": "Manager", "created": "2025-03-20", "updated": "2025-03-24", "priority": "Medium", "url": "https://jira.example.com/browse/PMS-3"}
```

### GitHub Integration

#### `create_github_pr`

Creates a Pull Request on GitHub using the github MCP server.

**Input Schema:**
```json
{
  "title": "String",
  "body": "String",
  "head": "String (branch name)",
  "base": "String (target branch)",
  "draft": "Boolean (optional)"
}
```

**Output Schema:**
```json
{
  "created": "Boolean",
  "pr_number": "Number",
  "url": "String",
  "html_url": "String",
  "state": "String"
}
```

**Example:**
```python
result = create_github_pr({
  "title": "PMS-3: Add branch validation",
  "body": "# PMS-3: Add branch validation...",
  "head": "feature/PMS-3-add-branch-validation",
  "base": "develop"
})
# Result: {"created": true, "pr_number": 42, "url": "https://api.github.com/repos/owner/repo/pulls/42", "html_url": "https://github.com/owner/repo/pull/42", "state": "open"}
```

#### `get_github_branches`

Gets a list of branches from GitHub using the github MCP server.

**Input Schema:**
```json
{
  "repo": "String (optional)",
  "pattern": "String (optional regex)"
}
```

**Output Schema:**
```json
{
  "branches": [
    {
      "name": "String",
      "commit": {
        "sha": "String",
        "url": "String"
      },
      "protected": "Boolean"
    }
  ],
  "count": "Number",
  "matched_pattern": "Number (if pattern provided)"
}
```

**Example:**
```python
result = get_github_branches({
  "pattern": "feature/.*"
})
# Result: {"branches": [{"name": "feature/PMS-3-add-branch-validation", "commit": {"sha": "abcdef123456", "url": "https://github.com/..."}, "protected": false}, ...], "count": 3, "matched_pattern": 3}
```

## Configuration Tools

#### `load_config`

Loads and validates a configuration from a project.

**Input Schema:**
```json
{
  "path": "String (optional)",
  "detect_project_type": "Boolean (optional)"
}
```

**Output Schema:**
```json
{
  "config": {
    "project_type": "String",
    "branching_strategy": "String",
    "...": "..."
  },
  "source": "String (path or 'default')",
  "is_valid": "Boolean",
  "validation_errors": ["String (if any)"],
  "detected_project_type": "String (if detected)"
}
```

**Example:**
```python
result = load_config({
  "path": "/path/to/project",
  "detect_project_type": true
})
# Result: {"config": {"project_type": "python", "branching_strategy": "gitflow", ...}, "source": "/path/to/project/.practices.yaml", "is_valid": true, "validation_errors": [], "detected_project_type": "python"}
```

#### `generate_default_config`

Generates a default configuration file for a project.

**Input Schema:**
```json
{
  "project_type": "String",
  "branching_strategy": "String",
  "output_path": "String (optional)",
  "jira_project_key": "String (optional)",
  "overwrite": "Boolean (optional)"
}
```

**Output Schema:**
```json
{
  "config": "String (YAML content)",
  "written": "Boolean",
  "path": "String (if written)",
  "template_used": "String"
}
```

**Example:**
```python
result = generate_default_config({
  "project_type": "python",
  "branching_strategy": "gitflow",
  "jira_project_key": "PMS",
  "output_path": "/path/to/project/.practices.yaml"
})
# Result: {"config": "project_type: python\nbranching_strategy: gitflow\n...", "written": true, "path": "/path/to/project/.practices.yaml", "template_used": "python-gitflow"}
```

## Command Line Interface

The Practices MCP server also includes a command-line interface (CLI) that provides access to all the above tools. The CLI is designed to be used directly by developers or in scripts and CI/CD pipelines.

```bash
# Validate a branch name
practices branch validate feature/PMS-3-add-branch-validation

# Create a branch
practices branch create --type feature --ticket PMS-4 --description "implement version management"

# Check version consistency
practices version check

# Bump version
practices version bump minor

# Generate a PR description
practices pr generate

# Prepare a PR
practices pr prepare

# Get workflow status
practices workflow status
```

The CLI provides help for all commands and subcommands:

```bash
# Get general help
practices --help

# Get help for a specific command
practices branch --help
```

## Error Handling

All tools follow a consistent error handling pattern:

1. Validation errors for input parameters
2. Execution errors with specific error codes
3. Integration errors for external services

Errors are returned in a structured format:

```json
{
  "error": true,
  "code": "String (error code)",
  "message": "String (user-friendly message)",
  "details": "Any (error-specific details)"
}
```

Common error codes include:
- `VALIDATION_ERROR`: Invalid input parameters
- `CONFIG_ERROR`: Configuration loading or parsing error
- `EXECUTION_ERROR`: Error during tool execution
- `INTEGRATION_ERROR`: Error with an external service
- `PERMISSION_ERROR`: Insufficient permissions for the operation

## Tool Implementation

The tools are implemented with a focus on:

1. **Configuration-driven behavior**: All tools adapt based on configuration
2. **Reusable components**: Common functionality is shared between tools
3. **Clear error reporting**: Errors provide actionable information
4. **Documentation**: All tools are self-documenting
5. **Testing**: Each tool has comprehensive tests

Tools are versioned along with the MCP server, and their interfaces follow semantic versioning principles.
