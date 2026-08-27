#!/usr/bin/env python3
"""
Create a public tunnel using Cloudflare Tunnel (no binary download needed)
Alternative: Use localtunnel service
"""
import subprocess
import sys
import os

print("=" * 60)
print("🌍 Creating Remote URL for MCP Server")
print("=" * 60)

# Try Method 1: Cloudflare Tunnel
print("\n📡 Attempting Method 1: Cloudflare Tunnel...")
try:
    result = subprocess.run(
        ["npx", "wrangler", "tunnel", "--url", "http://localhost:8000"],
        capture_output=True,
        text=True,
        timeout=30
    )
    if result.returncode == 0:
        print("✅ Cloudflare Tunnel started!")
        print(result.stdout)
        sys.exit(0)
except Exception as e:
    print(f"⚠️  Cloudflare method failed: {e}")

# Try Method 2: Localtunnel
print("\n📡 Attempting Method 2: Localtunnel (simpler)...")
print("Installing localtunnel...")
try:
    subprocess.run(["npm", "install", "-g", "localtunnel"], 
                   capture_output=True, check=True, timeout=60)
    print("\n✅ Starting localtunnel...\n")
    print("Your remote URL will appear below:")
    print("-" * 60)
    
    subprocess.run(["lt", "--port", "8000", "--open", "false"],
                   timeout=None)
    
except KeyboardInterrupt:
    print("\n\n❌ Tunnel stopped")
    sys.exit(0)
except Exception as e:
    print(f"❌ Localtunnel failed: {e}")
    print("\n📝 Alternative: Use ngrok from command line directly")
    print("   Run this in PowerShell:")
    print("   d:\\ngrok.exe http 8000")
    sys.exit(1)
