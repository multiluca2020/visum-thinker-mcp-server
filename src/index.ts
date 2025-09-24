#!/usr/bin/env node

import { z } from "zod";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import * as fs from "fs/promises";
import * as path from "path";
import * as os from "os";
import { spawn } from "child_process";

import { SimpleVisumController } from "./simple-visum-controller.js";

// =============================================================================
// INITIALIZATION
// =============================================================================

// Initialize Simple Visum controller with singleton pattern
const visumController = SimpleVisumController.getInstance();

// 🔧 CONFIGURAZIONE VISUM MCP TOOLS
const VISUM_MCP_CONFIG = {
  PYTHON_PATH: "H:\\Program Files\\PTV Vision\\PTV Visum 2025\\Exe\\Python\\python.exe",
  VISUM_EXE: "H:\\Program Files\\PTV Vision\\PTV Visum 2025\\Exe\\Visum250.exe",
  TEMP_DIR: "C:\\temp\\mcp_visum"
};

// =============================================================================
// STORAGE & STATE MANAGEMENT
// =============================================================================

interface ThinkingStep {
  id: number;
  thought: string;
  reasoning?: string;
  timestamp: string;
  category?: string;
}

interface ThinkingSession {
  currentSteps: ThinkingStep[];
  totalSteps: number;
  isComplete: boolean;
  summary?: string;
  metadata?: Record<string, any>;
  pdfContext?: {
    filename?: string;
    content?: string;
    metadata?: Record<string, any>;
  };
}

let thinkingSession: ThinkingSession = {
  currentSteps: [],
  totalSteps: 0,
  isComplete: false
};

const STORAGE_FILE = path.join(os.homedir(), '.mcp-sequential-thinking.json');

async function initializeStorage() {
  try {
    const data = await fs.readFile(STORAGE_FILE, 'utf-8');
    const saved = JSON.parse(data);
    thinkingSession = { ...thinkingSession, ...saved };
    console.error(`✅ Loaded thinking state: ${thinkingSession.currentSteps.length} steps`);
  } catch (error) {
    console.error("📝 Starting with fresh thinking state");
  }
}

async function saveThinkingState() {
  try {
    await fs.writeFile(STORAGE_FILE, JSON.stringify(thinkingSession, null, 2));
  } catch (error) {
    console.error("⚠️ Failed to save thinking state:", error);
  }
}

async function loadThinkingState() {
  return thinkingSession;
}

// =============================================================================
// MCP SERVER SETUP
// =============================================================================

const server = new McpServer({
  name: "visum-thinker",
  version: "2.0.0",
});

// =============================================================================
// SEQUENTIAL THINKING TOOLS
// =============================================================================

