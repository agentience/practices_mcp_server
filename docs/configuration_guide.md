# Practices MCP Server - Configuration Guide

This guide explains how to configure the Practices MCP Server for your specific project needs.

## Table of Contents

- [Configuration File](#configuration-file)
- [Project Types](#project-types)
- [Branching Strategies](#branching-strategies)
- [Version Management](#version-management)
- [Jira Integration](#jira-integration)
- [GitHub Integration](#github-integration)
- [Pre-commit Hooks](#pre-commit-hooks)
- [License Headers](#license-headers)
- [Configuration Examples](#configuration-examples)

## Configuration File

The Practices MCP Server is configured through a `.practices.yaml` file in your project root. This file defines your project's development practices and integrations.

### Basic Structure

```yaml
# .practices.yaml
project_type: python
branching_strategy: gitflow
workflow_mode: solo  # "solo" or "team"
main_branch: main
develop_branch: develop
jira_project: PMS
```

### Creating the Configuration

You can create a default configuration with:

```bash
practices init
```

This will create a `.practices.yaml` file with sensible defaults based on your project type.

## Project Types

The `project_type` setting determines language-specific behaviors:

```yaml
project_type: python  # Options: python, javascript, java, go, etc.
```

Each project type has defaults for:
- Version file locations and patterns
- File types for license headers
- Pre-commit hook configurations
- PR description templates

## Branching Strategies

The `branching_strategy` setting defines branch naming and workflow:

```yaml
branching_strategy: gitflow  # Options: gitflow, github-flow, trunk
```

### GitFlow Strategy

```yaml
branching_strategy: gitflow
main_branch: main
develop_branch: develop
branches:
  feature:
    pattern: "feature/([A-Z]+-\d+)-(.+)"
    base: develop
    version_bump: null
  bugfix:
    pattern: "bugfix/([A-Z]+-\d+)-(.+)"
    base: develop
    version_bump: null
  hotfix:
    pattern: "hotfix/(\d+\.\d+\.\d+)-(.+)"
    base: main
    version_bump: patch
  release:
    pattern: "release/(\d+\.\d+\.\d+)"
    base: develop
    version_bump: minor
  docs:
    pattern: "docs/(.+)"
    base: develop
    version_bump: null
```

### GitHub Flow Strategy

```yaml
branching_strategy: github-flow
main_branch: main
branches:
  feature:
    pattern: "feature/([A-Z]+-\d+)-(.+)"
    base: main
    version_bump: null
  bugfix:
    pattern: "bugfix/([A-Z]+-\d+)-(.+)"
    base: main
    version_bump: null
  hotfix:
    pattern: "hotfix/(\d+\.\d+\.\d+)-(.+)"
    base: main
    version_bump: patch
  docs:
    pattern: "docs/(.+)"
    base: main
    version_bump: null
```

### Trunk-Based Strategy

```yaml
branching_strategy: trunk
main_branch: main
branches:
  feature:
    pattern: "feature/([A-Z]+-\d+)-(.+)"
    base: main
    version_bump: null
  bugfix:
    pattern: "bugfix/([A-Z]+-\d+)-(.+)"
    base: main
    version_bump: null
  release:
    pattern: "release/(\d+\.\d+\.\d+)"
    base: main
    version_bump: minor
```

### Custom Patterns

You can customize branch patterns to match your team's conventions:

```yaml
branches:
  feature:
    pattern: "feat/([A-Z]+-\d+)/(.+)"  # Custom pattern
    base: develop
```

## Workflow Modes

The `workflow_mode` setting defines how branches are handled:

```yaml
workflow_mode: solo  # Options: "solo" or "team"
```

- **Solo Mode**: For single developers or small teams
  - Branch directly from and merge directly to base branches
  - After merging, delete both local and remote feature branches

- **Team Mode**: For larger teams or more formal processes
  - Create pull requests for all merges
  - After PR approval and merge, delete both local and remote feature branches

## Version Management

Configure version file patterns for your project:

```yaml
version:
  files:
    - path: src/package/__init__.py
      pattern: __version__ = "(\d+\.\d+\.\d+)"
    - path: package.json
      pattern: "\"version\": \"(\d+\.\d+\.\d+)\""
  use_bumpversion: true
  changelog: CHANGELOG.md
```

### Version Files

Each version file entry requires:
- `path`: Relative path to the file
- `pattern`: Regex pattern to match the version string (with capture group)

### Bumpversion Integration

If you use [bump2version](https://github.com/c4urself/bump2version), enable it with:

```yaml
version:
  use_bumpversion: true
```

This will use your `.bumpversion.cfg` configuration when bumping versions.

## Jira Integration

Configure Jira integration:

```yaml
jira:
  project: PMS
  server: jira.example.com
  transitions:
    in_progress: "In Progress"
    done: "Done"
```

## GitHub Integration

Configure GitHub integration:

```yaml
github:
  owner: Agentience
  repo: mcp_server_practices
  base_branches:
    develop: true
    main: true
```

## Pre-commit Hooks

Configure pre-commit hooks:

```yaml
pre_commit:
  hooks:
    - id: black
      name: black
      description: "Format Python code with Black"
      entry: black
      language: python
      types: [python]
    - id: isort
      name: isort
      description: "Sort Python imports"
      entry: isort
      language: python
      types: [python]
```

## License Headers

Configure license headers:

```yaml
license_headers:
  template: |
    Copyright (c) 2025 Agentience
    
    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files.
  file_types:
    - extension: .py
      prefix: "# "
    - extension: .js
      prefix: "// "
    - extension: .java
      start: "/*"
      prefix: " * "
      end: " */"
```

## Configuration Examples

### Python Project Example

```yaml
project_type: python
branching_strategy: gitflow
workflow_mode: team
main_branch: main
develop_branch: develop
jira_project: PMS

version:
  files:
    - path: src/mypackage/__init__.py
      pattern: __version__ = "(\d+\.\d+\.\d+)"
    - path: setup.py
      pattern: version="(\d+\.\d+\.\d+)"
  use_bumpversion: true
  changelog: CHANGELOG.md

jira:
  project: PMS
  transitions:
    in_progress: "In Progress"
    done: "Done"

github:
  owner: Agentience
  repo: my_python_project
  base_branches:
    develop: true
    main: true

pre_commit:
  hooks:
    - id: black
    - id: isort
    - id: flake8
    - id: mypy
```

### JavaScript Project Example

```yaml
project_type: javascript
branching_strategy: github-flow
workflow_mode: team
main_branch: main
jira_project: WEB

version:
  files:
    - path: package.json
      pattern: "\"version\": \"(\d+\.\d+\.\d+)\""
  changelog: CHANGELOG.md

jira:
  project: WEB
  transitions:
    in_progress: "In Progress"
    done: "Done"

github:
  owner: Agentience
  repo: my_js_project
  base_branches:
    main: true

pre_commit:
  hooks:
    - id: prettier
    - id: eslint
```

### Java Project Example

```yaml
project_type: java
branching_strategy: gitflow
workflow_mode: team
main_branch: main
develop_branch: develop
jira_project: API

version:
  files:
    - path: pom.xml
      pattern: "<version>(\d+\.\d+\.\d+)</version>"
  changelog: CHANGELOG.md

jira:
  project: API
  transitions:
    in_progress: "In Progress"
    done: "Done"

github:
  owner: Agentience
  repo: my_java_project
  base_branches:
    develop: true
    main: true

pre_commit:
  hooks:
    - id: checkstyle
    - id: spotless
```

## Advanced Configuration

### Custom Templates

You can define custom templates for PR descriptions:

```yaml
templates:
  pr:
    feature: |
      # {ticket_id}: {description}
      
      ## Summary
      This PR implements {description} functionality ({ticket_id}).
      
      ## Changes
      -
      
      ## Testing
      -
      
      ## Related Issues
      - {ticket_id}: {ticket_description}
```

### Environment-Specific Settings

You can use environment variables in your configuration:

```yaml
jira:
  project: ${JIRA_PROJECT}
  server: ${JIRA_SERVER}
```

These will be replaced with the corresponding environment variables at runtime.
