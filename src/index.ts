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

/**
 * Sanitizza le stringhe per l'uso sicuro nel codice Python generato
 */
function sanitizeForPython(str: string): string {
  return str
    .replace(/\\/g, '\\\\')  // Escape backslashes
    .replace(/'/g, "\\'")    // Escape single quotes
    .replace(/"/g, '\\"')    // Escape double quotes
    .replace(/\n/g, '\\n')   // Escape newlines
    .replace(/\r/g, '\\r');  // Escape carriage returns
}

/**
 * Genera codice Python automaticamente basato sulla richiesta di analisi
 */
function generateAnalysisCode(analysisRequest: string, returnFormat: string): string {
  const request = analysisRequest.toLowerCase();
  const sanitizedRequest = sanitizeForPython(analysisRequest);
  
  // ============= FASE 2: ASSIGNMENT E PERCORSI =============
  
  // Flexible PrT Assignment - Supports all Visum assignment methods with user-configured VDF
  if (request.includes('prt assignment') || request.includes('car assignment') || request.includes('private transport assignment') ||
      request.includes('equilibrium assignment') || request.includes('user equilibrium') ||
      request.includes('bpr assignment') || request.includes('boyce assignment') || 
      request.includes('sue assignment') || request.includes('stochastic user equilibrium') ||
      request.includes('luce assignment') || request.includes('tapias assignment') ||
      request.includes('incremental assignment') || request.includes('msa assignment') ||
      request.includes('assignment') || request.includes('assegnazione equilibrio') ||
      request.includes('assegnazione trasporto privato')) {
    
    // Determine assignment method from request
    let assignmentMethod = 'PrTAssignmentBPR'; // default
    let methodDescription = 'BPR (Bureau of Public Roads)';
    
    if (request.includes('boyce') || request.includes('metodo boyce')) {
      assignmentMethod = 'PrTAssignmentBoyce';
      methodDescription = 'Boyce Method';
    } else if (request.includes('sue') || request.includes('stochastic')) {
      assignmentMethod = 'PrTAssignmentSUE'; 
      methodDescription = 'Stochastic User Equilibrium';
    } else if (request.includes('luce')) {
      assignmentMethod = 'PrTAssignmentLuce';
      methodDescription = 'Luce Method';
    } else if (request.includes('tapias')) {
      assignmentMethod = 'PrTAssignmentTAPIAS';
      methodDescription = 'TAPIAS Method';
    } else if (request.includes('incremental')) {
      assignmentMethod = 'PrTAssignmentIncremental';
      methodDescription = 'Incremental Assignment';
    } else if (request.includes('msa') || request.includes('successive averages')) {
      assignmentMethod = 'PrTAssignmentMSA';
      methodDescription = 'Method of Successive Averages';
    }
    
    return `
# Flexible PrT Assignment - ${methodDescription}
try:
    import json
    print(f"Starting PrT Assignment with ${methodDescription}...")
    
    # === DEMAND SEGMENT CONFIGURATION ===
    # Detect and configure demand segments for assignment
    demand_segments = []
    segment_config = {}
    
    try:
        # Get all available demand segments
        all_segments = list(visum.Net.DemandSegments)
        prt_segments = [seg for seg in all_segments if seg.GetAttValue('Code').startswith('P') or 'PrT' in seg.GetAttValue('Code')]
        
        if not prt_segments:
            # If no PrT segments found, use all segments
            prt_segments = all_segments[:3]  # Limit to first 3 to avoid overload
            
        for seg in prt_segments[:5]:  # Limit to 5 segments max
            segment_info = {
                'code': seg.GetAttValue('Code'),
                'name': seg.GetAttValue('Name') if hasattr(seg, 'GetAttValue') else seg.GetAttValue('Code'),
                'mode': seg.GetAttValue('Mode') if hasattr(seg, 'GetAttValue') else 'PrT'
            }
            demand_segments.append(segment_info)
            
        segment_config = {
            'segments_found': len(demand_segments),
            'segments_selected': demand_segments,
            'auto_detected': True
        }
        
        print(f"Found {len(demand_segments)} demand segments for assignment:")
        for seg in demand_segments:
            print(f"  - {seg['code']}: {seg['name']} ({seg['mode']})")
            
    except Exception as e:
        print(f"Warning: Could not detect demand segments: {e}")
        # Fallback: try to use default segment configuration
        segment_config = {
            'segments_found': 0,
            'segments_selected': [],
            'auto_detected': False,
            'note': 'Using Visum default segment configuration'
        }
    
    # Read Volume Delay Function (VDF) configuration from user's General Procedure Settings
    # This respects user's impedance function configuration instead of hardcoding BPR
    vdf_config = {}
    try:
        # Get VDF settings from user's project
        vdf_functions = visum.Net.Links.GetAttValues('VolCapFormula')
        vdf_types = set(vdf_functions) if vdf_functions else {'BPR'}
        vdf_config['functions_in_use'] = list(vdf_types)
        
        # Check if custom VDF parameters are defined
        try:
            vdf_params = visum.Procedures.Functions.${assignmentMethod}.GetAttValue('UseUserDefinedVDF')
            vdf_config['user_defined'] = vdf_params
        except:
            vdf_config['user_defined'] = False
            
    except Exception as e:
        print(f"Warning: Could not read VDF configuration: {e}")
        vdf_config = {'functions_in_use': ['Default'], 'user_defined': False}
    
    # === ASSIGNMENT CONFIGURATION ===
    # Configure assignment method with flexible parameters
    assignment_function = visum.Procedures.Functions.${assignmentMethod}
    
    # Set demand segments if detected
    if demand_segments and len(demand_segments) > 0:
        try:
            # Set the demand segments for assignment (Visum-specific syntax may vary)
            segment_codes = [seg['code'] for seg in demand_segments]
            print(f"Configuring assignment for segments: {', '.join(segment_codes)}")
            
            # Note: Actual segment configuration depends on Visum version and setup
            # The assignment function will use the segments configured in the network
            
        except Exception as e:
            print(f"Warning: Could not configure demand segments: {e}")
    
    # Set standard convergence parameters (user can modify these in Visum GUI)
    try:
        assignment_function.SetAttValue('MaxIter', 20)
        assignment_function.SetAttValue('GapCriterion', 0.01)
        
        # Method-specific parameters
        if '${assignmentMethod}' == 'PrTAssignmentBPR':
            assignment_function.SetAttValue('InnerIterations', 10)
        elif '${assignmentMethod}' == 'PrTAssignmentSUE':
            assignment_function.SetAttValue('Theta', 1.0)  # Perception parameter
        elif '${assignmentMethod}' == 'PrTAssignmentMSA':
            assignment_function.SetAttValue('MSAParameters', 'Default')
            
    except Exception as e:
        print(f"Warning: Could not set all parameters: {e}")
    
    # === PROCEDURE SEQUENCE INTEGRATION ===
    # Instead of executing immediately, add to Procedure Sequence for user control
    procedure_added = False
    procedure_line = 0
    
    try:
        # Get current procedure sequence
        procedure_sequence = visum.Procedures.ProcedureSequence
        current_items = procedure_sequence.Count
        
        # Add assignment procedure to sequence
        procedure_sequence.AddProcedure(visum.Procedures.Functions.${assignmentMethod})
        procedure_line = current_items + 1
        procedure_added = True
        
        print(f"✅ Assignment procedure added to Procedure Sequence at line {procedure_line}")
        print(f"📋 Procedure: {assignmentMethod} - ${methodDescription}")
        print(f"⚠️  Please review the procedure settings in Visum GUI before execution")
        print(f"🚀 To execute: Go to Procedures > Procedure Sequence > Run from line {procedure_line}")
        
    except Exception as e:
        print(f"Warning: Could not add to Procedure Sequence: {e}")
        print("Falling back to direct execution...")
        
        # Fallback: Direct execution if Procedure Sequence fails
        try:
            assignment_function.Execute()
            print("✅ Assignment executed directly (Procedure Sequence not available)")
        except Exception as exec_error:
            print(f"❌ Direct execution also failed: {exec_error}")
            raise exec_error
    
    # === RESULTS COLLECTION ===
    # Collect results regardless of execution method
    if procedure_added:
        # If added to sequence, provide preview without executing
        print("📊 Collecting network preview (assignment not yet executed)...")
        
        result = {
            'assignment_type': '${assignmentMethod}',
            'method_description': '${methodDescription}',
            'status': 'prepared_in_sequence',
            'demand_segments': segment_config,
            'vdf_configuration': vdf_config,
            'procedure_sequence': {
                'added_to_sequence': True,
                'procedure_line': procedure_line,
                'total_procedures': procedure_line,
                'execution_instructions': f'Go to Procedures > Procedure Sequence > Run from line {procedure_line}'
            },
            'user_instructions': {
                'step_1': 'Review procedure settings in Visum GUI',
                'step_2': 'Check demand segments and VDF configuration',
                'step_3': f'Execute Procedure Sequence from line {procedure_line}',
                'step_4': 'Run this analysis again after execution to see results'
            },
            'convergence_info': {
                'method_configured': '${methodDescription}',
                'uses_user_vdf': vdf_config.get('user_defined', False),
                'vdf_functions': vdf_config.get('functions_in_use', ['Default']),
                'segments_configured': len(demand_segments)
            }
        }
        
    else:
        # If executed directly, collect actual results
        print("📊 Collecting assignment results...")
        
        total_volume = sum(link.GetAttValue('VolPrT(AP)') for link in visum.Net.Links)
        total_vmt = sum(link.GetAttValue('VolPrT(AP)') * link.GetAttValue('Length') for link in visum.Net.Links)
        avg_speed = sum(link.GetAttValue('Length') / max(link.GetAttValue('tCur_PrTSys(c)'), 0.01) for link in visum.Net.Links) / visum.Net.Links.Count
        
        # Advanced congestion analysis
        congestion_levels = {'low': 0, 'medium': 0, 'high': 0, 'severe': 0}
        vc_ratios = []
        
        for link in visum.Net.Links:
            volume = link.GetAttValue('VolPrT(AP)')
            capacity = link.GetAttValue('VolCapPrT')
            if capacity > 0:
                vc_ratio = volume / capacity
                vc_ratios.append(vc_ratio)
                
                if vc_ratio < 0.5:
                    congestion_levels['low'] += 1
                elif vc_ratio < 0.8:
                    congestion_levels['medium'] += 1
                elif vc_ratio < 1.0:
                    congestion_levels['high'] += 1
                else:
                    congestion_levels['severe'] += 1
        
        # Calculate network-level performance indicators
        avg_vc = sum(vc_ratios) / len(vc_ratios) if vc_ratios else 0
        max_vc = max(vc_ratios) if vc_ratios else 0
        
        result = {
            'assignment_type': '${assignmentMethod}',
            'method_description': '${methodDescription}',
            'status': 'completed',
            'demand_segments': segment_config,
            'vdf_configuration': vdf_config,
            'network_performance': {
                'total_volume': round(total_volume, 0),
                'total_vmt': round(total_vmt, 2),
                'average_speed': round(avg_speed, 2),
                'average_vc_ratio': round(avg_vc, 3),
                'max_vc_ratio': round(max_vc, 3)
            },
            'congestion_analysis': congestion_levels,
            'convergence_info': {
                'method_used': '${methodDescription}',
                'uses_user_vdf': vdf_config.get('user_defined', False),
                'vdf_functions': vdf_config.get('functions_in_use', ['Default']),
                'segments_processed': len(demand_segments)
            }
        }
    
except Exception as e:
    result = {
        'error': str(e), 
        'assignment_type': '${assignmentMethod}',
        'method_description': '${methodDescription}', 
        'status': 'failed'
    }
`;
  }
  
  // PuT Assignment
  if (request.includes('put assignment') || request.includes('transit assignment') || request.includes('public transport assignment')) {
    return `
# PuT Assignment - Public Transport
try:
    print("Starting PuT Assignment...")
    
    # Configure PuT assignment parameters
    visum.Procedures.Functions.PuTAssignment.SetAttValue('MaxIter', 10)
    visum.Procedures.Functions.PuTAssignment.SetAttValue('ShareOfSearch', 1.0)
    visum.Procedures.Functions.PuTAssignment.SetAttValue('ConnectionScanAlgorithm', True)
    
    # Execute assignment
    visum.Procedures.Functions.PuTAssignment.Execute()
    
    # Collect results
    total_passengers = sum(line.GetAttValue('PassTransfer(AP)') for line in visum.Net.Lines if line.GetAttValue('PassTransfer(AP)') is not None)
    total_boardings = sum(stop.GetAttValue('PassBoard(AP)') for stop in visum.Net.StopPoints if stop.GetAttValue('PassBoard(AP)') is not None)
    
    result = {
        'assignment_type': 'PuT',
        'status': 'completed',
        'transit_performance': {
            'total_passengers': round(total_passengers, 0),
            'total_boardings': round(total_boardings, 0),
            'lines_count': visum.Net.Lines.Count,
            'stops_count': visum.Net.StopPoints.Count
        }
    }
    
except Exception as e:
    result = {'error': str(e), 'assignment_type': 'PuT', 'status': 'failed'}
`;
  }
  
  // Shortest Path Analysis
  if (request.includes('shortest path') || request.includes('path analysis') || request.includes('route analysis') || request.includes('percorso minimo')) {
    return `
# Shortest Path Analysis
try:
    print("Performing Shortest Path Analysis...")
    
    # Get sample zone pairs for analysis
    zones = list(visum.Net.Zones)
    if len(zones) < 2:
        raise Exception("Need at least 2 zones for path analysis")
    
    sample_paths = []
    max_samples = min(10, len(zones))
    
    for i in range(max_samples):
        for j in range(i+1, min(i+4, len(zones))):  # Limited pairs to avoid timeout
            try:
                orig_zone = zones[i].GetAttValue('No')
                dest_zone = zones[j].GetAttValue('No')
                
                # Calculate shortest path
                path_result = visum.Analysis.PrTShortestPath.CreatePrTShortestPath(orig_zone, dest_zone)
                
                sample_paths.append({
                    'origin': orig_zone,
                    'destination': dest_zone,
                    'distance_km': round(path_result.GetAttValue('Distance'), 2),
                    'travel_time_min': round(path_result.GetAttValue('tCur_PrTSys(c)'), 2),
                    'generalized_cost': round(path_result.GetAttValue('ImpPrT(c)'), 2)
                })
                
            except:
                continue
    
    result = {
        'analysis_type': 'shortest_path',
        'status': 'completed',
        'sample_paths': sample_paths,
        'total_zones': len(zones),
        'paths_analyzed': len(sample_paths)
    }
    
except Exception as e:
    result = {'error': str(e), 'analysis_type': 'shortest_path', 'status': 'failed'}
`;
  }
  
  // Skim Matrix Creation
  if (request.includes('skim matrix') || request.includes('travel time matrix') || request.includes('distance matrix') || request.includes('cost matrix')) {
    return `
# Skim Matrix Creation
try:
    print("Creating Skim Matrices...")
    
    # Travel Time Skim Matrix
    visum.Procedures.Functions.PrTCreateSkimMatrix.SetAttValue('MatrixNumber', 901)
    visum.Procedures.Functions.PrTCreateSkimMatrix.SetAttValue('Operation', 'Set')
    visum.Procedures.Functions.PrTCreateSkimMatrix.SetAttValue('MatrixName', 'TravelTime_Skim')
    visum.Procedures.Functions.PrTCreateSkimMatrix.SetAttValue('ImpedanceAttribute', 'tCur_PrTSys(c)')
    visum.Procedures.Functions.PrTCreateSkimMatrix.Execute()
    
    # Distance Skim Matrix
    visum.Procedures.Functions.PrTCreateSkimMatrix.SetAttValue('MatrixNumber', 902)
    visum.Procedures.Functions.PrTCreateSkimMatrix.SetAttValue('MatrixName', 'Distance_Skim')
    visum.Procedures.Functions.PrTCreateSkimMatrix.SetAttValue('ImpedanceAttribute', 'Distance')
    visum.Procedures.Functions.PrTCreateSkimMatrix.Execute()
    
    # Generalized Cost Skim Matrix
    visum.Procedures.Functions.PrTCreateSkimMatrix.SetAttValue('MatrixNumber', 903)
    visum.Procedures.Functions.PrTCreateSkimMatrix.SetAttValue('MatrixName', 'GenCost_Skim')
    visum.Procedures.Functions.PrTCreateSkimMatrix.SetAttValue('ImpedanceAttribute', 'ImpPrT(c)')
    visum.Procedures.Functions.PrTCreateSkimMatrix.Execute()
    
    # Get matrix statistics
    tt_matrix = visum.Net.Matrices.ItemByKey(901)
    dist_matrix = visum.Net.Matrices.ItemByKey(902)
    cost_matrix = visum.Net.Matrices.ItemByKey(903)
    
    result = {
        'analysis_type': 'skim_matrices',
        'status': 'completed',
        'matrices_created': {
            'travel_time': {
                'matrix_number': 901,
                'average_value': round(tt_matrix.GetAttValue('AvgValue'), 2),
                'max_value': round(tt_matrix.GetAttValue('MaxValue'), 2)
            },
            'distance': {
                'matrix_number': 902,
                'average_value': round(dist_matrix.GetAttValue('AvgValue'), 2),
                'max_value': round(dist_matrix.GetAttValue('MaxValue'), 2)
            },
            'generalized_cost': {
                'matrix_number': 903,
                'average_value': round(cost_matrix.GetAttValue('AvgValue'), 2),
                'max_value': round(cost_matrix.GetAttValue('MaxValue'), 2)
            }
        }
    }
    
except Exception as e:
    result = {'error': str(e), 'analysis_type': 'skim_matrices', 'status': 'failed'}
`;
  }
  
  // Demand Segments Analysis
  if (request.includes('demand segment') || request.includes('segmenti domanda') || request.includes('segments analysis') || 
      request.includes('demand configuration') || request.includes('matrix segments') || request.includes('segmenti matrice')) {
    return `
# Demand Segments Analysis
try:
    print("Analyzing Demand Segments configuration...")
    
    # Get all demand segments
    all_segments = []
    segment_details = {}
    
    try:
        segments_list = list(visum.Net.DemandSegments)
        
        for seg in segments_list:
            segment_info = {
                'code': seg.GetAttValue('Code'),
                'name': seg.GetAttValue('Name') if hasattr(seg, 'GetAttValue') else 'N/A',
                'mode': seg.GetAttValue('Mode') if hasattr(seg, 'GetAttValue') else 'Unknown',
                'demand_matrices': []
            }
            
            # Get associated matrices for this segment
            try:
                matrices = seg.GetAttValue('DemandMatrixNumbers') if hasattr(seg, 'GetAttValue') else []
                if matrices:
                    segment_info['demand_matrices'] = matrices
            except:
                segment_info['demand_matrices'] = ['Matrix info not available']
            
            all_segments.append(segment_info)
            
        # Categorize segments by mode
        prt_segments = [seg for seg in all_segments if 'P' in seg.get('mode', '') or 'PrT' in seg.get('code', '')]
        put_segments = [seg for seg in all_segments if 'Pu' in seg.get('mode', '') or 'PuT' in seg.get('code', '')]
        other_segments = [seg for seg in all_segments if seg not in prt_segments and seg not in put_segments]
        
        segment_details = {
            'total_segments': len(all_segments),
            'prt_segments': prt_segments,
            'put_segments': put_segments,
            'other_segments': other_segments,
            'segments_by_mode': {
                'private_transport': len(prt_segments),
                'public_transport': len(put_segments), 
                'other': len(other_segments)
            }
        }
        
    except Exception as e:
        print(f"Warning: Could not analyze demand segments: {e}")
        segment_details = {
            'error': str(e),
            'note': 'Could not access demand segments - check project configuration'
        }
    
    # Check matrix configuration
    matrix_info = {}
    try:
        all_matrices = list(visum.Net.Matrices)
        matrix_count = len(all_matrices)
        
        # Sample first few matrices
        sample_matrices = []
        for i, matrix in enumerate(all_matrices[:10]):  # First 10 matrices
            matrix_data = {
                'number': matrix.GetAttValue('No'),
                'name': matrix.GetAttValue('Name') if hasattr(matrix, 'GetAttValue') else f'Matrix_{i}',
                'type': matrix.GetAttValue('MatrixType') if hasattr(matrix, 'GetAttValue') else 'Unknown'
            }
            sample_matrices.append(matrix_data)
            
        matrix_info = {
            'total_matrices': matrix_count,
            'sample_matrices': sample_matrices
        }
        
    except Exception as e:
        matrix_info = {'error': f'Could not analyze matrices: {e}'}
    
    result = {
        'analysis_type': 'demand_segments',
        'status': 'completed',
        'segment_configuration': segment_details,
        'matrix_information': matrix_info,
        'recommendations': {
            'assignment_ready': len(segment_details.get('prt_segments', [])) > 0,
            'suggested_segments': [seg['code'] for seg in segment_details.get('prt_segments', [])[:3]],
            'configuration_notes': [
                'PrT segments found' if len(segment_details.get('prt_segments', [])) > 0 else 'No PrT segments detected',
                'Multiple segments available' if segment_details.get('total_segments', 0) > 1 else 'Limited segments found',
                'Matrix configuration seems valid' if not matrix_info.get('error') else 'Matrix configuration may need review'
            ]
        }
    }
    
except Exception as e:
    result = {'error': str(e), 'analysis_type': 'demand_segments', 'status': 'failed'}
`;
  }
  
  // Volume Delay Function Analysis
  if (request.includes('vdf analysis') || request.includes('volume delay function') || request.includes('impedance function') || 
      request.includes('funzione impedenza') || request.includes('funzione ritardo') || request.includes('congestion function')) {
    return `
# Volume Delay Function (VDF) Analysis
try:
    print("Analyzing Volume Delay Functions and impedance configuration...")
    
    # Get VDF configuration from links
    vdf_analysis = {}
    
    # Analyze VDF formulas used in the network
    link_vdf_formulas = visum.Net.Links.GetMultiAttValues(['No', 'VolCapFormula', 'FreeFlowSpeed', 'VolCapPrT'])
    
    vdf_types = {}
    sample_links = []
    
    for i in range(min(50, len(link_vdf_formulas[0]))):
        link_no = link_vdf_formulas[0][i]
        formula = link_vdf_formulas[1][i]
        free_speed = link_vdf_formulas[2][i]
        capacity = link_vdf_formulas[3][i]
        
        # Count VDF types
        vdf_types[formula] = vdf_types.get(formula, 0) + 1
        
        # Sample links with different VDF types
        if len(sample_links) < 20:
            sample_links.append({
                'link_no': link_no,
                'vdf_formula': formula,
                'free_flow_speed': free_speed,
                'capacity': capacity
            })
    
    # Get VDF parameters if available
    vdf_parameters = {}
    try:
        # Try to access VDF parameter settings from General Procedure Settings
        # These may be stored in different places depending on Visum version
        vdf_parameters['bpr_alpha'] = visum.Net.NetPara.GetAttValue('BPRAlpha') if hasattr(visum.Net.NetPara, 'GetAttValue') else 'N/A'
        vdf_parameters['bpr_beta'] = visum.Net.NetPara.GetAttValue('BPRBeta') if hasattr(visum.Net.NetPara, 'GetAttValue') else 'N/A'
    except:
        vdf_parameters = {'note': 'VDF parameters configured in General Procedure Settings'}
    
    result = {
        'analysis_type': 'vdf_analysis',
        'status': 'completed',
        'vdf_distribution': vdf_types,
        'total_links_analyzed': len(link_vdf_formulas[0]),
        'vdf_parameters': vdf_parameters,
        'sample_links': sample_links,
        'supported_vdf_types': [
            'BPR (Bureau of Public Roads)',
            'Davidson Function', 
            'Akcelik Function',
            'Custom VDF',
            'Conical Function',
            'Polynomial Function'
        ]
    }
    
except Exception as e:
    result = {'error': str(e), 'analysis_type': 'vdf_analysis', 'status': 'failed'}
`;
  }
  
  // Procedure Sequence Management
  if (request.includes('procedure sequence') || request.includes('sequence management') || request.includes('procedura sequenza') || 
      request.includes('check sequence') || request.includes('execute sequence') || request.includes('run sequence')) {
    return `
# Procedure Sequence Management
try:
    print("Managing Procedure Sequence...")
    
    # Get current procedure sequence
    procedure_sequence = visum.Procedures.ProcedureSequence
    sequence_count = procedure_sequence.Count
    
    # List all procedures in sequence
    sequence_procedures = []
    for i in range(sequence_count):
        try:
            proc_item = procedure_sequence.Item(i)
            proc_info = {
                'line_number': i + 1,
                'procedure_name': proc_item.GetAttValue('ProcedureName') if hasattr(proc_item, 'GetAttValue') else f'Procedure_{i+1}',
                'procedure_type': str(type(proc_item).__name__),
                'is_enabled': proc_item.GetAttValue('Enabled') if hasattr(proc_item, 'GetAttValue') else True
            }
            sequence_procedures.append(proc_info)
        except Exception as e:
            sequence_procedures.append({
                'line_number': i + 1,
                'procedure_name': f'Unknown_Procedure_{i+1}',
                'error': str(e)
            })
    
    # Check for assignment procedures
    assignment_procedures = [proc for proc in sequence_procedures if 'Assignment' in proc.get('procedure_name', '')]
    
    # Execution instructions
    execution_instructions = {
        'manual_execution': 'Go to Procedures > Procedure Sequence in Visum GUI',
        'from_line_execution': f'Use "Execute from line X" to run specific procedures',
        'full_sequence': 'Use "Execute All" to run entire sequence',
        'selective_execution': 'Enable/disable procedures as needed before execution'
    }
    
    result = {
        'analysis_type': 'procedure_sequence',
        'status': 'completed',
        'sequence_info': {
            'total_procedures': sequence_count,
            'procedures_list': sequence_procedures,
            'assignment_procedures_found': len(assignment_procedures),
            'assignment_procedures': assignment_procedures
        },
        'execution_options': execution_instructions,
        'user_actions': {
            'step_1': 'Review procedures in Visum GUI: Procedures > Procedure Sequence',
            'step_2': 'Enable/disable procedures as needed',
            'step_3': 'Execute selected procedures using GUI controls',
            'step_4': 'Monitor execution progress in Visum'
        }
    }
    
except Exception as e:
    result = {'error': str(e), 'analysis_type': 'procedure_sequence', 'status': 'failed'}
`;
  }
  
  // Critical Link Analysis (CLA) with Flow Bundle
  if (request.includes('critical link') || request.includes('cla analysis') || request.includes('flow bundle') || request.includes('network vulnerability') || request.includes('bottleneck analysis')) {
    return `
# Critical Link Analysis with Flow Bundle
try:
    print("Performing Critical Link Analysis...")
    
    # Execute Flow Bundle analysis
    visum.Procedures.Functions.FlowBundle.SetAttValue('FlowBundleType', 'Volume')
    visum.Procedures.Functions.FlowBundle.SetAttValue('MinVolume', 100)  # Minimum volume threshold
    visum.Procedures.Functions.FlowBundle.Execute()
    
    # Analyze link criticality
    critical_links = []
    total_volume = sum(link.GetAttValue('VolPrT(AP)') for link in visum.Net.Links)
    
    for link in visum.Net.Links:
        volume = link.GetAttValue('VolPrT(AP)')
        capacity = link.GetAttValue('VolCapPrT')
        length = link.GetAttValue('Length')
        
        if volume > 0 and capacity > 0:
            vc_ratio = volume / capacity
            volume_share = volume / total_volume if total_volume > 0 else 0
            criticality_index = vc_ratio * volume_share * 100  # Combined criticality
            
            if criticality_index > 0.1:  # Threshold for critical links
                critical_links.append({
                    'from_node': link.GetAttValue('FromNodeNo'),
                    'to_node': link.GetAttValue('ToNodeNo'),
                    'volume': round(volume, 0),
                    'capacity': round(capacity, 0),
                    'vc_ratio': round(vc_ratio, 3),
                    'length_km': round(length, 2),
                    'volume_share_pct': round(volume_share * 100, 2),
                    'criticality_index': round(criticality_index, 3)
                })
    
    # Sort by criticality
    critical_links.sort(key=lambda x: x['criticality_index'], reverse=True)
    
    # Network vulnerability metrics
    high_vc_links = sum(1 for link in visum.Net.Links if link.GetAttValue('VolCapPrT') > 0 and link.GetAttValue('VolPrT(AP)') / link.GetAttValue('VolCapPrT') > 0.8)
    overloaded_links = sum(1 for link in visum.Net.Links if link.GetAttValue('VolCapPrT') > 0 and link.GetAttValue('VolPrT(AP)') / link.GetAttValue('VolCapPrT') > 1.0)
    
    result = {
        'analysis_type': 'critical_link_analysis',
        'status': 'completed',
        'network_vulnerability': {
            'total_links': visum.Net.Links.Count,
            'critical_links_count': len(critical_links),
            'high_vc_links': high_vc_links,
            'overloaded_links': overloaded_links,
            'vulnerability_ratio': round(len(critical_links) / visum.Net.Links.Count, 3)
        },
        'top_critical_links': critical_links[:10],  # Top 10 most critical
        'flow_concentration': {
            'total_network_volume': round(total_volume, 0),
            'top_10_links_volume': round(sum(link['volume'] for link in critical_links[:10]), 0)
        }
    }
    
except Exception as e:
    result = {'error': str(e), 'analysis_type': 'critical_link_analysis', 'status': 'failed'}
`;
  }
  
  // ============= FASE 1: STATISTICHE BASE (EXISTING) =============
  
  // Network Statistics
  if (request.includes('statistic') || request.includes('network') || request.includes('count') || request.includes('summary')) {
    return `
# Network Statistics Analysis
try:
    num_nodes = visum.Net.Nodes.Count
    num_links = visum.Net.Links.Count
    num_zones = visum.Net.Zones.Count
    num_connectors = getattr(visum.Net, 'Connectors', None)
    connector_count = num_connectors.Count if num_connectors else 0
    
    result = {
        'network_summary': {
            'nodes': num_nodes,
            'links': num_links,
            'zones': num_zones,
            'connectors': connector_count
        },
        'network_density': round(num_links / max((num_nodes * (num_nodes - 1) / 2), 1), 6),
        'avg_degree': round((num_links * 2) / max(num_nodes, 1), 2)
    }
except Exception as e:
    result = {'error': str(e)}
`;
  }
  
  // Node Analysis
  if (request.includes('node') || request.includes('nod')) {
    const sampleSize = returnFormat === 'detailed' ? '100' : '10';
    return `
# Node Distribution Analysis
try:
    nodes_data = visum.Net.Nodes.GetMultiAttValues(['No', 'XCoord', 'YCoord'])
    
    total_nodes = len(nodes_data[0])
    sample_size = min(${sampleSize}, total_nodes)
    
    # Sample nodes
    sample_nodes = []
    for i in range(sample_size):
        sample_nodes.append({
            'id': nodes_data[0][i],
            'x': nodes_data[1][i],
            'y': nodes_data[2][i]
        })
    
    # Bounding box
    x_coords = [x for x in nodes_data[1] if x is not None]
    y_coords = [y for y in nodes_data[2] if y is not None]
    
    result = {
        'total_nodes': total_nodes,
        'sample_nodes': sample_nodes,
        'bounding_box': {
            'min_x': min(x_coords) if x_coords else None,
            'max_x': max(x_coords) if x_coords else None,
            'min_y': min(y_coords) if y_coords else None,
            'max_y': max(y_coords) if y_coords else None
        } if x_coords and y_coords else None
    }
except Exception as e:
    result = {'error': str(e)}
`;
  }
  
  // Link Analysis
  if (request.includes('link') || request.includes('edge') || request.includes('connection')) {
    const sampleSize = returnFormat === 'detailed' ? '50' : '10';
    return `
# Link Analysis
try:
    links_data = visum.Net.Links.GetMultiAttValues(['No', 'FromNodeNo', 'ToNodeNo', 'Length'])
    
    total_links = len(links_data[0])
    sample_size = min(${sampleSize}, total_links)
    
    sample_links = []
    lengths = []
    
    for i in range(sample_size):
        length = links_data[3][i]
        sample_links.append({
            'id': links_data[0][i],
            'from_node': links_data[1][i],
            'to_node': links_data[2][i],
            'length': length
        })
        if length is not None:
            lengths.append(length)
    
    result = {
        'total_links': total_links,
        'sample_links': sample_links,
        'length_stats': {
            'avg_length': round(sum(lengths) / len(lengths), 2) if lengths else None,
            'min_length': min(lengths) if lengths else None,
            'max_length': max(lengths) if lengths else None,
            'total_length': round(sum(lengths), 2) if lengths else None
        } if lengths else None
    }
except Exception as e:
    result = {'error': str(e)}
`;
  }
  
  // Zone Analysis
  if (request.includes('zone') || request.includes('zon')) {
    return `
# Zone Analysis
try:
    zones_data = visum.Net.Zones.GetMultiAttValues(['No', 'XCoord', 'YCoord'])
    
    total_zones = len(zones_data[0])
    sample_size = min(20, total_zones)
    
    sample_zones = []
    for i in range(sample_size):
        sample_zones.append({
            'id': zones_data[0][i],
            'x': zones_data[1][i],
            'y': zones_data[2][i]
        })
    
    result = {
        'total_zones': total_zones,
        'sample_zones': sample_zones
    }
except Exception as e:
    result = {'error': str(e)}
`;
  }
  
  // Default: comprehensive analysis
  return `
# Comprehensive Network Analysis
try:
    # Basic counts
    num_nodes = visum.Net.Nodes.Count
    num_links = visum.Net.Links.Count
    num_zones = visum.Net.Zones.Count
    
    # Sample data
    if num_nodes > 0:
        nodes_sample = visum.Net.Nodes.GetMultiAttValues(['No', 'XCoord', 'YCoord'])
        sample_nodes = [{
            'id': nodes_sample[0][i],
            'x': nodes_sample[1][i],
            'y': nodes_sample[2][i]
        } for i in range(min(5, len(nodes_sample[0])))]
    else:
        sample_nodes = []
    
    result = {
        'analysis_type': 'comprehensive',
        'request': '${sanitizedRequest}',
        'network_summary': {
            'nodes': num_nodes,
            'links': num_links,
            'zones': num_zones
        },
        'sample_data': {
            'nodes': sample_nodes
        }
    }
except Exception as e:
    result = {'error': str(e), 'analysis_type': 'failed', 'request': '${sanitizedRequest}'}
`;
}

// Execute Project Analysis Tool
server.tool(
  "project_execute_analysis",
  "Execute intelligent analysis on specific project instance with ultra-fast performance. Automatically generates Python code based on analysis request.",
  {
    projectId: z.string().describe("Project identifier to execute analysis on"),
    analysisRequest: z.string().describe("Natural language description of the analysis you want to perform (e.g., 'get network statistics', 'analyze node distribution', 'check link lengths')"),
    returnFormat: z.enum(["summary", "detailed", "raw"]).optional().default("summary").describe("Format of results: summary (key metrics), detailed (comprehensive), raw (full data)")
  },
  async ({ projectId, analysisRequest, returnFormat = "summary" }) => {
    try {
      // Generate appropriate Python code based on the analysis request
      const analysisCode = generateAnalysisCode(analysisRequest, returnFormat);
      
      const result = await projectManager.executeProjectAnalysis(projectId, analysisCode, analysisRequest);
      
      if (result.success) {
        return {
          content: [
            {
              type: "text",
              text: `🚀 **Analisi Completata** (${result.projectInfo?.projectName})\n\n📋 **Richiesta:** ${analysisRequest}\n\n⚡ **Tempo esecuzione:** ${result.executionTimeMs}ms\n\n📊 **Risultati:**\n\`\`\`json\n${JSON.stringify(result.result, null, 2)}\n\`\`\``
            }
          ]
        };
      } else {
        return {
          content: [
            {
              type: "text",
              text: `❌ **Errore Analisi**\n\n**Richiesta:** ${analysisRequest}\n**Errore:** ${result.error}`
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

// Instance Diagnosis and Repair Tool - ALWAYS RUN FIRST WHEN ERRORS OCCUR
server.tool(
  "instance_diagnosis",
  "🔧 DIAGNOSTIC TOOL: Run this first when encountering errors. Diagnoses and repairs existing Visum instances instead of creating new ones.",
  {},
  async () => {
    try {
      console.error(`🔧 INSTANCE_DIAGNOSIS CHIAMATO: ${new Date().toISOString()}`);
      
      // Check all active instances and their health
      const instancesStatus = projectManager.getInstancesStatus();
      const activeProjects = serverManager.getActiveProjects();
      
      const diagnosis = {
        persistent_controller: { status: 'unknown', health: 'unknown' },
        project_instances: Object.keys(instancesStatus).length,
        tcp_servers: activeProjects.length,
        issues_found: [] as string[],
        repair_actions: [] as string[],
        recommendations: [] as string[]
      };
      
      // Test persistent controller
      try {
        const healthResult = await visumController.checkInstanceHealth();
        const statsResult = await visumController.getNetworkStats();
        
        if (healthResult.success && statsResult.success) {
          diagnosis.persistent_controller.status = 'healthy';
          diagnosis.persistent_controller.health = 'good';
          diagnosis.recommendations.push('✅ Persistent controller is healthy - use visum_custom_analysis or visum_network_stats');
        } else {
          diagnosis.persistent_controller.status = 'unhealthy';
          diagnosis.persistent_controller.health = 'poor';
          diagnosis.issues_found.push('❌ Persistent controller not responding');
          diagnosis.repair_actions.push('🔧 Restart persistent controller recommended');
        }
      } catch (error) {
        diagnosis.persistent_controller.status = 'error';
        diagnosis.issues_found.push(`❌ Persistent controller error: ${error instanceof Error ? error.message : String(error)}`);
        diagnosis.repair_actions.push('🔧 Reinitialize persistent controller');
      }
      
      // Check project instances
      for (const [projectId, info] of Object.entries(instancesStatus)) {
        try {
          const healthCheck = await projectManager.checkProjectHealth(projectId);
          if (!healthCheck.success) {
            diagnosis.issues_found.push(`❌ Project instance '${projectId}' unhealthy: ${healthCheck.error}`);
            diagnosis.repair_actions.push(`🔧 Consider shutting down and restarting instance '${projectId}'`);
          }
        } catch (error) {
          diagnosis.issues_found.push(`❌ Cannot check instance '${projectId}': ${error instanceof Error ? error.message : String(error)}`);
          diagnosis.repair_actions.push(`🔧 Force shutdown instance '${projectId}' if necessary`);
        }
      }
      
      // Check TCP servers
      activeProjects.forEach(project => {
        if (project.status !== 'active') {
          diagnosis.issues_found.push(`❌ TCP server for '${project.projectName}' status: ${project.status}`);
          diagnosis.repair_actions.push(`🔧 Restart TCP server for project '${project.projectId}'`);
        }
      });
      
      // Provide clear recommendations
      if (diagnosis.issues_found.length === 0) {
        diagnosis.recommendations.push('✅ All systems healthy - proceed with normal operations');
        diagnosis.recommendations.push('💡 Use existing instances instead of creating new ones');
      } else {
        diagnosis.recommendations.push('⚠️ Issues found - repair before creating new instances');
        diagnosis.recommendations.push('🛠️ Use repair actions listed above');
        diagnosis.recommendations.push('🚫 AVOID creating new instances until issues are resolved');
      }
      
      return {
        content: [
          {
            type: "text",
            text: `🔧 **Diagnosi Istanze Visum**\n\n` +
                  `**Controller Persistente:** ${diagnosis.persistent_controller.status}\n` +
                  `**Istanze Progetto:** ${diagnosis.project_instances}\n` +
                  `**Server TCP:** ${diagnosis.tcp_servers}\n\n` +
                  
                  `**❌ Problemi Rilevati (${diagnosis.issues_found.length}):**\n` +
                  (diagnosis.issues_found.length > 0 ? 
                    diagnosis.issues_found.map(issue => `• ${issue}`).join('\n') + '\n\n' : 
                    '• Nessun problema rilevato\n\n') +
                    
                  `**🔧 Azioni Riparazione:**\n` +
                  (diagnosis.repair_actions.length > 0 ?
                    diagnosis.repair_actions.map(action => `• ${action}`).join('\n') + '\n\n' :
                    '• Nessuna riparazione necessaria\n\n') +
                    
                  `**💡 Raccomandazioni:**\n` +
                  diagnosis.recommendations.map(rec => `• ${rec}`).join('\n') + '\n\n' +
                  
                  `**🚨 IMPORTANTE:** Prima di aprire nuove istanze, risolvi i problemi sopra elencati!`
          }
        ]
      };
      
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `❌ **Errore Diagnosi:** ${error instanceof Error ? error.message : String(error)}\n\n` +
                  `**Suggerimento:** Prova a riavviare completamente il server MCP.`
          }
        ]
      };
    }
  }
);

// Instance Cleanup and Repair Tool
server.tool(
  "instance_cleanup",
  "🧹 CLEANUP TOOL: Safely shutdown problematic instances and clean up resources. Use after instance_diagnosis identifies issues.",
  {
    force: z.boolean().optional().default(false).describe("Force cleanup even if instances appear healthy")
  },
  async ({ force = false }) => {
    try {
      console.error(`🧹 INSTANCE_CLEANUP CHIAMATO: force=${force}, ${new Date().toISOString()}`);
      
      const cleanupResults = {
        instances_shutdown: 0,
        tcp_servers_closed: 0,
        errors_encountered: [] as string[],
        actions_taken: [] as string[]
      };
      
      // Get current state
      const instancesStatus = projectManager.getInstancesStatus();
      const activeProjects = serverManager.getActiveProjects();
      
      // Shutdown problematic project instances
      for (const [projectId, info] of Object.entries(instancesStatus)) {
        try {
          const shouldCleanup = force || !info.isActive;
          if (shouldCleanup) {
            const shutdownResult = await projectManager.shutdownProjectInstance(projectId);
            if (shutdownResult.success) {
              cleanupResults.instances_shutdown++;
              cleanupResults.actions_taken.push(`✅ Shutdown project instance: ${projectId}`);
            } else {
              cleanupResults.errors_encountered.push(`❌ Failed to shutdown ${projectId}: ${shutdownResult.message}`);
            }
          }
        } catch (error) {
          cleanupResults.errors_encountered.push(`❌ Error shutting down ${projectId}: ${error instanceof Error ? error.message : String(error)}`);
        }
      }
      
      // Close problematic TCP servers
      for (const project of activeProjects) {
        try {
          const shouldClose = force || project.status !== 'active';
          if (shouldClose) {
            const closeResult = await serverManager.closeProject(project.projectId, false);
            if (closeResult.success) {
              cleanupResults.tcp_servers_closed++;
              cleanupResults.actions_taken.push(`✅ Closed TCP server: ${project.projectName}`);
            } else {
              cleanupResults.errors_encountered.push(`❌ Failed to close TCP server ${project.projectId}: ${closeResult.message}`);
            }
          }
        } catch (error) {
          cleanupResults.errors_encountered.push(`❌ Error closing TCP server ${project.projectId}: ${error instanceof Error ? error.message : String(error)}`);
        }
      }
      
      // Reset persistent controller if forced or if there were issues
      if (force) {
        try {
          // Note: We don't have a direct reset method, but we can check if it needs reinitialization
          cleanupResults.actions_taken.push(`ℹ️ Persistent controller status checked (reset not available)`);
        } catch (error) {
          cleanupResults.errors_encountered.push(`❌ Error checking persistent controller: ${error instanceof Error ? error.message : String(error)}`);
        }
      }
      
      const success = cleanupResults.errors_encountered.length === 0;
      const totalActions = cleanupResults.instances_shutdown + cleanupResults.tcp_servers_closed;
      
      return {
        content: [
          {
            type: "text",
            text: `🧹 **Pulizia Istanze Completata**\n\n` +
                  `**Risultati:**\n` +
                  `• Istanze chiuse: ${cleanupResults.instances_shutdown}\n` +
                  `• Server TCP chiusi: ${cleanupResults.tcp_servers_closed}\n` +
                  `• Errori riscontrati: ${cleanupResults.errors_encountered.length}\n\n` +
                  
                  `**Azioni Eseguite:**\n` +
                  (cleanupResults.actions_taken.length > 0 ?
                    cleanupResults.actions_taken.map(action => `• ${action}`).join('\n') + '\n\n' :
                    '• Nessuna azione necessaria\n\n') +
                    
                  (cleanupResults.errors_encountered.length > 0 ?
                    `**❌ Errori:**\n${cleanupResults.errors_encountered.map(err => `• ${err}`).join('\n')}\n\n` : '') +
                    
                  `**Status:** ${success ? '✅ Pulizia completata con successo' : '⚠️ Pulizia completata con alcuni errori'}\n\n` +
                  `**Prossimo passo:** ${totalActions > 0 ? 'Ora puoi procedere con operazioni normali' : 'Nessuna pulizia necessaria'}`
          }
        ]
      };
      
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `❌ **Errore durante pulizia:** ${error instanceof Error ? error.message : String(error)}`
          }
        ]
      };
    }
  }
);

// Open Project with TCP Server Tool - DEFAULT FOR OPENING PROJECTS
server.tool(
  "project_open",
  "🚀 DEFAULT TOOL for opening Visum projects. Always use this tool when asked to open, load, or launch any Visum project. Creates dedicated TCP server for ultra-fast communication. ⚠️ If you encounter errors, run 'instance_diagnosis' first!",
  {
    projectPath: z.string().describe("Full path to the Visum project file (.ver)")
  },
  async ({ projectPath }) => {
    console.error(`🚀 PROJECT_OPEN CHIAMATO: ${projectPath}`);
    console.error(`⏰ Timestamp: ${new Date().toISOString()}`);
    
    try {
      // Pre-flight check: warn if there are existing instances that might conflict
      const instancesStatus = projectManager.getInstancesStatus();
      const activeProjects = serverManager.getActiveProjects();
      const totalExistingInstances = Object.keys(instancesStatus).length + activeProjects.length;
      
      if (totalExistingInstances > 2) {
        console.error(`⚠️ WARNING: ${totalExistingInstances} existing instances detected. Consider running instance_diagnosis first.`);
        
        return {
          content: [
            {
              type: "text",
              text: `⚠️ **Troppe Istanze Attive**\n\n` +
                    `Rilevate **${totalExistingInstances} istanze** già attive:\n` +
                    `• Istanze progetto: ${Object.keys(instancesStatus).length}\n` +
                    `• Server TCP: ${activeProjects.length}\n\n` +
                    `**🔧 RACCOMANDAZIONE:**\n` +
                    `Prima di aprire un nuovo progetto, esegui:\n` +
                    `1. \`instance_diagnosis\` - Per verificare lo stato delle istanze\n` +
                    `2. \`instance_cleanup\` - Se necessario, per pulire istanze problematiche\n` +
                    `3. Poi riprova ad aprire il progetto\n\n` +
                    `**� Questo previene conflitti e migliorare le performance!**`
            }
          ]
        };
      }
      
      console.error(`�🔄 Avvio ProjectServerManager.openProject...`);
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
              text: `❌ **Errore Apertura Progetto**\n\n${result.message}\n\n**🔧 Suggerimenti:**\n• Verifica che il file .ver esista\n• Controlla che Visum sia installato correttamente\n• Esegui \`instance_diagnosis\` per verificare lo stato del sistema`
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
            text: `❌ **Errore:** ${error instanceof Error ? error.message : String(error)}\n\n**🔧 Prima di riprovare:**\n• Esegui \`instance_diagnosis\` per identificare problemi\n• Considera \`instance_cleanup\` se ci sono istanze problematiche`
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
    console.error("   DIAGNOSTIC Tools (NEW - ERROR PREVENTION):");
    console.error("   • instance_diagnosis - 🔧 Diagnose existing instances instead of creating new ones");
    console.error("   • instance_cleanup - 🧹 Clean up problematic instances safely");
    console.error("   PROJECT Tools (TCP SERVERS):");
    console.error("   • project_open - 🚀 DEFAULT: Open projects (with pre-flight checks)");
    console.error("   • project_save - Save project via TCP server");
    console.error("   • project_close - Close project TCP server");
    console.error("   • project_execute - Execute commands via TCP");
    console.error("   • project_status - View all active TCP servers");
    console.error("   PROJECT-SPECIFIC Instance Tools:");
    console.error("   • project_start_instance - Start dedicated project instance");
    console.error("   • project_execute_analysis - Execute ultra-fast analysis");
    console.error("   • project_instances_status - View all active instances");
    console.error("   • project_health_check - Check project instance health");
    console.error("   • project_shutdown_instance - Shutdown specific instance");
    console.error("   ⚠️  IMPORTANT: Run 'instance_diagnosis' FIRST when encountering errors!");
    
  } catch (error) {
    console.error("❌ Fatal error starting server:", error);
    process.exit(1);
  }
}

// Start the server
main();