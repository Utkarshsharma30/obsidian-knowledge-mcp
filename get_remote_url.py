#!/usr/bin/env python3
"""
Generate a remote URL for your MCP server using ngrok
"""
from pyngrok import ngrok
import os
import time

# Set ngrok auth token if you have one (optional)
# ngrok.set_auth_token("your_ngrok_auth_token")

print("🔌 Starting ngrok tunnel for MCP server...")
print("Tunneling http://localhost:8000 → Public URL\n")

try:
    # Open ngrok tunnel to localhost:8000
    public_url = ngrok.connect(8000, "http")
    print(f"✅ Remote URL for your MCP server:")
    print(f"   {public_url}\n")
    
    print(f"📋 Use this URL in Claude Desktop connector configuration:")
    print(f"   Replace 'http://localhost:8000' with: {public_url}\n")
    
    print(f"🔒 Keep your authentication token secure:")
    print("   Bearer Token: configure MCP_AUTH_TOKEN in your environment\n")
    
    print("⏳ Tunnel is now active. Press Ctrl+C to stop.\n")
    print("Dashboard: http://localhost:4040")
    
    # Keep tunnel alive
    ngrok_process = ngrok.get_ngrok_process()
    ngrok_process.proc.wait()
    
except KeyboardInterrupt:
    print("\n\n❌ Shutting down ngrok tunnel...")
    ngrok.kill()
    print("✅ Tunnel stopped")
except Exception as e:
    print(f"❌ Error: {e}")
    print("\n📝 To fix ngrok issues:")
    print("   1. Sign up at https://ngrok.com (free account)")
    print("   2. Get your auth token from https://dashboard.ngrok.com/auth/your-authtoken")
    print("   3. Run: ngrok authtoken <your_token>")
    ngrok.kill()
