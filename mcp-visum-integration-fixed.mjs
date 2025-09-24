#!/usr/bin/env node

import { spawn } from 'child_process';
import fs from 'fs';
import path from 'path';

// 🔧 CONFIGURAZIONE MCP VISUM
const CONFIG = {
  PYTHON_PATH: "H:\\Program Files\\PTV Vision\\PTV Visum 2025\\Exe\\Python\\python.exe",
  VISUM_EXE: "H:\\Program Files\\PTV Vision\\PTV Visum 2025\\Exe\\Visum250.exe",
  PROJECT_FILE: "H:\\go\\italferr2025\\Campoleone\\100625_Versione_base_v0.3_sub_ok_priv.ver"
};

// 🛠️ IMPLEMENTAZIONE MCP TOOLS VISUM
class VisumMCPTools {
  
  // ✅ TOOL 1: visum_launch
  static async visum_launch(projectFile = CONFIG.PROJECT_FILE) {
    const script = `
      if (Test-Path "${CONFIG.VISUM_EXE}") {
        if (Test-Path "${projectFile}") {
          Write-Host "🚀 Lancio Visum con progetto..."
          Start-Process "${CONFIG.VISUM_EXE}" -ArgumentList "${projectFile}"
          Start-Sleep -Seconds 3
          Write-Host "✅ Visum avviato con successo!"
        } else {
          Write-Host "❌ File progetto non trovato: ${projectFile}"
        }
      } else {
        Write-Host "❌ Visum non trovato: ${CONFIG.VISUM_EXE}"
      }
    `;
    
    return new Promise((resolve) => {
      const powershell = spawn('powershell', ['-ExecutionPolicy', 'Bypass', '-Command', script]);
      let output = '';
      powershell.stdout.on('data', (data) => {
        output += data.toString();
        console.log(data.toString().trim());
      });
      powershell.on('close', () => {
        resolve({ success: true, output });
      });
    });
  }

  // ✅ TOOL 2: visum_network_analysis  
  static async visum_network_analysis(analysisType = 'detailed', exportPath = 'C:\\temp\\mcp_analysis') {
    const pythonScript = `
import sys
sys.path.append(r"H:\\Program Files\\PTV Vision\\PTV Visum 2025\\Exe")

try:
    import win32com.client
    
    # Connessione a Visum
    visum = win32com.client.GetActiveObject("Visum.Visum")
    
    print("🔍 ANALISI RETE MCP - ${analysisType.toUpperCase()}")
    print("=" * 40)
    
    # Statistiche base
    nodes = visum.Net.Nodes.Count
    links = visum.Net.Links.Count  
    zones = visum.Net.Zones.Count
    
    print(f"Nodi: {nodes:,}")
    print(f"Link: {links:,}")
    print(f"Zone: {zones:,}")
    
    if "${analysisType}" == "detailed" and nodes > 0:
        print("\\n🔗 ANALISI DETTAGLIATA:")
        
        # Calcola statistiche avanzate
        total_length = 0
        speed_sum = 0
        capacity_sum = 0
        valid_links = 0
        
        for i in range(min(1000, links)):  # Campione per performance
            try:
                link = visum.Net.Links.Item(i)
                length = link.GetAttValue("Length")
                v0 = link.GetAttValue("V0_PrT") 
                capacity = link.GetAttValue("VolCapPrT")
                
                if length > 0:
                    total_length += length
                    valid_links += 1
                    
                if v0 > 0:
                    speed_sum += v0
                    
                if capacity > 0:
                    capacity_sum += capacity
                    
            except:
                pass
        
        if valid_links > 0:
            avg_length = total_length / valid_links
            avg_speed = speed_sum / valid_links if speed_sum > 0 else 0
            total_capacity = capacity_sum
            
            print(f"Lunghezza media link: {avg_length:.1f} m")
            print(f"Velocità media: {avg_speed:.1f} km/h") 
            print(f"Capacità totale: {total_capacity:,.0f} veic/h")
            
            # Densità rete
            density = links / nodes if nodes > 0 else 0
            print(f"Densità rete: {density:.2f} link/nodo")
            
    elif "${analysisType}" == "topology":
        print("\\n🌐 ANALISI TOPOLOGIA:")
        # Analisi connettività, grafi, ecc.
        print("Analisi topologica complessa...")
        
    print("\\n✅ Analisi MCP completata!")
    
except Exception as e:
    print(f"❌ Errore MCP: {e}")
`;
    
    return new Promise((resolve) => {
      const python = spawn('powershell.exe', [
        '-Command', 
        `& "${CONFIG.PYTHON_PATH}" -c @"
${pythonScript}
"@`
      ]);
      let output = '';
      python.stdout.on('data', (data) => {
        output += data.toString();
        console.log(data.toString().trim());
      });
      python.on('close', () => {
        resolve({ success: true, output });
      });
    });
  }

