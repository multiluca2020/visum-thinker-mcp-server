#!/usr/bin/env node

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import * as fs from "fs";
import * as path from "path";
import * as fsExtra from "fs-extra";
import pdfParse from "pdf-parse";

// Storage directory for persistent state
const STORAGE_DIR = path.join(process.cwd(), '.thinking-storage');
const STATE_FILE = path.join(STORAGE_DIR, 'thinking-state.json');

// Interface for thinking state with PDF context
interface ThinkingState {
  thoughts: Array<{
    number: number;
    content: string;
    isRevision?: boolean;
    revisesThought?: number;
    branchFromThought?: number;
    branchId?: string;
  }>;
  currentThoughtNumber: number;
  totalThoughts: number;
  isComplete: boolean;
  pdfContext?: {
    filename: string;
    content: string;
    pageCount: number;
    loadedAt: Date;
  };
}

// Global thinking state
let thinkingState: ThinkingState = {
  thoughts: [],
  currentThoughtNumber: 0,
  totalThoughts: 0,
  isComplete: false,
};

// Ensure storage directory exists
async function initializeStorage() {
  await fsExtra.ensureDir(STORAGE_DIR);
}

// Save thinking state to disk
async function saveThinkingState() {
  try {
    await fsExtra.writeJson(STATE_FILE, thinkingState, { spaces: 2 });
    console.error('Thinking state saved to disk');
  } catch (error) {
    console.error('Error saving thinking state:', error);
  }
}

// Load thinking state from disk
async function loadThinkingState(): Promise<boolean> {
  try {
    if (await fsExtra.pathExists(STATE_FILE)) {
      thinkingState = await fsExtra.readJson(STATE_FILE);
      console.error('Thinking state loaded from disk');
      return true;
    }
    return false;
  } catch (error) {
    console.error('Error loading thinking state:', error);
    return false;
  }
}

// Export thinking state for transfer
async function exportThinkingState(exportPath: string) {
  try {
    await fsExtra.writeJson(exportPath, {
      ...thinkingState,
      exportedAt: new Date().toISOString(),
      serverVersion: "1.0.0"
    }, { spaces: 2 });
    return true;
  } catch (error) {
    console.error('Error exporting thinking state:', error);
    return false;
  }
}

// Import thinking state from transfer
async function importThinkingState(importPath: string): Promise<boolean> {
  try {
    if (await fsExtra.pathExists(importPath)) {
      const importedState = await fsExtra.readJson(importPath);
      // Remove export metadata
      delete importedState.exportedAt;
      delete importedState.serverVersion;
      thinkingState = importedState;
      await saveThinkingState(); // Save to local storage
      return true;
    }
    return false;
  } catch (error) {
    console.error('Error importing thinking state:', error);
    return false;
  }
}

// Create server instance
const server = new McpServer({
  name: "visum-thinker",
  version: "1.0.0",
  capabilities: {
    resources: {},
    tools: {},
  },
});

