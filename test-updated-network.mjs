import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

console.log('=== TEST ANALISI RETE AGGIORNATA ===\n');

// Start the MCP server
const serverPath = join(__dirname, 'build', 'index.js');
console.log(`Starting MCP server: ${serverPath}`);

const serverProcess = spawn('node', [serverPath], {
  stdio: ['pipe', 'pipe', 'pipe'],
  env: { ...process.env }
});

let serverReady = false;
let responseBuffer = '';

// Handle server startup
serverProcess.stderr.on('data', (data) => {
  const message = data.toString();
  console.log(`[Server]: ${message.trim()}`);
  
  if (message.includes('MCP server running on stdio')) {
    serverReady = true;
    console.log('✅ Server ready, starting network analysis test...\n');
    testNetworkAnalysis();
  }
});

// Handle responses
serverProcess.stdout.on('data', (data) => {
  responseBuffer += data.toString();
  
  // Try to parse complete JSON responses
  const lines = responseBuffer.split('\n');
  responseBuffer = lines.pop() || ''; // Keep incomplete line in buffer
  
  for (const line of lines) {
    if (line.trim()) {
      try {
        const response = JSON.parse(line);
        console.log('📝 MCP Response:', JSON.stringify(response, null, 2));
        
        if (response.result?.content?.[0]?.text) {
          console.log('\n🎯 RISULTATO ANALISI:');
          console.log(response.result.content[0].text);
          console.log('\n' + '='.repeat(50));
        }
        
        // Close after getting result
        if (response.result) {
          setTimeout(() => {
            serverProcess.kill();
            process.exit(0);
          }, 1000);
        }
        
      } catch (e) {
        console.log(`[Raw Output]: ${line}`);
      }
    }
  }
});

function testNetworkAnalysis() {
  if (!serverReady) {
    console.log('❌ Server not ready yet');
    return;
  }
  
  const request = {
    jsonrpc: "2.0",
    id: 1,
    method: "tools/call",
    params: {
      name: "visum_network_analysis",
      arguments: {
        analysisType: "detailed"
      }
    }
  };
  
  console.log('🚀 Sending network analysis request...');
  console.log('Request:', JSON.stringify(request, null, 2));
  
  serverProcess.stdin.write(JSON.stringify(request) + '\n');
}

// Handle process events
serverProcess.on('close', (code) => {
  console.log(`\n📋 Test completato (exit code: ${code})`);
});

serverProcess.on('error', (error) => {
  console.error('❌ Server error:', error);
});

// Send initialization
setTimeout(() => {
  if (serverReady) return;
  
  const initRequest = {
    jsonrpc: "2.0",
    id: 0,
    method: "initialize",
    params: {
      protocolVersion: "2024-11-05",
      capabilities: {},
      clientInfo: { name: "test-client", version: "1.0.0" }
    }
  };
  
  console.log('📡 Sending initialization...');
  serverProcess.stdin.write(JSON.stringify(initRequest) + '\n');
}, 100);

console.log('⏳ Waiting for server to start...');