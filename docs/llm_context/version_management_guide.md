# Version Management Guide for AI Assistants

This document provides instructions for AI assistants on how to manage versions when working with projects that use the Practices MCP Server. When helping users with projects that follow semantic versioning through the practices MCP server, you should adhere to these guidelines.

## When to Apply Version Changes

As an AI assistant, you should help users manage versions at appropriate times:

1. **DO NOT** suggest version changes when working on:
   - Individual feature implementations (`feature/*` branches)
   - Bug fixes (`bugfix/*` branches)
   - Documentation updates (`docs/*` branches)

2. **DO** suggest version changes when:
   - Creating release branches (`release/*`)
   - Creating hotfix branches (`hotfix/*`)
   - Finalizing a set of features for release
   - Merging a series of completed features to develop

## How to Apply Version Changes

When it's appropriate to update the version, follow these steps:

### 1. Determine the Appropriate Version Change

Apply Semantic Versioning principles:

- **MAJOR**: For incompatible API changes
  ```bash
  bump2version major
  ```

- **MINOR**: For backward-compatible new functionality (most common)
  ```bash
  bump2version minor
  ```

- **PATCH**: For backward-compatible bug fixes
  ```bash
  bump2version patch
  ```

### 2. Suggest Creating a Release Branch

```bash
git checkout develop
git pull origin develop
git checkout -b release/x.y.0  # Use the new version number
```

### 3. Update the Version

```bash
bump2version minor  # Or major/patch as appropriate
```

### 4. Create or Update CHANGELOG.md

If a CHANGELOG.md file doesn't exist, recommend creating one with this structure:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [x.y.z] - YYYY-MM-DD
### Added
- Feature 1 (PROJ-123)
- Feature 2 (PROJ-124)

### Changed
- Change 1
- Change 2

### Fixed
- Fix 1 (PROJ-125)
- Fix 2 (PROJ-126)
```

### 5. Validate Version Consistency

```bash
practices version check
```

Or use the MCP tool:

```python
call_tool("practices", "validate_version", {})
```

## Example Scenarios and Responses

### Scenario 1: User asks for help implementing a feature

**User**: I need help implementing the authentication feature for my project.

**Appropriate Response**: 
Help implement the feature. DO NOT suggest version changes.

### Scenario 2: User asks about finalizing several features for release

**User**: I've completed several features and want to prepare for release. What should I do?

**Appropriate Response**:
"I recommend creating a release branch and bumping the version number to reflect the new features. Here are the steps:

1. Create a release branch:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b release/0.2.0  # Adjust version as needed
   ```

2. Bump the version number:
   ```bash
   bump2version minor  # For new features
   ```

3. Update the CHANGELOG.md with details of your new features

4. Commit and push the changes:
   ```bash
   git add .
   git commit -m "Bump version to 0.2.0 for release"
   git push -u origin release/0.2.0
   ```"

### Scenario 3: User asks about fixing a critical bug in production

**User**: We found a critical bug in production. How do I fix it?

**Appropriate Response**:
"For a critical bug in production, I recommend creating a hotfix branch and bumping the patch version. Here's how:

1. Create a hotfix branch from main:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b hotfix/1.0.1-fix-critical-bug  # Adjust version as needed
   ```

2. Bump the patch version:
   ```bash
   bump2version patch
   ```

3. Fix the bug and update the CHANGELOG.md

4. Commit and push the changes
5. After testing, merge to both main and develop"

## Additional Guidelines

1. Always check if the project uses the Practices MCP Server for version management
2. Validate that bumping the version is necessary before suggesting it
3. Ensure version numbers are consistent across all files
4. Remember that version changes should reflect the nature of the changes:
   - New features → minor version bump
   - Bug fixes → patch version bump
   - Breaking changes → major version bump
5. Encourage users to create meaningful CHANGELOG entries

## Common Pitfalls to Avoid

1. Suggesting version bumps for every small change
2. Forgetting to update the CHANGELOG
3. Bumping the wrong version component
4. Not validating version consistency across files
5. Suggesting version changes on feature or bugfix branches

By following these guidelines, you'll help users maintain proper version management in their projects.
