// Test the echo server
import { spawn } from 'child_process';

console.log('🔍 Testing Basic STDIO Communication');
console.log('=' .repeat(40));

async function testEcho() {
  return new Promise((resolve) => {
    const server = spawn('node', ['echo-server.mjs'], {
      stdio: ['pipe', 'pipe', 'pipe'],
      cwd: process.cwd()
    });

    let responseReceived = false;
    
    server.stdout.on('data', (data) => {
      const text = data.toString();
      console.log('📥 STDOUT:', text.trim());
      
      // Look for JSON response
      try {
        const lines = text.split('\n');
        for (const line of lines) {
          if (line.trim().startsWith('{')) {
            const response = JSON.parse(line.trim());
            if (response.jsonrpc && response.result) {
              console.log('✅ JSON response received!');
              console.log(`📋 Message: ${response.result.message}`);
              responseReceived = true;
              setTimeout(() => {
                server.kill();
                resolve(true);
              }, 500);
            }
          }
        }
      } catch (e) {
        // Not JSON
      }
    });

    server.stderr.on('data', (data) => {
      console.log('📋 STDERR:', data.toString().trim());
      
      if (data.toString().includes('running')) {
        console.log('✅ Echo server started');
        
        // Send test request
        const testRequest = {
          jsonrpc: "2.0",
          id: 42,
          method: "test",
          params: { hello: "world" }
        };
        
        console.log('📤 Sending test request...');
        server.stdin.write(JSON.stringify(testRequest) + '\n');
      }
    });

    server.on('close', (code) => {
      console.log(`📋 Server closed: ${code}`);
      if (!responseReceived) {
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

testEcho().then(success => {
  console.log('\n' + '=' .repeat(40));
  if (success) {
    console.log('✅ Basic STDIO communication works!');
    console.log('💡 The issue is with the MCP SDK, not STDIO itself');
    console.log('💡 We need to debug the MCP server implementation');
  } else {
    console.log('❌ Basic STDIO communication fails');
    console.log('💡 There may be a fundamental Node.js/environment issue');
  }
}).catch(console.error);