// Sequential thinking tool
server.tool(
  "sequential_thinking",
  "Engage in systematic step-by-step thinking to analyze complex problems, make decisions, or explore ideas. Each thought builds on the previous ones, creating a chain of reasoning.",
  {
    thought: z.string().describe("Your current thought or analysis step"),
    reasoning: z.string().optional().describe("Optional: Explain why this thought follows from previous ones"),
    category: z.string().optional().describe("Optional: Categorize this thought (analysis, synthesis, evaluation, etc.)"),
    revise_step: z.number().optional().describe("Optional: Revise a previous step by its number"),
    branch_from_step: z.number().optional().describe("Optional: Create a new reasoning branch from a specific step number"),
    target_steps: z.number().optional().describe("Optional: Target number of thinking steps for this session"),
    complete_thinking: z.boolean().optional().describe("Optional: Mark the thinking session as complete")
  },
  async ({ thought, reasoning, category, revise_step, branch_from_step, target_steps, complete_thinking }) => {
    try {
      const timestamp = new Date().toISOString();
      
      // Handle revision of existing step
      if (revise_step !== undefined) {
        const stepIndex = thinkingSession.currentSteps.findIndex(step => step.id === revise_step);
        if (stepIndex !== -1) {
          thinkingSession.currentSteps[stepIndex] = {
            ...thinkingSession.currentSteps[stepIndex],
            thought,
            reasoning,
            category,
            timestamp
          };
        } else {
          return {
            content: [{
              type: "text",
              text: `❌ Step ${revise_step} not found. Available steps: ${thinkingSession.currentSteps.map(s => s.id).join(', ')}`
            }]
          };
        }
      }
      // Handle branching from existing step  
      else if (branch_from_step !== undefined) {
        const branchPoint = thinkingSession.currentSteps.find(step => step.id === branch_from_step);
        if (!branchPoint) {
          return {
            content: [{
              type: "text",
              text: `❌ Cannot branch from step ${branch_from_step}. Step not found.`
            }]
          };
        }
        
        // Create new branch
        thinkingSession.totalSteps++;
        const newStep: ThinkingStep = {
          id: thinkingSession.totalSteps,
          thought: `[Branch from Step ${branch_from_step}] ${thought}`,
          reasoning,
          category,
          timestamp
        };
        thinkingSession.currentSteps.push(newStep);
      }
      // Add new step
      else {
        thinkingSession.totalSteps++;
        const newStep: ThinkingStep = {
          id: thinkingSession.totalSteps,
          thought,
          reasoning,
          category,
          timestamp
        };
        thinkingSession.currentSteps.push(newStep);
      }
      
      // Handle completion
      if (complete_thinking) {
        thinkingSession.isComplete = true;
        thinkingSession.summary = `Sequential thinking completed with ${thinkingSession.currentSteps.length} steps.`;
      }
      
      // Update target if provided
      if (target_steps) {
        thinkingSession.metadata = { ...thinkingSession.metadata, target_steps };
      }
      
      // Auto-save state
      await saveThinkingState();
      
      // Generate progress report
      const progress = target_steps ? ` (${thinkingSession.currentSteps.length}/${target_steps})` : '';
      const recentSteps = thinkingSession.currentSteps.slice(-3);
      
      let content = `🧠 **Sequential Thinking${progress}**\n\n`;
      
      if (revise_step !== undefined) {
        content += `📝 **Step ${revise_step} Revised**\n\n`;
      } else if (branch_from_step !== undefined) {
        content += `🌿 **New Branch from Step ${branch_from_step}**\n\n`;
      } else {
        content += `💭 **Step ${thinkingSession.totalSteps} Added**\n\n`;
      }
      
      content += "**Recent Thinking Chain:**\n";
      recentSteps.forEach(step => {
        const categoryLabel = step.category ? ` [${step.category}]` : '';
        content += `**${step.id}.${categoryLabel}** ${step.thought}\n`;
        if (step.reasoning) {
          content += `   *Reasoning: ${step.reasoning}*\n`;
        }
        content += '\n';
      });
      
      if (thinkingSession.isComplete) {
        content += `✅ **Thinking Complete**: ${thinkingSession.summary}\n\n`;
      }
      
      content += `*Continue with next thought or use 'get_thinking_summary' to review all steps*`;
      
      return {
        content: [{
          type: "text",
          text: content
        }]
      };
      
    } catch (error) {
      return {
        content: [{
          type: "text",
          text: `❌ **Error in sequential thinking**: ${error instanceof Error ? error.message : String(error)}`
        }]
      };
    }
  }
);

// Reset thinking tool
server.tool(
  "reset_thinking", 
  "Clear the current thinking session and start fresh",
  {},
  async () => {
    try {
      const previousSteps = thinkingSession.currentSteps.length;
      thinkingSession = {
        currentSteps: [],
        totalSteps: 0,
        isComplete: false
      };
      
      await saveThinkingState();
      
      return {
        content: [{
          type: "text",
          text: `🗑️ **Thinking Reset**\n\nPrevious session cleared (${previousSteps} steps removed).\nReady for fresh sequential thinking.`
        }]
      };
    } catch (error) {
      return {
        content: [{
          type: "text",
          text: `❌ **Error resetting thinking**: ${error instanceof Error ? error.message : String(error)}`
        }]
      };
    }
  }
);

