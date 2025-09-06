#!/bin/bash

# GitHub Switcher - Quick update and install script
# This ensures changes are properly picked up by uv tool install

echo "🔄 Updating GitHub Switcher installation..."

# Uninstall current version
echo "📤 Uninstalling current version..."
uv tool uninstall github-switcher 2>/dev/null || echo "   (no version installed)"

# Clean build
echo "🏗️  Building fresh package..."
rm -rf dist/
uv build

# Install from built wheel  
echo "📥 Installing from wheel..."
uv tool install dist/github_switcher-0.1.0-py3-none-any.whl

echo "✅ Installation complete!"
echo "🚀 Run 'ghsw create' to test"