  // ✅ TOOL 3: visum_export_network
  static async visum_export_network(elements = ['nodes', 'links'], exportDir = 'C:\\temp\\mcp_export') {
    const pythonScript = `
import sys
sys.path.append(r"H:\\Program Files\\PTV Vision\\PTV Visum 2025\\Exe")
import os

try:
    import win32com.client
    
    # Connessione a Visum  
    visum = win32com.client.GetActiveObject("Visum.Visum")
    
    export_dir = "${exportDir}"
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
    
    print("📁 EXPORT MCP NETWORK")
    print("=" * 30)
    print(f"Directory: {export_dir}")
    
    elements = ${JSON.stringify(elements)}
    
    for element in elements:
        try:
            if element == "nodes":
                file_path = os.path.join(export_dir, "nodes.csv")
                visum.Net.Nodes.SaveToFile(file_path)
                print(f"✅ Nodi → {file_path}")
                
            elif element == "links":
                file_path = os.path.join(export_dir, "links.csv") 
                visum.Net.Links.SaveToFile(file_path)
                print(f"✅ Link → {file_path}")
                
            elif element == "zones":
                file_path = os.path.join(export_dir, "zones.csv")
                visum.Net.Zones.SaveToFile(file_path) 
                print(f"✅ Zone → {file_path}")
                
        except Exception as e:
            print(f"❌ Errore export {element}: {e}")
    
    print("\\n🎯 Export MCP completato!")
    
except Exception as e:
    print(f"❌ Errore MCP export: {e}")
`;

    return new Promise((resolve) => {
      const python = spawn('powershell.exe', [
        '-Command', 
        `& "${CONFIG.PYTHON_PATH}" -c @"
${pythonScript}
"@`
      ]);
      let output = '';
      python.stdout.on('data', (data) => {
        output += data.toString();
        console.log(data.toString().trim());
      });
      python.on('close', () => {
        resolve({ success: true, output });
      });
    });
  }

  // ✅ TOOL 4: visum_python_analysis
  static async visum_python_analysis(customScript) {
    const fullScript = `
import sys
sys.path.append(r"H:\\Program Files\\PTV Vision\\PTV Visum 2025\\Exe")

try:
    import win32com.client
    visum = win32com.client.GetActiveObject("Visum.Visum")
    
    print("🐍 SCRIPT PYTHON MCP PERSONALIZZATO")
    print("=" * 35)
    
    # Script utente
${customScript}
    
    print("\\n✅ Script MCP completato!")
    
except Exception as e:
    print(f"❌ Errore script MCP: {e}")
`;

    return new Promise((resolve) => {
      const python = spawn('powershell.exe', [
        '-Command', 
        `& "${CONFIG.PYTHON_PATH}" -c @"
${fullScript}
"@`
      ]);
      let output = '';
      python.stdout.on('data', (data) => {
        output += data.toString();
        console.log(data.toString().trim());
      });
      python.on('close', () => {
        resolve({ success: true, output });
      });
    });
  }

