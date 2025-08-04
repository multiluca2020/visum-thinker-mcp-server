// Test integrazione MCP con Visum visibile
import { spawn } from 'child_process';

console.log("🔗 TEST MCP ↔ VISUM VISIBILE");
console.log("═".repeat(40));

// Simula una richiesta MCP al server
async function testMCPTool(toolName, args = {}) {
  console.log(`\n🛠️  TEST TOOL: ${toolName}`);
  console.log("-".repeat(30));
  
  const request = {
    jsonrpc: "2.0",
    id: 1,
    method: "tools/call",
    params: {
      name: toolName,
      arguments: args
    }
  };

  console.log("📤 Invio richiesta MCP:", JSON.stringify(request, null, 2));

  // Avvia il server MCP
  const server = spawn('node', ['enhanced-visum-mcp.mjs'], {
    stdio: ['pipe', 'pipe', 'pipe']
  });

  let output = '';
  let errors = '';

  server.stdout.on('data', (data) => {
    const text = data.toString();
    output += text;
    console.log("📥 MCP Output:", text.trim());
  });

  server.stderr.on('data', (data) => {
    const text = data.toString();
    errors += text;
    console.log("⚠️  MCP Error:", text.trim());
  });

  // Invia la richiesta
  server.stdin.write(JSON.stringify(request) + '\n');

  return new Promise((resolve) => {
    const timeout = setTimeout(() => {
      console.log("⏱️  TIMEOUT - terminando server");
      server.kill();
      resolve({
        success: false,
        error: 'Timeout dopo 12 secondi',
        output: output,
        errors: errors
      });
    }, 12000);

    server.on('close', (code) => {
      clearTimeout(timeout);
      console.log(`🏁 Server MCP chiuso con codice: ${code}`);
      
      // Cerca JSON response nell'output
      const jsonMatch = output.match(/\{"jsonrpc".*?\}/);
      let response = null;
      
      if (jsonMatch) {
        try {
          response = JSON.parse(jsonMatch[0]);
          console.log("✅ Risposta MCP ricevuta:", response);
        } catch (e) {
          console.log("❌ Errore parsing JSON:", e.message);
        }
      }
      
      resolve({
        success: response ? !response.error : false,
        response: response,
        output: output,
        errors: errors,
        code: code
      });
    });
  });
}

async function runFullTest() {
  console.log("🏁 Inizio test completo MCP con Visum visibile...\n");
  
  // Test 1: Check status
  console.log("📊 TEST 1: Verifica status Visum");
  const statusTest = await testMCPTool('get_visum_status');
  
  console.log("\n" + "═".repeat(40));
  console.log("📊 RISULTATO TEST STATUS");
  console.log("═".repeat(40));
  
  if (statusTest.success) {
    console.log("✅ Status check RIUSCITO!");
    console.log("   Visum è accessibile via MCP");
  } else {
    console.log("❌ Status check FALLITO");
    console.log(`   Errore: ${statusTest.error || 'Comunicazione MCP interrotta'}`);
  }
  
  // Breve pausa
  await new Promise(r => setTimeout(r, 2000));
  
  // Test 2: Check Visum details
  console.log("\n📊 TEST 2: Verifica dettagli Visum");
  const checkTest = await testMCPTool('check_visum');
  
  console.log("\n" + "═".repeat(40));
  console.log("📊 RISULTATO TEST CHECK");
  console.log("═".repeat(40));
  
  if (checkTest.success) {
    console.log("✅ Check Visum RIUSCITO!");
    console.log("   Dati Visum recuperati correttamente");
  } else {
    console.log("❌ Check Visum FALLITO");
    console.log(`   Errore: ${checkTest.error || 'Comunicazione MCP interrotta'}`);
  }
  
  console.log("\n" + "═".repeat(40));
  console.log("🎯 CONCLUSIONI FINALI");
  console.log("═".repeat(40));
  
  if (statusTest.success && checkTest.success) {
    console.log("🎉 🏆 INTEGRAZIONE COMPLETA RIUSCITA!");
    console.log("   ✅ Visum visibile in esecuzione");
    console.log("   ✅ MCP server funzionante");
    console.log("   ✅ Comunicazione MCP ↔ Visum operativa");
    console.log("\n🚀 Claude può ora utilizzare Visum tramite MCP!");
  } else if (statusTest.success || checkTest.success) {
    console.log("⚠️  🔧 INTEGRAZIONE PARZIALE");
    console.log("   - Visum è attivo e visibile");
    console.log("   - Problemi di comunicazione MCP intermittenti");
    console.log("   - Necessario fine-tuning dei timeout");
  } else {
    console.log("❌ 🔧 INTEGRAZIONE NON RIUSCITA");
    console.log("   - Visum è visibile ma inaccessibile via MCP");
    console.log("   - Verificare configurazione COM");
    console.log("   - Timeout MCP troppo stringenti");
  }
}

runFullTest().catch(console.error);
