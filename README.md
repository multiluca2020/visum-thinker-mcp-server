# Visum Thinker MCP Server

A Model Context Protocol (MCP) server that provides structured sequential thinking capabilities for problem-solving and analysis. This server enables AI assistants to break down complex problems into manageable steps, revise thoughts, and explore alternative reasoning paths.

## Features

- **Step-by-step reasoning**: Break down complex problems into sequential thoughts
- **Dynamic revision**: Revise and refine thoughts as understanding deepens  
- **Branching logic**: Branch into alternative reasoning paths
- **Adaptive planning**: Adjust the total number of thoughts dynamically
- **State management**: Maintain thinking context across multiple tool calls
- **Progress tracking**: Monitor completion status and thought progression
- **PDF Analysis**: Load and analyze PDF documents for problem-solving context
- **Content Search**: Find relevant sections in PDFs based on queries and search terms
- **Persistent Storage**: Auto-save state to disk, survive server restarts
- **Knowledge Transfer**: Export/import thinking sessions between servers

## Installation

### Prerequisites

- Node.js 16 or higher
- npm or yarn

### Build the Server

```bash
npm install
npm run build
```

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
