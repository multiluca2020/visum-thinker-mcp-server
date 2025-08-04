// Test enhanced MCP server with network analysis tools
import { spawn } from 'child_process';

console.log("Testing Enhanced MCP Server with Network Analysis...\n");

function sendRequest(request) {
  return new Promise((resolve) => {
    const child = spawn('node', ['enhanced-visum-mcp.mjs'], { 
      stdio: ['pipe', 'pipe', 'pipe'],
      cwd: process.cwd()
    });

    let output = '';
    child.stdout.on('data', (data) => {
      output += data.toString();
    });

    child.on('close', () => {
      try {
        const response = JSON.parse(output.trim());
        resolve(response);
      } catch (error) {
        resolve({ error: 'Failed to parse response', raw: output });
      }
    });

    child.stdin.write(JSON.stringify(request) + '\n');
    child.stdin.end();
  });
}

async function runTests() {
  // Test 1: List all tools
  console.log("🔍 Test 1: List available tools");
  const toolsRequest = {
    jsonrpc: "2.0",
    id: 1,
    method: "tools/list"
  };
  
  const toolsResponse = await sendRequest(toolsRequest);
  console.log("✅ Tools available:", toolsResponse.result?.tools?.length || 0);
  console.log("📋 Tool names:", toolsResponse.result?.tools?.map(t => t.name).join(', ') || "None");
  console.log();

  // Test 2: Analyze network
  console.log("🔍 Test 2: Analyze network");
  const analyzeRequest = {
    jsonrpc: "2.0",
    id: 2,
    method: "tools/call",
    params: {
      name: "analyze_network",
      arguments: {}
    }
  };
  
  const analyzeResponse = await sendRequest(analyzeRequest);
  console.log("✅ Network analysis:", analyzeResponse.result ? "Success" : "Failed");
  if (analyzeResponse.result?.content?.[0]?.text) {
    console.log("📊 Analysis result preview:", analyzeResponse.result.content[0].text.substring(0, 200) + "...");
  }
  console.log();

  // Test 3: Get network stats
  console.log("🔍 Test 3: Get network statistics");
  const statsRequest = {
    jsonrpc: "2.0",
    id: 3,
    method: "tools/call",
    params: {
      name: "get_network_stats",
      arguments: {}
    }
  };
  
  const statsResponse = await sendRequest(statsRequest);
  console.log("✅ Network stats:", statsResponse.result ? "Success" : "Failed");
  if (statsResponse.result?.content?.[0]?.text) {
    console.log("📈 Stats result preview:", statsResponse.result.content[0].text.substring(0, 200) + "...");
  }
  console.log();

  console.log("🎉 Enhanced MCP Server testing completed!");
  console.log("📢 Claude can now use 'analyze_network' and 'get_network_stats' commands!");
}

runTests().catch(console.error);
