// Test del tool analyze_network con Visum già attivo
import { spawn } from 'child_process';

console.log("📊 TEST ANALISI NETWORK VISUM");
console.log("═".repeat(40));

async function testAnalyzeNetwork() {
  console.log("🔍 Analizzando la rete di trasporto Campoleone...");
  
  const child = spawn('node', ['enhanced-visum-mcp.mjs'], { 
    stdio: ['pipe', 'pipe', 'pipe'],
    cwd: process.cwd()
  });

  let fullOutput = '';
  let fullStderr = '';
  
  child.stdout.on('data', (data) => {
    const text = data.toString();
    fullOutput += text;
    if (text.includes('{"jsonrpc"')) {
      console.log("📡 Risposta MCP ricevuta!");
    }
  });

  child.stderr.on('data', (data) => {
    const text = data.toString();
    fullStderr += text;
    if (text.includes('ready for Claude')) {
      console.log("✅ MCP Server connesso!");
    }
  });

  // Richiesta MCP per analyze_network
  const request = {
    jsonrpc: "2.0",
    id: 1,
    method: "tools/call",
    params: {
      name: "analyze_network",
      arguments: {}
    }
  };

  console.log("📤 Invio richiesta analyze_network...");
  
  setTimeout(() => {
    child.stdin.write(JSON.stringify(request) + '\n');
    child.stdin.end();
  }, 2000);

  return new Promise((resolve) => {
    child.on('close', (code) => {
      console.log(`\n🏁 Processo chiuso con codice: ${code}`);
      
      try {
        const lines = fullOutput.split('\n');
        for (const line of lines) {
          if (line.trim().startsWith('{') && line.includes('"jsonrpc"')) {
            const response = JSON.parse(line.trim());
            resolve({ success: true, response });
            return;
          }
        }
        resolve({ success: false, error: 'Nessuna risposta JSON trovata' });
      } catch (error) {
        resolve({ success: false, error: error.message });
      }
    });
    
    setTimeout(() => {
      child.kill();
      resolve({ success: false, error: 'Timeout dopo 30 secondi' });
    }, 30000);
  });
}

async function runNetworkAnalysis() {
  console.log("🚀 Avvio analisi della rete Campoleone...\n");
  
  const result = await testAnalyzeNetwork();
  
  console.log("\n" + "═".repeat(50));
  console.log("📊 RISULTATI ANALISI NETWORK");
  console.log("═".repeat(50));
  
  if (result.success && result.response.result) {
    const content = result.response.result.content?.[0]?.text;
    
    if (content) {
      console.log("✅ ANALISI COMPLETATA CON SUCCESSO!\n");
      console.log(content);
      
      // Estrai statistiche specifiche se disponibili
      const nodesMatch = content.match(/\*\*Nodes:\*\* (\d+)/);
      const linksMatch = content.match(/\*\*Links:\*\* (\d+)/);
      const zonesMatch = content.match(/\*\*Zones:\*\* (\d+)/);
      
      if (nodesMatch || linksMatch || zonesMatch) {
        console.log("\n🎯 STATISTICHE ESTRATTE:");
        console.log("═".repeat(30));
        if (nodesMatch) console.log(`🔗 Nodi: ${nodesMatch[1]}`);
        if (linksMatch) console.log(`🛣️  Collegamenti: ${linksMatch[1]}`);
        if (zonesMatch) console.log(`🏘️  Zone: ${zonesMatch[1]}`);
      }
      
      return true;
    }
  } else if (result.response?.error) {
    console.log("❌ ERRORE NELL'ANALISI:");
    console.log(JSON.stringify(result.response.error, null, 2));
    return false;
  } else {
    console.log("❌ FALLIMENTO:");
    console.log(`Errore: ${result.error}`);
    return false;
  }
}

// Verifica prima che Visum sia attivo
async function checkVisum() {
  console.log("🔍 Verifico che Visum sia attivo...");
  
  const checkScript = `
    Get-Process -Name "Visum250" -ErrorAction SilentlyContinue | 
    Select-Object ProcessName, Id | ConvertTo-Json
  `;
  
  const powershell = spawn('powershell', ['-ExecutionPolicy', 'Bypass', '-Command', checkScript]);
  
  let output = '';
  powershell.stdout.on('data', (data) => {
    output += data.toString();
  });
  
  return new Promise((resolve) => {
    powershell.on('close', () => {
      try {
        if (output.trim()) {
          const processes = JSON.parse(output.trim());
          console.log("✅ Visum attivo:", processes);
          resolve(true);
        } else {
          console.log("❌ Nessun processo Visum trovato");
          resolve(false);
        }
      } catch (e) {
        console.log("⚠️ Errore verifica:", e.message);
        resolve(false);
      }
    });
  });
}

async function main() {
  const visumActive = await checkVisum();
  
  if (!visumActive) {
    console.log("❌ Visum non è attivo! Avvia prima Visum con il progetto.");
    return;
  }
  
  const success = await runNetworkAnalysis();
  
  console.log("\n" + "═".repeat(50));
  console.log("🏁 RIEPILOGO FINALE");
  console.log("═".repeat(50));
  
  if (success) {
    console.log("🎉 ✅ ANALISI NETWORK COMPLETATA!");
    console.log("📊 La rete Campoleone è stata analizzata con successo");
    console.log("🤖 Claude ora ha informazioni dettagliate sulla rete");
  } else {
    console.log("❌ ANALISI FALLITA");
    console.log("🔧 Potrebbero esserci problemi di connessione COM");
  }
}

main().catch(console.error);
