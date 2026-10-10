"""Remote Jobs API — public MCP client package.

This is the MCP *client* only: a thin, keyless stdlib HTTP wrapper around the
public Remote Jobs API at https://remote-jobs-api.tten.no. It contains no
secrets, no credentials, and no backend logic — it simply calls the public API
so MCP clients (Claude, Cursor, Claude Code, any MCP harness) can use live
remote-job data.
"""
__version__ = "1.0.0"