// Get thinking summary tool
server.tool(
  "get_thinking_summary",
  "Get a complete summary of the current thinking session with all steps and analysis",
  {},
  async () => {
    try {
      if (thinkingSession.currentSteps.length === 0) {
        return {
          content: [{
            type: "text",
            text: "📝 **No Active Thinking Session**\n\nUse 'sequential_thinking' to start your first thought."
          }]
        };
      }
      
      const targetSteps = thinkingSession.metadata?.target_steps;
      const progress = targetSteps ? ` (${thinkingSession.currentSteps.length}/${targetSteps})` : '';
      
      let content = `📋 **Thinking Session Summary${progress}**\n\n`;
      content += `**Status**: ${thinkingSession.isComplete ? 'Complete ✅' : 'In Progress 🔄'}\n`;
      content += `**Total Steps**: ${thinkingSession.currentSteps.length}\n`;
      content += `**Started**: ${thinkingSession.currentSteps[0]?.timestamp ? new Date(thinkingSession.currentSteps[0].timestamp).toLocaleString() : 'Unknown'}\n\n`;
      
      content += "**Complete Thinking Chain:**\n";
      thinkingSession.currentSteps.forEach((step, index) => {
        const categoryLabel = step.category ? ` [${step.category}]` : '';
        content += `**${step.id}.${categoryLabel}** ${step.thought}\n`;
        if (step.reasoning) {
          content += `   *Reasoning: ${step.reasoning}*\n`;
        }
        content += '\n';
      });
      
      if (thinkingSession.summary) {
        content += `**Session Summary**: ${thinkingSession.summary}\n`;
      }
      
      if (thinkingSession.pdfContext) {
        content += `**PDF Context**: ${thinkingSession.pdfContext.filename || 'Document loaded'}\n`;
      }
      
      return {
        content: [{
          type: "text", 
          text: content
        }]
      };
      
    } catch (error) {
      return {
        content: [{
          type: "text",
          text: `❌ **Error getting thinking summary**: ${error instanceof Error ? error.message : String(error)}`
        }]
      };
    }
  }
);

// =============================================================================
// VISUM INTEGRATION TOOLS - Using SimpleVisumController with Persistent VisumPy
// =============================================================================

// Project Launch Tool
server.tool(
  "visum_launch_project",
  "Launch and load a specific Visum project using persistent VisumPy instance",
  {
    projectPath: z.string().describe("Full path to the Visum project file (.ver)")
  },
  async ({ projectPath }) => {
    try {
      const result = await visumController.executeVisumAnalysis(
        `# Load specific Visum project
import time
try:
    start_time = time.time()
    visum.LoadVersion(r"${projectPath}")
    load_time = time.time() - start_time
    
    # Get basic network info
    num_nodes = visum.Net.Nodes.Count
    num_links = visum.Net.Links.Count  
    num_zones = visum.Net.Zones.Count
    
    result = {
        'project_path': r"${projectPath}",
        'loaded_successfully': True,
        'load_time_seconds': round(load_time, 3),
        'network_summary': {
            'nodes': num_nodes,
            'links': num_links, 
            'zones': num_zones
        }
    }
except Exception as e:
    result = {
        'project_path': r"${projectPath}",
        'loaded_successfully': False,
        'error': str(e)
    }`,
        `Loading Visum project: ${projectPath}`
      );

      if (result.success && result.result?.loaded_successfully) {
        const info = result.result;
        return {
          content: [
            {
              type: "text",
              text: `✅ **Progetto Visum Caricato**\n\n` +
                    `**Progetto:** \`${info.project_path}\`\n` +
                    `**Tempo di Caricamento:** ${info.load_time_seconds}s\n\n` +
                    `**Statistiche Rete:**\n` +
                    `• **Nodi:** ${info.network_summary?.nodes?.toLocaleString() || 'N/A'}\n` +
                    `• **Link:** ${info.network_summary?.links?.toLocaleString() || 'N/A'}\n` +
                    `• **Zone:** ${info.network_summary?.zones?.toLocaleString() || 'N/A'}\n\n` +
                    `**Performance:**\n` +
                    `• **Tempo Esecuzione:** ${result.executionTimeMs?.toFixed(3) || 'N/A'}ms\n\n` +
                    `*Progetto pronto per l'analisi della rete*`
            }
          ]
        };
      } else {
        return {
          content: [
            {
              type: "text",
              text: `❌ **Errore Caricamento Progetto**\n\n` +
                    `**Progetto:** \`${projectPath}\`\n` +
                    `**Errore:** ${result.result?.error || result.error || 'Errore sconosciuto'}\n\n` +
                    `*Verificare che il percorso del file sia corretto e che il progetto sia valido*`
            }
          ]
        };
      }
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `❌ **Errore durante il caricamento:**\n\n${error instanceof Error ? error.message : String(error)}`
          }
        ]
      };
    }
  }
);

