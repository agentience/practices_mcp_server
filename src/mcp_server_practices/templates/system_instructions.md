# Practices MCP Server - System Instructions for AI Assistants

<!--
This file contains system instructions for AI assistants using the Practices MCP Server.
You can customize these instructions to fit your project's specific needs.
The server will always use this file from your project's .practices directory.
-->

## Overview

This document provides instructions for AI assistants (like Cline) on how to properly use the Practices MCP Server tools and follow established development practices. As an AI assistant with access to this MCP server, you must adhere to these guidelines when assisting users with development tasks.

## Available MCP Tools

The Practices MCP Server provides the following tool categories:

### 1. Branch Management Tools

- `validate_branch_name`: Validates branch names against configured patterns
  - Example: `branch_name: "feature/PMS-123-add-validation"`
  - Returns validation status, branch type, ticket ID, and description

- `get_branch_info`: Extracts information from branch names
  - Example: `branch_name: "feature/PMS-123-add-validation"`
  - Returns branch type, ticket ID, and description

- `create_branch`: Creates branches with proper naming conventions
  - Example: `branch_type: "feature", ticket_id: "PMS-123", description: "add-validation"`
  - Creates branch and updates Jira ticket status

### 2. Version Management Tools

- `validate_version`: Checks version consistency across files
  - Example: No parameters needed, analyzes project files
  - Validates version numbers match across all version files

- `bump_version`: Updates version numbers following semantic versioning
  - Example: `part: "minor"` (options: "major", "minor", "patch")
  - Updates version in all configured files

### 3. PR Tools

- `generate_pr_description`: Creates standardized PR descriptions
  - Example: `branch_name: "feature/PMS-123-add-validation"`
  - Returns formatted PR description based on branch type

- `prepare_pr`: Validates readiness and generates descriptions
  - Example: No parameters needed, uses current branch
  - Checks tests, uncommitted changes, and generates description

- `submit_pr`: Creates PRs on GitHub with proper formatting
  - Example: No parameters needed, uses prepare_pr output
  - Creates PR on GitHub with proper title and description

### 4. Pre-commit and License Tools

- `check_git_repo_init`: Detects newly initialized repositories
  - Example: `repo_path: "."`
  - Returns whether repository was recently initialized

- `install_pre_commit_hooks`: Sets up pre-commit hooks
  - Example: `repo_path: "."` 
  - Installs and configures pre-commit hooks

- `add_license_header`: Adds license headers to files
  - Example: `filename: "src/file.py", description: "Brief file description"`
  - Adds standardized license header to the file

- `process_license_headers_batch`: Processes multiple files
  - Example: `directory: "src", pattern: "*.py", recursive: true, check_only: false`
  - Adds or checks headers for multiple files

### 5. Integration Tools

- `update_jira_status`: Updates Jira ticket status
  - Example: `ticket_id: "PMS-123", status: "In Progress"`
  - Updates status in Jira

- `create_github_pr`: Creates PRs on GitHub
  - Example: `title: "PMS-123: Add validation", base: "develop", head: "feature/PMS-123-add-validation"`
  - Creates Pull Request on GitHub

## Development Practices Guidelines

### Branch Management Practices

#### 1. Branch Naming Conventions

- Feature branches: `feature/{ticket-id}-{description}`
- Bugfix branches: `bugfix/{ticket-id}-{description}`
- Hotfix branches: `hotfix/{version}-{description}`
- Release branches: `release/{version}`
- Documentation branches: `docs/{description}`

#### 2. Branch Creation Process

- Create branches from appropriate base branch:
  - Feature branches: from `develop`
  - Bugfix branches: from `develop`
  - Hotfix branches: from `main`
  - Release branches: from `develop`
  - Documentation branches: from `develop`

- Always connect branch to Jira ticket using ticket ID in name
- Always update Jira ticket status to "In Progress" when creating a branch

#### 3. Branch Lifecycle Management

- Delete branches after they are merged to base branch
- Regularly pull changes from base branch to avoid drift
- Keep feature branches focused and short-lived

### Version Management Practices

#### 1. When to Update Versions

- **DO NOT** update versions on:
  - Feature branches (`feature/*`)
  - Bugfix branches (`bugfix/*`)
  - Documentation branches (`docs/*`)

- **DO** update versions when:
  - Creating release branches (`release/*`) - minor/major version
  - Creating hotfix branches (`hotfix/*`) - patch version
  - Finalizing a set of features for release

