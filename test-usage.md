# Quick Usage Test

## Test the server manually:

```bash
# Build the server
npm run build

# Test basic functionality
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0.0"}}}' | node build/index.js
```

## Expected response:
You should see a JSON response with server capabilities and tools list.

## Claude Desktop Configuration:
Add this to your claude_desktop_config.json:

```json
{
  "mcpServers": {
    "visum-thinker": {
      "command": "node",
      "args": ["H:\\visum-thinker-mcp-server\\build\\index.js"],
      "env": {}
    }
  }
}
```

Then restart Claude Desktop and ask:
"Can you help me think through a problem step by step?"