// Network Analysis Tool
server.tool(
  "visum_network_analysis",
  "Analyze the loaded Visum network with detailed statistics and performance metrics",
  {
    includeGeometry: z.boolean().optional().default(false).describe("Include geometric analysis of network elements"),
    sampleSize: z.number().optional().default(50).describe("Number of sample elements to analyze (default: 50)")
  },
  async ({ includeGeometry, sampleSize }) => {
    try {
      let analysisCode = `
# Comprehensive network analysis
import time
try:
    start_time = time.time()
    
    # Basic network statistics
    num_nodes = visum.Net.Nodes.Count
    num_links = visum.Net.Links.Count
    num_zones = visum.Net.Zones.Count
    num_stops = visum.Net.Stops.Count if hasattr(visum.Net, 'Stops') else 0
    num_lines = visum.Net.Lines.Count if hasattr(visum.Net, 'Lines') else 0
    
    # Sample node analysis
    sample_nodes = []
    if num_nodes > 0:
        node_iter = visum.Net.Nodes.Iterator
        count = 0
        while node_iter.Valid and count < ${sampleSize}:
            node = node_iter.Item
            sample_nodes.append({
                'id': node.AttValue('No'),
                'x': node.AttValue('XCoord') if hasattr(node, 'AttValue') else None,
                'y': node.AttValue('YCoord') if hasattr(node, 'AttValue') else None
            })
            node_iter.Next()
            count += 1
    
    # Sample link analysis  
    sample_links = []
    if num_links > 0:
        link_iter = visum.Net.Links.Iterator
        count = 0
        while link_iter.Valid and count < ${sampleSize}:
            link = link_iter.Item
            sample_links.append({
                'from_node': link.AttValue('FromNodeNo'),
                'to_node': link.AttValue('ToNodeNo'),
                'length': link.AttValue('Length') if hasattr(link, 'AttValue') else None
            })
            link_iter.Next()
            count += 1
    `;

      if (includeGeometry) {
        analysisCode += `
    # Geometric analysis
    total_length = 0.0
    if num_links > 0:
        link_iter = visum.Net.Links.Iterator
        while link_iter.Valid:
            try:
                length = link_iter.Item.AttValue('Length')
                if length:
                    total_length += length
            except:
                pass
            link_iter.Next()
    `;
      }

      analysisCode += `
    analysis_time = time.time() - start_time
    
    result = {
        'network_statistics': {
            'nodes': num_nodes,
            'links': num_links,
            'zones': num_zones,
            'stops': num_stops,
            'lines': num_lines
        },
        'sample_analysis': {
            'nodes': sample_nodes[:10],  # Limit output
            'links': sample_links[:10]   # Limit output
        },${includeGeometry ? `
        'geometric_analysis': {
            'total_network_length_km': round(total_length / 1000, 2) if 'total_length' in locals() else None
        },` : ''}
        'performance': {
            'analysis_time_seconds': round(analysis_time, 3)
        },
        'analysis_successful': True
    }
    
except Exception as e:
    result = {
        'analysis_successful': False,
        'error': str(e)
    }`;

      const result = await visumController.executeCustomCode(
        analysisCode,
        "Analisi completa della rete Visum"
      );

      if (result.success && result.result?.analysis_successful) {
        const analysis = result.result;
        const stats = analysis.network_statistics;
        
        let geometryInfo = '';
        if (includeGeometry && analysis.geometric_analysis) {
          geometryInfo = `**Analisi Geometrica:**\n` +
                        `• **Lunghezza Totale Rete:** ${analysis.geometric_analysis.total_network_length_km || 'N/A'} km\n\n`;
        }

        let sampleInfo = '';
        if (analysis.sample_analysis) {
          const sampleNodes = analysis.sample_analysis.nodes?.length || 0;
          const sampleLinks = analysis.sample_analysis.links?.length || 0;
          sampleInfo = `**Analisi Campionaria:**\n` +
                      `• **Nodi Analizzati:** ${sampleNodes}\n` +
                      `• **Link Analizzati:** ${sampleLinks}\n\n`;
        }

        return {
          content: [
            {
              type: "text", 
              text: `✅ **Analisi Rete Completata**\n\n` +
                    `**Statistiche Rete:**\n` +
                    `• **Nodi:** ${stats.nodes?.toLocaleString() || 'N/A'}\n` +
                    `• **Link:** ${stats.links?.toLocaleString() || 'N/A'}\n` +
                    `• **Zone:** ${stats.zones?.toLocaleString() || 'N/A'}\n` +
                    `• **Fermate:** ${stats.stops?.toLocaleString() || 'N/A'}\n` +
                    `• **Linee:** ${stats.lines?.toLocaleString() || 'N/A'}\n\n` +
                    sampleInfo +
                    geometryInfo +
                    `**Performance:**\n` +
                    `• **Tempo Analisi:** ${analysis.performance?.analysis_time_seconds || 'N/A'}s\n` +
                    `• **Tempo Esecuzione Tool:** ${result.executionTimeMs?.toFixed(3) || 'N/A'}ms\n\n` +
                    `*Analisi della rete completata con successo*`
            }
          ]
        };
      } else {
        return {
          content: [
            {
              type: "text",
              text: `❌ **Errore Analisi Rete**\n\n` +
                    `**Errore:** ${result.result?.error || result.error || 'Errore sconosciuto'}\n\n` +
                    `*Assicurarsi che un progetto Visum sia caricato correttamente*`
            }
          ]
        };
      }
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `❌ **Errore durante l'analisi:**\n\n${error instanceof Error ? error.message : String(error)}`
          }
        ]
      };
    }
  }
);

