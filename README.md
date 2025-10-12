# Visum Thinker MCP Server

A Model Context Protocol (MCP) server that provides **PTV Visum automation** and sequential thinking capabilities for transportation planning and analysis.

## 🎯 Quick Start

**New to Visum automation?** → Start here: **[QUICKSTART_PRT_WORKFLOW.md](QUICKSTART_PRT_WORKFLOW.md)**

**AI Assistant integration?** → Read: **[CLAUDE_WORKFLOW_GUIDE.md](CLAUDE_WORKFLOW_GUIDE.md)**

**Full Documentation?** → See: **[DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)**

## ✨ New Features (2025-10-10)

### 🚗 **Interactive Visum Procedure Creation with Auto-Organization**

Create and configure PTV Visum procedures with **automatic organization in "Visum-BOT" group**:

```javascript
// 1. Create procedure → Automatic group creation + delete operation
visum_create_procedure({procedureType: "PrT_Assignment"})
// → Returns: 
//   - group_position: 577 (Visum-BOT group)
//   - delete_position: 580 (Initialize Assignment)
//   - actual_position: 581 (PrT Assignment) ⭐ Use this!

// 2. List available demand segments (numbered 1-36)
visum_list_demand_segments()

// 3. Configure with user's choice
visum_configure_dsegset({
  procedurePosition: 581,        // Use actual_position!
  segmentNumbers: "1-10"         // or filterMode: "C", etc.
})
```

**✨ Automatic Features:**
- 📦 **Group Organization:** All MCP operations in "Visum-BOT" group
- 🗑️ **Auto-Delete:** Initialize Assignment added before PrT/PuT assignments
- 🔄 **Group Reuse:** Subsequent calls add to existing group
- 📍 **Smart Positioning:** Operations added at end of group

**📖 Documentation:** See [VISUM_BOT_GROUP.md](VISUM_BOT_GROUP.md) for complete details
```

**Key Features:**
- ✅ **Automatic position detection** - No manual position tracking
- ✅ **Numbered segment selection** - Easy "1-10" notation instead of long codes
- ✅ **4 flexible input formats** - Numbers, mode filter, ALL keyword, or explicit codes
- ✅ **Interactive workflow** - AI assistants guide users through configuration
- ✅ **Complete validation** - Automatic verification of all configurations

**See [QUICKSTART_PRT_WORKFLOW.md](QUICKSTART_PRT_WORKFLOW.md) for the 3-step workflow!**

## Features

### 🚗 Visum Transportation Planning

- **Procedure Management**: Create PrT/PuT Assignment, Demand Models, Matrix Calculations
- **Demand Segments**: List and configure demand segments with numbered selection
- **Interactive Configuration**: Guide users through DSEGSET setup with 4 input formats
- **Smart Position Tracking**: Automatically track actual procedure positions
- **Complete Validation**: Verify all configurations before execution

### 🧠 Sequential Thinking

- **Step-by-step reasoning**: Break down complex problems into sequential thoughts
- **Dynamic revision**: Revise and refine thoughts as understanding deepens  
- **Branching logic**: Branch into alternative reasoning paths
- **Adaptive planning**: Adjust the total number of thoughts dynamically
- **State management**: Maintain thinking context across multiple tool calls
- **Progress tracking**: Monitor completion status and thought progression

### 📄 PDF Analysis

- **PDF Loading**: Load and analyze PDF documents for problem-solving context
- **Content Search**: Find relevant sections in PDFs based on queries and search terms
- **Persistent Storage**: Auto-save state to disk, survive server restarts
- **Knowledge Transfer**: Export/import thinking sessions between servers

## Installation

### Quick Installation

```bash
# Option 1: Install from NPM
npm install -g visum-thinker-mcp-server

# Option 2: Use with npx (no installation)
npx visum-thinker-mcp-server

# Option 3: Clone from GitHub
git clone https://github.com/yourusername/visum-thinker-mcp-server.git
cd visum-thinker-mcp-server
npm install && npm run build
```

See [INSTALLATION.md](./INSTALLATION.md) for detailed setup instructions.

## Prerequisites

- Node.js 16 or higher
- npm or yarn

## Usage

### With Claude Desktop

Add to your Claude Desktop configuration (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "visum-thinker": {
      "command": "node",
      "args": ["/absolute/path/to/sequential_thinking/build/index.js"]
    }
  }
}
```

### With VS Code

The project includes a `.vscode/mcp.json` configuration file for VS Code MCP integration.

### Direct Usage

```bash
npm run dev
```

## Tools

### `sequential_thinking`

Main tool for step-by-step reasoning process.

