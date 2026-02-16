# Starting Serena Web3 MCP Server

## Quick Start Test

To test the server locally:

```bash
cd /home/dok/MCP/serena_v-web3
uv run serena start-mcp-server
```

## Replacing Original Serena MCP Configurations

### 1. Claude Desktop

Edit: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)
or `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
or `~/.config/Claude/claude_desktop_config.json` (Linux)

**Replace this:**
```json
{
    "mcpServers": {
        "serena": {
            "command": "/abs/path/to/uvx",
            "args": ["--from", "git+https://github.com/oraios/serena", "serena", "start-mcp-server"]
        }
    }
}
```

**With this (local installation):**
```json
{
    "mcpServers": {
        "serena": {
            "command": "/home/dok/.local/bin/uv",
            "args": ["run", "--directory", "/home/dok/MCP/serena_v-web3", "serena", "start-mcp-server"]
        }
    }
}
```

**Or with uvx (from your repo):**
```json
{
    "mcpServers": {
        "serena": {
            "command": "/home/dok/.local/bin/uvx",
            "args": ["--from", "git+https://github.com/avaloki108/serena_v-web3", "serena", "start-mcp-server"]
        }
    }
}
```

### 2. Claude Code

From your project directory, remove old serena and add new one:

```bash
# Remove old serena
claude mcp remove serena

# Add Web3-enhanced serena
claude mcp add serena -- /home/dok/.local/bin/uv run --directory /home/dok/MCP/serena_v-web3 serena start-mcp-server --context ide-assistant --project "$(pwd)"
```

### 3. Codex

Edit: `~/.codex/config.toml`

**Replace:**
```toml
[mcp_servers.serena]
command = "uvx"
args = ["--from", "git+https://github.com/oraios/serena", "serena", "start-mcp-server", "--context", "codex"]
```

**With:**
```toml
[mcp_servers.serena]
command = "/home/dok/.local/bin/uv"
args = ["run", "--directory", "/home/dok/MCP/serena_v-web3", "serena", "start-mcp-server", "--context", "codex"]
```

### 4. Other MCP Clients (Cursor, Cline, etc.)

Update the MCP server configuration to point to:
- Command: `/home/dok/.local/bin/uv`
- Args: `["run", "--directory", "/home/dok/MCP/serena_v-web3", "serena", "start-mcp-server"]`

## Testing the Server

Test that it works:
```bash
cd /home/dok/MCP/serena_v-web3
uv run serena start-mcp-server --help
```

The server should start and show available options.
