// Test diretto del tool open_project con timeout esteso
import { spawn } from 'child_process';

console.log("🔧 TEST DIRETTO: open_project tool (TIMEOUT ESTESO)");
console.log("═".repeat(60));

const projectPath = "H:\\go\\italferr2025\\Campoleone\\100625_Versione_base_v0.3_sub_ok_priv.ver";

async function testOpenProjectExtended() {
  console.log(`📁 File progetto: ${projectPath}`);
  
  const child = spawn('node', ['enhanced-visum-mcp.mjs'], { 
    stdio: ['pipe', 'pipe', 'pipe'],
    cwd: process.cwd()
  });

  let fullOutput = '';
  let fullStderr = '';
  let jsonFound = false;
  
  child.stdout.on('data', (data) => {
    const text = data.toString();
    fullOutput += text;
    console.log("📡 STDOUT:", text.trim());
    
    // Cerca JSON in tempo reale
    if (text.includes('{"jsonrpc"')) {
      jsonFound = true;
      console.log("🎯 JSON RESPONSE FOUND!");
    }
  });

  child.stderr.on('data', (data) => {
    const text = data.toString();
    fullStderr += text;
    console.log("📡 STDERR:", text.trim());
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

  // Attendi più tempo prima di inviare
  setTimeout(() => {
    console.log("⏰ Invio richiesta ora...");
    child.stdin.write(JSON.stringify(request) + '\n');
    child.stdin.end();
  }, 3000);

  return new Promise((resolve) => {
    child.on('close', (code) => {
      console.log(`\n🏁 Processo chiuso con codice: ${code}`);
      console.log("📥 OUTPUT COMPLETO:");
      console.log("STDOUT LENGTH:", fullOutput.length);
      console.log("STDERR LENGTH:", fullStderr.length);
      
      try {
        // Cerca una risposta JSON valida
        const lines = fullOutput.split('\n');
        for (const line of lines) {
          if (line.trim().startsWith('{') && line.includes('"jsonrpc"')) {
            const response = JSON.parse(line.trim());
            console.log("🎯 Risposta JSON trovata e parsata!");
            resolve({ success: true, response });
            return;
          }
        }
        
        resolve({ 
          success: false, 
          error: 'Nessuna risposta JSON valida trovata',
          outputLength: fullOutput.length,
          stderrLength: fullStderr.length,
          jsonFound: jsonFound
        });
      } catch (error) {
        resolve({ success: false, error: error.message, rawOutput: fullOutput });
      }
    });
    
    // Timeout molto più lungo per le operazioni su file
    setTimeout(() => {
      console.log("⏰ TIMEOUT RAGGIUNTO - termino processo");
      child.kill('SIGTERM');
      
      setTimeout(() => {
        child.kill('SIGKILL');
      }, 2000);
      
      resolve({ success: false, error: 'Timeout dopo 60 secondi' });
    }, 60000);
  });
}

async function runExtendedTest() {
  const result = await testOpenProjectExtended();
  
  console.log("\n" + "═".repeat(50));
  console.log("🏁 RISULTATO TEST ESTESO:");
  console.log("═".repeat(50));
  
  if (result.success && result.response) {
    if (result.response.result) {
      console.log("✅ SUCCESSO!");
      console.log("📊 Contenuto risposta:");
      const content = result.response.result.content?.[0]?.text;
      if (content) {
        console.log(content);
      }
    } else if (result.response.error) {
      console.log("❌ ERRORE MCP:");
      console.log(JSON.stringify(result.response.error, null, 2));
    }
  } else {
    console.log("❌ FALLIMENTO:");
    console.log(`Errore: ${result.error}`);
    console.log(`JSON trovato: ${result.jsonFound}`);
    console.log(`Output Length: ${result.outputLength}`);
    console.log(`Stderr Length: ${result.stderrLength}`);
  }
}

runExtendedTest().catch(console.error);
