from __future__ import annotations
import hmac
import json, logging, os
from urllib.parse import urlparse
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp.server.auth.provider import AccessToken, TokenVerifier
from mcp.server.auth.settings import AuthSettings
from mcp.server.transport_security import TransportSecuritySettings
from database import repository as db

load_dotenv(); logging.basicConfig(level=os.getenv("LOG_LEVEL","INFO")); log=logging.getLogger(__name__)

transport = os.getenv("MCP_TRANSPORT", "streamable-http")
host = os.getenv("MCP_SERVER_HOST", "0.0.0.0")
port = int(os.getenv("MCP_SERVER_PORT") or os.getenv("PORT", "8000"))
auth_token = os.getenv("MCP_AUTH_TOKEN")
public_url = os.getenv("MCP_PUBLIC_URL", f"http://{host}:{port}").rstrip("/")
public_host = urlparse(public_url).netloc

class StaticTokenVerifier(TokenVerifier):
    async def verify_token(self, token: str) -> AccessToken | None:
        if not auth_token or not hmac.compare_digest(token, auth_token):
            return None
        return AccessToken(token=token, client_id="mcp-client", scopes=[])

mcp_kwargs = {"name": "Obsidian Knowledge Base"}
if transport == "streamable-http":
    mcp_kwargs.update({
        "host": host,
        "port": port,
        "stateless_http": True,
        "json_response": True,
        "transport_security": TransportSecuritySettings(
            allowed_hosts=[f"{host}:{port}", "localhost", "localhost:8000", public_host],
        ),
    })
    if auth_token:
        mcp_kwargs.update({
            "token_verifier": StaticTokenVerifier(),
            "auth": AuthSettings(
                issuer_url=public_url,
                resource_server_url=f"{public_url}/mcp",
            ),
        })
mcp=FastMCP(**mcp_kwargs)

def output(value): return json.dumps(value, default=str, ensure_ascii=False)

@mcp.tool()
def search_knowledge(query: str, limit: int = 20) -> str:
    """Search concepts and source documents by name or full text."""
    if not query.strip(): raise ValueError("query must not be empty")
    return output(db.search_knowledge(query, limit))

@mcp.tool()
def get_node(node_name: str) -> str:
    """Get a node, tags, source document, and adjacent relationships."""
    result=db.get_node(node_name)
    return output(result or {"error":"node not found"})

@mcp.tool()
def get_document(document_id: int) -> str:
    """Retrieve an original imported Markdown document by database id."""
    result=db.get_document(document_id)
    return output(result or {"error":"document not found"})

@mcp.tool()
def get_related_nodes(node_name: str, depth: int = 1, relationship_type: str|None = None, limit: int = 20) -> str:
    """Find graph neighbors up to five hops away."""
    return output(db.related(node_name, depth, relationship_type, limit))

@mcp.tool()
def find_path(source: str, target: str, max_depth: int = 5) -> str:
    """Find one shortest relationship path between two nodes."""
    return output({"path": db.find_path(source, target, max_depth)})

@mcp.tool()
def list_nodes(limit: int = 20, offset: int = 0, type: str|None = None, tag: str|None = None) -> str:
    """List nodes with pagination and optional type/tag filters."""
    return output(db.list_nodes(limit, offset, type, tag))

@mcp.tool()
def search_documents(query: str, limit: int = 20) -> str:
    """Full-text search imported Wiki documents."""
    if not query.strip(): raise ValueError("query must not be empty")
    return output(db.search_documents(query, limit))

@mcp.resource("knowledge://node/{node_name}")
def node_resource(node_name: str) -> str:
    """Structured node resource for MCP clients."""
    return get_node(node_name)

if __name__ == "__main__":
    mcp.run(transport=transport)

def main() -> None:
    mcp.run(transport=transport)