// Sequential thinking tool
server.tool(
  "sequential_thinking",
  "Facilitates a detailed, step-by-step thinking process for problem-solving and analysis",
  {
    thought: z.string().describe("The current thinking step"),
    nextThoughtNeeded: z.boolean().describe("Whether another thought step is needed"),
    thoughtNumber: z.number().int().positive().describe("Current thought number"),
    totalThoughts: z.number().int().positive().describe("Estimated total thoughts needed"),
    isRevision: z.boolean().optional().describe("Whether this revises previous thinking"),
    revisesThought: z.number().int().positive().optional().describe("Which thought is being reconsidered"),
    branchFromThought: z.number().int().positive().optional().describe("Branching point thought number"),
    branchId: z.string().optional().describe("Branch identifier"),
    needsMoreThoughts: z.boolean().optional().describe("If more thoughts are needed"),
  },
  async ({ thought, nextThoughtNeeded, thoughtNumber, totalThoughts, isRevision, revisesThought, branchFromThought, branchId, needsMoreThoughts }) => {
    try {
      // Initialize or update thinking state
      if (thoughtNumber === 1) {
        thinkingState = {
          thoughts: [],
          currentThoughtNumber: 0,
          totalThoughts,
          isComplete: false,
        };
      }

      // Add the new thought
      const newThought = {
        number: thoughtNumber,
        content: thought,
        isRevision,
        revisesThought,
        branchFromThought,
        branchId,
      };

      thinkingState.thoughts.push(newThought);
      thinkingState.currentThoughtNumber = thoughtNumber;
      
      // Update total thoughts if needed
      if (needsMoreThoughts && totalThoughts > thinkingState.totalThoughts) {
        thinkingState.totalThoughts = totalThoughts;
      }

      // Mark as complete if no more thoughts needed
      if (!nextThoughtNeeded) {
        thinkingState.isComplete = true;
      }

      // Auto-save state after each thought
      await saveThinkingState();

      // Format response
      let responseText = `**Thought ${thoughtNumber}${totalThoughts ? ` of ~${totalThoughts}` : ''}**`;
      
      if (isRevision && revisesThought) {
        responseText += ` (Revision of Thought ${revisesThought})`;
      }
      
      if (branchFromThought && branchId) {
        responseText += ` (Branch ${branchId} from Thought ${branchFromThought})`;
      }
      
      responseText += `\n\n${thought}`;

      if (thinkingState.isComplete) {
        responseText += `\n\n---\n**Thinking Complete** ✓\nTotal thoughts processed: ${thinkingState.thoughts.length}`;
      } else {
        responseText += `\n\n*→ Continuing to next thought...*`;
      }

      return {
        content: [
          {
            type: "text",
            text: responseText,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `Error in sequential thinking: ${error instanceof Error ? error.message : String(error)}`,
          },
        ],
      };
    }
  },
);

// Reset thinking state tool
server.tool(
  "reset_thinking",
  "Reset the sequential thinking state to start fresh",
  {},
  async () => {
    thinkingState = {
      thoughts: [],
      currentThoughtNumber: 0,
      totalThoughts: 0,
      isComplete: false,
    };

    return {
      content: [
        {
          type: "text",
          text: "Sequential thinking state has been reset. Ready for new thinking session.",
        },
      ],
    };
  },
);

// Get thinking summary tool
server.tool(
  "get_thinking_summary",
  "Get a summary of the current thinking session",
  {},
  async () => {
    if (thinkingState.thoughts.length === 0) {
      return {
        content: [
          {
            type: "text",
            text: "No active thinking session. Use sequential_thinking tool to start.",
          },
        ],
      };
    }

    let summary = `**Thinking Session Summary**\n\n`;
    summary += `Status: ${thinkingState.isComplete ? 'Complete ✓' : 'In Progress ⏳'}\n`;
    summary += `Thoughts: ${thinkingState.thoughts.length}\n`;
    summary += `Current: ${thinkingState.currentThoughtNumber}\n`;
    summary += `Estimated Total: ${thinkingState.totalThoughts}\n`;
    
    if (thinkingState.pdfContext) {
      summary += `PDF Context: ${thinkingState.pdfContext.filename} (${thinkingState.pdfContext.pageCount} pages)\n`;
    }
    summary += `\n`;

    summary += `**Thought History:**\n`;
    thinkingState.thoughts.forEach((thought, index) => {
      summary += `${index + 1}. Thought ${thought.number}`;
      if (thought.isRevision && thought.revisesThought) {
        summary += ` (revision of #${thought.revisesThought})`;
      }
      if (thought.branchFromThought && thought.branchId) {
        summary += ` (branch ${thought.branchId} from #${thought.branchFromThought})`;
      }
      summary += `\n   "${thought.content.substring(0, 100)}${thought.content.length > 100 ? '...' : ''}"\n\n`;
    });

    return {
      content: [
        {
          type: "text",
          text: summary,
        },
      ],
    };
  },
);

