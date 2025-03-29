# Practices MCP Server

![Version](https://img.shields.io/badge/version-0.2.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)

**Enhance AI interactions with standardized development practices**

The Practices MCP Server is a specialized MCP (Model Context Protocol) server that enables AI assistants like Claude to help you implement consistent development practices across your projects and teams.

## 🚀 What Does This MCP Server Do?

This server empowers AI assistants with the ability to:

- **Manage Git Branches** - Create and validate standardized branch names that follow your conventions
- **Handle Versioning** - Check and update version numbers across multiple files consistently
- **Prepare Pull Requests** - Generate standardized PR descriptions and validate readiness
- **Integrate with Tools** - Connect with GitHub and Jira to automate workflows

## 💬 Natural Language Interaction

Simply ask Claude using natural language:

> "Create a new feature branch for ticket PMS-123 about user authentication"

> "Check if our version numbers are consistent across the project"

> "Prepare a pull request for my current branch with a standardized description"

The MCP server provides Claude with the context and tools to understand and execute these requests properly according to your project's configuration.

## 🔮 How It Works

1. **AI + MCP Server Collaboration**: The Practices MCP Server provides tools and resources that Claude can utilize to help with development workflows
2. **Contextual Understanding**: The server provides Claude with your project's specific configurations and conventions
3. **Intelligent Assistance**: Claude can then interpret your natural language requests and use the appropriate MCP tools to help you follow best practices

### Behind the Scenes

While you interact through natural language, the server provides structured tools for:

- Validating branch names against configurable patterns
- Detecting branch information and issue references
- Checking version consistency across files
- Generating standardized PR descriptions
- Automating Jira and GitHub interactions

## 🛠️ Configuration

The server adapts to your project's specific needs through a `.practices.yaml` configuration file, which defines:

- Your preferred branching strategy (GitFlow, GitHub Flow, etc.)
- Version file locations and patterns
- Jira and GitHub integration settings
- PR description templates

## 🏁 Getting Started

### 1. Installation

```bash
# Install with uv (recommended)
uv tool install mcp_server_practices
```

### 2. Configure Claude

Add the server to your Claude configuration:

```json
{
  "mcpServers": {
    "practices": {
      "command": "practices",
      "args": ["server"],
      "disabled": false,
      "autoApprove": [
        "validate_branch_name",
        "get_branch_info",
        "validate_version"
      ]
    }
  }
}
```

### 3. Start Interacting

Now you can simply ask Claude to help you follow your development practices:

- "Create a feature branch for ticket PMS-123"
- "Is my current branch name valid?"
- "Check if versions are consistent across our files"
- "Bump our minor version for the new release"
- "Generate a PR description for my current branch"

## 📖 Documentation

- [User Guide](docs/user_guide.md) - Detailed usage with natural language examples
- [Configuration Guide](docs/configuration_guide.md) - Customizing the server for your projects
- [CLI Reference](docs/user_guide.md#cli-reference) - Direct command-line usage (for advanced users)
- [Developer Documentation](docs/developer_documentation.md) - Extending the server

## 🤝 Support and Contributing

Issues and pull requests are welcome! See our [contributing guidelines](docs/developer_documentation.md#contributing) for more information.

## 📄 License

MIT