// Custom Python Analysis Tool  
server.tool(
  "visum_custom_analysis",
  "Execute custom Python code with access to the active Visum instance",
  {
    pythonCode: z.string().describe("Python code to execute. The 'visum' variable contains the active VisumPy instance. Store results in 'result' dictionary."),
    description: z.string().optional().describe("Optional description of the analysis being performed")
  },
  async ({ pythonCode, description }) => {
    try {
      const result = await visumController.executeCustomCode(pythonCode, description);
      
      if (result.success) {
        let analysisResults = '';
        if (result.result) {
          analysisResults = `**Risultati Analisi:**\n\`\`\`json\n${JSON.stringify(result.result, null, 2)}\n\`\`\`\n\n`;
        }
        
        let executionOutput = '';
        if (result.output) {
          const outputLines = result.output.split('\n').filter(line => 
            line.trim() && 
            !line.includes('=====') && 
            !line.includes('Executing analysis') &&
            !line.includes('SUCCESS: Tool call completed')
          );
          if (outputLines.length > 0) {
            executionOutput = `**Output Esecuzione:**\n\`\`\`\n${outputLines.slice(-20).join('\n')}\n\`\`\`\n\n`;
          }
        }
        
        return {
          content: [
            {
              type: "text",
              text: `✅ **Analisi Personalizzata Completata**\n\n` +
                    `**Descrizione:** ${description || 'Analisi Python personalizzata'}\n\n` +
                    analysisResults +
                    executionOutput +
                    `**Performance:**\n` +
                    `• **Tempo Esecuzione:** ${result.executionTimeMs?.toFixed(3) || 'N/A'}ms\n\n` +
                    `*Eseguito su istanza VisumPy persistente*`
            }
          ]
        };
      } else {
        return {
          content: [
            {
              type: "text",
              text: `❌ **Analisi personalizzata fallita**\n\n` +
                    `**Errore:** ${result.error || 'Errore sconosciuto'}\n\n` +
                    `**Codice tentato:**\n\`\`\`python\n${pythonCode}\n\`\`\`\n\n` +
                    `*Controllare la sintassi Python e l'uso corretto della variabile 'visum'*`
            }
          ]
        };
      }
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `❌ **Errore esecuzione analisi personalizzata:**\n\n${error instanceof Error ? error.message : String(error)}`
          }
        ]
      };
    }
  }
);

