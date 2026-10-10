# Dockerfile for the Remote Jobs API MCP server (stdio transport).
#
# Glama's MCP-directory auto-crawl (and any stdio MCP client that builds this
# image) needs the MCP *stdio* server as the entrypoint — NOT an HTTP server.
# A stdio MCP container speaks JSON-RPC over stdin/stdout; running anything
# else makes Glama's introspection (initialize / tools/list) fail.
#
# Build:  docker build -t remote-jobs-api-mcp .
# Run:    docker run -i --rm remote-jobs-api-mcp   # speaks MCP over stdio
#
# The server is keyless and calls the public live API by default (override
# with RJA_BASE_URL). No env vars or volumes required.
FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY remote_jobs_api ./remote_jobs_api
RUN pip install --no-cache-dir .

ENV RJA_BASE_URL=https://remote-jobs-api.tten.no \
    PYTHONUNBUFFERED=1

# The stdio MCP entrypoint (remote_jobs_api.mcp_server:main).
CMD ["remote-jobs-api-mcp"]