**Parameters:**
- `thought` (string): The current thinking step
- `nextThoughtNeeded` (boolean): Whether another thought step is needed
- `thoughtNumber` (integer): Current thought number
- `totalThoughts` (integer): Estimated total thoughts needed
- `isRevision` (boolean, optional): Whether this revises previous thinking
- `revisesThought` (integer, optional): Which thought is being reconsidered
- `branchFromThought` (integer, optional): Branching point thought number
- `branchId` (string, optional): Branch identifier
- `needsMoreThoughts` (boolean, optional): If more thoughts are needed

### `load_pdf`

Load a PDF file to provide context for analysis.

**Parameters:**
- `filePath` (string): Absolute path to the PDF file

### `analyze_pdf_section`

Analyze specific sections of the loaded PDF.

**Parameters:**
- `query` (string): What to look for or analyze in the PDF
- `startPage` (integer, optional): Starting page number (1-based)
- `endPage` (integer, optional): Ending page number (1-based)
- `searchTerms` (array of strings, optional): Specific terms to search for

### `reset_thinking`

Clears the current thinking state to start fresh.

### `get_thinking_summary`

Returns a summary of the current thinking session including PDF context if loaded.

### `export_knowledge`

Export the current thinking state and PDF knowledge to a file.

**Parameters:**
- `exportPath` (string): Absolute path where to save the exported knowledge file

### `import_knowledge`

Import thinking state and PDF knowledge from an exported file.

**Parameters:**
- `importPath` (string): Absolute path to the exported knowledge file to import

### 🚗 Visum Transportation Planning Tools

The server includes comprehensive PTV Visum integration with intelligent path learning:

- **`check_visum`**: Check Visum availability and learn custom installation paths
- **`load_visum_model`**: Load transportation models (.ver files)  
- **`run_visum_calculation`**: Execute transportation calculations and analyses
- **`get_network_statistics`**: Analyze network topology and characteristics
- **`analyze_visum_matrices`**: Examine demand and flow matrices
- **`export_visum_results`**: Export analysis results to various formats

**Key Features:**
- **🧠 Smart Path Learning**: Automatically remembers custom Visum installation paths
- **🔄 Zero Setup**: Works seamlessly after initial path discovery
- **🎯 Demo Mode**: Full testing capability without Visum installation
- **📊 Complete Analysis**: All major transportation planning workflows supported

See [VISUM-PATH-LEARNING.md](./VISUM-PATH-LEARNING.md) for detailed information about the intelligent path learning system.

## 🤖 GitHub Copilot Integration

The Sequential Thinking MCP Server includes comprehensive GitHub Copilot integration for enhanced AI-assisted development:

### 🚀 Quick Start with Copilot
1. **Server Status**: Ensure MCP server is running (`npm run dev`)
2. **Open Copilot Chat**: `Ctrl+Shift+I` in VS Code
3. **Test Integration**: Ask `@copilot List available MCP tools`
4. **Start Solving**: `@copilot Use sequential thinking to solve [your problem]`

### 🎯 Copilot Capabilities
- **🧠 Sequential Thinking**: AI-guided step-by-step problem solving
- **📄 PDF Analysis**: Intelligent document processing and analysis  
- **🚗 Transportation Planning**: Expert Visum integration and workflow automation
- **🔧 Smart Configuration**: Automatic Visum path learning and persistence
- **💡 Context-Aware Suggestions**: Code completion with domain knowledge

### 💬 Example Copilot Interactions
```
@copilot Can you use sequential thinking to analyze this transportation network problem?

@copilot Check if Visum is available and help me load a network model

@copilot Use the PDF analysis tools to extract data from this traffic report

@copilot Create a complete workflow for transportation demand analysis
```

See [COPILOT-INTEGRATION.md](./COPILOT-INTEGRATION.md) for comprehensive setup and usage guide.

## Development

### Project Structure

```
sequential_thinking/
├── src/
│   └── index.ts          # Main server implementation
├── build/                # Compiled JavaScript output
├── .vscode/
│   └── mcp.json         # VS Code MCP configuration
├── .github/
│   └── copilot-instructions.md
├── package.json
├── tsconfig.json
└── README.md
```

### Scripts

- `npm run build`: Compile TypeScript to JavaScript
- `npm run dev`: Build and run the server
- `npm test`: Run tests (placeholder)

### Debugging

The server logs to stderr for compatibility with STDIO transport. Use VS Code's debugging features or add console.error statements for debugging.

## Architecture

The server maintains a global thinking state that tracks:
- All thoughts in the current session
- Current progress and estimated completion
- Revision and branching relationships
- Session completion status

Each tool call updates this state and provides formatted responses that help users follow the thinking process.

## License

MIT
