// Quick test of enhanced MCP server
import { spawn } from 'child_process';

console.log("Testing Enhanced MCP Server Communication...\n");

function testServerResponse() {
  return new Promise((resolve) => {
    const child = spawn('node', ['enhanced-visum-mcp.mjs'], { 
      stdio: ['pipe', 'pipe', 'pipe'],
      cwd: process.cwd()
    });

    let output = '';
    child.stdout.on('data', (data) => {
      output += data.toString();
    });

    child.stderr.on('data', (data) => {
      console.log('Server stderr:', data.toString());
    });

    child.on('close', () => {
      try {
        const response = JSON.parse(output.trim());
        resolve(response);
      } catch (error) {
        resolve({ error: 'Failed to parse response', raw: output });
      }
    });

    // Send initialize request
    const initRequest = {
      jsonrpc: "2.0",
      id: 1,
      method: "initialize",
      params: {
        protocolVersion: "2024-11-05",
        capabilities: {},
        clientInfo: {
          name: "test-client",
          version: "1.0.0"
        }
      }
    };

    child.stdin.write(JSON.stringify(initRequest) + '\n');
    child.stdin.end();

    // Timeout after 5 seconds
    setTimeout(() => {
      child.kill();
      resolve({ error: 'Timeout - server not responding' });
    }, 5000);
  });
}

async function runQuickTest() {
  console.log("🔍 Testing MCP server response...");
  const result = await testServerResponse();
  
  if (result.error) {
    console.log("❌ Server test failed:", result.error);
    if (result.raw) {
      console.log("Raw output:", result.raw);
    }
  } else {
    console.log("✅ Server responded correctly");
    console.log("Server info:", result.result?.serverInfo?.name || "Unknown");
  }
}

runQuickTest().catch(console.error);
