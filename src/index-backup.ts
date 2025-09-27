#!/usr/bin/env node

import { z } from "zod";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import * as fs from "fs/promises";
import * as path from "path";
import * as os from "os";
import { spawn } from "child_process";

import { SimpleVisumController } from "./simple-visum-controller.js";
import { PersistentVisumController } from "./persistent-visum-controller.js";
import { ProjectInstanceManager } from "./project-instance-manager.js";
import { ProjectServerManager } from "./project-server-manager.js";

// =============================================================================
// INITIALIZATION
// =============================================================================

// Initialize controllers with singleton pattern
const visumController = PersistentVisumController.getInstance();
const legacyController = SimpleVisumController.getInstance(); // For backward compatibility
const projectManager = ProjectInstanceManager.getInstance(); // Project-specific instances
const serverManager = ProjectServerManager.getInstance(); // TCP server manager

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
    console.error(`LOADED: thinking state: ${thinkingSession.currentSteps.length} steps`);
  } catch (error) {
    console.error("INIT: Starting with fresh thinking state");
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

// Project Launch Tool - DEPRECATED! Use project_open instead
server.tool(
  "visum_launch_project",
  "⚠️ DEPRECATED: Use 'project_open' tool instead. This tool is obsolete and slower than the new TCP-based project_open tool.",
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
              text: `✅ **Statistiche Rete PERSISTENTE**\n\n` +
                    `**Riepilogo Rete:**\n` +
                    `• **Nodi:** ${result.result?.nodes?.toLocaleString() || 'N/A'}\n` +
                    `• **Link:** ${result.result?.links?.toLocaleString() || 'N/A'}\n` +
                    `• **Zone:** ${result.result?.zones?.toLocaleString() || 'N/A'}\n\n` +
                    `**Performance ULTRA-VELOCE:**\n` +
                    `• **Tempo Query:** ${result.result?.query_time_ms?.toFixed(3) || 'N/A'}ms\n` +
                    `• **Tempo Totale:** ${result.executionTimeMs?.toFixed(3) || 'N/A'}ms\n` +
                    `• **Persistente:** ${result.result?.persistent ? '✅ SÌ' : '❌ NO'}\n\n` +
                    `*Dati recuperati da istanza VisumPy PERSISTENTE - Ultra-veloce!*`
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
      // First check persistent process health
      const healthResult = await visumController.checkInstanceHealth();
      const statsResult = await visumController.getNetworkStats();
      
      if (statsResult.success && healthResult.success) {
        const nodes = statsResult.result?.nodes || 0;
        const isHealthy = nodes > 0;
        const isPersistent = statsResult.result?.persistent === true;
        const queryTime = statsResult.result?.query_time_ms || 0;
        const performance = queryTime < 50 ? 'Ultra-Veloce 🚀' :
                           queryTime < 200 ? 'Veloce ⚡' :
                           queryTime < 1000 ? 'Normale' : 'Lenta';
        
        return {
          content: [
            {
              type: "text", 
              text: `${isHealthy ? '🚀' : '⚠️'} **Controllo Salute Istanza VisumPy PERSISTENTE**\n\n` +
                    `**Stato:** ${isHealthy ? 'ATTIVO e PERSISTENTE ✅' : 'Attenzione ⚠️'}\n` +
                    `**Performance:** ${performance}\n` +
                    `**Tempo Query:** ${queryTime.toFixed(1)}ms\n` +
                    `**Tempo Totale:** ${statsResult.executionTimeMs?.toFixed(3) || 'N/A'}ms\n` +
                    `**Persistente:** ${isPersistent ? '✅ SÌ' : '❌ NO'}\n\n` +
                    `**Dettagli Istanza:**\n` +
                    `• **Nodi Disponibili:** ${nodes.toLocaleString()}\n` +
                    `• **Link Disponibili:** ${statsResult.result?.links?.toLocaleString() || 'N/A'}\n` +
                    `• **Zone Disponibili:** ${statsResult.result?.zones?.toLocaleString() || 'N/A'}\n` +
                    `• **Richieste Processate:** ${healthResult.result?.requestCount || 0}\n` +
                    `• **Progetto Caricato:** ${healthResult.result?.projectLoaded ? '✅ SÌ' : '❌ NO'}\n\n` +
                    `*${isHealthy && isPersistent ? '🚀 Istanza persistente pronta - Performance ultra-veloce garantita!' : 'Istanza potrebbe necessitare reinizializzazione'}*`
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
// PROJECT-SPECIFIC INSTANCE MANAGEMENT TOOLS
// =============================================================================

// Start Project Instance Tool
server.tool(
  "project_start_instance",
  "Start dedicated persistent instance for specific Visum project",
  {
    projectId: z.string().describe("Project identifier (campoleone, testProject, etc.)")
  },
  async ({ projectId }) => {
    try {
      const result = await projectManager.startProjectInstance(projectId);
      
      if (result.success) {
        return {
          content: [
            {
              type: "text",
              text: `🚀 **Istanza Progetto Avviata**\n\n✅ ${result.message}\n\n📊 **Network Stats:**\n- Nodi: ${result.stats?.nodes}\n- Link: ${result.stats?.links}\n- Zone: ${result.stats?.zones}\n\n🔄 L'istanza è ora attiva e pronta per ricevere comandi.`
            }
          ]
        };
      } else {
        return {
          content: [
            {
              type: "text",
              text: `❌ **Errore Avvio Istanza**\n\n${result.message}`
            }
          ]
        };
      }
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `❌ **Errore:** ${error instanceof Error ? error.message : String(error)}`
          }
        ]
      };
    }
  }
);

// Execute Project Analysis Tool
server.tool(
  "project_execute_analysis",
  "Execute analysis on specific project instance with ultra-fast performance",
  {
    projectId: z.string().describe("Project identifier to execute analysis on"),
    analysisCode: z.string().describe("Python code to execute on the project instance"),
    description: z.string().optional().describe("Optional description of the analysis")
  },
  async ({ projectId, analysisCode, description }) => {
    try {
      const result = await projectManager.executeProjectAnalysis(projectId, analysisCode, description);
      
      if (result.success) {
        return {
          content: [
            {
              type: "text",
              text: `🚀 **Analisi Completata** (${result.projectInfo?.projectName})\n\n⚡ **Tempo esecuzione:** ${result.executionTimeMs}ms\n\n📊 **Risultati:**\n\`\`\`json\n${JSON.stringify(result.result, null, 2)}\n\`\`\``
            }
          ]
        };
      } else {
        return {
          content: [
            {
              type: "text",
              text: `❌ **Errore Analisi**\n\n${result.error}`
            }
          ]
        };
      }
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `❌ **Errore:** ${error instanceof Error ? error.message : String(error)}`
          }
        ]
      };
    }
  }
);

