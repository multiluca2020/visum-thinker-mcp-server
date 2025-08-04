#!/usr/bin/env node

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import * as fs from "fs";
import * as path from "path";
import * as fsExtra from "fs-extra";
import { VisumController } from "./visum-controller.js";

// Dynamic import for pdf-parse to avoid startup issues
let pdfParse: any = null;

async function initializePdfParser() {
  try {
    if (!pdfParse) {
      pdfParse = (await import("pdf-parse")).default;
    }
    return pdfParse;
  } catch (error) {
    console.error("Warning: PDF parsing unavailable:", error instanceof Error ? error.message : String(error));
    return null;
  }
}

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
    processingInfo?: {
      processedPages?: string;
      chunksUsed?: number;
      chunkSize?: number;
      summaryMode?: boolean;
      comprehensiveKnowledge?: boolean;
      files?: Array<{
        filename: string;
        pages: number;
        sizeMB: number;
      }>;
    };
  };
}

// Global thinking state
let thinkingState: ThinkingState = {
  thoughts: [],
  currentThoughtNumber: 0,
  totalThoughts: 0,
  isComplete: false,
};

// Initialize Visum controller
const visumController = new VisumController();

// Ensure storage directory exists
async function initializeStorage() {
  await fsExtra.ensureDir(STORAGE_DIR);
}

// Save thinking state to disk
async function saveThinkingState() {
  try {
    fs.writeFileSync(STATE_FILE, JSON.stringify(thinkingState, null, 2));
    console.error('Thinking state saved to disk');
  } catch (error) {
    console.error('Error saving thinking state:', error);
  }
}

