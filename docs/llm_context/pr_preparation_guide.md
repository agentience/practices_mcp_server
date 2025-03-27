# PR Preparation Guide for MCP Server Practices

## Overview

This document provides guidance on using the PR preparation functionality provided by the MCP Server Practices module. The PR preparation tools help automate the creation and submission of pull requests, ensuring consistency and adherence to best practices.

## Key Components

The PR preparation system consists of the following components:

1. **PR Templates** - Pre-defined templates for different branch types
2. **PR Description Generator** - Automatically generates PR descriptions based on branch information
3. **PR Workflow** - Manages the PR preparation process, including validation and readiness checks
4. **GitHub Integration** - Submits PRs to GitHub using the GitHub MCP server

## Best Practices

### Test-Driven Development

**Tests MUST pass before a feature is considered complete.** The PR preparation workflow automatically runs tests and will not mark a PR as ready if tests fail. This ensures:

1. Code quality remains high
2. Regressions are caught early
3. Features work as expected
4. Documentation accurately reflects implementation

### PR Preparation Workflow

Following the proper PR preparation workflow helps maintain quality:

1. Make sure your branch follows the naming convention (e.g., `feature/PMS-123-new-feature`)
2. Ensure all changes are committed (the workflow checks for uncommitted changes)
3. Run `prepare_pr` to validate your branch and generate a PR description
4. Address any warnings or suggestions provided by the readiness check
5. Use `submit_pr` to create the PR on GitHub

### PR Description Template Usage

PR descriptions help reviewers understand changes:

- Use the templates provided for your branch type
- Add detailed descriptions of changes made
- Link to relevant Jira tickets
- Include testing details
- Document any breaking changes

## Usage Examples

### Generating a PR Description

```python
from mcp_server_practices.pr import generate_pr_description

# Generate a description for the current branch
result = generate_pr_description("feature/PMS-123-new-feature")
if result["success"]:
    print(result["description"])
else:
    print(f"Error: {result['error']}")
```

### Preparing a PR

```python
from mcp_server_practices.pr import prepare_pr

# Prepare a PR for the current branch
result = prepare_pr()
if result["success"]:
    print(f"PR is ready: {result['title']}")
    print(f"Base branch: {result['base_branch']}")
    print(result["description"])
else:
    print(f"Error: {result['error']}")
```

### Submitting a PR

```python
from mcp_server_practices.pr import submit_pr

# Submit a PR for the current branch
result = submit_pr()
if result["success"]:
    print(f"PR submitted: {result['title']}")
    print(f"Details: {result['pull_request']}")
else:
    print(f"Error: {result['error']}")
```

## Testing Requirements

Before submitting a PR, ensure:

1. All tests pass (the workflow will check this automatically)
2. New features have corresponding tests
3. Tests cover both success and failure cases
4. Integration with other components is tested
5. Edge cases are considered and tested

The PR workflow includes automatic test running, and PRs will only be marked as ready if all tests pass. This is a strict requirement to maintain code quality.

## CLI Interface

For command line usage:

```bash
practices prepare-pr  # Prepare PR for current branch
practices submit-pr   # Submit PR for current branch
```

## Common Issues

### "Tests failed" error

If you see "Tests failed" when preparing a PR:

1. Run tests locally with `pytest`
2. Fix any failing tests
3. Ensure all changes are committed
4. Try the PR preparation again

### "Uncommitted changes" error

The PR workflow requires all changes to be committed:

1. Check for uncommitted changes with `git status`
2. Commit or stash changes
3. Try the PR preparation again

## Conclusion

Following these guidelines ensures that PRs maintain high quality standards and are easier to review. The automated PR preparation tools help enforce these practices.
