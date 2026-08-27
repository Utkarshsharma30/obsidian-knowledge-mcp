#!/usr/bin/env python3
"""
Get localtunnel URL using requests
"""
import requests
import json
import time

print("Getting your remote URL...")
time.sleep(2)

try:
    # Call localtunnel API
    response = requests.get('http://localhost:54321/api/tunnels', timeout=5)
    if response.status_code == 200:
        data = response.json()
        if 'tunnels' in data and len(data['tunnels']) > 0:
            url = data['tunnels'][0]['public_url']
            print(f"\n✅ Your Remote MCP Server URL:")
            print(f"   {url}")
        else:
            print("Tunnel not ready yet, retrying...")
except Exception as e:
    print(f"Localtunnel is starting up... Please wait a moment.")
    print(f"Once it's ready, your URL will appear in the localtunnel terminal.")
