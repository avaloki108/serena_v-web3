
● Based on my analysis of the codebase, here's how to enable different contexts and
  modes for your Serena web3 MCP server:

  Available Contexts

  Contexts (choose one - cannot be changed at runtime):
  - desktop-app (DEFAULT) - For Claude Desktop or similar apps
  - ide-assistant - For IDEs like Claude Code, Cline, Cursor
  - agent - For standalone agent mode
  - chatgpt - For ChatGPT integration
  - codex - For Codex integration
  - oaicompat-agent - For OpenAI-compatible agents

  Available Modes

  Modes (can select multiple and switch at runtime):
  - interactive (DEFAULT) - Multi-turn interactions
  - editing (DEFAULT) - All editing tools enabled
  - planning - Read-only, no editing tools
  - one-shot - Autonomous task completion
  - onboarding - For project onboarding
  - no-onboarding - Skip onboarding

  How to Configure

  1. Via MCP Client Configuration (Recommended)

  If using Claude Desktop, edit your MCP configuration file (usually at
  ~/AppData/Roaming/Claude/claude_desktop_config.json on Windows or
  ~/Library/Application Support/Claude/claude_desktop_config.json on macOS):

  {
    "mcpServers": {
      "serena-web3": {
        "command": "uv",
        "args": [
          "--directory",
          "/home/dok/MCP/serena_v-web3",
          "run",
          "serena-mcp-server",
          "--context", "ide-assistant",
          "--mode", "interactive",
          "--mode", "editing"
        ]
      }
    }
  }

  2. Via Command Line

  Start the server directly with custom context/modes:

  # Different context
  uv run serena-mcp-server --context agent --mode interactive --mode editing

  # Planning mode only (read-only)
  uv run serena-mcp-server --context desktop-app --mode interactive --mode planning

  # One-shot mode for autonomous work
  uv run serena-mcp-server --mode one-shot --mode editing

  3. Switch Modes at Runtime

  Use the switch_modes tool during a session:
  # In chat with Claude
  "Please switch to planning mode"
  # This will call the switch_modes tool

  4. Create Custom Contexts/Modes

  Create custom YAML files:

  Custom context (~/.serena/contexts/my-context.yml):
  name: my-custom-context
  description: My custom context
  prompt: |
    Custom prompt text here
  excluded_tools: []
  included_optional_tools: []

  Custom mode (~/.serena/modes/my-mode.yml):
  name: my-custom-mode
  description: My custom mode
  prompt: |
    Custom mode prompt
  excluded_tools: []
  included_optional_tools: []

  Then use: --context my-custom-context --mode my-custom-mode

  Useful Context/Mode Combinations

  - Bug bounty hunting: --context ide-assistant --mode interactive --mode editing
  - Code analysis only: --context desktop-app --mode interactive --mode planning
  - Autonomous agent: --context agent --mode one-shot --mode editing

  Note: Contexts are set at startup and cannot be changed during runtime. Modes can be
  switched using the switch_modes tool.



        "--mode", "debugging"
        "--mode", "testing"
        "--mode", "refactoring"
        "--mode", "optimizing"
        "--mode", "securing"
        "--mode", "deploying"
        "--mode", "monitoring"
