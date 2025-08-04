// Debug interattivo per MCP Server
import { spawn } from 'child_process';
import { createInterface } from 'readline';

console.log("🔧 DEBUG INTERATTIVO MCP SERVER 🔧\n");

class MCPTester {
  constructor() {
    this.requestId = 1;
  }

  async sendRequest(method, params = {}) {
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
            resolve({ success: false, error: 'No JSON response found', output, stderr });
          }
        } catch (error) {
          resolve({ success: false, error: error.message, output, stderr });
        }
      });

      const request = {
        jsonrpc: "2.0",
        id: this.requestId++,
        method: method,
        params: params
      };

      child.stdin.write(JSON.stringify(request) + '\n');
      child.stdin.end();

      // Timeout dopo 10 secondi
      setTimeout(() => {
        child.kill();
        resolve({ success: false, error: 'Timeout' });
      }, 10000);
    });
  }

  async testInitialize() {
    console.log("🔍 Test 1: Initialize");
    const result = await this.sendRequest("initialize", {
      protocolVersion: "2024-11-05",
      capabilities: {},
      clientInfo: { name: "debug-client", version: "1.0.0" }
    });
    
    if (result.success) {
      console.log("✅ Initialize OK");
      console.log("   Server:", result.response.result?.serverInfo?.name);
      console.log("   Version:", result.response.result?.serverInfo?.version);
    } else {
      console.log("❌ Initialize FAILED:", result.error);
    }
    console.log();
    return result;
  }

  async testToolsList() {
    console.log("🔍 Test 2: Tools List");
    const result = await this.sendRequest("tools/list");
    
    if (result.success) {
      const tools = result.response.result?.tools || [];
      console.log(`✅ Tools List OK - ${tools.length} tools disponibili:`);
      tools.forEach((tool, i) => {
        console.log(`   ${i+1}. ${tool.name} - ${tool.description}`);
      });
    } else {
      console.log("❌ Tools List FAILED:", result.error);
    }
    console.log();
    return result;
  }

  async testCheckVisum() {
    console.log("🔍 Test 3: Check Visum");
    const result = await this.sendRequest("tools/call", {
      name: "check_visum",
      arguments: {}
    });
    
    if (result.success) {
      console.log("✅ Check Visum OK");
      const content = result.response.result?.content?.[0]?.text;
      if (content) {
        // Estrai info principali
        const versionMatch = content.match(/Version:\*\* (.+)/);
        const statusMatch = content.match(/Status:\*\* (.+)/);
        console.log("   Version:", versionMatch ? versionMatch[1] : "N/A");
        console.log("   Status:", statusMatch ? statusMatch[1] : "N/A");
      }
    } else {
      console.log("❌ Check Visum FAILED:", result.error);
    }
    console.log();
    return result;
  }

  async testAnalyzeNetwork() {
    console.log("🔍 Test 4: Analyze Network");
    const result = await this.sendRequest("tools/call", {
      name: "analyze_network", 
      arguments: {}
    });
    
    if (result.success) {
      console.log("✅ Analyze Network OK");
      const content = result.response.result?.content?.[0]?.text;
      if (content) {
        // Estrai statistiche di rete
        const nodesMatch = content.match(/Nodes:\*\* (.+)/);
        const linksMatch = content.match(/Links:\*\* (.+)/);
        const zonesMatch = content.match(/Zones:\*\* (.+)/);
        console.log("   Nodes:", nodesMatch ? nodesMatch[1] : "N/A");
        console.log("   Links:", linksMatch ? linksMatch[1] : "N/A");
        console.log("   Zones:", zonesMatch ? zonesMatch[1] : "N/A");
      }
    } else {
      console.log("❌ Analyze Network FAILED:", result.error);
    }
    console.log();
    return result;
  }

  async runFullTest() {
    console.log("🚀 ESECUZIONE TEST COMPLETO\n");
    
    const results = {
      initialize: await this.testInitialize(),
      toolsList: await this.testToolsList(), 
      checkVisum: await this.testCheckVisum(),
      analyzeNetwork: await this.testAnalyzeNetwork()
    };

    console.log("📊 RIEPILOGO RISULTATI:");
    console.log(`Initialize: ${results.initialize.success ? '✅' : '❌'}`);
    console.log(`Tools List: ${results.toolsList.success ? '✅' : '❌'}`);
    console.log(`Check Visum: ${results.checkVisum.success ? '✅' : '❌'}`);
    console.log(`Analyze Network: ${results.analyzeNetwork.success ? '✅' : '❌'}`);
    
    return results;
  }
}

// Esegui test automatico
const tester = new MCPTester();
tester.runFullTest().then(() => {
  console.log("\n🎉 Test completato!");
}).catch(console.error);
