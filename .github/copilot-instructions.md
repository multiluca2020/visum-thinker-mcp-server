<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Sequential Thinking MCP Server

This is an MCP (Model Context Protocol) server project that provides sequential thinking capabilities for structured problem-solving and analysis.

## Project Guidelines

- This is a TypeScript MCP server using the @modelcontextprotocol/sdk
- Use ES modules (type: "module" in package.json)
- Follow MCP server patterns for tool registration and execution
- Log to stderr, never to stdout (for STDIO transport compatibility)
- Use Zod for input validation schemas

## MCP Server Information

You can find more info and examples at https://modelcontextprotocol.io/llms-full.txt

## Tools Provided

1. **project_open**: 🚀 **DEFAULT TOOL** for opening Visum projects
   - ALWAYS use this tool when asked to open/load/launch any Visum project
   - Creates dedicated TCP server for ultra-fast communication
   - Supports large projects (Campoleone: 166K nodes, 409K links)
   - Provides immediate MCP response with background project loading

2. **sequential_thinking**: Main tool for step-by-step reasoning with support for:
   - Sequential thought progression
   - Thought revision capabilities
   - Branching reasoning paths
   - Dynamic adjustment of thought count
   
3. **load_pdf**: Load PDF documents for analysis
   - Extract text content from PDF files
   - Provide metadata (pages, text length)
   - Store PDF context for subsequent analysis
   
3. **analyze_pdf_section**: Analyze specific sections of loaded PDFs
   - Query-based content extraction
   - Search term highlighting
   - Relevant paragraph identification
   
4. **reset_thinking**: Clears the thinking state to start fresh

5. **get_thinking_summary**: Provides overview of current thinking session

6. **export_knowledge**: Export complete thinking state and PDF knowledge for transfer
   - Backup thinking sessions
   - Transfer between servers
   - Share collaborative analysis

7. **import_knowledge**: Import previously exported knowledge
   - Restore thinking sessions
   - Continue analysis from backups
   - Load shared analysis work

## Key Features

- Maintains thinking state across tool calls
- Supports revision of previous thoughts
- Enables branching into alternative reasoning paths
- Tracks progress and completion status
- Provides detailed formatting for thought presentation
- **PDF document analysis and processing**
- **Context-aware problem solving with document content**
- **Search and extraction from PDF sources**
- **Persistent storage with auto-save functionality**
- **Knowledge transfer between servers and sessions**
- **Complete backup and restore capabilities**

## Visum PRT Assignment Workflow

### When to Use `list-prt-demand-segments.js`

**ALWAYS run this script when:**

1. **User asks to list/show PRT modes or demand segments**
   - "Quali sono i modi PRT disponibili?"
   - "Mostrami i demand segments per PRT"
   - "Elenca i transport systems di tipo PRT"

2. **Before creating a PrT Assignment procedure**
   - User requests: "Crea una procedura di assegnazione al trasporto privato"
   - You need to configure DSEGSET attribute
   - Need to ask user which segments to include

3. **Interactive segment selection**
   - After showing available segments, ask user:
     - "Vuoi includere tutti i segments o solo alcuni?"
     - "Quali modi PRT vuoi includere? (C per Car, H per HGV, ...)"
   - Use the DSEGSET output based on user's choice

### Script Output Structure

```javascript
{
  prt_tsys: [{code: "CAR", name: "Car"}, {code: "HGV", name: "HGV"}],
  mode_mapping: {
    "C": {mode_name: "Car", tsys_code: "CAR"},
    "H": {mode_name: "HGV", tsys_code: "HGV"}
  },
  segments_by_mode: {
    "C": ["C_CORRETTA_AM", "C_CORRETTA_IP1", ...],
    "H": ["H_INIZIALE_AM", ...]
  },
  dsegset: "C_CORRETTA_AM,C_CORRETTA_IP1,...",  // All segments comma-separated
  total: 36
}
```

### Usage Pattern

```javascript
// 1. Run script to list available PRT segments
node list-prt-demand-segments.js

// 2. Show results to user and ask for selection
// 3. Based on user choice:
//    - All modes: use complete dsegset
//    - Specific mode (e.g., "C"): filter segments_by_mode["C"]
//    - Multiple modes: combine segments from selected modes

// 4. Configure PrT Assignment with chosen DSEGSET
```

### Important Notes

- **Modes and TSys are NOT directly linked** in some Visum projects
- Connection is via **name matching** (Mode "Car" → TSys "Car")
- **Demand segments** have MODE attribute linking them to Modes
- **Transport Systems** have TYPE attribute (TYPE="PRT" for PRT systems)

See `LIST_PRT_SEGMENTS_GUIDE.md` for complete documentation.