// Get Instances Status Tool
server.tool(
  "project_instances_status",
  "Get status of all active project instances",
  {},
  async () => {
    try {
      const status = projectManager.getInstancesStatus();
      const instanceCount = Object.keys(status).length;
      
      if (instanceCount === 0) {
        return {
          content: [
            {
              type: "text", 
              text: `📊 **Status Istanze Progetto**\n\n❌ Nessuna istanza attiva.`
            }
          ]
        };
      }

      let statusText = `📊 **Status Istanze Progetto** (${instanceCount} attive)\n\n`;
      
      for (const [projectId, info] of Object.entries(status)) {
        const uptime = Math.floor((info.uptime || 0) / 1000);
        const lastUsed = info.lastUsed ? Math.floor((Date.now() - info.lastUsed) / 1000) : 'Mai';
        
        statusText += `🔧 **${info.name}**\n`;
        statusText += `   • ID: ${projectId}\n`;
        statusText += `   • Status: ${info.isActive ? '✅ Attiva' : '❌ Inattiva'}\n`;
        statusText += `   • Uptime: ${uptime}s\n`;
        statusText += `   • Ultimo uso: ${lastUsed}s fa\n`;
        statusText += `   • Network: ${info.stats?.nodes} nodi, ${info.stats?.links} link\n\n`;
      }
      
      return {
        content: [
          {
            type: "text",
            text: statusText
          }
        ]
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `❌ **Errore:** ${error instanceof Error ? error.message : String(error)}`
          }
        ]
      };
    }
  }
);

// Project Health Check Tool
server.tool(
  "project_health_check",
  "Check health of specific project instance",
  {
    projectId: z.string().describe("Project identifier to check health for")
  },
  async ({ projectId }) => {
    try {
      const result = await projectManager.checkProjectHealth(projectId);
      
      if (result.success) {
        const health = result.health;
        const uptime = Math.floor((health.uptime || 0) / 1000);
        
        return {
          content: [
            {
              type: "text", 
              text: `💚 **Health Check - ${health.projectName}**\n\n✅ **Status:** Salutare\n🔄 **Uptime:** ${uptime}s\n⚡ **Performance:** ${health.response_time_ms}ms\n📊 **Memory Usage:** ${health.memory_mb}MB\n📂 **Progetto Caricato:** ${health.project_loaded ? '✅' : '❌'}\n🔗 **Network:** ${health.network_ready ? '✅' : '❌'}`
            }
          ]
        };
      } else {
        return {
          content: [
            {
              type: "text",
              text: `❌ **Health Check Fallito**\n\n${result.error}`
            }
          ]
        };
      }
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `❌ **Errore:** ${error instanceof Error ? error.message : String(error)}`
          }
        ]
      };
    }
  }
);

