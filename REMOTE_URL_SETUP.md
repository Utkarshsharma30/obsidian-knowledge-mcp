# Remote MCP Server URL Setup

Your MCP server is currently running on `http://localhost:8000`

## Option 1: Manual ngrok Setup (Recommended)

### Step 1: Create ngrok Account
1. Go to https://ngrok.com and sign up (free account)
2. Verify your email

### Step 2: Get Your Auth Token
1. Log in to https://dashboard.ngrok.com/auth/your-authtoken
2. Copy your auth token (looks like: `2abc_xyz123...`)

### Step 3: Download ngrok Manually
1. Go to https://ngrok.com/download
2. Download for Windows (64-bit recommended)
3. Extract the `ngrok.exe` file to: `D:\MCP_connection\tools\` (create if doesn't exist)

### Step 4: Add Auth Token
Open PowerShell and run:
```powershell
D:\MCP_connection\tools\ngrok.exe authtoken YOUR_AUTH_TOKEN_HERE
```

### Step 5: Start the Tunnel
Open a new PowerShell terminal and run:
```powershell
D:\MCP_connection\tools\ngrok.exe http 8000
```

This will show your public URL, something like:
```
Forwarding  https://abc123def456.ngrok.io -> http://localhost:8000
```

The MCP endpoint is the forwarding URL with `/mcp` appended:
`https://abc123def456.ngrok.io/mcp`

---

## Option 2: Use the Remote URL in Claude Connector

Once you have your ngrok URL from above, update your Claude Desktop connector:

Claude's web custom connector is configured in Claude Settings -> Connectors -> Add custom connector.
Use the HTTPS MCP URL ending in `/mcp`, then provide the `MCP_AUTH_TOKEN` value from `.env` when Claude asks for bearer authentication.
Do not paste `.env` into Claude or commit the token.

---

## Option 3: Alternative Tunneling Services

If ngrok doesn't work, try:
- **Cloudflare Tunnel** (free, no account needed for CLI)
  - https://developers.cloudflare.com/cloudflare-one/connections/connect-applications/
  
- **Localtunnel** (simple, free)
  - https://localtunnel.me
  - `npx localtunnel --port 8000`

- **SSH Reverse Tunnel** (if you have a remote server)
  - `ssh -R 8000:localhost:8000 user@your-server.com`

---

## Configuration File Location
📁 `%APPDATA%\Claude\claude_desktop_config.json`

## Connection Values
- **Local URL**: http://localhost:8000/mcp
- **Remote URL**: `https://your-ngrok-url.ngrok.io/mcp`
- **Bearer token**: the value of `MCP_AUTH_TOKEN` in `.env`
- **Server name**: Obsidian Knowledge Base

## Testing Your Connection
Once configured, test in Claude Desktop:
1. Restart Claude Desktop
2. Try asking a question that uses your MCP tools
3. Check if your knowledge base is accessible
