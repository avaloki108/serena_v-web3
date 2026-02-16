#!/bin/bash
# Script to find existing Serena MCP configurations

echo "Searching for Serena MCP configurations..."
echo ""

# Claude Desktop configs
echo "=== Claude Desktop Configs ==="
if [ -f "$HOME/Library/Application Support/Claude/claude_desktop_config.json" ]; then
    echo "Found: ~/Library/Application Support/Claude/claude_desktop_config.json"
    grep -l "serena\|oraios/serena" "$HOME/Library/Application Support/Claude/claude_desktop_config.json" 2>/dev/null && echo "  Contains serena reference"
fi
if [ -f "$HOME/.config/Claude/claude_desktop_config.json" ]; then
    echo "Found: ~/.config/Claude/claude_desktop_config.json"
    grep -l "serena\|oraios/serena" "$HOME/.config/Claude/claude_desktop_config.json" 2>/dev/null && echo "  Contains serena reference"
fi

# Codex config
echo ""
echo "=== Codex Config ==="
if [ -f "$HOME/.codex/config.toml" ]; then
    echo "Found: ~/.codex/config.toml"
    grep -i "serena\|oraios" "$HOME/.codex/config.toml" 2>/dev/null && echo "  Contains serena reference"
fi

# Claude Code (check for .claude directory)
echo ""
echo "=== Claude Code ==="
if [ -d "$HOME/.claude" ]; then
    echo "Found: ~/.claude directory"
    find "$HOME/.claude" -name "*.json" -o -name "*.toml" -o -name "*.yaml" -o -name "*.yml" 2>/dev/null | while read f; do
        if grep -q "serena\|oraios" "$f" 2>/dev/null; then
            echo "  $f contains serena reference"
        fi
    done
fi

# General search in common config locations
echo ""
echo "=== Other Common Locations ==="
for dir in "$HOME/.config" "$HOME/.local/share" "$HOME/.cache"; do
    if [ -d "$dir" ]; then
        find "$dir" -type f \( -name "*serena*" -o -name "*mcp*" \) 2>/dev/null | head -5
    fi
done

echo ""
echo "Done!"
