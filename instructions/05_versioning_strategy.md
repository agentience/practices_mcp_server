# Practices MCP Server - Versioning Strategy

## Overview

This document outlines the versioning strategy for the Practices MCP server project. We follow Semantic Versioning 2.0.0 to provide clear and predictable version numbers that communicate the impact of changes.

## Semantic Versioning

The Practices MCP server follows [Semantic Versioning 2.0.0](https://semver.org/):

```
MAJOR.MINOR.PATCH[-PRERELEASE]
```

- **MAJOR**: Incremented for incompatible API changes
- **MINOR**: Incremented for backward-compatible new functionality
- **PATCH**: Incremented for backward-compatible bug fixes
- **PRERELEASE**: Optional tag for pre-release versions (alpha, beta, rc)

### Version Progression

```
0.1.0      # Initial development version
0.1.1      # Bug fixes
0.2.0      # New features, no breaking changes
0.2.1-beta # Beta version with some fixes
1.0.0      # First stable release (API considered stable)
1.1.0      # New features added
2.0.0      # Breaking changes to API
```

## Versioning Rules

### Pre-1.0 Development Phase

While in the 0.x.y stage:

- **MINOR** version indicates significant new features
- **PATCH** version indicates bug fixes and minor enhancements
- API should be considered unstable and subject to change

### Post-1.0 Stable Release

After reaching 1.0.0:

- **MAJOR** version indicates breaking changes:
  - Incompatible API changes
  - Removal of deprecated functionality
  - Major architectural changes
- **MINOR** version indicates new functionality:
  - New MCP tools
  - New resource templates
  - Additional configuration options
  - Backward-compatible changes
- **PATCH** version indicates bug fixes:
  - Security patches
  - Performance improvements
  - Bug fixes without API changes

## Version Management

### Single Source of Truth

The version is maintained in the following files:

- `src/mcp_server_practices/__init__.py` - Primary source of truth
- `pyproject.toml` - For packaging

### Example Version Definition

```python
# In __init__.py
__version__ = "0.1.0"
```

```toml
# In pyproject.toml
[project]
name = "mcp-server-practices"
version = "0.1.0"
```

### Automated Version Bumping

The project uses bump2version to update versions consistently:

```bash
# Increment patch version (0.1.0 -> 0.1.1)
bump2version patch

# Increment minor version (0.1.0 -> 0.2.0)
bump2version minor

# Increment major version (0.1.0 -> 1.0.0)
bump2version major

# Create pre-release version (0.1.0 -> 0.1.0-beta)
bump2version --new-version 0.1.0-beta pre
```

## Version Bumping in the Development Workflow

Version bumping is tied to the branching strategy:

| Branch Type | When to Bump  | Version Change |
|-------------|---------------|----------------|
| feature/*   | Never         | No change      |
| bugfix/*    | Never         | No change      |
| release/*   | During creation | Minor/Major  |
| hotfix/*    | During creation | Patch        |
| docs/*      | Never         | No change      |

### Feature and Bugfix Branches

Feature and bugfix branches should never include version changes. This prevents version conflicts when multiple features are being developed in parallel.

### Release Branches

When creating a release branch:

1. Create the branch from develop: `release/X.Y.0`
2. Bump the appropriate version:
   - For new features: `bump2version minor`
   - For breaking changes: `bump2version major`
3. Update CHANGELOG.md with the new version details

### Hotfix Branches

When creating a hotfix branch:

1. Create the branch from main: `hotfix/X.Y.Z-description`
2. Bump the patch version: `bump2version patch`
3. Update CHANGELOG.md with the hotfix details

## Version Consistency Checking

The Practices MCP server includes functionality to check version consistency across all files, ensuring that the version is the same everywhere it appears. This is exposed both programmatically and via the CLI:

```bash
# Check version consistency
practices version check
```

## Changelog Management

Each version change should be documented in CHANGELOG.md following the [Keep a Changelog](https://keepachangelog.com/) format:

```markdown
# Changelog

## [Unreleased]

## [0.2.0] - 2025-03-30
### Added
- New feature X
- Support for Y configuration

### Changed
- Improved performance of Z

## [0.1.0] - 2025-03-15
### Added
- Initial implementation
```

## Version Display

Version information is available through:

- CLI: `practices version`
- API: Response headers and status endpoint
- Logs: Displayed on server startup

## Version Implementation in MCP Tools

The Practices MCP server will provide tools to help other projects implement this versioning strategy:

1. **`validate_version`**: Check version consistency across project files
2. **`bump_version`**: Bump version according to semantic versioning rules
3. **Version file templates**: Templates for different project types

By following these versioning practices in the development of the Practices MCP server itself, we demonstrate their effectiveness and provide a real-world example of the patterns the server will help enforce in other projects.