// Network Statistics Tool
server.tool(
  "visum_network_stats",
  "Get comprehensive network statistics from the loaded Visum project",
  {},
  async () => {
    try {
      const result = await visumController.getNetworkStats();
      
      if (result.success) {
        return {
          content: [
            {
              type: "text",
              text: `✅ **Statistiche Rete**\n\n` +
                    `**Riepilogo Rete:**\n` +
                    `• **Nodi:** ${result.nodes?.toLocaleString() || 'N/A'}\n` +
                    `• **Link:** ${result.links?.toLocaleString() || 'N/A'}\n` +
                    `• **Zone:** ${result.zones?.toLocaleString() || 'N/A'}\n\n` +
                    `**Performance:**\n` +
                    `• **Tempo Esecuzione:** ${result.executionTimeMs?.toFixed(3) || 'N/A'}ms\n\n` +
                    `*Dati rete recuperati da istanza VisumPy attiva*`
            }
          ]
        };
      } else {
        return {
          content: [
            {
              type: "text",
              text: `❌ **Impossibile ottenere statistiche rete**\n\n` +
                    `Il progetto Visum potrebbe non essere caricato o accessibile.\n` +
                    `La prima chiamata potrebbe richiedere più tempo per inizializzare l'istanza VisumPy.`
            }
          ]
        };
      }
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `❌ **Errore ottenimento statistiche rete:**\n\n${error instanceof Error ? error.message : String(error)}`
          }
        ]
      };
    }
  }
);

// Health Check Tool
server.tool(
  "visum_health_check", 
  "Check the health and status of the VisumPy instance",
  {},
  async () => {
    try {
      const statsResult = await visumController.getNetworkStats();
      
      if (statsResult.success) {
        const isHealthy = statsResult.nodes && statsResult.nodes > 0;
        const performance = statsResult.executionTimeMs && statsResult.executionTimeMs < 1000 ? 'Eccellente' :
                           statsResult.executionTimeMs && statsResult.executionTimeMs < 5000 ? 'Buona' : 'Lenta';
        
        return {
          content: [
            {
              type: "text", 
              text: `${isHealthy ? '✅' : '⚠️'} **Controllo Salute Istanza VisumPy**\n\n` +
                    `**Stato:** ${isHealthy ? 'Sano' : 'Attenzione'}\n` +
                    `**Performance:** ${performance}\n` +
                    `**Tempo Risposta:** ${statsResult.executionTimeMs?.toFixed(3) || 'N/A'}ms\n\n` +
                    `**Dettagli Istanza:**\n` +
                    `• **Nodi Disponibili:** ${statsResult.nodes?.toLocaleString() || 'N/A'}\n` +
                    `• **Link Disponibili:** ${statsResult.links?.toLocaleString() || 'N/A'}\n` +
                    `• **Zone Disponibili:** ${statsResult.zones?.toLocaleString() || 'N/A'}\n\n` +
                    `*${isHealthy ? 'Istanza pronta per analisi' : 'Istanza potrebbe necessitare reinizializzazione'}*`
            }
          ]
        };
      } else {
        return {
          content: [
            {
              type: "text",
              text: `❌ **Istanza VisumPy Non Sana**\n\n` +
                    `L'istanza VisumPy non risponde o non è inizializzata.\n` +
                    `Prova a eseguire visum_network_stats per inizializzare l'istanza.`
            }
          ]
        };
      }
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `❌ **Errore controllo salute:**\n\n${error instanceof Error ? error.message : String(error)}`
          }
        ]
      };
    }
  }
);

// =============================================================================
// SERVER STARTUP
// =============================================================================

async function main() {
  try {
    console.error("🔧 Initializing Sequential Thinking MCP Server with VisumPy Integration...");
    
    // Initialize storage for thinking state
    await initializeStorage();
    await loadThinkingState(); // Load saved state on startup
    
    console.error("✅ Storage and thinking state initialized");
    
    // Start MCP server
    const transport = new StdioServerTransport();
    await server.connect(transport);
    
    console.error("🚀 Sequential Thinking MCP Server with VisumPy Integration running on stdio");
    console.error("📋 Available Tools:");
    console.error("   • sequential_thinking - Step-by-step reasoning");
    console.error("   • reset_thinking - Clear thinking state");
    console.error("   • get_thinking_summary - View current progress");
    console.error("   • visum_launch_project - Launch Visum projects");
    console.error("   • visum_network_analysis - Comprehensive network analysis");
    console.error("   • visum_network_stats - Quick network statistics");
    console.error("   • visum_custom_analysis - Execute custom Python code");
    console.error("   • visum_health_check - Check VisumPy instance status");
    
  } catch (error) {
    console.error("❌ Fatal error starting server:", error);
    process.exit(1);
  }
}

// Start the server
main();