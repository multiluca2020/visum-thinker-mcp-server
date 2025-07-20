# Multi-Client MCP Server Configuration

## Overview
This configuration allows both GitHub Copilot and Claude Desktop to access the Sequential Thinking MCP Server simultaneously.

## Server Architecture
- **Single Server Instance**: One MCP server handles multiple clients
- **Shared State**: Sequential thinking state and Visum configuration shared across clients
- **Concurrent Access**: Both AIs can use all 14 tools simultaneously

## Client Configurations

### GitHub Copilot (VS Code)
**Location**: `.vscode/settings.json` and `.vscode/mcp.json`
```json
{
  "mcp.servers": {
    "visum-thinker": {
      "command": "node",
      "args": ["build/index.js"],
      "cwd": "${workspaceFolder}",
      "env": {"NODE_ENV": "development"}
    }
  }
}
```

### Claude Desktop
**Location**: `claude_desktop_config.json` (copy to Claude config directory)
```json
{
  "mcpServers": {
    "visum-thinker": {
      "command": "node", 
      "args": ["H:/visum-thinker-mcp-server/build/index.js"],
      "cwd": "H:/visum-thinker-mcp-server",
      "env": {"NODE_ENV": "production"}
    }
  }
}
```

## Usage Scenarios

### Collaborative Analysis
- **GitHub Copilot**: Code generation and development assistance
- **Claude Desktop**: Complex problem analysis and documentation
- **Shared Context**: Both AIs access the same thinking sessions and Visum data

### Workflow Examples

#### 1. Transportation Planning Project
1. **Claude**: Use sequential thinking to plan analysis approach
2. **GitHub Copilot**: Generate code for data processing
3. **Both**: Access Visum integration for calculations
4. **Claude**: Document findings and create reports

#### 2. PDF Analysis Workflow  
1. **Claude**: Load and analyze PDF documents
2. **GitHub Copilot**: Create code to process extracted data
3. **Both**: Use sequential thinking for systematic analysis

## Installation Steps

### For Claude Desktop:
1. Copy `claude_desktop_config.json` to:
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. Restart Claude Desktop

3. Test connection by asking: "Can you list the available MCP tools?"

### For GitHub Copilot:
- Already configured in VS Code
- Test with: `@copilot Are you connected to the MCP server?`

## Benefits of Dual Access

### Enhanced Capabilities
- **Complementary Strengths**: Each AI excels in different areas
- **Workflow Flexibility**: Switch between AIs based on task needs
- **Shared Intelligence**: Both learn from the same context and data

### Use Case Examples
- **Claude**: Strategic planning and complex analysis
- **GitHub Copilot**: Code completion and technical implementation
- **Both**: Transportation planning and problem-solving workflows

## Troubleshooting

### Server Management
- **Check Status**: `Get-Process -Name "node"`
- **Restart Server**: `npm run dev` 
- **Verify Tools**: Both clients should see all 14 tools

### Common Issues
- **Port Conflicts**: MCP uses stdio, so no port conflicts
- **State Synchronization**: Both clients share the same server state
- **Path Issues**: Ensure absolute paths in configurations

---

**Ready for Dual AI Access!** 🚀
Both GitHub Copilot and Claude Desktop can now access your enhanced MCP server with all transportation planning and sequential thinking capabilities.
