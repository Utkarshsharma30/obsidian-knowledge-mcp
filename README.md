# Obsidian Knowledge MCP

A read-only Obsidian-to-PostgreSQL importer and MCP server. The vault is the source of truth: ingestion reads Markdown files and never edits or deletes them.

## Architecture

`Obsidian vault -> Python parser/upsert importer -> PostgreSQL -> FastMCP tools/resources -> Claude Connector`

Documents retain their relative paths and original Markdown body. Each note becomes a `document` node; `[[links]]` become directed `related_to` edges and `document_links`. Tags, aliases, headings, and unrecognized frontmatter are retained in JSONB. Missing link targets are logged and skipped. Re-running ingestion updates records by file path and prevents duplicate edges/tags.

## Setup

Requirements: Python 3.11+, Docker Desktop, and a PostgreSQL client only if you want manual SQL inspection.

1. Copy `.env.example` to `.env`, set `POSTGRES_PASSWORD`, and set `OBSIDIAN_VAULT_PATH` to the existing vault. Do not put the vault inside this project unless you want it there.
2. Create the environment and install dependencies:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -e ".[test]"
   ```

3. Start PostgreSQL. The port is bound to localhost only:

   ```powershell
   docker compose up -d postgres
   ```

4. Import the vault:

   ```powershell
   python -m ingestion.importer
   # or: obsidian-ingest "C:\path\to\vault"
   ```

5. Verify it:

   ```powershell
   docker compose exec postgres psql -U knowledge_app -d knowledge -c "select count(*) from documents; select count(*) from edges;"
   pytest
   ```

The schema is mounted as an initialization script. For an existing volume, apply changes explicitly with `psql -f database/schema.sql`.

## Deploy on Render

This repository includes `render.yaml` for a Render Web Service and PostgreSQL database. In Render, create a new Blueprint from this repository and deploy it. Render will generate `MCP_AUTH_TOKEN`, use its `PORT`, and initialize the schema before starting the service. The default public endpoint is:

```text
https://obsidian-knowledge-mcp.onrender.com/mcp
```

If you change the service name, update `MCP_PUBLIC_URL` in the Render environment to the resulting `https://<service-name>.onrender.com` URL. Do not add `/mcp` to `MCP_PUBLIC_URL`; `/mcp` belongs only in the Claude connector URL.

The Render service cannot read a Windows or OneDrive vault. Import the vault into the Render PostgreSQL database from a machine that can access both the vault and the database, or add a separate Render-accessible storage/import job before querying it.

## MCP server

Run locally with:

```powershell
python -m mcp_server.server
```

The default endpoint is `http://127.0.0.1:8000/mcp` using Streamable HTTP. For local clients, set `MCP_TRANSPORT=stdio` and use `obsidian-mcp` as the command. The server exposes `search_knowledge`, `get_node`, `get_document`, `get_related_nodes`, `find_path`, `list_nodes`, and `search_documents`, plus `knowledge://node/{node_name}` resources. Limits are capped at 100 and SQL is parameterized.

## Claude Connector

Claude Connectors need a remotely reachable MCP endpoint, not a PostgreSQL endpoint. In Claude Settings -> Connectors, add the Render URL ending in `/mcp`, for example `https://obsidian-knowledge-mcp.onrender.com/mcp`. When prompted, use the generated `MCP_AUTH_TOKEN` as the bearer token, complete the authentication flow required by your Claude workspace, then test with `What do I have in my knowledge base about Python?`.

For production, use an identity-aware proxy (OAuth/OIDC) or mTLS rather than a static token. Do not expose port 5432. If Claude reports a connection error, check `docker compose ps`, `docker compose logs postgres`, the MCP process logs, HTTPS certificate/DNS, proxy forwarding of `/mcp`, and whether the endpoint is reachable from outside your network. Keep an authenticated health check separate from database errors and do not expose stack traces.

## Example queries

- What concepts are connected to Machine Learning?
- Find the relationship path between Python and Artificial Intelligence.
- What concepts are within two hops of RAG?
- Which documents mention both Python and Machine Learning?

## Assumptions and extension points

No vault was available in this workspace to inspect, so parsing follows standard Obsidian conventions and is covered by fixtures in `tests/test_parser.py`. Dataview-specific syntax is preserved as content. The repository layer isolates SQL from MCP, making future bidirectional sync possible without changing the MCP contract. `MCP_AUTH_TOKEN` is enforced by the Streamable HTTP server; use an identity-aware proxy (OAuth/OIDC) for stronger production access control.
