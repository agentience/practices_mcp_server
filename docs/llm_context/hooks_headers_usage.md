# LLM Context: Pre-commit Hooks and License Headers Usage

This document provides instructions for AI assistants on how to effectively use the pre-commit hooks and license headers functionality provided by the Practices MCP Server.

## Pre-commit Hooks Usage

### Detecting Git Repository Initialization

When a user is setting up a new project or initializing a Git repository, you should:

1. Detect the repository initialization using the `check_git_repo_init` tool:

```python
# Check if a Git repository was recently initialized
check_result = call_tool("practices", "check_git_repo_init", {
    "repo_path": "path/to/repo"  # Usually "." for current directory
})

# If the repository is newly initialized
if check_result.get("is_newly_initialized", False):
    # Prompt the user to install pre-commit hooks
    response = ask_user("Would you like to install pre-commit hooks for this repository?")
    
    if response.affirmative:
        # Install pre-commit hooks
        install_result = call_tool("practices", "install_pre_commit_hooks", {
            "repo_path": "path/to/repo"  # Usually "." for current directory
        })
        
        # Inform the user about the result
        if install_result.get("success", False):
            print(install_result.get("message", "Pre-commit hooks installed successfully"))
        else:
            print(f"Error installing pre-commit hooks: {install_result.get('error', 'Unknown error')}")
```

### When to Suggest Installing Pre-commit Hooks

Suggest installing pre-commit hooks in the following scenarios:

1. When a new Git repository is created or initialized
2. When a user is setting up a new project from scratch
3. When a user mentions code quality, consistent formatting, or standards enforcement
4. When working on a project that doesn't currently have pre-commit hooks

### CLI Usage Examples

Provide these CLI examples to users when relevant:

```bash
# Install pre-commit hooks in the current directory
practices hooks install

# Install pre-commit hooks with project type specification
practices hooks install --project-type python

# Update existing pre-commit hooks
practices hooks update
```

## License Headers Usage

### Adding License Headers to New Files

When creating a new code file, automatically add a license header using the following approach:

```python
# First, create the file with its content
write_file("path/to/new_file.py", file_content)

# Then, add the license header
header_result = call_tool("practices", "add_license_header", {
    "filename": "path/to/new_file.py",
    "description": "Brief description of what this file does"  # Optional but recommended
})

# Inform the user about the result
if header_result.get("success", False):
    print(f"Added license header: {header_result.get('message', '')}")
```

### Checking for Missing License Headers

When a user is working on code quality or compliance tasks, offer to check for missing license headers:

```python
# Check a directory for missing license headers
batch_result = call_tool("practices", "process_license_headers_batch", {
    "directory": "src",
    "pattern": "*.py",
    "check_only": True,  # Only check, don't modify
    "recursive": True    # Check subdirectories
})

# Report the results
if batch_result.get("success", False):
    print(f"Checked {batch_result.get('total_files', 0)} files.")
    print(f"Missing headers: {batch_result.get('missing_headers', 0)}")
    
    # If missing headers were found, offer to add them
    if batch_result.get("missing_headers", 0) > 0:
        response = ask_user("Would you like to add license headers to the missing files?")
        
        if response.affirmative:
            # Add headers to all files
            add_result = call_tool("practices", "process_license_headers_batch", {
                "directory": "src",
                "pattern": "*.py",
                "check_only": False,  # Actually add headers
                "description": "Generated code file",  # Optional description
                "recursive": True
            })
            
            print(f"Added headers to {add_result.get('modified_files', 0)} files.")
```

### When to Add License Headers

Add license headers in the following scenarios:

1. When creating any new source code file
2. When a user is setting up a new project
3. When a user mentions license compliance or copyright
4. When migrating or refactoring code that doesn't have proper headers

### Default Header Format

The default license header format looks like:

```
filename: example.py
description: Brief description of this file's purpose

Copyright (c) 2025 Agentience.ai
Author: Troy Molander
License: MIT License - See LICENSE file for details

Version: 0.1.0
```

### CLI Usage Examples

Provide these CLI examples to users when relevant:

```bash
# Add a license header to a single file
practices header add path/to/file.py --description "Brief description"

# Verify if a file has a proper license header
practices header verify path/to/file.py

# Process multiple files in a directory
practices header batch src --pattern "*.py" --recursive

# Check multiple files without adding headers
practices header batch src --pattern "*.py" --recursive --check
```

## Integration with Other Workflows

### Version Management

When bumping versions, suggest updating license headers with the new version:

```bash
# After bumping the version
practices version bump minor

# Update license headers in the code
practices header batch src --pattern "*.py" --recursive
```

### PR Creation

When creating a PR, remind users about checking for missing license headers:

```bash
# Before creating a PR, check for missing headers
practices header batch src --pattern "*.py" --recursive --check
```

## Best Practices for AI Assistants

1. **Be Proactive**: Automatically suggest adding license headers whenever creating new files
2. **Explain the Purpose**: Briefly explain why license headers and pre-commit hooks are important
3. **Show CLI Options**: In addition to tool calls, show the equivalent CLI commands
4. **Context Awareness**: Consider the project type when suggesting specific hooks or header formats
5. **Follow Up**: After adding headers or installing hooks, explain what they do and how they help

## Troubleshooting Common Issues

### Pre-commit Hooks

- If hooks installation fails, check for pre-commit installation: `pip install pre-commit`
- If hooks don't run, suggest running `pre-commit install` manually
- For performance issues, suggest using `pre-commit run --all-files` instead of running on each commit

### License Headers

- If header template doesn't match project style, suggest creating a custom template
- If headers are rejected by pre-commit checks, ensure the format matches project requirements
- For mixing different license types, warn about potential legal complications
