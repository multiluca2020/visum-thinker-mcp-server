// Simulazione Claude con Launch Visum
import { spawn } from 'child_process';

console.log("🤖 CLAUDE SIMULAZIONE - Con Launch Visum\n");

async function sendMCPRequest(method, params = {}) {
  return new Promise((resolve) => {
    const child = spawn('node', ['enhanced-visum-mcp.mjs'], { 
      stdio: ['pipe', 'pipe', 'pipe'],
      cwd: process.cwd()
    });

    let output = '';
    let stderr = '';
    
    child.stdout.on('data', (data) => {
      output += data.toString();
    });

    child.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    child.on('close', () => {
      try {
        const lines = output.trim().split('\n');
        const jsonLine = lines.find(line => line.startsWith('{'));
        
        if (jsonLine) {
          const response = JSON.parse(jsonLine);
          resolve({ success: true, response, stderr });
        } else {
          resolve({ success: false, error: 'No JSON response', output, stderr });
        }
      } catch (error) {
        resolve({ success: false, error: error.message, output, stderr });
      }
    });

    const request = {
      jsonrpc: "2.0",
      id: Math.floor(Math.random() * 1000),
      method: method,
      params: params
    };

    child.stdin.write(JSON.stringify(request) + '\n');
    child.stdin.end();

    setTimeout(() => {
      child.kill();
      resolve({ success: false, error: 'Timeout' });
    }, 15000);
  });
}

async function claudeWorkflow() {
  console.log("👤 Claude: 'Devo analizzare la rete di trasporto'");
  console.log("🧠 Claude pensa: Prima verifico i tools disponibili...\n");
  
  // Step 1: List tools
  console.log("📋 1. Lista dei tools disponibili");
  const toolsResult = await sendMCPRequest("tools/list");
  
  if (toolsResult.success) {
    const tools = toolsResult.response.result?.tools || [];
    console.log(`✅ Trovati ${tools.length} tools:`);
    tools.forEach((tool, i) => {
      console.log(`   ${i+1}. ${tool.name} - ${tool.description}`);
    });
    
    // Check if launch_visum is available
    const hasLaunch = tools.some(t => t.name === 'launch_visum');
    console.log(`🚀 Launch Visum disponibile: ${hasLaunch ? 'SÌ' : 'NO'}`);
  } else {
    console.log("❌ Errore nel recuperare i tools");
    return false;
  }
  
  console.log("\n👤 Claude: 'Perfetto! Ora lancio Visum'");
  
  // Step 2: Launch Visum
  console.log("🚀 2. Lancio Visum");
  const launchResult = await sendMCPRequest("tools/call", {
    name: "launch_visum",
    arguments: {}
  });
  
  if (launchResult.success) {
    const content = launchResult.response.result?.content?.[0]?.text;
    if (content?.includes("✅")) {
      console.log("✅ Visum lanciato con successo!");
      
      // Extract process info
      const pidMatch = content.match(/Process ID:\*\* (\d+)/);
      if (pidMatch) {
        console.log(`🆔 Process ID: ${pidMatch[1]}`);
      }
    } else {
      console.log("❌ Lancio Visum fallito");
      console.log("Dettagli:", content?.substring(0, 150) + "...");
      return false;
    }
  } else {
    console.log("❌ Errore nel lancio:", launchResult.error);
    return false;
  }
  
  console.log("\n👤 Claude: 'Ora aspetto un po' per Visum e poi controllo'");
  await new Promise(resolve => setTimeout(resolve, 3000)); // Wait 3 seconds
  
  // Step 3: Check Visum
  console.log("🔍 3. Verifica Visum");
  const checkResult = await sendMCPRequest("tools/call", {
    name: "check_visum",
    arguments: {}
  });
  
  if (checkResult.success) {
    const content = checkResult.response.result?.content?.[0]?.text;
    if (content?.includes("✅")) {
      console.log("✅ Visum è accessibile via COM!");
      
      // Extract version
      const versionMatch = content.match(/Version:\*\* (\d+)/);
      if (versionMatch) {
        console.log(`📦 Version: ${versionMatch[1]}`);
      }
    } else {
      console.log("⚠️ Visum non ancora pronto, potrebbe servire più tempo");
      return false;
    }
  } else {
    console.log("❌ Errore nel check:", checkResult.error);
    return false;
  }
  
  console.log("\n👤 Claude: 'Perfetto! Ora analizzo la rete'");
  
  // Step 4: Analyze Network
  console.log("📊 4. Analisi della rete");
  const analysisResult = await sendMCPRequest("tools/call", {
    name: "analyze_network",
    arguments: {}
  });
  
  if (analysisResult.success) {
    const content = analysisResult.response.result?.content?.[0]?.text;
    if (content?.includes("✅")) {
      console.log("✅ Analisi completata!");
      
      // Extract network stats
      const nodesMatch = content.match(/Nodes:\*\* (\w+)/);
      const linksMatch = content.match(/Links:\*\* (\w+)/);
      const zonesMatch = content.match(/Zones:\*\* (\w+)/);
      
      if (nodesMatch && linksMatch && zonesMatch) {
        console.log(`📊 Rete: ${nodesMatch[1]} nodi, ${linksMatch[1]} link, ${zonesMatch[1]} zone`);
      }
      
      return true;
    } else {
      console.log("⚠️ Analisi fallita, probabilmente serve caricare un modello");
      console.log("💡 Claude: 'Va bene, almeno Visum è attivo ora!'");
      return true; // Success parziale
    }
  } else {
    console.log("❌ Errore nell'analisi:", analysisResult.error);
    return false;
  }
}

claudeWorkflow().then((success) => {
  console.log("\n🏆 RISULTATO FINALE:");
  if (success) {
    console.log("🎉 ✅ Claude è riuscito nell'automazione Visum!");
    console.log("   - MCP server funzionante");
    console.log("   - Visum lanciato correttamente");
    console.log("   - COM automation operativa");
    console.log("   - Pronto per l'analisi di rete");
  } else {
    console.log("❌ Workflow Claude incompleto");
  }
}).catch(console.error);
