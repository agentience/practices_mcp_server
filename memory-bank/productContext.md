# Practices MCP Server - Product Context

## Why This Project Exists

The Practices MCP Server exists to solve the challenge of maintaining consistent development practices across projects and teams. Initially, these practices were implemented within the Tribal project, but as the need for standardization grew, it became clear that these practices deserved their own dedicated server that could be used across multiple projects.

By extracting and standardizing these practices into a separate MCP server, we achieve:

1. **Reusability**: The same practices can be applied to any project, not just Tribal
2. **Focus**: Each MCP server can focus on its core responsibility
3. **Maintainability**: Updates to practices can be made in one place
4. **Extensibility**: New practices and templates can be added without modifying other systems

## Problems It Solves

### 1. Inconsistent Development Practices

Different developers and teams may follow different branching strategies, versioning approaches, and PR workflows. This leads to:
- Confusion and friction when collaborating
- Merge conflicts and integration issues
- Inconsistent version histories
- Difficulty tracking changes across the project

### 2. Manual Workflow Management

Without automation, developers must:
- Manually create properly formatted branches
- Remember to update versions in multiple files
- Generate PR descriptions with the right format
- Manually update Jira tickets during development
- Remember workflow rules for each project

### 3. Context Switching

Developers often need to switch between multiple tools:
- Git for version control
- Jira for issue tracking
- GitHub for PRs and code review
- Documentation for workflow rules
This context switching reduces productivity and increases the chance of errors.

### 4. Knowledge Silos

Without standardized practices:
- New team members take longer to onboard
- Knowledge about workflows is tribal (ironically)
- Best practices may vary between projects
- Changes to workflows are hard to communicate

## How It Should Work

The Practices MCP Server implements a modular, configuration-driven approach:

1. **Configuration File**: Each project has a `.practices.yaml` file defining its specific practices
2. **Default Templates**: Common practices are provided as templates for quick adoption
3. **MCP Tools**: Tools for branch validation, version management, PR creation, etc.
4. **Integration Adapters**: Connect with GitHub, Jira, and other services
5. **Command Line Interface**: Direct developer access to the tools

The server works by:

1. Loading the project's configuration
2. Providing tools that adapt to that configuration
3. Enforcing rules defined in the configuration
4. Automating workflows between systems (Git, GitHub, Jira)
5. Generating standardized artifacts (branches, PRs, etc.)

## User Experience Goals

### For Developers

1. **Simplicity**: Make it easy to follow best practices without memorizing rules
2. **Guidance**: Provide clear instructions and feedback when rules are violated
3. **Automation**: Reduce manual steps in common workflows
4. **Transparency**: Make it clear what actions are being performed
5. **Integration**: Seamlessly connect with existing tools and services

### For Teams

1. **Consistency**: Ensure all team members follow the same practices
2. **Visibility**: Make it easy to see the current state of development
3. **Flexibility**: Allow customization of practices for team preferences
4. **Adoption**: Make it easy to adopt and enforce standard practices
5. **Evolution**: Allow practices to evolve over time with minimal disruption

### For AI Assistants

1. **Context**: Provide clear context about project practices
2. **Tools**: Expose tools for assisting with development workflows
3. **Validation**: Validate actions against project rules
4. **Guidance**: Help guide users through complex workflows
5. **Integration**: Connect with other MCP servers for complete workflows

## Key User Journeys

### 1. Creating a Feature Branch

1. Developer needs to implement a new feature
2. They use the `create_branch` tool to create a properly formatted branch
3. The tool transitions the Jira ticket to "In Progress"
4. Development proceeds with clear connection to the ticket

### 2. Preparing a Release

1. Developer needs to prepare a release
2. They use the `create_branch` tool to create a release branch
3. The `bump_version` tool updates version numbers in all files
4. The `prepare_pr` tool creates a PR with standardized description
5. After approval, the release is merged and tagged

### 3. Enforcing Practices in CI/CD

1. CI pipeline runs on PR creation
2. It uses the `validate_branch_name` tool to check branch format
3. It uses the `validate_version` tool to check version consistency
4. It rejects PRs that don't follow the project's practices

### 4. Onboarding a New Developer

1. New developer joins the team
2. They use the `generate_default_config` tool to create a config file
3. The configuration provides clear rules for development
4. The tools guide them through the correct processes

## Success Metrics

1. **Adoption Rate**: Percentage of projects using the server
2. **Error Reduction**: Fewer workflow errors and inconsistencies
3. **Time Savings**: Reduced time spent on manual workflow tasks
4. **Compliance**: Higher compliance with development practices
5. **Satisfaction**: Developer satisfaction with the workflow tools
