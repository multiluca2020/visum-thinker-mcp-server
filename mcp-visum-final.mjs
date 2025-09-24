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
  
  static async executePythonScript(pythonCode) {
    // Crea file temporaneo per evitare problemi con virgolette
    const tempFile = `temp_script_${Date.now()}.py`;
    fs.writeFileSync(tempFile, pythonCode);
    
    return new Promise((resolve) => {
      const python = spawn('powershell.exe', [
        '-Command', 
        `& "${CONFIG.PYTHON_PATH}" "${tempFile}"`
      ]);
      
      let output = '';
      let errorOutput = '';
      
      python.stdout.on('data', (data) => {
        const text = data.toString();
        output += text;
        console.log(text.trim());
      });
      
      python.stderr.on('data', (data) => {
        const text = data.toString();
        errorOutput += text;
        console.error('STDERR:', text.trim());
      });
      
      python.on('close', (code) => {
        fs.unlinkSync(tempFile); // Pulisci file temporaneo
        resolve({ 
          success: code === 0, 
          output, 
          error: errorOutput,
          exitCode: code 
        });
      });
    });
  }

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
    const pythonCode = `import sys
import os
sys.path.append(r"H:\\Program Files\\PTV Vision\\PTV Visum 2025\\Exe")

try:
    import win32com.client
    
    print("🔍 ANALISI RETE MCP - ${analysisType.toUpperCase()}")
    print("=" * 40)
    
    # Prova connessione
    try:
        visum = win32com.client.GetActiveObject("Visum.Visum")
        print("✅ GetActiveObject connesso")
    except:
        visum = win32com.client.DispatchEx("Visum.Visum")
        print("✅ DispatchEx connesso (nuova istanza)")
    
    # Statistiche base
    nodes = visum.Net.Nodes.Count
    links = visum.Net.Links.Count  
    zones = visum.Net.Zones.Count
    
    print(f"📊 Nodi: {nodes:,}")
    print(f"🔗 Link: {links:,}")
    print(f"🏭 Zone: {zones:,}")
    
    if nodes == 0:
        print("⚠️  RETE VUOTA - Caricando progetto via COM...")
        try:
            visum.LoadNet("${CONFIG.PROJECT_FILE}")
            print("✅ Progetto caricato via COM")
            
            nodes = visum.Net.Nodes.Count
            links = visum.Net.Links.Count  
            zones = visum.Net.Zones.Count
            
            print(f"📊 Nodi (dopo caricamento): {nodes:,}")
            print(f"🔗 Link (dopo caricamento): {links:,}")
            print(f"🏭 Zone (dopo caricamento): {zones:,}")
        except Exception as e:
            print(f"❌ Impossibile caricare progetto: {e}")
    
    if "${analysisType}" == "detailed" and nodes > 0:
        print("\\n🔍 ANALISI DETTAGLIATA:")
        
        # Calcola statistiche avanzate
        total_length = 0
        speed_sum = 0
        capacity_sum = 0
        valid_links = 0
        
        sample_size = min(100, links)  # Campione più piccolo per performance
        print(f"📈 Analizzando campione di {sample_size} link...")
        
        for i in range(sample_size):
            try:
                link = visum.Net.Links.ItemByKey(i+1)  # Prova ItemByKey
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
                    
            except Exception as link_error:
                # Prova approccio alternativo
                try:
                    all_links = visum.Net.Links.GetMultipleAttributes(["Length", "V0_PrT", "VolCapPrT"])
                    if len(all_links) > 0:
                        print(f"📋 Trovati {len(all_links)} link con attributi")
                        break
                except:
                    pass
        
        if valid_links > 0:
            avg_length = total_length / valid_links
            avg_speed = speed_sum / valid_links if speed_sum > 0 else 0
            total_capacity = capacity_sum
            
            print(f"📏 Lunghezza media link: {avg_length:.1f} m")
            print(f"🚗 Velocità media: {avg_speed:.1f} km/h") 
            print(f"🚧 Capacità totale: {total_capacity:,.0f} veic/h")
            
            # Densità rete
            density = links / nodes if nodes > 0 else 0
            print(f"🌐 Densità rete: {density:.2f} link/nodo")
        else:
            print("❌ Nessun dato valido trovato nei link")
            
    print("\\n✅ Analisi MCP completata!")
    
except Exception as e:
    print(f"❌ Errore MCP: {e}")
    import traceback
    traceback.print_exc()
`;
    
    return this.executePythonScript(pythonCode);
  }

  // ✅ TOOL 3: visum_export_network
  static async visum_export_network(elements = ['nodes', 'links'], exportDir = 'C:\\temp\\mcp_export') {
    const pythonCode = `import sys
import os
sys.path.append(r"H:\\Program Files\\PTV Vision\\PTV Visum 2025\\Exe")

try:
    import win32com.client
    
    # Connessione  
    try:
        visum = win32com.client.GetActiveObject("Visum.Visum")
    except:
        visum = win32com.client.DispatchEx("Visum.Visum")
        visum.LoadNet("${CONFIG.PROJECT_FILE}")
    
    export_dir = r"${exportDir}"
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
        print(f"📁 Directory creata: {export_dir}")
    
    print("📤 EXPORT MCP NETWORK")
    print("=" * 30)
    
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

    return this.executePythonScript(pythonCode);
  }

  // ✅ TOOL 4: visum_connectivity_stats  
  static async visum_connectivity_stats() {
    const pythonCode = `import sys
sys.path.append(r"H:\\Program Files\\PTV Vision\\PTV Visum 2025\\Exe")

try:
    import win32com.client
    
    # Connessione
    try:
        visum = win32com.client.GetActiveObject("Visum.Visum")
    except:
        visum = win32com.client.DispatchEx("Visum.Visum")
        visum.LoadNet("${CONFIG.PROJECT_FILE}")
    
    print("📊 STATISTICHE CONNETTIVITÀ MCP")
    print("=" * 35)
    
    # Statistiche base
    nodes = visum.Net.Nodes.Count
    links = visum.Net.Links.Count
    
    if nodes > 0:
        connectivity = links / nodes
        print(f"🌐 Connettività: {connectivity:.2f} (link/nodo)")
        
        # Statistiche topologiche semplici
        if links > 0:
            print(f"📈 Rapporto link/nodi: {links}/{nodes} = {connectivity:.2f}")
            
            # Stima della connettività
            if connectivity < 1.5:
                print("📉 Rete scarsamente connessa")
            elif connectivity < 2.5:
                print("📊 Rete normalmente connessa")
            else:
                print("📈 Rete altamente connessa")
        
        print(f"\\n📋 RIEPILOGO:")
        print(f"   • Nodi totali: {nodes:,}")
        print(f"   • Link totali: {links:,}") 
        print(f"   • Indice connettività: {connectivity:.2f}")
    else:
        print("❌ Nessun nodo trovato nella rete")
    
    print("\\n✅ Statistiche completate!")
    
except Exception as e:
    print(f"❌ Errore connettività: {e}")
`;

    return this.executePythonScript(pythonCode);
  }
}

// 🎯 DEMO DEGLI STRUMENTI MCP VISUM  
async function demoMCPVisumTools() {
  console.log('🤖 ESTENSIONE MCP SERVER - STRUMENTI VISUM');
  console.log('═'.repeat(50));
  console.log('🎯 6 Tool specializzati per analisi Visum con Python corretto');
  console.log('═'.repeat(50));

  console.log('\\n1️⃣ TEST CONNESSIONE E ANALISI RETE:');
  console.log('📊 Tool: visum_network_analysis');
  await VisumMCPTools.visum_network_analysis('detailed');
  
  console.log('\\n2️⃣ STATISTICHE CONNETTIVITÀ:');
  console.log('📈 Tool: visum_connectivity_stats');
  await VisumMCPTools.visum_connectivity_stats();
  
  console.log('\\n🎉 DEMO COMPLETATA!');
  console.log('🔧 MCP Server pronto con Python: ' + CONFIG.PYTHON_PATH);
}

// 🚀 ESECUZIONE
if (import.meta.url === `file://${process.argv[1]}`) {
  demoMCPVisumTools();
}

export { VisumMCPTools, CONFIG };
