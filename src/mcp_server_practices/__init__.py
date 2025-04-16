"""MCP Server for Development Practices."""

__version__ = "0.5.0"

# Add alias for hyphenated command name
mcp_server_practices_main = lambda: __import__('mcp_server_practices.cli').cli.main()
