// Test diretto dell'MCP per verificare la comunicazione
import { spawn } from 'child_process';

console.log("🔧 TEST DIRETTO MCP - Comunicazione Raw\n");

async function testDirectMCP() {
  console.log("📡 Avvio MCP server per test diretto...");
  
  const server = spawn('node', ['enhanced-visum-mcp.mjs'], { 
    stdio: ['pipe', 'pipe', 'pipe'],
    cwd: process.cwd()
  });

  let responses = [];
  let serverReady = false;

  // Gestisci stderr per vedere quando il server è pronto
  server.stderr.on('data', (data) => {
    const output = data.toString();
    console.log("📟 Server stderr:", output.trim());
    if (output.includes('ready for Claude')) {
      serverReady = true;
    }
  });

  // Gestisci stdout per le risposte JSON
  server.stdout.on('data', (data) => {
    const output = data.toString().trim();
    console.log("📤 Server risposta raw:", output);
    
    try {
      const response = JSON.parse(output);
      responses.push(response);
      console.log("✅ JSON valido ricevuto:", response.result ? "Success" : "Error");
    } catch (e) {
      console.log("⚠️ Output non-JSON:", output.substring(0, 100));
    }
  });

  // Aspetta che il server sia pronto
  await new Promise(resolve => {
    const checkReady = () => {
      if (serverReady) {
        resolve();
      } else {
        setTimeout(checkReady, 100);
      }
    };
    setTimeout(checkReady, 500);
  });

  console.log("\n🚀 Server pronto, invio richieste...");

  // Test 1: Initialize
  console.log("\n📤 Test 1: Initialize");
  const initRequest = {
    jsonrpc: "2.0",
    id: 1,
    method: "initialize",
    params: {
      protocolVersion: "2024-11-05",
      capabilities: {},
      clientInfo: { name: "test", version: "1.0.0" }
    }
  };
  
  server.stdin.write(JSON.stringify(initRequest) + '\n');
  await new Promise(resolve => setTimeout(resolve, 2000));

  // Test 2: Tools List
  console.log("\n📤 Test 2: Tools List");
  const toolsRequest = {
    jsonrpc: "2.0", 
    id: 2,
    method: "tools/list"
  };
  
  server.stdin.write(JSON.stringify(toolsRequest) + '\n');
  await new Promise(resolve => setTimeout(resolve, 2000));

  // Test 3: Check Visum (con output dettagliato)
  console.log("\n📤 Test 3: Check Visum");
  const checkRequest = {
    jsonrpc: "2.0",
    id: 3, 
    method: "tools/call",
    params: {
      name: "check_visum",
      arguments: {}
    }
  };
  
  server.stdin.write(JSON.stringify(checkRequest) + '\n');
  await new Promise(resolve => setTimeout(resolve, 5000)); // Più tempo per Visum COM

  console.log("\n📊 RIEPILOGO TEST:");
  console.log(`Risposte ricevute: ${responses.length}`);
  responses.forEach((resp, i) => {
    console.log(`  ${i+1}. ID: ${resp.id}, Metodo: ${resp.result ? 'Success' : 'Error'}`);
  });

  // Chiudi il server
  server.kill();
  
  return responses.length >= 3;
}

testDirectMCP().then((success) => {
  console.log(`\n🏁 Test diretto: ${success ? 'COMPLETATO' : 'PARZIALE'}`);
}).catch(console.error);
