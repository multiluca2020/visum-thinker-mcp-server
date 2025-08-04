// Quick test of the working server with correct tool names
import { spawn } from 'child_process';

console.log('🔍 Testing Working Server Connection');
console.log('=' .repeat(40));

async function testWorkingServerConnection() {
  return new Promise((resolve) => {
    console.log('📡 Testing working-visum-mcp.mjs...');
    
    const server = spawn('node', ['working-visum-mcp.mjs'], {
      stdio: ['pipe', 'pipe', 'pipe'],
      cwd: process.cwd()
    });

    let serverReady = false;
    let responseReceived = false;
    
    server.stdout.on('data', (data) => {
      const text = data.toString();
      
      const lines = text.split('\n');
      for (const line of lines) {
        if (line.trim().startsWith('{')) {
          try {
            const response = JSON.parse(line.trim());
            console.log('✅ Server response received!');
            console.log(JSON.stringify(response, null, 2));
            responseReceived = true;
            
            setTimeout(() => {
              server.kill();
              resolve(true);
            }, 1000);
          } catch (e) {
            // Not JSON
          }
        }
      }
    });

    server.stderr.on('data', (data) => {
      const text = data.toString().trim();
      console.log('📋 Server:', text);
      
      if (text.includes('ready for Claude') && !serverReady) {
        serverReady = true;
        console.log('✅ Server started, testing...');
        
        // Send a simple tools/list request
        const request = {
          jsonrpc: "2.0",
          id: 1,
          method: "tools/list",
          params: {}
        };
        
        console.log('📤 Sending tools/list request...');
        server.stdin.write(JSON.stringify(request) + '\n');
      }
    });

    server.on('close', (code) => {
      if (!responseReceived) {
        console.log('❌ No response received');
        resolve(false);
      }
    });

    setTimeout(() => {
      if (!responseReceived) {
        console.log('⏱️  Timeout');
        server.kill();
        resolve(false);
      }
    }, 5000);
  });
}

testWorkingServerConnection().then(success => {
  if (success) {
    console.log('\n✅ Working server responds correctly');
    console.log('💡 The issue may be with Claude\'s MCP configuration');
  } else {
    console.log('\n❌ Working server has issues');
    console.log('💡 Need to fix the server implementation');
  }
}).catch(console.error);