// Load PDF for analysis tool
server.tool(
  "load_pdf",
  "Load a PDF file to provide context for sequential thinking and problem solving",
  {
    filePath: z.string().describe("Absolute path to the PDF file to load"),
  },
  async ({ filePath }) => {
    try {
      // Check if file exists
      if (!fs.existsSync(filePath)) {
        return {
          content: [
            {
              type: "text",
              text: `Error: PDF file not found at path: ${filePath}`,
            },
          ],
        };
      }

      // Check if it's a PDF file
      if (!path.extname(filePath).toLowerCase().includes('pdf')) {
        return {
          content: [
            {
              type: "text",
              text: `Error: File must be a PDF. Got: ${path.extname(filePath)}`,
            },
          ],
        };
      }

      // Read and parse PDF
      const pdfBuffer = fs.readFileSync(filePath);
      const pdfData = await pdfParse(pdfBuffer);

      // Store PDF context
      thinkingState.pdfContext = {
        filename: path.basename(filePath),
        content: pdfData.text,
        pageCount: pdfData.numpages,
        loadedAt: new Date(),
      };

      const preview = pdfData.text.substring(0, 500);
      
      return {
        content: [
          {
            type: "text",
            text: `✅ **PDF Loaded Successfully**\n\n` +
                  `**File:** ${path.basename(filePath)}\n` +
                  `**Pages:** ${pdfData.numpages}\n` +
                  `**Text Length:** ${pdfData.text.length} characters\n\n` +
                  `**Preview (first 500 characters):**\n\n` +
                  `${preview}${pdfData.text.length > 500 ? '...' : ''}\n\n` +
                  `*PDF content is now available for sequential thinking analysis.*`,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `Error loading PDF: ${error instanceof Error ? error.message : String(error)}`,
          },
        ],
      };
    }
  },
);

// Analyze PDF with sequential thinking
server.tool(
  "analyze_pdf_section",
  "Analyze a specific section of the loaded PDF using sequential thinking",
  {
    query: z.string().describe("What to look for or analyze in the PDF"),
    startPage: z.number().int().positive().optional().describe("Starting page number (1-based)"),
    endPage: z.number().int().positive().optional().describe("Ending page number (1-based)"),
    searchTerms: z.array(z.string()).optional().describe("Specific terms to search for in the PDF"),
  },
  async ({ query, startPage, endPage, searchTerms }) => {
    if (!thinkingState.pdfContext) {
      return {
        content: [
          {
            type: "text",
            text: "❌ No PDF loaded. Please use the 'load_pdf' tool first to load a PDF file.",
          },
        ],
      };
    }

    try {
      let analysisText = `**PDF Analysis: ${thinkingState.pdfContext.filename}**\n\n`;
      analysisText += `**Query:** ${query}\n\n`;

      // Search for specific terms if provided
      if (searchTerms && searchTerms.length > 0) {
        analysisText += `**Search Results:**\n`;
        searchTerms.forEach(term => {
          const regex = new RegExp(term, 'gi');
          const matches = thinkingState.pdfContext!.content.match(regex);
          const count = matches ? matches.length : 0;
          analysisText += `- "${term}": ${count} occurrences\n`;
        });
        analysisText += `\n`;
      }

      // Extract relevant sections based on query
      const contentToAnalyze = thinkingState.pdfContext.content;
      const queryWords = query.toLowerCase().split(' ');
      
      // Find relevant paragraphs containing query terms
      const paragraphs = contentToAnalyze.split('\n\n');
      const relevantParagraphs = paragraphs.filter(para => 
        queryWords.some(word => para.toLowerCase().includes(word))
      );

      if (relevantParagraphs.length > 0) {
        analysisText += `**Relevant Content Found:**\n\n`;
        relevantParagraphs.slice(0, 3).forEach((para, index) => {
          analysisText += `**Section ${index + 1}:**\n${para.trim()}\n\n`;
        });
        
        if (relevantParagraphs.length > 3) {
          analysisText += `*... and ${relevantParagraphs.length - 3} more relevant sections*\n\n`;
        }
      } else {
        analysisText += `**Note:** No content directly matching your query was found. Consider broader search terms.\n\n`;
        // Provide a sample of the PDF content
        const sampleContent = contentToAnalyze.substring(0, 1000);
        analysisText += `**PDF Content Sample:**\n${sampleContent}${contentToAnalyze.length > 1000 ? '...' : ''}\n\n`;
      }

      analysisText += `**Next Steps:**\n`;
      analysisText += `Use the 'sequential_thinking' tool to analyze this content step by step.\n`;
      analysisText += `Example: Start with thought 1 about understanding the problem context.`;

      return {
        content: [
          {
            type: "text",
            text: analysisText,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `Error analyzing PDF: ${error instanceof Error ? error.message : String(error)}`,
          },
        ],
      };
    }
  },
);

