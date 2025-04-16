#!/bin/sh
set -e
echo "Cleaning previous build artifacts..."
rm -rf dist/ build/ *.egg-info
echo "Building package..."
python -m build
WHEEL_FILE=$(ls dist/*.whl | tail -n 1)
echo "Installing package from wheel: $WHEEL_FILE"
uv tool uninstall mcp-server-practices 2>/dev/null || true
uv tool install "$WHEEL_FILE" -v
echo "Installation complete!"