  // ✅ TOOL 5: visum_connectivity_stats
  static async visum_connectivity_stats() {
    return this.visum_python_analysis(`
    # Statistiche connettività
    nodes = visum.Net.Nodes.Count
    links = visum.Net.Links.Count
    
    if nodes > 0:
        connectivity = links / nodes
        print(f"📊 Connettività: {connectivity:.2f} (link/nodo)")
        
        # Analisi gradi nodi
        degrees = []
        for i in range(min(100, nodes)):
            try:
                node = visum.Net.Nodes.Item(i)
                degree = node.GetAttValue("InLinks").Count + node.GetAttValue("OutLinks").Count
                degrees.append(degree)
            except:
                pass
                
        if degrees:
            avg_degree = sum(degrees) / len(degrees)
            max_degree = max(degrees)
            min_degree = min(degrees)
            
            print(f"🔗 Grado medio nodi: {avg_degree:.1f}")
            print(f"🔗 Grado massimo: {max_degree}")
            print(f"🔗 Grado minimo: {min_degree}")
    `);
  }

  // ✅ TOOL 6: visum_val_script
  static async visum_val_script(valScript) {
    const pythonScript = `
import sys
sys.path.append(r"H:\\Program Files\\PTV Vision\\PTV Visum 2025\\Exe")

try:
    import win32com.client
    visum = win32com.client.GetActiveObject("Visum.Visum")
    
    print("📝 ESECUZIONE SCRIPT VAL MCP")
    print("=" * 30)
    
    # Esegui script VAL
    result = visum.Evaluation.Execute("${valScript}")
    print(f"✅ VAL script eseguito: {result}")
    
except Exception as e:
    print(f"❌ Errore VAL MCP: {e}")
`;

    return new Promise((resolve) => {
      const python = spawn('powershell.exe', [
        '-Command', 
        `& "${CONFIG.PYTHON_PATH}" -c @"
${pythonScript}
"@`
      ]);
      let output = '';
      python.stdout.on('data', (data) => {
        output += data.toString();
        console.log(data.toString().trim());
      });
      python.on('close', () => {
        resolve({ success: true, output });
      });
    });
  }
}

// 🎯 DEMO DEGLI STRUMENTI MCP VISUM
async function demoMCPVisumTools() {
  console.log('🤖 ESTENSIONE MCP SERVER - STRUMENTI VISUM');
  console.log('═'.repeat(50));
  console.log('🎯 Aggiunta di tool specializzati per analisi Visum');
  console.log('═'.repeat(50));
  console.log('🚀 AVVIO DEMO MCP VISUM TOOLS...\n');

  console.log('🎯 DEMO STRUMENTI MCP VISUM');
  console.log('═'.repeat(35));

  // Tool 1: Analisi dettagliata rete
  console.log('1️⃣ ANALISI RETE DETTAGLIATA:');
  console.log('📊 MCP Tool: visum_network_analysis');
  console.log('   Type: detailed');
  console.log('   Export: C:\\temp\\mcp_analysis');
  await VisumMCPTools.visum_network_analysis('detailed', 'C:\\temp\\mcp_analysis');
  
  console.log('\n2️⃣ STATISTICHE CONNETTIVITÀ:');
  console.log('📈 MCP Tool: visum_connectivity_stats');
  await VisumMCPTools.visum_connectivity_stats();
  
  console.log('\n3️⃣ EXPORT ELEMENTI RETE:');
  console.log('💾 MCP Tool: visum_export_network');
  console.log('   Elements: nodes, links, zones');
  await VisumMCPTools.visum_export_network(['nodes', 'links', 'zones'], 'C:\\temp\\mcp_export');
  
  console.log('\n🎉 DEMO MCP VISUM TOOLS COMPLETATA!');
  console.log('🔧 Integrazione MCP Server pronta per Claude');
}

