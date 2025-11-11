# Setting Up Web3-Enhanced Serena MCP Server

## Quick Test

First, verify the server works:

```bash
cd /home/dok/MCP/serena_v-web3
uv run serena start-mcp-server --help
```

## Configuration Paths

**Your Web3 Serena location:** `/home/dok/MCP/serena_v-web3`  
**UV executable:** `/home/dok/.local/bin/uv`

## Setup Instructions by Client

### 1. Claude Desktop

**Config file location:**
- Linux: `~/.config/Claude/claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

**Add this configuration:**
```json
{
    "mcpServers": {
        "serena": {
            "command": "/home/dok/.local/bin/uv",
            "args": [
                "run",
                "--directory",
                "/home/dok/MCP/serena_v-web3",
                "serena",
                "start-mcp-server"
            ]
        }
    }
}
```

**After adding:**
1. Fully quit Claude Desktop (File → Exit, don't just close)
2. Restart Claude Desktop
3. You should see Serena's tools (hammer icon) in the interface

### 2. Claude Code

From your project directory:

```bash
# Remove old serena if it exists
claude mcp remove serena

# Add Web3-enhanced serena
claude mcp add serena -- /home/dok/.local/bin/uv run --directory /home/dok/MCP/serena_v-web3 serena start-mcp-server --context ide-assistant --project "$(pwd)"
```

### 3. Codex

Edit `~/.codex/config.toml` and add:

```toml
[mcp_servers.serena]
command = "/home/dok/.local/bin/uv"
args = ["run", "--directory", "/home/dok/MCP/serena_v-web3", "serena", "start-mcp-server", "--context", "codex"]
```

Then activate the project in Codex by saying:
"Activate the current dir as project using serena"

### 4. Cursor IDE

Edit `~/.config/Cursor/User/globalStorage/kilocode.kilo-code/settings/mcp_settings.json`

Add or update the serena entry:
```json
{
    "mcpServers": {
        "serena": {
            "command": "/home/dok/.local/bin/uv",
            "args": [
                "run",
                "--directory",
                "/home/dok/MCP/serena_v-web3",
                "serena",
                "start-mcp-server",
                "--context",
                "ide-assistant"
            ]
        }
    }
}
```

### 5. Alternative: Using uvx (from GitHub)

If you prefer to run directly from your GitHub repo:

```json
{
    "mcpServers": {
        "serena": {
            "command": "/home/dok/.local/bin/uvx",
            "args": [
                "--from",
                "git+https://github.com/avaloki108/serena_v-web3",
                "serena",
                "start-mcp-server"
            ]
        }
    }
}
```

## What's New in Web3 Version

Your Serena now includes:

1. **Web3 Vulnerability Hunting Tools:**
   - `analyze_smart_contract` - Analyze Solidity/Vyper contracts
   - `analyze_transaction` - Check blockchain transactions
   - `check_defi_protocol` - DeFi protocol security checks
   - `web3_threat_intelligence` - Threat intelligence integration

2. **Native Web3 Language Support:**
   - Solidity (Ethereum)
   - Vyper (Ethereum alternative)
   - Move (Aptos)
   - Sui Move (Sui blockchain)
   - Cairo (Starknet)

## Testing

After configuration, test that tools are available:

1. Start your MCP client (Claude Desktop, Claude Code, etc.)
2. Look for Serena's tools (usually shown with a hammer icon)
3. Try asking: "What Web3 tools are available?"
4. Test a Web3 tool: "Analyze the smart contract at contracts/Token.sol"

## Troubleshooting

**Server won't start:**
- Check that `uv` is installed: `which uv`
- Verify path: `ls -la /home/dok/MCP/serena_v-web3`
- Check logs in the dashboard (usually at `http://localhost:24282/dashboard/index.html`)

**Tools not showing:**
- Make sure you fully restarted the client after configuration
- Check that the paths in config are absolute (not relative)
- Verify the server is running (check dashboard URL)

**Web3 tools not available:**
- Make sure you're using this Web3-enhanced version (not original serena)
- Check that `src/serena/tools/web3_tools.py` exists
- Verify the import in `src/serena/tools/__init__.py`

## Next Steps

1. Configure your preferred MCP client using the instructions above
2. Test with a Web3 project
3. Try the Web3 vulnerability hunting tools
4. Explore the new language server support for Solidity, Move, etc.


