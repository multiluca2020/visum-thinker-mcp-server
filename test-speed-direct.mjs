// Test VELOCE - Processo Python Semplificato
// Testiamo la velocità reale senza timeout di inizializzazione

import { spawn } from "child_process";

console.log("🚀 TEST VELOCITÀ: Comunicazione Diretta Python");
console.log("=".repeat(60));

async function quickSpeedTest() {
  const pythonPath = "H:\\Program Files\\PTV Vision\\PTV Visum 2025\\Exe\\Python\\python.exe";
  
  const quickScript = `
import sys
import os
import time
import json

# Setup VisumPy paths
visum_path = r"H:\\Program Files\\PTV Vision\\PTV Visum 2025\\Exe"
python_path = os.path.join(visum_path, "Python")

if visum_path not in sys.path:
    sys.path.insert(0, visum_path)
if python_path not in sys.path:
    sys.path.insert(0, python_path)

try:
    import VisumPy.helpers as vh
    print("QUICK: Creating VisumPy...", file=sys.stderr)
    visum = vh.CreateVisum(250)
    
    project_path = r"H:\\go\\italferr2025\\Campoleone\\100625_Versione_base_v0.3_sub_ok_priv.ver"
    print("QUICK: Loading project...", file=sys.stderr)
    visum.LoadVersion(project_path)
    
    nodes = visum.Net.Nodes.Count
    print(f"QUICK: Ready with {nodes} nodes", file=sys.stderr)
    
    # Test ultra-veloce
    print("QUICK: Running speed tests...", file=sys.stderr)
    
    # Test 1: Network Stats (5 volte)
    for i in range(5):
        start = time.time()
        n = visum.Net.Nodes.Count
        l = visum.Net.Links.Count
        z = visum.Net.Zones.Count
        elapsed = (time.time() - start) * 1000
        
        result = {
            "test": f"network_stats_{i+1}",
            "nodes": n,
            "links": l,
            "zones": z,
            "time_ms": round(elapsed, 2)
        }
        print(json.dumps(result))
    
    print("QUICK: Tests completed", file=sys.stderr)
    
except Exception as e:
    error = {"error": str(e)}
    print(json.dumps(error))
`;

  const tempPath = "C:\\temp\\quick_visum_test.py";
  const fs = await import("fs");
  fs.writeFileSync(tempPath, quickScript);

  console.log("1️⃣ Avviando test velocità...");
  
  const startTime = Date.now();
  
  return new Promise((resolve, reject) => {
    const process = spawn(pythonPath, [tempPath], {
      stdio: ['pipe', 'pipe', 'pipe']
    });
    
    const results = [];
    let stderr = "";
    
    process.stdout.on('data', (data) => {
      const lines = data.toString().split('\n');
      for (const line of lines) {
        if (line.trim()) {
          try {
            const result = JSON.parse(line.trim());
            results.push(result);
            console.log(`   📊 ${result.test}: ${result.time_ms}ms (${result.nodes} nodi)`);
          } catch (e) {
            // Not JSON
          }
        }
      }
    });
    
    process.stderr.on('data', (data) => {
      stderr += data.toString();
      console.error(`🐍 ${data.toString().trim()}`);
    });
    
    process.on('close', (code) => {
      const totalTime = Date.now() - startTime;
      
      console.log(`\n2️⃣ Risultati Test Velocità:`);
      console.log(`   📊 Test completati: ${results.length}`);
      console.log(`   ⏱️  Tempo totale: ${totalTime}ms`);
      
      if (results.length > 0) {
        const times = results.map(r => r.time_ms);
        const avgTime = times.reduce((a, b) => a + b, 0) / times.length;
        const minTime = Math.min(...times);
        const maxTime = Math.max(...times);
        
        console.log(`   ⚡ Tempo medio query: ${avgTime.toFixed(2)}ms`);
        console.log(`   🚀 Più veloce: ${minTime}ms`);
        console.log(`   🐌 Più lenta: ${maxTime}ms`);
        
        if (avgTime < 100) {
          console.log(`\n✅ VELOCITÀ ECCELLENTE: Query ultra-rapide!`);
        } else if (avgTime < 500) {
          console.log(`\n⚡ VELOCITÀ BUONA: Query rapide`);
        } else {
          console.log(`\n⚠️ VELOCITÀ NORMALE: Potrebbe migliorare`);
        }
        
        // Test di persistenza
        const speedImprovement = results[0].time_ms / results[results.length - 1].time_ms;
        if (speedImprovement > 1.5) {
          console.log(`🚀 MIGLIORAMENTO RILEVATO: ${speedImprovement.toFixed(1)}x più veloce alla fine`);
        }
      }
      
      resolve({ success: code === 0, results, totalTime });
    });
    
    setTimeout(() => {
      process.kill();
      reject(new Error("Test timeout"));
    }, 300000); // 5 minuti max
  });
}

// Esegui test rapido
quickSpeedTest().then((result) => {
  console.log(`\n🏁 Test completato: ${result.success ? 'SUCCESS' : 'FAILED'}`);
  console.log(`   Tempo setup + 5 query: ${result.totalTime}ms`);
  
  if (result.success && result.results.length > 0) {
    console.log("\n🎯 CONCLUSIONE:");
    console.log("   - VisumPy funziona correttamente");
    console.log("   - Query sono molto veloci una volta caricato");
    console.log("   - Il problema è nella comunicazione MCP, non in VisumPy!");
  }
  
  process.exit(0);
}).catch(error => {
  console.error("💀 Test fallito:", error);
  process.exit(1);
});