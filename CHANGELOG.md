# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.0] - 2025-03-29
### Added
- Unified CLI and Server Commands (PMS-27)
  - Made server mode the default behavior
  - Added CLI functionality via 'cli' subcommand
  - Updated branch creation parsing logic for CLI
  - Updated documentation with new usage examples
  - Fixed branch tool parameter to use 'ticket_id' instead of 'identifier' (PMS-26)

### Fixed
- Added command-line argument to control logging level, default to ERROR to suppress INFO logs (PMS-21)
- Fixed BaseModel errors in MCP tools by using keyword-only arguments (PMS-22)
- Removed console logging functionality for silent operation (PMS-24)

## [0.3.0] - 2025-03-28
### Changed
- Migrated build system from setuptools to hatchling (PMS-14)
- Updated Python requirement from 3.9+ to 3.12+
- Replaced mcp-python-sdk dependency with mcp[cli]>=1.3.0
- Added uv configuration and lock file
- Updated documentation for the new build system and dependencies
- Refactored MCP server to use FastMCP implementation (PMS-15)

### Added
- Fixed MCP dependency resolution (PMS-16)
- Implemented modernized MCP server with decorator pattern (PMS-17)
- Added system instructions for LLM context (PMS-18)
- Enhanced Jira integration with issue linking capabilities (PMS-7)
- Expanded Jira workflow instructions (PMS-19)

## [0.2.0] - 2025-03-27
### Added
- Branch management functionality (PMS-3)
  - Branch validation with configurable patterns
  - Branch creation with standardized naming
  - Jira integration for issue status updates
  - CLI commands for branch operations
- Version management functionality (PMS-4)
  - Version validation with consistency checking
  - Version bumping with semantic versioning support
  - Integration with bump2version tool
  - CLI commands for version operations
- Pre-commit hooks and license headers (PMS-12)
  - Pre-commit hooks installation and management
  - License header management with templates
  - CLI commands for hooks and headers
  - Tool definitions for self-documentation
- PR preparation tools (PMS-5)
  - PR templates for different branch types
  - PR description generation from branch info
  - PR workflow with readiness checks
  - GitHub integration for PR submission

### Changed
- Enhanced project documentation with best practices for maintaining clean Git history
- Updated branching strategy documentation
- Improved error handling and feedback messages

## [0.1.0] - 2025-03-24
### Added
- Initial project scaffolding (PMS-1)
  - Basic directory structure
  - Configuration files
  - Development environment setup
  - CI/CD workflows setup
- Initial MCP server framework
