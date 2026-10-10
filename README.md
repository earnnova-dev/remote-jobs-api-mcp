# Remote Jobs API — MCP Server

A [Model Context Protocol](https://modelcontextprotocol.io) server that gives any
MCP client — Claude Desktop, Cursor, Claude Code, OpenRouter agents, or any
MCP-compatible harness — access to **live, normalized remote-job data** across
multiple job boards through the keyless [Remote Jobs API](https://remote-jobs-api.tten.no).

One endpoint, one schema. No API key. No account.

## What it gives your agent

Three tools, all backed by live data:

- **`search_jobs_tool`** — search live remote jobs by skill keywords and/or a
  minimum-salary floor. Returns a lean per-job shape (title, company, location,
  salary, category, source, link).
- **`market_stats_tool`** — live feed health: which boards are up and how many
  jobs are live right now.
- **`salary_band_tool`** — a live salary band (min / median / max) for a skill
  filter, so your agent can answer *"what does a senior backend engineer pay
  remote?"* from real listings.

## Install

```bash
pip install remote-jobs-api-mcp
```

Or from this repo:

```bash
pip install .
```

## Run

```bash
remote-jobs-api-mcp          # stdio transport (what MCP clients launch)
# or
python -m remote_jobs_api.mcp_server
```

No environment variables or volumes required. The base URL defaults to the
public, keyless instance `https://remote-jobs-api.tten.no` and can be
overridden with the `RJA_BASE_URL` environment variable.

## Claude Desktop / Claude Code

Add to `~/.claude/claude_desktop_config.json` (or your MCP client config):

```json
{
  "mcpServers": {
    "remote-jobs-api": {
      "command": "remote-jobs-api-mcp",
      "env": { "RJA_BASE_URL": "https://remote-jobs-api.tten.no" }
    }
  }
}
```

## Docker

```bash
docker build -t remote-jobs-api-mcp .
docker run -i --rm remote-jobs-api-mcp   # speaks MCP over stdio
```

## Notes

This package is the **client** only: a thin, stdlib-only HTTP wrapper around the
public API. It contains no secrets, credentials, or backend logic. The data
source is the free, keyless tier of the Remote Jobs API.

## License

MIT
