# Version Compliance Guide

This guide provides detailed instructions for maintaining proper version compliance when using or contributing to projects that use the Practices MCP Server.

## Versioning Overview

The Practices MCP Server implements [Semantic Versioning 2.0.0](https://semver.org/) with a structured version management process. This approach ensures that version numbers communicate meaningful information about the changes they contain.

### Version Format: MAJOR.MINOR.PATCH

- **MAJOR**: Incremented for incompatible API changes
- **MINOR**: Incremented for backward-compatible new functionality
- **PATCH**: Incremented for backward-compatible bug fixes

Examples:
- `0.1.0` - Initial development version
- `0.2.0` - Added new features
- `1.0.0` - First stable release (API considered stable)
- `1.0.1` - Bug fixes to stable release
- `1.1.0` - New features added to stable release
- `2.0.0` - Breaking changes to the API

## Version Management Process

### 1. Development Phase

During the development phase, follow these guidelines:

- Create feature branches from develop: `feature/PROJ-123-feature-description`
- Create bugfix branches from develop: `bugfix/PROJ-123-bug-description`
- Create documentation branches from develop: `docs/update-guide`

**Important**: Feature and bugfix branches should never contain version changes directly. This prevents version conflicts when multiple features are being developed in parallel.

### 2. Creating Releases

When you've completed one or more features and are ready to create a release:

1. **Create a release branch** from develop:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b release/x.y.0
   ```

2. **Update the version** using bump2version:
   ```bash
   # For new features (most common):
   bump2version minor
   
   # For bug fixes only:
   bump2version patch
   
   # For breaking changes:
   bump2version major
   ```

3. **Update the CHANGELOG.md** with details of the new features and changes:
   - Follow the [Keep a Changelog](https://keepachangelog.com/) format
   - Document all significant changes, new features, deprecations, and fixes
   - Include references to issue/ticket numbers where applicable

4. **Push the release branch** to remote:
   ```bash
   git push -u origin release/x.y.0
   ```

### 3. Finalizing Releases

After the release branch has been tested and reviewed:

1. **Merge to main**:
   ```bash
   git checkout main
   git pull origin main
   git merge --no-ff release/x.y.0
   git tag v1.2.0 # Use the actual version number
   git push origin main --tags
   ```

2. **Merge back to develop**:
   ```bash
   git checkout develop
   git pull origin develop
   git merge --no-ff release/x.y.0
   git push origin develop
   ```

3. **Delete the release branch** (after it's been successfully merged):
   ```bash
   git branch -d release/x.y.0
   git push origin --delete release/x.y.0
   ```

### 4. Hotfixes

For urgent fixes to production code:

1. **Create a hotfix branch** from main:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b hotfix/x.y.z-description
   ```

2. **Bump the patch version**:
   ```bash
   bump2version patch
   ```

3. **Fix the issue** and update the CHANGELOG.md

4. **Merge to main and develop** following the same process as for release branches

## Using Version Management Tools

The Practices MCP Server provides tools to help with version management:

### Via MCP Tools

```python
from mcp.tools import call_tool

# Validate version consistency across files
result = call_tool(
    "practices", 
    "validate_version",
    {}
)

# Bump version (minor, patch, or major)
result = call_tool(
    "practices", 
    "bump_version", 
    {"type": "minor"}
)
```

### Via Command Line

```bash
# Check version consistency
practices version check

# Bump version (minor, patch, or major)
practices version bump minor
```

## Integration with CI/CD

For projects with CI/CD pipelines, consider adding automated checks:

- Validate version consistency in pull requests
- Ensure release branches include version bumps
- Automatically generate or update the changelog
- Validate that hotfix branches include patch version bumps

## Common Issues and Solutions

### Version Conflicts

**Issue**: Multiple developers working on version changes simultaneously.

**Solution**: Only perform version changes on release or hotfix branches, never on feature branches.

### Missing Version Updates

**Issue**: Forgetting to update version numbers when creating releases.

**Solution**: Add a checklist to your release process and consider using automation to verify version bumps.

### Inconsistent Versions

**Issue**: Version numbers in different files don't match.

**Solution**: Use the `validate_version` tool regularly and during CI checks.

## Conclusion

Proper version management communicates important information about your software and helps users understand the impact of updates. By following these guidelines, you'll maintain a clear and consistent versioning strategy that benefits both developers and users.

For more information, see:
- [Semantic Versioning 2.0.0](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