// Load thinking state from disk
async function loadThinkingState(): Promise<boolean> {
  try {
    if (fs.existsSync(STATE_FILE)) {
      thinkingState = JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
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
    const exportData = {
      ...thinkingState,
      exportedAt: new Date().toISOString(),
      serverVersion: "1.0.0"
    };
    fs.writeFileSync(exportPath, JSON.stringify(exportData, null, 2));
    return true;
  } catch (error) {
    console.error('Error exporting thinking state:', error);
    return false;
  }
}

// Import thinking state from transfer
async function importThinkingState(importPath: string): Promise<boolean> {
  try {
    if (fs.existsSync(importPath)) {
      const importedData = JSON.parse(fs.readFileSync(importPath, 'utf8'));
      
      // Check if this is a comprehensive knowledge base (new format)
      if (importedData.files && importedData.totalPages && importedData.content) {
        // This is a comprehensive knowledge base from process-pdf.js
        console.error('Detected comprehensive knowledge base format');
        
        thinkingState.pdfContext = {
          filename: `${importedData.files.length} merged documents`,
          content: importedData.content,
          pageCount: importedData.totalPages,
          loadedAt: new Date(importedData.processedAt),
          processingInfo: {
            processedPages: `Multiple documents (${importedData.totalPages} total pages)`,
            chunksUsed: importedData.files.length,
            chunkSize: 0, // Variable chunk size
            summaryMode: true,
            comprehensiveKnowledge: true,
            files: importedData.files.map((f: any) => ({
              filename: f.filename,
              pages: f.pages,
              sizeMB: f.sizeMB
            }))
          }
        };
        
        await saveThinkingState();
        console.error('Comprehensive knowledge base imported successfully');
        return true;
        
      } else if (importedData.thoughts && Array.isArray(importedData.thoughts)) {
        // This is a standard thinking state export
        const importedState = importedData;
        // Remove export metadata
        delete importedState.exportedAt;
        delete importedState.serverVersion;
        thinkingState = importedState;
        await saveThinkingState(); // Save to local storage
        return true;
        
      } else {
        console.error('Invalid import data structure');
        return false;
      }
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

// Load PDF for analysis tool with large file support
server.tool(
  "load_pdf",
  "Load a PDF file to provide context for sequential thinking and problem solving. Optimized for large files.",
  {
    filePath: z.string().describe("Absolute path to the PDF file to load"),
    maxPages: z.number().int().positive().optional().describe("Maximum number of pages to process (default: all)"),
    chunkSize: z.number().int().positive().optional().describe("Process PDF in chunks of this many pages (default: 10)"),
  },
  async ({ filePath, maxPages, chunkSize = 10 }) => {
    try {
      console.error(`Loading PDF: ${filePath}`);
      
      // Check if file exists
      if (!fs.existsSync(filePath)) {
        return {
          content: [
            {
              type: "text",
              text: `❌ Error: PDF file not found at path: ${filePath}`,
            },
          ],
        };
      }

      // Check file size
      const stats = fs.statSync(filePath);
      const fileSizeMB = stats.size / (1024 * 1024);
      console.error(`PDF file size: ${fileSizeMB.toFixed(2)} MB`);

      // Check if it's a PDF file
      if (!path.extname(filePath).toLowerCase().includes('pdf')) {
        return {
          content: [
            {
              type: "text",
              text: `❌ Error: File must be a PDF. Got: ${path.extname(filePath)}`,
            },
          ],
        };
      }

      // For very large files, warn and suggest chunking
      if (fileSizeMB > 50) {
        console.error(`Warning: Large PDF file (${fileSizeMB.toFixed(2)} MB). Processing with optimization...`);
      }

      // Read and parse PDF with memory optimization
      const pdfBuffer = fs.readFileSync(filePath);
      
      // Initialize PDF parser dynamically
      const parser = await initializePdfParser();
      if (!parser) {
        return {
          content: [
            {
              type: "text",
              text: `❌ **PDF processing unavailable**\n\nPDF parsing library could not be loaded. Please check your installation.`,
            },
          ],
        };
      }
      
      // Parse PDF with options for large files
      const pdfData = await parser(pdfBuffer, {
        max: maxPages || undefined,  // Limit pages if specified
        version: 'v1.10.100',       // Use specific version for stability
      });

      // If text is very large, truncate but keep structure
      let processedText = pdfData.text;
      const originalLength = processedText.length;
      
      // For very large texts (>1MB), process in chunks
      if (processedText.length > 1024 * 1024) {
        console.error(`Large text content (${(processedText.length / 1024 / 1024).toFixed(2)} MB). Optimizing for processing...`);
        
        // Keep first part, middle part, and last part to maintain context
        const chunkSize = 300000; // 300KB chunks
        const firstChunk = processedText.substring(0, chunkSize);
        const middleStart = Math.floor(processedText.length / 2) - chunkSize / 2;
        const middleChunk = processedText.substring(middleStart, middleStart + chunkSize);
        const lastChunk = processedText.substring(processedText.length - chunkSize);
        
        processedText = firstChunk + 
          "\n\n[... MIDDLE SECTION OPTIMIZED FOR PROCESSING ...]\n\n" + 
          middleChunk + 
          "\n\n[... CONTENT CONTINUES ...]\n\n" + 
          lastChunk;
          
        console.error(`Text optimized: ${originalLength} chars → ${processedText.length} chars`);
      }

      // Store PDF context
      thinkingState.pdfContext = {
        filename: path.basename(filePath),
        content: processedText,
        pageCount: pdfData.numpages,
        loadedAt: new Date(),
      };

      // Auto-save after loading PDF
      await saveThinkingState();

      const preview = processedText.substring(0, 500);
      
      return {
        content: [
          {
            type: "text",
            text: `✅ **Large PDF Loaded Successfully**\n\n` +
                  `**File:** ${path.basename(filePath)}\n` +
                  `**Size:** ${fileSizeMB.toFixed(2)} MB\n` +
                  `**Pages:** ${pdfData.numpages}\n` +
                  `**Original Text:** ${originalLength.toLocaleString()} characters\n` +
                  `**Processed Text:** ${processedText.length.toLocaleString()} characters\n` +
                  `${processedText.length < originalLength ? '**Optimization:** Content optimized for processing\n' : ''}` +
                  `**Pages Limit:** ${maxPages || 'All pages'}\n\n` +
                  `**Preview (first 500 characters):**\n\n` +
                  `${preview}${processedText.length > 500 ? '...' : ''}\n\n` +
                  `*PDF content is now available for sequential thinking analysis.*\n\n` +
                  `${fileSizeMB > 50 ? '**Note:** Large file detected. Use analyze_pdf_section with specific queries for best performance.' : ''}`,
          },
        ],
      };
    } catch (error) {
      console.error('PDF loading error:', error);
      return {
        content: [
          {
            type: "text",
            text: `❌ **Error loading large PDF**: ${error instanceof Error ? error.message : String(error)}\n\n` +
                  `**Troubleshooting for large files:**\n` +
                  `1. Try loading with page limits: maxPages parameter\n` +
                  `2. Ensure sufficient system memory (RAM)\n` +
                  `3. Consider splitting the PDF into smaller files\n` +
                  `4. Close other applications to free memory\n\n` +
                  `**File size limit:** Recommended < 100MB for optimal performance`,
          },
        ],
      };
    }
  },
);

// Analyze specific sections of loaded PDF tool with enhanced search
server.tool(
  "analyze_pdf_section",
  "Search and analyze specific sections of a loaded PDF document. Optimized for large documents.",
  {
    query: z.string().describe("Search query or topic to look for in the PDF"),
    contextWindow: z.number().int().positive().optional().describe("Number of characters around each match to include (default: 2000)"),
    maxMatches: z.number().int().positive().optional().describe("Maximum number of matches to return (default: 10)"),
    caseSensitive: z.boolean().optional().describe("Whether search should be case sensitive (default: false)"),
  },
  async ({ query, contextWindow = 2000, maxMatches = 10, caseSensitive = false }) => {
    try {
      if (!thinkingState.pdfContext) {
        return {
          content: [
            {
              type: "text",
              text: `❌ **No PDF loaded**\n\nPlease use the 'load_pdf' tool first to load a PDF document.`,
            },
          ],
        };
      }

      console.error(`Searching PDF for: "${query}"`);
      
      const content = thinkingState.pdfContext.content;
      const searchText = caseSensitive ? content : content.toLowerCase();
      const searchQuery = caseSensitive ? query : query.toLowerCase();

      // Find all matches with their positions
      const matches: Array<{position: number, context: string, snippet: string}> = [];
      let position = 0;

      while (position < searchText.length && matches.length < maxMatches) {
        const matchIndex = searchText.indexOf(searchQuery, position);
        if (matchIndex === -1) break;

        // Extract context around the match
        const start = Math.max(0, matchIndex - contextWindow / 2);
        const end = Math.min(content.length, matchIndex + searchQuery.length + contextWindow / 2);
        const context = content.substring(start, end);
        
        // Create a snippet showing the match in context
        const snippetStart = Math.max(0, matchIndex - 100);
        const snippetEnd = Math.min(content.length, matchIndex + searchQuery.length + 100);
        const snippet = content.substring(snippetStart, snippetEnd);

        matches.push({
          position: matchIndex,
          context: context.trim(),
          snippet: snippet.trim(),
        });

        position = matchIndex + 1;
      }

      if (matches.length === 0) {
        // Try fuzzy matching for better results
        const words = searchQuery.split(/\s+/);
        let fuzzyMatches: Array<{position: number, context: string, snippet: string}> = [];
        
        for (const word of words) {
          if (word.length < 3) continue; // Skip very short words
          
          let wordPosition = 0;
          while (wordPosition < searchText.length && fuzzyMatches.length < maxMatches) {
            const wordIndex = searchText.indexOf(word, wordPosition);
            if (wordIndex === -1) break;

            const start = Math.max(0, wordIndex - contextWindow / 2);
            const end = Math.min(content.length, wordIndex + word.length + contextWindow / 2);
            const context = content.substring(start, end);
            
            const snippetStart = Math.max(0, wordIndex - 100);
            const snippetEnd = Math.min(content.length, wordIndex + word.length + 100);
            const snippet = content.substring(snippetStart, snippetEnd);

            fuzzyMatches.push({
              position: wordIndex,
              context: context.trim(),
              snippet: snippet.trim(),
            });

            wordPosition = wordIndex + 1;
          }
        }

        if (fuzzyMatches.length > 0) {
          // Sort by position and remove duplicates
          fuzzyMatches.sort((a, b) => a.position - b.position);
          const uniqueMatches = fuzzyMatches.filter((match, index, arr) => 
            index === 0 || Math.abs(match.position - arr[index - 1].position) > 500
          );

          return {
            content: [
              {
                type: "text",
                text: `🔍 **Fuzzy Search Results for "${query}"**\n\n` +
                      `**PDF:** ${thinkingState.pdfContext.filename}\n` +
                      `**Partial matches found:** ${uniqueMatches.length}\n` +
                      `**Note:** No exact matches found, showing related content\n\n` +
                      uniqueMatches.slice(0, maxMatches).map((match, index) => 
                        `**Match ${index + 1}** (Position: ${match.position.toLocaleString()})\n` +
                        `${match.snippet.replace(/\n+/g, ' ').replace(/\s+/g, ' ')}\n`
                      ).join('\n') +
                      `\n*Use these results to refine your search or ask for specific sections.*`,
              },
            ],
          };
        }

        return {
          content: [
            {
              type: "text",
              text: `❌ **No matches found for "${query}"**\n\n` +
                    `**PDF:** ${thinkingState.pdfContext.filename}\n` +
                    `**Searched:** ${content.length.toLocaleString()} characters\n\n` +
                    `**Suggestions:**\n` +
                    `• Try different keywords or phrases\n` +
                    `• Use broader search terms\n` +
                    `• Check spelling and try variations\n` +
                    `• Consider searching for specific concepts or topics\n\n` +
                    `**Available PDF content:** ${thinkingState.pdfContext.pageCount} pages`,
            },
          ],
        };
      }

      // Sort matches by position
      matches.sort((a, b) => a.position - b.position);

      return {
        content: [
          {
            type: "text",
            text: `🎯 **Search Results for "${query}"**\n\n` +
                  `**PDF:** ${thinkingState.pdfContext.filename}\n` +
                  `**Matches found:** ${matches.length}${matches.length >= maxMatches ? ` (showing first ${maxMatches})` : ''}\n` +
                  `**Context window:** ${contextWindow} characters\n\n` +
                  matches.map((match, index) => 
                    `**Match ${index + 1}** (Position: ${match.position.toLocaleString()})\n\n` +
                    `${match.context.replace(/\n+/g, '\n').trim()}\n\n` +
                    `---\n`
                  ).join('\n') +
                  `\n*Found ${matches.length} relevant sections. Use this content for sequential thinking analysis.*`,
          },
        ],
      };
    } catch (error) {
      console.error('PDF analysis error:', error);
      return {
        content: [
          {
            type: "text",
            text: `❌ **Error analyzing PDF**: ${error instanceof Error ? error.message : String(error)}\n\n` +
                  `**For large documents, try:**\n` +
                  `• More specific search terms\n` +
                  `• Smaller context windows\n` +
                  `• Fewer maximum matches\n` +
                  `• Breaking query into smaller parts`,
          },
        ],
      };
    }
  },
);

// Process large PDFs in chunks
server.tool(
  "process_large_pdf",
  "Process a large PDF file in smaller chunks to handle memory constraints. Use this for PDFs over 50MB.",
  {
    filePath: z.string().describe("Absolute path to the large PDF file"),
    chunkSizePages: z.number().int().positive().optional().describe("Number of pages to process at a time (default: 20)"),
    startPage: z.number().int().positive().optional().describe("Starting page number (1-based, default: 1)"),
    endPage: z.number().int().positive().optional().describe("Ending page number (1-based, default: all)"),
    outputSummary: z.boolean().optional().describe("Whether to provide a summary instead of full content (default: true)"),
  },
  async ({ filePath, chunkSizePages = 20, startPage = 1, endPage, outputSummary = true }) => {
    try {
      console.error(`Processing large PDF in chunks: ${filePath}`);
      
      // Check if file exists
      if (!fs.existsSync(filePath)) {
        return {
          content: [
            {
              type: "text",
              text: `❌ Error: PDF file not found at path: ${filePath}`,
            },
          ],
        };
      }

      // Check file size
      const stats = fs.statSync(filePath);
      const fileSizeMB = stats.size / (1024 * 1024);
      console.error(`Processing PDF: ${fileSizeMB.toFixed(2)} MB`);

      // First, get basic PDF info without loading full content
      const pdfBuffer = fs.readFileSync(filePath);
      
      // Initialize PDF parser dynamically
      const parser = await initializePdfParser();
      if (!parser) {
        return {
          content: [
            {
              type: "text",
              text: `❌ **PDF processing unavailable**\n\nPDF parsing library could not be loaded. Please check your installation.`,
            },
          ],
        };
      }
      
      // Parse just the metadata first
      let pdfInfo;
      try {
        pdfInfo = await parser(pdfBuffer, { 
          max: 1, // Just get first page to check structure
          version: 'v1.10.100' 
        });
      } catch (error) {
        console.error('PDF parsing error:', error);
        return {
          content: [
            {
              type: "text",
              text: `❌ **Error parsing PDF**: ${error instanceof Error ? error.message : String(error)}\n\n` +
                    `**This might be due to:**\n` +
                    `• Corrupted PDF file\n` +
                    `• Password-protected PDF\n` +
                    `• Unsupported PDF version\n` +
                    `• Insufficient system memory\n\n` +
                    `**File size:** ${fileSizeMB.toFixed(2)} MB`,
            },
          ],
        };
      }

      // Get total pages from metadata (this is usually available without loading content)
      const totalPages = pdfInfo.numpages;
      const actualEndPage = endPage || totalPages;
      const pagesToProcess = actualEndPage - startPage + 1;
      const chunks = Math.ceil(pagesToProcess / chunkSizePages);

      console.error(`Total pages: ${totalPages}, Processing: ${startPage}-${actualEndPage}, Chunks: ${chunks}`);

      let processedContent = '';
      let processedPages = 0;
      let totalCharacters = 0;

      for (let chunkIndex = 0; chunkIndex < chunks; chunkIndex++) {
        const chunkStart = startPage + (chunkIndex * chunkSizePages);
        const chunkEnd = Math.min(chunkStart + chunkSizePages - 1, actualEndPage);
        
        console.error(`Processing chunk ${chunkIndex + 1}/${chunks}: pages ${chunkStart}-${chunkEnd}`);

        try {
          // Process this chunk
          const chunkData = await parser(pdfBuffer, {
            max: chunkEnd,
            version: 'v1.10.100'
          });

          // Extract just the content for this chunk (this is approximate)
          let chunkContent = chunkData.text;
          
          // If we have processed previous chunks, try to get just the new content
          if (chunkIndex > 0 && processedContent.length > 0) {
            // This is a simplified approach - for better results, you'd need
            // more sophisticated page boundary detection
            const estimatedPreviousLength = Math.floor((processedContent.length / processedPages) * (chunkStart - startPage));
            if (chunkContent.length > estimatedPreviousLength) {
              chunkContent = chunkContent.substring(estimatedPreviousLength);
            }
          }

          // Add chunk content
          if (outputSummary && chunkContent.length > 10000) {
            // For summary mode, take key parts of each chunk
            const chunkSummary = chunkContent.substring(0, 3000) + 
                               "\n\n[...chunk content abbreviated...]\n\n" +
                               chunkContent.substring(Math.max(0, chunkContent.length - 1000));
            processedContent += `\n\n=== CHUNK ${chunkIndex + 1} (Pages ${chunkStart}-${chunkEnd}) ===\n\n${chunkSummary}`;
            totalCharacters += chunkContent.length;
          } else {
            processedContent += `\n\n=== CHUNK ${chunkIndex + 1} (Pages ${chunkStart}-${chunkEnd}) ===\n\n${chunkContent}`;
            totalCharacters += chunkContent.length;
          }

          processedPages += (chunkEnd - chunkStart + 1);

          // Add a small delay to prevent memory issues
          if (chunkIndex < chunks - 1) {
            await new Promise(resolve => setTimeout(resolve, 100));
          }

        } catch (chunkError) {
          console.error(`Error processing chunk ${chunkIndex + 1}:`, chunkError);
          processedContent += `\n\n=== CHUNK ${chunkIndex + 1} ERROR ===\n\nFailed to process pages ${chunkStart}-${chunkEnd}: ${chunkError instanceof Error ? chunkError.message : String(chunkError)}\n\n`;
        }
      }

      // Store the processed content
      thinkingState.pdfContext = {
        filename: path.basename(filePath),
        content: processedContent,
        pageCount: totalPages,
        loadedAt: new Date(),
        processingInfo: {
          processedPages: `${startPage}-${actualEndPage}`,
          chunksUsed: chunks,
          chunkSize: chunkSizePages,
          summaryMode: outputSummary,
        },
      };

      // Auto-save after processing
      await saveThinkingState();

      const preview = processedContent.substring(0, 1000);

      return {
        content: [
          {
            type: "text",
            text: `✅ **Large PDF Processed Successfully (Chunked)**\n\n` +
                  `**File:** ${path.basename(filePath)}\n` +
                  `**Size:** ${fileSizeMB.toFixed(2)} MB\n` +
                  `**Total Pages:** ${totalPages}\n` +
                  `**Processed Pages:** ${startPage}-${actualEndPage} (${processedPages} pages)\n` +
                  `**Processing Method:** ${chunks} chunks of ${chunkSizePages} pages\n` +
                  `**Content Mode:** ${outputSummary ? 'Summary (optimized)' : 'Full content'}\n` +
                  `**Total Characters:** ${totalCharacters.toLocaleString()}\n` +
                  `**Final Content:** ${processedContent.length.toLocaleString()} characters\n\n` +
                  `**Preview:**\n\n${preview}${processedContent.length > 1000 ? '...' : ''}\n\n` +
                  `*✨ PDF content is now available for sequential thinking and analysis.*\n\n` +
                  `**Next steps:**\n` +
                  `• Use 'analyze_pdf_section' to search for specific content\n` +
                  `• Use 'sequential_thinking' to analyze the processed content\n` +
                  `• For more detail, reprocess with outputSummary=false`,
          },
        ],
      };
    } catch (error) {
      console.error('Large PDF processing error:', error);
      return {
        content: [
          {
            type: "text",
            text: `❌ **Error processing large PDF**: ${error instanceof Error ? error.message : String(error)}\n\n` +
                  `**For very large files (>85MB), try:**\n` +
                  `1. **Smaller chunks**: Use chunkSizePages=5-10\n` +
                  `2. **Page range**: Process specific page ranges\n` +
                  `3. **Summary mode**: Keep outputSummary=true\n` +
                  `4. **Memory management**: Close other applications\n` +
                  `5. **File splitting**: Consider splitting the PDF externally\n\n` +
                  `**Alternative approaches:**\n` +
                  `• Convert PDF to text externally (pdftotext, etc.)\n` +
                  `• Use online PDF processing services\n` +
                  `• Split PDF into smaller files using PDF tools`,
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
          isComprehensive: thinkingState.pdfContext?.processingInfo?.comprehensiveKnowledge || false,
          fileCount: thinkingState.pdfContext?.processingInfo?.files?.length || 0,
          importedAt: new Date().toISOString()
        };

        let knowledgeDescription = '';
        if (stats.isComprehensive && thinkingState.pdfContext?.processingInfo?.files) {
          knowledgeDescription += `\n**📚 Comprehensive Knowledge Base:**\n`;
          thinkingState.pdfContext.processingInfo.files.forEach((file, index) => {
            knowledgeDescription += `  ${index + 1}. ${file.filename} (${file.pages} pages, ${file.sizeMB.toFixed(1)}MB)\n`;
          });
        }

        return {
          content: [
            {
              type: "text",
              text: `✅ **Knowledge Imported Successfully**\n\n` +
                    `**Import Source:** ${importPath}\n` +
                    `**Thoughts Imported:** ${stats.thoughts}\n` +
                    `**PDF Context:** ${stats.pdfLoaded ? `✅ ${stats.pdfFile} (${stats.pdfPages?.toLocaleString()} pages)` : '❌ None'}\n` +
                    `**Type:** ${stats.isComprehensive ? `🧠 Comprehensive Knowledge Base (${stats.fileCount} documents)` : '📄 Single PDF'}\n` +
                    knowledgeDescription +
                    `**Imported At:** ${stats.importedAt}\n\n` +
                    `*Your ${stats.isComprehensive ? 'comprehensive knowledge base' : 'thinking session and PDF knowledge'} ${stats.isComprehensive ? 'is ready for advanced analysis' : 'have been restored'}. You can ${stats.isComprehensive ? 'now perform sequential thinking with access to all documents' : 'continue where you left off'}.*`,
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

// =============================================================================
// VISUM INTEGRATION TOOLS
// =============================================================================

// Check Visum availability
server.tool(
  "check_visum",
  "Check if PTV Visum is installed and accessible on the local system",
  {
    customPath: z.string().optional().describe("Optional custom path to Visum executable (e.g., 'D:\\Software\\Visum\\Visum240.exe')"),
  },
  async ({ customPath }) => {
    try {
      const availability = await visumController.isVisumAvailable(customPath);
      
      if (availability.available) {
        const installationsList = availability.installations?.map((inst, index) => 
          `${index + 1}. ${inst.path} (Version: ${inst.version})`
        ).join('\n') || '';

        // Create informative message about path source
        let pathSourceInfo = '';
        if (availability.pathSource === 'learned-preferred') {
          pathSourceInfo = `📚 **Remembered Installation** (Preferred path from previous setup)\n`;
        } else if (availability.pathSource === 'learned-known') {
          pathSourceInfo = `📚 **Remembered Installation** (Known from previous discovery)\n`;
        } else {
          pathSourceInfo = `🔍 **Newly Discovered Installation**\n`;
        }

        let configInfo = '';
        if (availability.totalKnownPaths && availability.totalKnownPaths > 0) {
          configInfo = `\n**MCP Server Memory:**\n` +
                      `• **Known Installations:** ${availability.totalKnownPaths}\n` +
                      `• **Last Updated:** ${new Date(availability.lastConfigUpdate || '').toLocaleString()}\n` +
                      `• **Configuration:** Persistent across conversations and server restarts\n`;
        }

        return {
          content: [
            {
              type: "text",
              text: `✅ **Visum Available**\n\n` +
                    pathSourceInfo +
                    `**Primary Installation:**\n` +
                    `• **Path:** ${availability.path}\n` +
                    `• **Version:** ${availability.version || 'Unknown'}\n` +
                    `• **COM Registered:** ${availability.comRegistered ? '✅ Yes' : '❌ No'}\n` +
                    configInfo +
                    `${availability.installations && availability.installations.length > 1 ? 
                      `\n**All Found Installations:**\n${installationsList}\n` : ''
                    }` +
                    `${availability.error ? `\n**Note:** ${availability.error}\n` : ''}` +
                    `\n*Ready to load models and execute transportation analysis.*`
            }
          ]
        };
      } else {
        let message = `❌ **Visum Not Found**\n\n${availability.error}\n\n`;
        
        if (availability.suggestCustomPath) {
          message += `**💡 Custom Installation Path**\n` +
                    `If Visum is installed in a non-standard location, please provide the full path to the Visum executable.\n\n` +
                    `**Examples:**\n` +
                    `• \`D:\\Software\\PTV\\Visum\\Exe\\Visum240.exe\`\n` +
                    `• \`C:\\MyPrograms\\Visum2024\\Visum240.exe\`\n` +
                    `• \`E:\\Transportation\\Visum\\Visum230.exe\`\n\n` +
                    `**Usage:** Use this tool again with the \`customPath\` parameter pointing to your Visum executable.\n\n`;
        }
        
        message += `**Standard Installation Paths Checked:**\n` +
                  `• C:\\Program Files\\PTV Vision\\PTV Visum 202X\\Exe\\VisumXXX.exe\n` +
                  `• C:\\Program Files (x86)\\PTV Vision\\PTV Visum 202X\\Exe\\VisumXXX.exe\n\n` +
                  `**COM Registration:** ${availability.comRegistered ? '✅ Available' : '❌ Not found'}`;

        return {
          content: [
            {
              type: "text", 
              text: message
            }
          ]
        };
      }
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `❌ **Error checking Visum availability:**\n\n${error instanceof Error ? error.message : String(error)}\n\n` +
                  `**Troubleshooting:**\n` +
                  `• Check if you have permission to access the installation directories\n` +
                  `• Try providing a custom path if Visum is installed elsewhere\n` +
                  `• Ensure Visum is properly installed and not corrupted`
          }
        ]
      };
    }
  }
);

// Initialize Visum COM connection
server.tool(
  "initialize_visum",
  "Initialize connection to Visum COM interface for automation",
  {},
  async () => {
    try {
      const result = await visumController.initializeVisum();
      
      if (result.success) {
        return {
          content: [
            {
              type: "text",
              text: `✅ **Visum Initialized**\n\n` +
                    `COM connection established successfully.\n` +
                    `Visum is now ready for automation.\n\n` +
                    `*You can now load models and execute procedures.*`
            }
          ]
        };
      } else {
        return {
          content: [
            {
              type: "text",
              text: `❌ **Initialization Failed**\n\n` +
                    `Error: ${result.error}\n\n` +
                    `*Make sure Visum is installed and you have COM automation permissions.*`
            }
          ]
        };
      }
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `Error initializing Visum: ${error instanceof Error ? error.message : String(error)}`
          }
        ]
      };
    }
  }
);

// Load Visum model
server.tool(
  "load_visum_model", 
  "Load a Visum model file (.ver) for analysis and operations",
  {
    modelPath: z.string().describe("Full path to the Visum model file (.ver)"),
  },
  async ({ modelPath }) => {
    try {
      const result = await visumController.loadModel(modelPath);
      
      if (result.success && result.modelInfo) {
        const info = result.modelInfo;
        return {
          content: [
            {
              type: "text",
              text: `✅ **Model Loaded Successfully**\n\n` +
                    `**Model:** ${info.modelPath}\n` +
                    `**Loaded At:** ${info.loadedAt}\n\n` +
                    `**Network Statistics:**\n` +
                    `• **Nodes:** ${info.nodes?.toLocaleString() || 'N/A'}\n` +
                    `• **Links:** ${info.links?.toLocaleString() || 'N/A'}\n` +
                    `• **Zones:** ${info.zones?.toLocaleString() || 'N/A'}\n\n` +
                    `*Model is ready for analysis. You can now run procedures, get detailed statistics, or execute custom operations.*`
            }
          ]
        };
      } else {
        return {
          content: [
            {
              type: "text",
              text: `❌ **Failed to Load Model**\n\n` +
                    `Error: ${result.error}\n\n` +
                    `*Check that the file path is correct and the model file is valid.*`
            }
          ]
        };
      }
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `Error loading model: ${error instanceof Error ? error.message : String(error)}`
          }
        ]
      };
    }
  }
);

// Get network statistics
server.tool(
  "analyze_visum_network",
  "Analyze the currently loaded Visum network and get detailed statistics",
  {},
  async () => {
    try {
      const result = await visumController.getNetworkStats();
      
      if (result.success && result.stats) {
        const stats = result.stats;
        return {
          content: [
            {
              type: "text",
              text: `📊 **Network Analysis Results**\n\n` +
                    `**Infrastructure:**\n` +
                    `• **Nodes:** ${stats.nodes?.toLocaleString() || 'N/A'}\n` +
                    `• **Links:** ${stats.links?.toLocaleString() || 'N/A'}\n` +
                    `• **Zones:** ${stats.zones?.toLocaleString() || 'N/A'}\n\n` +
                    `**Public Transport:**\n` +
                    `• **Lines:** ${stats.lines?.toLocaleString() || 'N/A'}\n` +
                    `• **Stops:** ${stats.stops?.toLocaleString() || 'N/A'}\n` +
                    `• **Time Profiles:** ${stats.timeProfiles?.toLocaleString() || 'N/A'}\n` +
                    `• **Vehicle Journeys:** ${stats.vehicleJourneys?.toLocaleString() || 'N/A'}\n\n` +
                    `*Network analysis complete. Use this data for sequential thinking about transportation optimization.*`
            }
          ]
        };
      } else {
        return {
          content: [
            {
              type: "text",
              text: `❌ **Network Analysis Failed**\n\n` +
                    `Error: ${result.error}\n\n` +
                    `*Make sure a model is loaded first using load_visum_model.*`
            }
          ]
        };
      }
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `Error analyzing network: ${error instanceof Error ? error.message : String(error)}`
          }
        ]
      };
    }
  }
);