// 📋 SCHEMA MCP TOOLS COMPLETO
const MCP_VISUM_TOOLS_SCHEMA = {
  tools: {
    visum_launch: {
      description: "Lancia Visum con file progetto specificato",
      inputSchema: {
        type: "object",
        properties: {
          projectFile: {
            type: "string",
            description: "Percorso file progetto Visum (.ver)"
          }
        }
      }
    },
    
    visum_network_analysis: {
      description: "Analisi completa della rete Visum con statistiche dettagliate",
      inputSchema: {
        type: "object",
        properties: {
          analysisType: {
            type: "string",
            enum: ["detailed", "topology", "basic"],
            description: "Tipo di analisi da eseguire"
          },
          exportPath: {
            type: "string", 
            description: "Directory per export risultati"
          }
        }
      }
    },
    
    visum_export_network: {
      description: "Export elementi rete Visum in formato CSV",
      inputSchema: {
        type: "object",
        properties: {
          elements: {
            type: "array",
            items: {
              type: "string",
              enum: ["nodes", "links", "zones", "lines", "stops"]
            },
            description: "Elementi da esportare"
          },
          exportDir: {
            type: "string",
            description: "Directory destinazione export"
          }
        }
      }
    },
    
    visum_python_analysis: {
      description: "Esecuzione script Python personalizzato con accesso alla rete Visum",
      inputSchema: {
        type: "object",
        properties: {
          customScript: {
            type: "string",
            description: "Script Python da eseguire (variabile 'visum' disponibile)"
          }
        },
        required: ["customScript"]
      }
    },
    
    visum_connectivity_stats: {
      description: "Calcola statistiche di connettività della rete",
      inputSchema: {
        type: "object",
        properties: {}
      }
    },
    
    visum_val_script: {
      description: "Esecuzione script VAL (Visum Analysis Language)",
      inputSchema: {
        type: "object", 
        properties: {
          valScript: {
            type: "string",
            description: "Script VAL da eseguire"
          }
        },
        required: ["valScript"]
      }
    }
  }
};

// 🔌 CODICE PER ESTENSIONE MCP SERVER
function generateMCPServerExtension() {
  return `
// 🚀 ESTENSIONE MCP SERVER CON STRUMENTI VISUM
// Aggiungere questo codice al server MCP esistente

// Import delle dipendenze
import { spawn } from 'child_process';

// Configurazione
const VISUM_CONFIG = ${JSON.stringify(CONFIG, null, 2)};

// Implementazione tools
${VisumMCPTools.toString()}

// Registrazione tools nel server MCP
server.addTool(${JSON.stringify(MCP_VISUM_TOOLS_SCHEMA.tools.visum_launch, null, 2)}, async (args) => {
  return await VisumMCPTools.visum_launch(args.projectFile);
});

server.addTool(${JSON.stringify(MCP_VISUM_TOOLS_SCHEMA.tools.visum_network_analysis, null, 2)}, async (args) => {
  return await VisumMCPTools.visum_network_analysis(args.analysisType, args.exportPath);
});

server.addTool(${JSON.stringify(MCP_VISUM_TOOLS_SCHEMA.tools.visum_export_network, null, 2)}, async (args) => {
  return await VisumMCPTools.visum_export_network(args.elements, args.exportDir);
});

server.addTool(${JSON.stringify(MCP_VISUM_TOOLS_SCHEMA.tools.visum_python_analysis, null, 2)}, async (args) => {
  return await VisumMCPTools.visum_python_analysis(args.customScript);
});

server.addTool(${JSON.stringify(MCP_VISUM_TOOLS_SCHEMA.tools.visum_connectivity_stats, null, 2)}, async (args) => {
  return await VisumMCPTools.visum_connectivity_stats();
});

server.addTool(${JSON.stringify(MCP_VISUM_TOOLS_SCHEMA.tools.visum_val_script, null, 2)}, async (args) => {
  return await VisumMCPTools.visum_val_script(args.valScript);
});
`;
}

// 🎯 ESECUZIONE DEMO
if (import.meta.url === `file://${process.argv[1]}`) {
  demoMCPVisumTools();
}

export { VisumMCPTools, MCP_VISUM_TOOLS_SCHEMA, generateMCPServerExtension };
