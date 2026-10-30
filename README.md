# gpt-codex-connector

Connects Claude Code and OpenAI Codex CLI in both directions via MCP.

- **Claude Code -> Codex**: `.mcp.json` registers `codex mcp-server`.
- **Codex -> Claude Code**: `codex-config.toml` registers `claude mcp serve`.

## Setup

    ./setup.sh
    codex login        # or export OPENAI_API_KEY

Then in Claude Code, ask it to use the `codex` tool; in Codex, use the `claude-code` tool.