// Shutdown Project Instance Tool
server.tool(
  "project_shutdown_instance",
  "Shutdown specific project instance",
  {
    projectId: z.string().describe("Project identifier to shutdown")
  },
  async ({ projectId }) => {
    try {
      const result = await projectManager.shutdownProjectInstance(projectId);
      
      return {
        content: [
          {
            type: "text",
            text: result.success ? 
              `🔚 **Istanza Terminata**\n\n✅ ${result.message}` :
              `❌ **Errore Terminazione**\n\n${result.message}`
          }
        ]
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `❌ **Errore:** ${error instanceof Error ? error.message : String(error)}`
          }
        ]
      };
    }
  }
);

// =============================================================================
// PROJECT TCP SERVER MANAGEMENT TOOLS
// =============================================================================

// Open Project with TCP Server Tool - DEFAULT FOR OPENING PROJECTS
server.tool(
  "project_open",
  "🚀 DEFAULT TOOL for opening Visum projects. Always use this tool when asked to open, load, or launch any Visum project. Creates dedicated TCP server for ultra-fast communication.",
  {
    projectPath: z.string().describe("Full path to the Visum project file (.ver)")
  },
  async ({ projectPath }) => {
    console.error(`🚀 PROJECT_OPEN CHIAMATO: ${projectPath}`);
    console.error(`⏰ Timestamp: ${new Date().toISOString()}`);
    
    try {
      console.error(`🔄 Avvio ProjectServerManager.openProject...`);
      const result = await serverManager.openProject(projectPath);
      console.error(`✅ ProjectServerManager.openProject completato: ${result.success}`);
      
      if (result.success) {
        return {
          content: [
            {
              type: "text",
              text: `🚀 **Progetto Aperto con Server TCP**\n\n✅ ${result.message}\n\n📊 **Dettagli Server:**\n- **ID Progetto:** ${result.projectId}\n- **Nome:** ${result.serverInfo.projectName}\n- **Porta TCP:** ${result.serverInfo.port}\n- **PID:** ${result.serverInfo.pid}\n- **Status:** ${result.serverInfo.status}\n\n🔗 **Connessione Client:**\n- Host: localhost\n- Porta: ${result.serverInfo.port}\n\n⚡ Server pronto per ricevere comandi ultra-veloci dai client TCP!`
            }
          ]
        };
      } else {
        console.error(`❌ ProjectServerManager.openProject fallito: ${result.message}`);
        return {
          content: [
            {
              type: "text",
              text: `❌ **Errore Apertura Progetto**\n\n${result.message}`
            }
          ]
        };
      }
    } catch (error) {
      console.error(`💥 Eccezione in project_open: ${error instanceof Error ? error.message : String(error)}`);
      return {
        content: [
          {
            type: "text",
            text: `❌ **Errore:** ${error instanceof Error ? error.message : String(error)}`
          }
        ]
      };
    }
  }
);

// Save Project Tool
server.tool(
  "project_save",
  "Save the currently opened project in its TCP server",
  {
    projectId: z.string().describe("Project ID to save"),
    saveAs: z.string().optional().describe("Optional: Save with a different filename")
  },
  async ({ projectId, saveAs }) => {
    try {
      const result = await serverManager.saveProject(projectId, saveAs);
      
      if (result.success) {
        return {
          content: [
            {
              type: "text",
              text: `💾 **Progetto Salvato**\n\n✅ ${result.message}${saveAs ? `\n\n📁 Salvato come: ${saveAs}` : ''}`
            }
          ]
        };
      } else {
        return {
          content: [
            {
              type: "text",
              text: `❌ **Errore Salvataggio**\n\n${result.message || result.error}`
            }
          ]
        };
      }
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `❌ **Errore:** ${error instanceof Error ? error.message : String(error)}`
          }
        ]
      };
    }
  }
);

