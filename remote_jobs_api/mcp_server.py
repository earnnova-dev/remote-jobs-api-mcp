"""Remote Jobs API — Model Context Protocol (MCP) server.

Give any MCP client (Claude Desktop, Cursor, Claude Code, OpenRouter agents,
or any MCP-compatible harness) access to live, normalized remote-job data
across 5 boards — one endpoint, one schema, skill fit-score. No API key.

Stdlib-only HTTP client (urllib); the MCP transport is the official `mcp`
Python SDK. Run with:

    remote-jobs-api-mcp          # stdio transport (what MCP clients launch)
or:
    python -m remote_jobs_api.mcp_server

The base URL defaults to the public, keyless instance
https://remote-jobs-api.tten.no and can be overridden with the
RJA_BASE_URL environment variable.
"""
from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:  # pragma: no cover - MCP SDK not installed in this env
    FastMCP = None

BASE_URL = os.environ.get("RJA_BASE_URL", "https://remote-jobs-api.tten.no").rstrip("/")
UA = "Mozilla/5.0 (X11; Linux x86_464) AppleWebKit/537.36 (compatible; RJA-MCP/1.0)"


def _get(path, params=None, timeout=25):
    url = BASE_URL + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def _trim(job):
    """Lean per-job shape for LLM consumption (drop the long description)."""
    return {
        "title": job.get("title"),
        "company": job.get("company"),
        "location": job.get("location"),
        "salary": job.get("salary"),
        "salary_min": job.get("salary_min"),
        "salary_max": job.get("salary_max"),
        "salary_period": job.get("salary_period"),
        "fit_score": job.get("fit_score"),
        "category": job.get("category"),
        "source": job.get("source"),
        "published": job.get("published"),
        "url": job.get("url"),
    }


# ---- pure helpers (importable + unit-testable without the MCP SDK) ----

def search_jobs(skills=None, min_salary=None, limit=10):
    """Query live remote jobs. skills = comma-separated keywords; min_salary =
    floor on the parsed annual salary (salary_min). Returns {count, jobs:[...]}."""
    params = {"limit": max(1, min(100, int(limit)))}
    if skills:
        params["skills"] = skills
    if min_salary is not None and int(min_salary) > 0:
        params["min_salary"] = int(min_salary)
    d = _get("/v1/jobs", params)
    return {"count": d.get("count"), "jobs": [_trim(j) for j in d.get("jobs", [])]}


def market_stats():
    """Live feed health: status, source list, and how many jobs are live now."""
    return _get("/health")


def salary_band(skills=None, limit=100):
    """Compute a live salary band (min / median / max of parsed annual floors)
    for an optional skill filter, so agents can answer 'what does X pay?'.
    Only jobs that disclose a numeric salary_min are included."""
    params = {"limit": max(1, min(100, int(limit)))}
    if skills:
        params["skills"] = skills
    d = _get("/v1/jobs", params)
    jobs = d.get("jobs", [])
    floors = sorted(int(j["salary_min"]) for j in jobs if j.get("salary_min"))
    if not floors:
        return {"n_with_salary": 0, "min": None, "median": None, "max": None,
                "note": "no live jobs disclose a numeric salary for this filter"}
    med = floors[len(floors) // 2]
    return {"n_with_salary": len(floors), "min": floors[0], "median": med, "max": floors[-1]}


# ---- MCP transport ----

def build_mcp():
    """Construct the FastMCP server with the RJA tools, or None if the MCP SDK
    is not installed (the pure helpers above still work)."""
    if FastMCP is None:
        return None
    mcp = FastMCP("remote-jobs-api")

    @mcp.tool()
    def search_jobs_tool(skills: str = "", min_salary: int = 0, limit: int = 10) -> str:
        """Search live normalized remote jobs across 5 boards. `skills` is a
        comma-separated skill filter (e.g. "python,backend"); `min_salary` is a
        floor on the parsed annual salary. Returns JSON {count, jobs:[...]}.
        No API key required."""
        s = (skills or "").strip()
        return json.dumps(search_jobs(s or None, min_salary or None, limit))

    @mcp.tool()
    def market_stats_tool() -> str:
        """Return the live feed health: status, the 5 source boards, and the
        number of jobs live right now. Returns JSON from the public keyless API."""
        return json.dumps(market_stats())

    @mcp.tool()
    def salary_band_tool(skills: str = "", limit: int = 100) -> str:
        """Compute a live salary band (min / median / max annual floor) for an
        optional skill filter so you can answer 'what does <role> pay remote?'.
        Only jobs disclosing a numeric salary are counted. Returns JSON."""
        s = (skills or "").strip()
        return json.dumps(salary_band(s or None, limit))

    return mcp


def main() -> None:
    server = build_mcp()
    if server is None:
        raise SystemExit(
            "The `mcp` Python package is required for the MCP server. "
            "Install it with: pip install mcp  (or: uv add mcp)"
        )
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