// Run Visum procedure
server.tool(
  "run_visum_procedure",
  "Execute a Visum procedure (like traffic assignment) by procedure number",
  {
    procedureNumber: z.number().int().positive().describe("Visum procedure number to execute"),
    description: z.string().optional().describe("Optional description of what this procedure does"),
  },
  async ({ procedureNumber, description }) => {
    try {
      const result = await visumController.runProcedure(procedureNumber);
      
      if (result.success) {
        return {
          content: [
            {
              type: "text",
              text: `✅ **Procedure Executed Successfully**\n\n` +
                    `**Procedure:** ${procedureNumber}${description ? ` (${description})` : ''}\n` +
                    `**Status:** Completed\n\n` +
                    `*Procedure execution finished. You can now analyze results or run additional procedures.*`
            }
          ]
        };
      } else {
        return {
          content: [
            {
              type: "text",
              text: `❌ **Procedure Execution Failed**\n\n` +
                    `**Procedure:** ${procedureNumber}\n` +
                    `**Error:** ${result.error}\n\n` +
                    `*Check that the procedure number is valid and all required data is available.*`
            }
          ]
        };
      }
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `Error executing procedure: ${error instanceof Error ? error.message : String(error)}`
          }
        ]
      };
    }
  }
);

// Execute custom Visum script
server.tool(
  "execute_visum_script",
  "Execute custom VBScript code in Visum for advanced operations",
  {
    script: z.string().describe("VBScript code to execute in Visum"),
    description: z.string().optional().describe("Optional description of what this script does"),
  },
  async ({ script, description }) => {
    try {
      const result = await visumController.executeCustomScript(script);
      
      if (result.success) {
        return {
          content: [
            {
              type: "text",
              text: `✅ **Custom Script Executed**\n\n` +
                    `${description ? `**Purpose:** ${description}\n` : ''}` +
                    `**Status:** Completed successfully\n\n` +
                    `**Result:** ${result.result || 'Script executed without output'}\n\n` +
                    `*Custom script execution finished.*`
            }
          ]
        };
      } else {
        return {
          content: [
            {
              type: "text",
              text: `❌ **Script Execution Failed**\n\n` +
                    `**Error:** ${result.error}\n\n` +
                    `*Check your VBScript syntax and Visum object references.*`
            }
          ]
        };
      }
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `Error executing script: ${error instanceof Error ? error.message : String(error)}`
          }
        ]
      };
    }
  }
);

