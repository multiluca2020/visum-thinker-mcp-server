# Installation Guide

## 🚀 Quick Installation

### Option 1: Install from NPM (Recommended)
```bash
# Install globally
npm install -g visum-thinker-mcp-server

# Run anywhere
visum-thinker
```

### Option 2: Install from GitHub
```bash
# Clone the repository
git clone https://github.com/yourusername/visum-thinker-mcp-server.git
cd visum-thinker-mcp-server

# Install dependencies
npm install

# Build the server
npm run build

# Run the server
npm run dev
```

### Option 3: Use with npx (No Installation)
```bash
# Run directly without installation
npx visum-thinker-mcp-server
```

## 🎯 Claude Desktop Integration

Add to your `claude_desktop_config.json`:

### Using Global Installation
```json
{
  "mcpServers": {
    "visum-thinker": {
      "command": "visum-thinker"
    }
  }
}
```

### Using NPX
```json
{
  "mcpServers": {
    "visum-thinker": {
      "command": "npx",
      "args": ["-y", "visum-thinker-mcp-server"]
    }
  }
}
```

### Using Local Installation
```json
{
  "mcpServers": {
    "visum-thinker": {
      "command": "node",
      "args": ["/path/to/visum-thinker-mcp-server/build/index.js"]
    }
  }
}
```

## 🖥️ VS Code Integration

If using VS Code with MCP support, create `.vscode/mcp.json`:

```json
{
  "servers": {
    "visum-thinker": {
      "type": "stdio",
      "command": "visum-thinker"
    }
  }
}
```

## 🔧 Development Setup

For contributing or customizing:

```bash
# Fork and clone the repo
git clone https://github.com/yourusername/visum-thinker-mcp-server.git
cd visum-thinker-mcp-server

# Install dependencies
npm install

# Start development mode (auto-rebuild)
npm run dev

# Build for production
npm run build
```

## 📋 System Requirements

- **Node.js:** v16.0.0 or higher
- **npm:** v7.0.0 or higher
- **Operating System:** macOS, Linux, Windows
- **Memory:** Minimum 512MB RAM
- **Storage:** 100MB free space

## 🛠️ Troubleshooting

### Common Issues

1. **Permission denied on macOS/Linux:**
   ```bash
   sudo npm install -g visum-thinker-mcp-server
   ```

2. **Node version too old:**
   ```bash
   # Update Node.js
   # Visit: https://nodejs.org/
   ```

3. **Build fails:**
   ```bash
   # Clear npm cache
   npm cache clean --force
   
   # Reinstall dependencies
   rm -rf node_modules package-lock.json
   npm install
   npm run build
   ```

4. **Server won't start:**
   ```bash
   # Check Node.js version
   node --version  # Should be v16+
   
   # Test installation
   visum-thinker --help
   ```

## 🔄 Updates

### Check for Updates
```bash
npm outdated -g visum-thinker-mcp-server
```

### Update to Latest Version
```bash
npm update -g visum-thinker-mcp-server
```

### Update from GitHub
```bash
cd visum-thinker-mcp-server
git pull origin main
npm install
npm run build
```

## 🌟 First Run

After installation:

1. **Start the server:** `visum-thinker` or `npm run dev`
2. **Load a PDF:** Use the `load_pdf` tool
3. **Start thinking:** Use the `sequential_thinking` tool
4. **Explore features:** Check out the documentation files

## 📚 Documentation

- **README.md** - Main project overview
- **KNOWLEDGE_TRANSFER.md** - Knowledge persistence and transfer
- **PDF_WORKFLOW.md** - PDF analysis workflows  
- **MULTIPLE_SERVERS.md** - Running multiple specialized servers
- **EXAMPLES.md** - Usage examples and test scenarios

## 🤝 Support

- **Issues:** [GitHub Issues](https://github.com/yourusername/visum-thinker-mcp-server/issues)
- **Documentation:** Check the included markdown files
- **Community:** Discussions tab on GitHub

Happy thinking! 🧠✨