// Export knowledge for transfer
server.tool(
  "export_knowledge",
  "Export the current thinking state and PDF knowledge to a file for transfer to another server",
  {
    exportPath: z.string().describe("Absolute path where to save the exported knowledge file"),
  },
  async ({ exportPath }) => {
    try {
      const success = await exportThinkingState(exportPath);
      
      if (success) {
        const stats = {
          thoughts: thinkingState.thoughts.length,
          pdfLoaded: !!thinkingState.pdfContext,
          pdfFile: thinkingState.pdfContext?.filename,
          exportedAt: new Date().toISOString()
        };

        return {
          content: [
            {
              type: "text",
              text: `✅ **Knowledge Exported Successfully**\n\n` +
                    `**Export Location:** ${exportPath}\n` +
                    `**Thoughts Exported:** ${stats.thoughts}\n` +
                    `**PDF Context:** ${stats.pdfLoaded ? `✅ ${stats.pdfFile}` : '❌ None'}\n` +
                    `**Exported At:** ${stats.exportedAt}\n\n` +
                    `*You can now transfer this file to another server and import it using the import_knowledge tool.*`,
            },
          ],
        };
      } else {
        return {
          content: [
            {
              type: "text",
              text: `❌ Failed to export knowledge to ${exportPath}`,
            },
          ],
        };
      }
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `Error exporting knowledge: ${error instanceof Error ? error.message : String(error)}`,
          },
        ],
      };
    }
  },
);

// Import knowledge from transfer
server.tool(
  "import_knowledge",
  "Import thinking state and PDF knowledge from an exported file",
  {
    importPath: z.string().describe("Absolute path to the exported knowledge file to import"),
  },
  async ({ importPath }) => {
    try {
      const success = await importThinkingState(importPath);
      
      if (success) {
        const stats = {
          thoughts: thinkingState.thoughts.length,
          pdfLoaded: !!thinkingState.pdfContext,
          pdfFile: thinkingState.pdfContext?.filename,
          pdfPages: thinkingState.pdfContext?.pageCount,
          importedAt: new Date().toISOString()
        };

        return {
          content: [
            {
              type: "text",
              text: `✅ **Knowledge Imported Successfully**\n\n` +
                    `**Import Source:** ${importPath}\n` +
                    `**Thoughts Imported:** ${stats.thoughts}\n` +
                    `**PDF Context:** ${stats.pdfLoaded ? `✅ ${stats.pdfFile} (${stats.pdfPages} pages)` : '❌ None'}\n` +
                    `**Imported At:** ${stats.importedAt}\n\n` +
                    `*Your thinking session and PDF knowledge have been restored. You can continue where you left off.*`,
            },
          ],
        };
      } else {
        return {
          content: [
            {
              type: "text",
              text: `❌ Failed to import knowledge from ${importPath}. File may not exist or be corrupted.`,
            },
          ],
        };
      }
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `Error importing knowledge: ${error instanceof Error ? error.message : String(error)}`,
          },
        ],
      };
    }
  },
);

async function main() {
  await initializeStorage();
  await loadThinkingState(); // Load saved state on startup
  
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Visum Thinker MCP Server running on stdio");
}

main().catch((error) => {
  console.error("Fatal error in main():", error);
  process.exit(1);
});