// Close Project Tool
server.tool(
  "project_close",
  "Close a project TCP server with optional save",
  {
    projectId: z.string().describe("Project ID to close"),
    save: z.boolean().optional().describe("Save project before closing (default: false)")
  },
  async ({ projectId, save }) => {
    try {
      const result = await serverManager.closeProject(projectId, save || false);
      
      if (result.success) {
        return {
          content: [
            {
              type: "text",
              text: `🔚 **Progetto Chiuso**\n\n✅ ${result.message}`
            }
          ]
        };
      } else {
        return {
          content: [
            {
              type: "text",
              text: `❌ **Errore Chiusura**\n\n${result.message}`
            }
          ]
        };
      }
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `❌ **Errore:** ${error instanceof Error ? error.message : String(error)}`
          }
        ]
      };
    }
  }
);

// Execute Project Command Tool
server.tool(
  "project_execute",
  "Execute a command on a project TCP server",
  {
    projectId: z.string().describe("Project ID to execute command on"),
    code: z.string().describe("Python code to execute in the Visum context"),
    description: z.string().describe("Description of what the code does")
  },
  async ({ projectId, code, description }) => {
    try {
      const result = await serverManager.executeCommand(projectId, code, description);
      
      if (result.success) {
        return {
          content: [
            {
              type: "text",
              text: `⚡ **Comando Eseguito**\n\n✅ ${description}\n\n📊 **Risultato:**\n\`\`\`json\n${JSON.stringify(result.result, null, 2)}\n\`\`\`\n\n⏱️ **Performance:**\n- Tempo risposta: ${result.responseTimeMs}ms\n- Esecuzione VisumPy: ${result.executionTimeMs}ms`
            }
          ]
        };
      } else {
        return {
          content: [
            {
              type: "text",
              text: `❌ **Errore Esecuzione**\n\n${result.error}`
            }
          ]
        };
      }
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `❌ **Errore:** ${error instanceof Error ? error.message : String(error)}`
          }
        ]
      };
    }
  }
);

// Project Status Tool
server.tool(
  "project_status",
  "Get status of all active project TCP servers",
  {},
  async () => {
    try {
      const projects = serverManager.getActiveProjects();
      
      if (projects.length === 0) {
        return {
          content: [
            {
              type: "text",
              text: `📊 **Status Server Progetti**\n\n❌ Nessun progetto attivo.`
            }
          ]
        };
      }
      
      let statusText = `📊 **Status Server Progetti** (${projects.length} attivi)\n\n`;
      
      projects.forEach((project, index) => {
        statusText += `**${index + 1}. ${project.projectName}**\n`;
        statusText += `   • ID: ${project.projectId}\n`;
        statusText += `   • Porta TCP: ${project.port}\n`;
        statusText += `   • PID: ${project.pid}\n`;
        statusText += `   • Status: ${project.status}\n`;
        statusText += `   • Avviato: ${project.startTime}\n`;
        statusText += `   • Path: \`${project.projectPath}\`\n\n`;
      });
      
      return {
        content: [
          {
            type: "text",
            text: statusText
          }
        ]
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `❌ **Errore:** ${error instanceof Error ? error.message : String(error)}`
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
    console.error("INFO: Initializing Sequential Thinking MCP Server with VisumPy Integration...");
    
    // Initialize storage for thinking state
    await initializeStorage();
    await loadThinkingState(); // Load saved state on startup
    
    console.error("✅ Storage and thinking state initialized");
    
    // Start MCP server
    const transport = new StdioServerTransport();
    await server.connect(transport);
    
    console.error("STARTED: Sequential Thinking MCP Server with VisumPy Integration running on stdio");
    console.error("TOOLS Available Tools:");
    console.error("   THINKING Tools:");
    console.error("   • sequential_thinking - Step-by-step reasoning");
    console.error("   • reset_thinking - Clear thinking state");
    console.error("   • get_thinking_summary - View current progress");
    console.error("   PROJECT Tools (NEW - TCP SERVERS):");
    console.error("   • project_open - 🚀 DEFAULT: Open projects with TCP server");
    console.error("   LEGACY Visum Tools:");
    console.error("   • visum_launch_project - ⚠️ DEPRECATED: Use project_open instead");
    console.error("   • visum_network_analysis - Comprehensive network analysis");
    console.error("   • visum_network_stats - Quick network statistics");
    console.error("   • visum_custom_analysis - Execute custom Python code");
    console.error("   • visum_health_check - Check VisumPy instance status");
    console.error("   PROJECT-SPECIFIC Instance Tools:");
    console.error("   • project_start_instance - Start dedicated project instance");
    console.error("   • project_execute_analysis - Execute ultra-fast analysis");
    console.error("   • project_instances_status - View all active instances");
    console.error("   • project_health_check - Check project instance health");
    console.error("   • project_shutdown_instance - Shutdown specific instance");
    
  } catch (error) {
    console.error("❌ Fatal error starting server:", error);
    process.exit(1);
  }
}

// Start the server
main();