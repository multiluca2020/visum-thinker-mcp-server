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

2. **visum_create_procedure**: 🎯 Create Visum procedures (Assignments, Models, etc.)
   - Verified API using `visum.Procedures.Operations.AddOperation()`
   - Supports: PrT Assignment, PuT Assignment, Demand Model, Matrix Calculation
   - **📦 AUTO-ORGANIZATION:** All operations created inside "Visum-BOT" group
   - **🔄 AUTO-DELETE:** PrT/PuT Assignments automatically include Initialize Assignment (delete) operation
   - **⚠️ CRITICAL:** Returns `actual_position` (NOT requested position!)
   - ALWAYS save and use `actual_position` for subsequent operations
   - See `VISUM_PROCEDURES_API.md` and `VISUM_BOT_GROUP.md` for complete documentation

3. **visum_list_demand_segments**: 📋 List demand segments for configuration
   - Shows all available PrT demand segments with numbering (1-36)
   - Can filter by mode (C, H, etc.)
   - Returns numbered list for easy user selection
   - **ALWAYS use this before configuring DSEGSET** - Ask user which segments to include
   - Show the 4 selection options to the user

4. **visum_configure_dsegset**: ⚙️ Configure demand segments on procedures
   - Applies DSEGSET to PrT Assignment procedures
   - **⚠️ CRITICAL:** Use `actual_position` from visum_create_procedure!
   - Supports 4 input formats:
     * Numeric selection: `segmentNumbers: "1-10,15,20"`
     * Mode filter: `filterMode: "C"` or `"H"`
     * ALL keyword: `dsegset: "ALL"` (use filterMode instead if fails)
     * Explicit codes: `dsegset: "C_CORRETTA_AM,C_CORRETTA_IP1,..."`
   - See `WORKFLOW_PRT_ASSIGNMENT.md` for complete workflow

5. **project_list_available_layouts**: 📂 List available Global Layout files
   - Shows all .lay files in project directory
   - Returns filename, size (MB), and full path
   - **ALWAYS use this before loading a layout** - Ask user which to load
   - See `GLOBAL_LAYOUTS_WORKFLOW.md` for complete documentation

6. **project_load_global_layout**: 🎨 Load Global Layout into project
   - Loads .lay file into active Visum project
   - Use filename from `project_list_available_layouts`
   - Can use just filename (searches project dir) or full path
   - **⚠️ CORRECT API:** Uses `visum.LoadGlobalLayout(file_path)`
   - Loading time: ~1-6 seconds depending on file size
   - See `GLOBAL_LAYOUTS_WORKFLOW.md` for usage examples

7. **project_export_visible_tables**: 📊 Export GUI-visible tables to CSV
   - **COMPLETE SOLUTION** - Exports ONLY tables visible in Global Layout
   - Parses .lay XML file to extract exact table/column definitions
   - **Supports sub-attributes (formula columns):** VEHKMTRAVPRT_DSEG(C_CORRETTA_FERIALE,AP)
   - Maintains exact column order as displayed to user
   - CSV format: semicolon delimiter, UTF-8 encoding, no empty lines
   - Filename: `{projectName}_{tableName}.csv`
   - **WORKFLOW:** List layouts → User selects → Export tables
   - **Performance:** 227K rows × 29 cols in ~6.7 seconds
   - See `TABLE_EXPORT_WORKFLOW.md` for complete guide
   - Standalone script: `export-all-tables-from-layout.py`


## 🎨 Global Layouts Workflow

**Interactive Pattern:**
1. **List Layouts** → Show available .lay files to user
2. **User Selects** → User chooses which layout to load
3. **Load Layout** → Activate selected layout in Visum

**Example:**
```javascript
// Step 1: List
response = project_list_available_layouts({projectId: "S000009result_1278407893"})
// Shows: tabelle_report.lay (11.36 MB)

// Step 2: User selects "tabelle_report.lay"

// Step 3: Load
project_load_global_layout({
  projectId: "S000009result_1278407893",
  layoutFile: "tabelle_report.lay"  // or full path
})
```

**Key Discovery:** 
- ✅ Correct method: `visum.LoadGlobalLayout(path)`
- ❌ Don't use: `project_list_global_layouts` (deprecated - API not accessible)
- ❌ Don't use: `visum.IO.LoadGlobalLayout()` (doesn't exist)
- ❌ Don't use: `visum.Graphics.AssociateGlobalLayoutFile()` (visum.Graphics doesn't exist)

See `GLOBAL_LAYOUTS_WORKFLOW.md` for complete guide!

## 🤖 Interactive Workflow for AI Assistants

**⚠️ IMPORTANT:** When creating and configuring PrT procedures, follow this pattern:

1. **Create Procedure** → Save `actual_position` from response
2. **List Segments** → Show numbered list (1-36) to user
3. **Ask User** → Present 4 options: "all", "mode filter", "numbers", or "codes"
4. **Configure** → Use saved `actual_position` + user's choice

**See `CLAUDE_WORKFLOW_GUIDE.md` for complete interactive workflow patterns!**

### Quick Example:
```javascript
// Step 1: Create
response = visum_create_procedure({procedureType: "PrT_Assignment"})
position = response.actual_position  // e.g., 580

// Step 2: List & Ask
visum_list_demand_segments()
// Show to user: "Found 36 segments. Options: 1) all, 2) mode C/H, 3) numbers 1-10, 4) codes"

// Step 3: Configure with user's choice
visum_configure_dsegset({
  procedurePosition: position,  // ⚠️ Use actual_position!
  segmentNumbers: "1-10"        // or filterMode: "C", etc.
})
```

5. **sequential_thinking**: Main tool for step-by-step reasoning with support for:
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