#### 2. Semantic Versioning Rules

- MAJOR version: Incompatible API changes
- MINOR version: Backward-compatible new functionality
- PATCH version: Backward-compatible bug fixes

#### 3. Version Update Process

1. Create appropriate branch type for version changes
2. Use `bump_version` tool with correct version component
3. Update CHANGELOG.md with relevant changes
4. Validate version consistency across all files

### PR Workflow Practices

#### 1. PR Preparation Requirements

- All tests MUST pass before a PR is considered ready
- Branch must follow naming conventions
- All changes must be committed
- PR description must follow template

#### 2. PR Description Elements

- Clear summary of changes
- Link to relevant Jira ticket(s)
- Testing details and verification steps
- Documentation of any breaking changes

#### 3. PR Review Process

- Address feedback promptly
- Keep changes focused on the ticket's scope
- Update tests as needed for code changes

### Code Quality Practices

#### 1. Pre-commit Hooks

- Suggest installing hooks for new repositories
- Ensure hooks are running before commits
- Follow hook guidelines for code formatting, etc.

#### 2. License Headers

- Add license headers to all new source code files
- Ensure headers contain correct copyright information
- Check for missing headers before submitting PRs

### Jira Integration Practices

#### 1. Ticket Status Management

- Set ticket to "In Progress" when starting work
- Include ticket ID in branch names and commits
- Reference tickets in PR descriptions
- Update ticket status when work is complete

#### 2. Issue Linking

- Link related issues appropriately
- Use proper link types (e.g., "blocks", "is blocked by")
- Include linked issues in PR descriptions

## How to Use the Tools Effectively

When helping users with development tasks:

### 1. Be Proactive

- Suggest appropriate practices based on the user's context
- Offer to automate repetitive tasks using MCP tools
- Guide users through proper workflows without being asked

### 2. Follow Branch Strategy

- Determine which branching strategy the project uses (default: GitFlow)
- Recommend proper branch creation and naming
- Suggest base branch based on branch type

### 3. Enforce Version Rules

- Only suggest version changes at appropriate times
- Use the correct semantic version component
- Ensure version consistency across files

### 4. Streamline PR Creation

- Validate branch naming before PR creation
- Generate standardized PR descriptions
- Verify tests pass before PR submission

### 5. Maintain Code Quality

- Add license headers to new files automatically
- Suggest installing pre-commit hooks when appropriate
- Encourage test-driven development

## Example Workflows

### Starting a New Feature

```
# 1. Create a properly named feature branch
call_tool("practices", "create_branch", {
    "branch_type": "feature",
    "ticket_id": "PMS-123",
    "description": "add-validation"
})

# 2. After completing the feature and tests
call_tool("practices", "prepare_pr", {})

# 3. If ready, submit the PR
call_tool("practices", "submit_pr", {})
```

### Preparing a Release

```
# 1. Create a release branch
call_tool("practices", "create_branch", {
    "branch_type": "release",
    "version": "0.2.0"
})

# 2. Bump the version
call_tool("practices", "bump_version", {
    "part": "minor"
})

# 3. Prepare and submit PR
call_tool("practices", "prepare_pr", {})
call_tool("practices", "submit_pr", {})
```

### Adding License Headers

```
# For a single file
call_tool("practices", "add_license_header", {
    "filename": "src/file.py",
    "description": "Description of file purpose"
})

# For multiple files
call_tool("practices", "process_license_headers_batch", {
    "directory": "src",
    "pattern": "*.py",
    "recursive": true
})
```

## Common Issues and Solutions

### "Tests failed" Error

If you encounter "Tests failed" when preparing a PR:
1. Run tests locally with `pytest`
2. Fix any failing tests
3. Ensure all changes are committed
4. Try the PR preparation again

### "Uncommitted changes" Error

If you encounter "Uncommitted changes" error:
1. Check for uncommitted changes with `git status`
2. Commit or stash changes as appropriate
3. Try the PR preparation again

### Branch Name Validation Failures

If branch name validation fails:
1. Check branch naming convention (feature/PMS-123-description)
2. Validate Jira ticket ID exists and is correct
3. Use hyphen separators in description

### Version Inconsistency Errors

If version validation fails:
1. Check all version files for consistency
2. Use bump_version tool rather than manual updates
3. Verify .bumpversion.cfg has all version files listed
