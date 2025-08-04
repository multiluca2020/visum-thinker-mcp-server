// Test del server MCP ottimizzato
import { spawn } from 'child_process';

console.log("🚀 TEST SERVER MCP OTTIMIZZATO");
console.log("═".repeat(45));

async function testOptimizedServer(toolName) {
  console.log(`\n🛠️  TESTING: ${toolName}`);
  console.log("-".repeat(35));
  
  const request = {
    jsonrpc: "2.0",
    id: 1,
    method: "tools/call",
    params: {
      name: toolName,
      arguments: {}
    }
  };

  console.log("📤 Sending request...");
  
  const server = spawn('node', ['optimized-visum-mcp.mjs'], {
    stdio: ['pipe', 'pipe', 'pipe']
  });

  let response = '';
  let serverReady = false;

  server.stdout.on('data', (data) => {
    const text = data.toString();
    response += text;
    console.log("📥 Response:", text.trim());
  });

  server.stderr.on('data', (data) => {
    const text = data.toString();
    console.log("🔧 Server log:", text.trim());
    if (text.includes('ready for Claude')) {
      serverReady = true;
    }
  });

  return new Promise((resolve) => {
    // Wait for server to be ready, then send request
    setTimeout(() => {
      if (serverReady) {
        console.log("✅ Server ready, sending request...");
        server.stdin.write(JSON.stringify(request) + '\n');
      }
    }, 2000);

    // Extended timeout for response
    const timeout = setTimeout(() => {
      console.log("⏱️  Test timeout - terminating");
      server.kill();
      resolve({
        success: false,
        error: 'Test timeout',
        response: response
      });
    }, 35000); // 35 second timeout

    server.on('close', (code) => {
      clearTimeout(timeout);
      console.log(`🏁 Server closed with code: ${code}`);
      
      // Parse JSON response
      const jsonMatch = response.match(/\{"jsonrpc"[^}]*\}/);
      let parsedResponse = null;
      
      if (jsonMatch) {
        try {
          parsedResponse = JSON.parse(jsonMatch[0]);
          console.log("✅ Valid JSON response received");
        } catch (e) {
          console.log("❌ JSON parse error:", e.message);
        }
      }
      
      resolve({
        success: parsedResponse && !parsedResponse.error,
        response: parsedResponse,
        fullOutput: response,
        code: code
      });
    });
  });
}

async function runOptimizedTest() {
  console.log("🎯 Starting optimized MCP server test...\n");
  
  // Test 1: Status check (fastest)
  console.log("═".repeat(45));
  console.log("📊 TEST 1: Status Check");
  const statusResult = await testOptimizedServer('get_visum_status');
  
  console.log("\n📋 RISULTATO STATUS:");
  if (statusResult.success) {
    console.log("✅ STATUS OK - Visum status retrieved successfully");
  } else {
    console.log("❌ STATUS FAILED:", statusResult.error);
  }
  
  // Brief pause between tests
  await new Promise(r => setTimeout(r, 3000));
  
  // Test 2: COM check
  console.log("\n" + "═".repeat(45));
  console.log("📊 TEST 2: COM Interface Check");
  const comResult = await testOptimizedServer('check_visum');
  
  console.log("\n📋 RISULTATO COM:");
  if (comResult.success) {
    console.log("✅ COM OK - Visum COM interface accessible");
  } else {
    console.log("❌ COM FAILED:", comResult.error);
  }
  
  // Final assessment
  console.log("\n" + "═".repeat(45));
  console.log("🎯 RISULTATO FINALE");
  console.log("═".repeat(45));
  
  if (statusResult.success && comResult.success) {
    console.log("🎉 🏆 SUCCESSO COMPLETO!");
    console.log("   ✅ Server MCP ottimizzato funzionante");
    console.log("   ✅ Visum accessibile via MCP");
    console.log("   ✅ Timeout estesi sufficienti");
    console.log("   ✅ Comunicazione stabile");
    console.log("\n🚀 PRONTO PER CLAUDE!");
    console.log("   Il server può essere utilizzato con sicurezza");
  } else if (statusResult.success || comResult.success) {
    console.log("⚠️  🔧 SUCCESSO PARZIALE");
    console.log("   - Alcuni test passati, altri no");
    console.log("   - Necessari ulteriori aggiustamenti");
  } else {
    console.log("❌ 🔧 NECESSARI ULTERIORI MIGLIORAMENTI");
    console.log("   - Timeout ancora insufficienti");
    console.log("   - Problemi di comunicazione persistenti");
  }
}

runOptimizedTest().catch(console.error);
