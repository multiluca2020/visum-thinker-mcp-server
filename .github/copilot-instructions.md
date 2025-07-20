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

1. **sequential_thinking**: Main tool for step-by-step reasoning with support for:
   - Sequential thought progression
   - Thought revision capabilities
   - Branching reasoning paths
   - Dynamic adjustment of thought count
   
2. **load_pdf**: Load PDF documents for analysis
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
