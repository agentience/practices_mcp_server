# Practices MCP Server - Resource Templates

## Overview

Resource templates are a key feature of the Practices MCP server, providing standardized templates for branching strategies, PR descriptions, configuration files, and other project artifacts. This document outlines the types of resource templates available, their structure, and how they are used.

## Resource Types

The Practices MCP server provides the following types of resource templates:

1. **Branching Strategy Templates**: Templates for different branching strategies
2. **PR Templates**: Templates for Pull Request descriptions
3. **Version File Templates**: Templates for version files in different languages
4. **Configuration Templates**: Templates for `.practices.yaml` configuration

## Template Structure

### MCP Resource URIs

Resources are accessed through the MCP protocol using URIs with the following pattern:

```
practices://templates/{template_type}/{template_name}
```

For example:

- `practices://templates/branching-strategy/gitflow`
- `practices://templates/pr/feature`
- `practices://templates/version-files/python`

### Template Format

Templates can have different formats depending on their purpose:

- Markdown (`.md`) for PR templates and documentation
- YAML (`.yaml`) for configuration templates
- Various formats for version files (Python, JavaScript, etc.)

## Branching Strategy Templates

### GitFlow Template

```yaml
# practices://templates/branching-strategy/gitflow
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
  release:
    pattern: "release/(\d+\.\d+\.\d+)(?:-(.+))?"
    base: develop
    target: [main, develop]
    version_bump: minor
  hotfix:
    pattern: "hotfix/(\d+\.\d+\.\d+)-(.+)"
    base: main
    target: [main, develop]
    version_bump: patch
  docs:
    pattern: "docs/(.+)"
    base: develop
    version_bump: null
```

### GitHub Flow Template

```yaml
# practices://templates/branching-strategy/github-flow
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

### Trunk-Based Template

```yaml
# practices://templates/branching-strategy/trunk
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
    target: [main]
    version_bump: minor
```

## PR Templates

### Feature PR Template

```markdown
# practices://templates/pr/feature

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

### Bugfix PR Template

```markdown
# practices://templates/pr/bugfix

# {ticket_id}: Fix {description}

## Summary
This PR fixes an issue with {description} ({ticket_id}).

## Problem
Describe the issue that was occurring.

## Solution
Explain how the fix resolves the issue.

## Testing
-

## Related Issues
- {ticket_id}: {ticket_description}
```

### Release PR Template

```markdown
# practices://templates/pr/release

# Release {version}

## Summary
This PR prepares release version {version}.

## Changes since last release
{changelog}

## Testing
-

## Deployment checklist
- [ ] Version numbers updated
- [ ] Changelog updated
- [ ] Documentation updated
- [ ] Tests passing
```

### Hotfix PR Template

```markdown
# practices://templates/pr/hotfix

# Hotfix {version}: {description}

## Summary
This is a critical hotfix for version {version} addressing {description}.

## Problem
Describe the critical issue that needed immediate fixing.

## Solution
Explain how the hotfix resolves the issue.

## Testing
-

## Deployment checklist
- [ ] Version number incremented
- [ ] Changelog updated
- [ ] Tests passing
```

## Version File Templates

### Python Version File Template

```python
# practices://templates/version-files/python/__init__.py
"""Package initialization."""

__version__ = "0.1.0"
```

### JavaScript Version File Template

```json
# practices://templates/version-files/javascript/package.json
{
  "name": "project-name",
  "version": "0.1.0",
  "description": "Project description",
  "main": "index.js",
  "scripts": {
    "test": "echo \"Error: no test specified\" && exit 1"
  },
  "author": "",
  "license": "MIT"
}
```

### Java Version File Template

```xml
# practices://templates/version-files/java/pom.xml
<project>
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>project-name</artifactId>
    <version>0.1.0</version>
</project>
```

## Configuration Templates

### Python Project Template

```yaml
# practices://templates/configuration/python
project_type: python
branching_strategy: gitflow
main_branch: main
develop_branch: develop

version:
  files:
    - path: src/{package}/__init__.py
      pattern: __version__ = "(\d+\.\d+\.\d+)"
    - path: pyproject.toml
      pattern: version = "(\d+\.\d+\.\d+)"
  use_bumpversion: true
  bumpversion_config: .bumpversion.cfg

# Branch configuration follows GitFlow template
```

### JavaScript Project Template

```yaml
# practices://templates/configuration/javascript
project_type: javascript
branching_strategy: github-flow
main_branch: main

version:
  files:
    - path: package.json
      pattern: "\"version\": \"(\d+\.\d+\.\d+)\""

# Branch configuration follows GitHub Flow template
```

## Template Customization

Templates can be customized in several ways:

1. **Local Templates**:
   Create a `.practices/templates/` directory in your project to store custom templates.

2. **Template Inheritance**:
   Extend built-in templates with custom modifications:

```yaml
# Extend the GitFlow template with custom settings
_extends: practices://templates/branching-strategy/gitflow

# Override specific settings
main_branch: master  # Use 'master' instead of 'main'
```

3. **Template Variables**:
   Templates can include variables that will be replaced when used:

```markdown
# PR template with variables
# {ticket_id}: {description}

## Summary
This PR implements {description} functionality ({ticket_id}).
```

## Template API

### Loading Templates

```python
# Load a template by URI
template = load_template("practices://templates/pr/feature")

# Load a template with variables
template_with_vars = load_template("practices://templates/pr/feature", {
    "ticket_id": "PMS-3",
    "description": "branch validation"
})
```

### Creating Custom Templates

```python
# Create a custom template
create_template(
    template_type="pr",
    template_name="custom-feature",
    content="# Custom Feature PR Template\n..."
)
```

### Listing Available Templates

```python
# List all templates of a specific type
branching_templates = list_templates("branching-strategy")
```

## Template Usage in MCP Tools

The resource templates are used by various MCP tools:

1. **`create_branch`**: Uses branching strategy templates to create correctly formatted branches
2. **`prepare_pr`**: Uses PR templates to generate PR descriptions
3. **`generate_default_config`**: Uses configuration templates for new projects

## Template Storage

Templates are stored and loaded from several locations:

1. **Built-in templates**: Packaged with the Practices MCP server
2. **User templates**: Stored in `~/.practices/templates/`
3. **Project templates**: Stored in `.practices/templates/` in the project directory

Templates are loaded with the following precedence:
1. Project-specific templates
2. User templates
3. Built-in templates

This allows for customization at both the user and project level, while providing sensible defaults.
