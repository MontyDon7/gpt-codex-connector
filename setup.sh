#!/usr/bin/env bash
# Connects Claude Code and OpenAI Codex CLI in both directions over MCP.
set -euo pipefail

command -v claude >/dev/null || { echo "Install Claude Code first: npm i -g @anthropic-ai/claude-code" >&2; exit 1; }
command -v codex  >/dev/null || npm i -g @openai/codex

# Claude Code -> Codex: Claude can call Codex as an MCP tool (`codex mcp-server`).
claude mcp add --scope project codex -- codex mcp-server

# Codex -> Claude Code: Codex can call Claude Code as an MCP tool (`claude mcp serve`).
mkdir -p "$HOME/.codex"
grep -q '^\[mcp_servers.claude-code\]' "$HOME/.codex/config.toml" 2>/dev/null \
  || cat "$(dirname "$0")/codex-config.toml" >> "$HOME/.codex/config.toml"

echo "Done. Run 'codex login' (or set OPENAI_API_KEY) if you haven't authenticated Codex."
