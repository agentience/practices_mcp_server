# Pre-commit Hooks and License Headers

This document outlines the implementation plan for adding pre-commit hooks and license header functionality to the Practices MCP Server.

## Overview

Pre-commit hooks and license headers are essential components of a structured development workflow:

- **Pre-commit hooks** automatically check code quality, formatting, and adherence to standards before commits
- **License headers** ensure all code files include proper licensing information

Both features were previously implemented in the Tribal project and will be migrated to the Practices MCP Server.

## Pre-commit Hooks Implementation

### Purpose

Pre-commit hooks enforce code quality standards and automatically fix common issues before they enter the codebase. They provide:

- Consistent code formatting
- Detection of common issues (trailing whitespace, large files, etc.)
- Enforcement of project-specific standards
- Automatic insertion of license headers

### Implementation Details

1. **Directory Structure**:
   ```
   src/mcp_server_practices/hooks/
   ├── __init__.py
   ├── installer.py        # Pre-commit installation functionality
   ├── templates.py        # Pre-commit template configurations
   └── integrations.py     # Integration with other modules
   ```

2. **Key Components**:
   - `installer.py`: Functions to install and update pre-commit hooks
   - `templates.py`: Default pre-commit configurations
   - `.pre-commit-config.yaml`: Base configuration file to be copied to projects

3. **Configuration**:
   Default configuration includes:
   - Standard code quality hooks (trailing-whitespace, end-of-file-fixer, etc.)
   - Linting with ruff
   - Code formatting with black
   - Type checking with mypy
   - License header insertion

4. **MCP Tools**:
   - `install_pre_commit_hooks`: Install hooks in a Git repository
   - `check_git_repo_init`: Check if a Git repository was recently initialized

5. **CLI Commands**:
   - `practices hooks install`: Install pre-commit hooks
   - `practices hooks update`: Update existing hooks
   - `practices hooks list`: List available hooks

### Git Repository Initialization Detection

The system will detect when a Git repository is initialized and prompt users to install pre-commit hooks:

1. LLM will check for Git repository initialization using the `check_git_repo_init` tool
2. If a new repository is detected, prompt the user: "Would you like to install pre-commit hooks for this repository?"
3. If the user agrees, use the `install_pre_commit_hooks` tool

## License Headers Implementation

### Purpose

License headers ensure all code files include proper licensing information, copyright notices, and metadata.

### Implementation Details

1. **Directory Structure**:
   ```
   src/mcp_server_practices/headers/
   ├── __init__.py
   ├── manager.py          # License header management
   ├── templates.py        # Header templates
   └── LICENSE_HEADER.txt  # Default header template
   ```

2. **Key Components**:
   - `manager.py`: Functions to add and verify license headers
   - `templates.py`: Header templates for different file types
   - `LICENSE_HEADER.txt`: Default header template

3. **Default Header Template**:
   ```
   filename: {filename}
   description:

   Copyright (c) 2025 Agentience.ai
   Author: Troy Molander
   License: MIT License - See LICENSE file for details

   Version: 0.1.0
   ```

4. **MCP Tools**:
   - `add_license_header`: Add license header to a file
   - `verify_license_header`: Check if a file has the proper license header

5. **CLI Commands**:
   - `practices header add <filename>`: Add header to file
   - `practices header verify <filename>`: Verify header in file
   - `practices header batch <directory>`: Process multiple files

### Integration with File Creation

The LLM will be instructed to:
1. Invoke the `add_license_header` tool after creating any new code file
2. Pass the filename as a parameter

## LLM Context Integration

### For License Headers

The following context will be provided to the LLM:

```
When creating new code files, you should:
1. Create the file with the appropriate content
2. Use the `add_license_header` tool to add a license header to the file
   Example: call_tool("practices", "add_license_header", {"filename": "path/to/file.py"})
```

### For Pre-commit Hooks

The following context will be provided to the LLM:

```
When a Git repository is initialized or detected:
1. Use the `check_git_repo_init` tool to verify repository initialization
2. Ask the user: "Would you like to install pre-commit hooks for this repository?"
3. If the user agrees, use the `install_pre_commit_hooks` tool
   Example: call_tool("practices", "install_pre_commit_hooks", {"repo_path": "path/to/repo"})
```

## Integration Plan

1. **MCP Server Integration**:
   - Register new tools in the MCP server
   - Add resource templates for headers and pre-commit configs

2. **CLI Integration**:
   - Add new command groups for hooks and headers
   - Integrate with existing commands where appropriate

3. **Documentation**:
   - Update README with new functionality
   - Create examples for both human and AI users

## Implementation Timeline

1. **Phase 1**: Create basic structure and core functionality
2. **Phase 2**: MCP Server Integration
3. **Phase 3**: CLI Implementation
4. **Phase 4**: Testing and Documentation

## Dependencies

- pre-commit
- GitPython (for repository interaction)
