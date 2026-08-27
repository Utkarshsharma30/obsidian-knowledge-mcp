#!/usr/bin/env python3
"""
Configure ngrok with auth token and create a tunnel for MCP server
"""
from pyngrok import ngrok
from dotenv import load_dotenv
import os
import sys

# Load environment variables
load_dotenv()

ngrok_token = os.getenv("NGROK_AUTH_TOKEN")
if not ngrok_token:
    print("❌ NGROK_AUTH_TOKEN not found in .env file")
    sys.exit(1)

try:
    print("🔐 Authenticating with ngrok...")
    ngrok.set_auth_token(ngrok_token)
    print("✅ Authentication successful!\n")
    
    print("🔌 Starting ngrok tunnel for MCP server...")
    print("   Tunneling http://localhost:8000 → Public URL\n")
    
    # Open ngrok tunnel to localhost:8000
    public_url = ngrok.connect(8000, "http")
    print(f"✅ Remote URL generated:")
    mcp_url = f"{public_url.rstrip('/')}/mcp"
    print(f"   {mcp_url}\n")
    
    print(f"📋 Your remote MCP server is now accessible at:")
    print(f"   {mcp_url}\n")
    
    print("🔒 Use the MCP_AUTH_TOKEN value from .env as the Claude bearer token.\n")
    
    print(f"📝 Next Step:")
    print(f"   Copy this URL and update your Claude Desktop config with:")
    print(f"   URL: {mcp_url}\n")
    
    print(f"⏳ Tunnel is now active. Press Ctrl+C to stop.\n")
    print("📊 Dashboard: http://localhost:4040\n")
    print("="*60)
    
    # Keep tunnel alive
    ngrok_process = ngrok.get_ngrok_process()
    ngrok_process.proc.wait()
    
except KeyboardInterrupt:
    print("\n\n❌ Shutting down ngrok tunnel...")
    ngrok.kill()
    print("✅ Tunnel stopped")
except Exception as e:
    print(f"❌ Error: {e}")
    print(f"\n📝 Troubleshooting:")
    print(f"   - Check your auth token is correct")
    print(f"   - Ensure MCP server is running on localhost:8000")
    print(f"   - Check firewall settings")
    ngrok.kill()