// Get current Visum session status and COM connection details
server.tool(
  "get_visum_status",
  "Get the current status of Visum COM connection and active session",
  {},
  async () => {
    try {
      const status = visumController.getStatus();
      
      let statusInfo = `🔍 **Current Visum Session Status**\n\n`;
      
      statusInfo += `**COM Connection:**\n`;
      statusInfo += `• **COM Available:** ${status.comAvailable === true ? '✅ Yes' : status.comAvailable === false ? '❌ No' : '❓ Unknown'}\n`;
      statusInfo += `• **Demo Mode:** ${status.demoMode ? '✅ Active (No UI)' : '❌ Inactive'}\n`;
      
      if (status.currentModel) {
        statusInfo += `\n**Loaded Model:**\n`;
        statusInfo += `• **Path:** ${status.currentModel}\n`;
      } else {
        statusInfo += `\n**Model Status:** ❌ No model currently loaded\n`;
      }
      
      if (status.customPath) {
        statusInfo += `\n**Visum Installation:**\n`;
        statusInfo += `• **Path:** ${status.customPath}\n`;
      }
      
      if (status.directories) {
        statusInfo += `\n**Working Directories:**\n`;
        statusInfo += `• **Log:** ${status.directories.log}\n`;
        statusInfo += `• **Temp:** ${status.directories.temp}\n`;
        statusInfo += `• **Work:** ${status.directories.work}\n`;
      }
      
      statusInfo += `\n**What "Visum Opened" Means:**\n`;
      statusInfo += `🔹 **COM Interface Active:** Visum's automation interface is running\n`;
      statusInfo += `🔹 **Background Process:** Visum runs without visible UI in automation mode\n`;
      statusInfo += `🔹 **Ready for Commands:** Can load models, run procedures, analyze data\n`;
      statusInfo += `🔹 **Memory Resident:** Faster subsequent operations\n\n`;
      
      if (!status.currentModel) {
        statusInfo += `**Next Steps:**\n`;
        statusInfo += `1. **Load a Model:** Use \`load_visum_model\` with your .ver file path\n`;
        statusInfo += `2. **Analyze Network:** Once loaded, use \`analyze_visum_network\`\n`;
        statusInfo += `3. **Run Procedures:** Execute traffic assignments or other operations\n`;
        statusInfo += `4. **Custom Scripts:** Run VBScript for advanced automation\n`;
      } else {
        statusInfo += `**Available Actions:**\n`;
        statusInfo += `✅ Network analysis\n`;
        statusInfo += `✅ Procedure execution\n`;
        statusInfo += `✅ Custom scripting\n`;
        statusInfo += `✅ Data extraction\n`;
      }
      
      statusInfo += `\n**Important Notes:**\n`;
      statusInfo += `• Visum COM automation runs **silently in the background**\n`;
      statusInfo += `• You won't see a Visum window - this is normal!\n`;
      statusInfo += `• The process is ready to receive commands through this MCP server\n`;
      statusInfo += `• If you want to see Visum GUI, open it separately from Start menu\n`;
      
      return {
        content: [
          {
            type: "text",
            text: statusInfo
          }
        ]
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `❌ **Error getting Visum status:**\n\n${error instanceof Error ? error.message : String(error)}`
          }
        ]
      };
    }
  }
);

