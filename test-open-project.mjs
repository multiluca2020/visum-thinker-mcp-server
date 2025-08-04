// Test diretto del tool open_project
import { spawn } from 'child_process';

console.log("🔧 TEST DIRETTO: open_project tool");
console.log("═".repeat(50));

const projectPath = "H:\\go\\italferr2025\\Campoleone\\100625_Versione_base_v0.3_sub_ok_priv.ver";

async function testOpenProject() {
  console.log(`📁 File progetto: ${projectPath}`);
  console.log("🔍 Verifico esistenza file...");
  
  const child = spawn('node', ['enhanced-visum-mcp.mjs'], { 
    stdio: ['pipe', 'pipe', 'pipe'],
    cwd: process.cwd()
  });

  let fullOutput = '';
  let fullStderr = '';
  
  child.stdout.on('data', (data) => {
    const text = data.toString();
    fullOutput += text;
    // Mostra solo messaggi importanti
    if (text.includes('ready for Claude') || text.includes('{"jsonrpc"')) {
      console.log("📡 MCP:", text.trim());
    }
  });

  child.stderr.on('data', (data) => {
    const text = data.toString();
    fullStderr += text;
    if (text.includes('ready for Claude')) {
      console.log("✅ MCP Server attivo!");
    }
  });

  // Costruisci la richiesta MCP
  const request = {
    jsonrpc: "2.0",
    id: 1,
    method: "tools/call",
    params: {
      name: "open_project",
      arguments: {
        projectPath: projectPath
      }
    }
  };

  console.log("📤 Invio richiesta a MCP...");
  console.log(JSON.stringify(request, null, 2));

  // Attendi un po' prima di inviare
  setTimeout(() => {
    child.stdin.write(JSON.stringify(request) + '\n');
    child.stdin.end();
  }, 2000);

  return new Promise((resolve) => {
    child.on('close', (code) => {
      console.log("\n📥 RISPOSTA COMPLETA:");
      console.log("═".repeat(30));
      console.log("STDOUT:");
      console.log(fullOutput);
      console.log("\nSTDERR:");
      console.log(fullStderr);
      console.log("═".repeat(30));
      
      try {
        // Cerca una risposta JSON valida
        const lines = fullOutput.split('\n');
        for (const line of lines) {
          if (line.trim().startsWith('{') && line.includes('"jsonrpc"')) {
            const response = JSON.parse(line.trim());
            console.log("🎯 Risposta JSON trovata:");
            console.log(JSON.stringify(response, null, 2));
            resolve({ success: true, response });
            return;
          }
        }
        resolve({ success: false, error: 'Nessuna risposta JSON valida trovata' });
      } catch (error) {
        resolve({ success: false, error: error.message, rawOutput: fullOutput });
      }
    });
    
    // Timeout più lungo per operazioni su file
    setTimeout(() => {
      child.kill();
      resolve({ success: false, error: 'Timeout dopo 45 secondi' });
    }, 45000);
  });
}

async function runTest() {
  const result = await testOpenProject();
  
  console.log("\n🏁 RISULTATO TEST:");
  console.log("═".repeat(30));
  
  if (result.success && result.response) {
    if (result.response.result) {
      console.log("✅ SUCCESSO!");
      console.log("📊 Contenuto risposta:");
      const content = result.response.result.content?.[0]?.text;
      if (content) {
        console.log(content);
      } else {
        console.log("Nessun contenuto testuale nella risposta");
      }
    } else if (result.response.error) {
      console.log("❌ ERRORE MCP:");
      console.log(JSON.stringify(result.response.error, null, 2));
    }
  } else {
    console.log("❌ FALLIMENTO:");
    console.log(`Errore: ${result.error}`);
    if (result.rawOutput) {
      console.log("Output grezzo:", result.rawOutput.substring(0, 500));
    }
  }
}

runTest().catch(console.error);