// Get MCP server's stored Visum configuration and learning data
server.tool(
  "get_visum_memory",
  "Get information about what Visum installations and configurations the MCP server remembers",
  {},
  async () => {
    try {
      const status = visumController.getStatus();
      const availability = await visumController.isVisumAvailable();
      
      let memoryInfo = `🧠 **MCP Server Memory Status**\n\n`;
      
      if (availability.totalKnownPaths && availability.totalKnownPaths > 0) {
        memoryInfo += `**Learned Visum Installations:** ${availability.totalKnownPaths}\n`;
        
        if (availability.installations && availability.installations.length > 0) {
          memoryInfo += `**Known Paths:**\n`;
          availability.installations.forEach((inst, index) => {
            const isPreferred = inst.path === status.customPath;
            memoryInfo += `${index + 1}. ${inst.path}\n   └─ Version: ${inst.version}${isPreferred ? ' (Preferred)' : ''}\n`;
          });
        }
        
        memoryInfo += `\n**Configuration Details:**\n`;
        memoryInfo += `• **Last Updated:** ${new Date(availability.lastConfigUpdate || '').toLocaleString()}\n`;
        memoryInfo += `• **Current Status:** ${availability.available ? '✅ Available' : '❌ Not Available'}\n`;
        memoryInfo += `• **Path Source:** ${availability.pathSource || 'Unknown'}\n`;
        memoryInfo += `• **Demo Mode:** ${status.demoMode ? '✅ Active' : '❌ Inactive'}\n`;
        
        if (status.directories) {
          memoryInfo += `\n**Configured Directories:**\n`;
          memoryInfo += `• **Log Dir:** ${status.directories.log}\n`;
          memoryInfo += `• **Temp Dir:** ${status.directories.temp}\n`;
          memoryInfo += `• **Work Dir:** ${status.directories.work}\n`;
        }
        
        memoryInfo += `\n**Memory Persistence:**\n`;
        memoryInfo += `✅ Survives server restarts\n`;
        memoryInfo += `✅ Survives conversation changes\n`;
        memoryInfo += `✅ Shared between AI clients\n`;
        memoryInfo += `✅ Automatic path learning enabled\n`;
        
        memoryInfo += `\n*The MCP server remembers your Visum installation and you should not need to provide the path again.*`;
      } else {
        memoryInfo += `**No Learned Installations**\n\n`;
        memoryInfo += `The MCP server has not yet learned any Visum installation paths.\n`;
        memoryInfo += `Use the \`check_visum\` tool with a custom path to teach the server about your installation.\n`;
        memoryInfo += `\n**Once learned, the server will remember:**\n`;
        memoryInfo += `• Your Visum installation path\n`;
        memoryInfo += `• Version information\n`;
        memoryInfo += `• Preferences and settings\n`;
        memoryInfo += `• Directory configurations\n`;
      }
      
      return {
        content: [
          {
            type: "text",
            text: memoryInfo
          }
        ]
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `❌ **Error retrieving MCP memory:**\n\n${error instanceof Error ? error.message : String(error)}`
          }
        ]
      };
    }
  }
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
