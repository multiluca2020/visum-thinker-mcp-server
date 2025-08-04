// Test the minimal MCP server
import { spawn } from 'child_process';

console.log('🧪 Testing Minimal MCP Server');
console.log('=' .repeat(40));

async function testMinimalServer() {
  return new Promise((resolve) => {
    console.log('📡 Starting minimal test server...');
    
    const server = spawn('node', ['test-server.mjs'], {
      stdio: ['pipe', 'pipe', 'pipe'],
      cwd: process.cwd()
    });

    let serverReady = false;
    
    server.stdout.on('data', (data) => {
      const text = data.toString();
      
      if (text.includes('running on stdio') && !serverReady) {
        serverReady = true;
        console.log('✅ Test server started');
        
        // Test tools/list first
        const listRequest = {
          jsonrpc: "2.0",
          id: 1,
          method: "tools/list",
          params: {}
        };
        
        console.log('📤 Requesting tools list...');
        server.stdin.write(JSON.stringify(listRequest) + '\n');
        
        // Wait a bit then test the Visum tool
        setTimeout(() => {
          const visumRequest = {
            jsonrpc: "2.0", 
            id: 2,
            method: "tools/call",
            params: {
              name: "check_visum",
              arguments: {}
            }
          };
          
          console.log('📤 Testing check_visum tool...');
          server.stdin.write(JSON.stringify(visumRequest) + '\n');
        }, 2000);
      }
      
      // Parse responses
      const lines = text.split('\n');
      for (const line of lines) {
        if (line.trim().startsWith('{') && line.includes('"jsonrpc"')) {
          try {
            const response = JSON.parse(line.trim());
            
            if (response.id === 1 && response.result?.tools) {
              console.log(`✅ Tools list received: ${response.result.tools.length} tools`);
              response.result.tools.forEach(tool => {
                console.log(`   • ${tool.name}`);
              });
            } else if (response.id === 2) {
              console.log('✅ Visum tool response received!');
              if (response.result?.content?.[0]?.text) {
                const text = response.result.content[0].text;
                console.log('📋 Response:', text.split('\n')[0]);
                
                if (text.includes('✅ **Visum Available**')) {
                  console.log('🎉 SUCCESS: Visum is working through minimal MCP!');
                } else {
                  console.log('⚠️  Visum not available, but MCP communication works');
                }
              }
              
              setTimeout(() => {
                server.kill();
                resolve(true);
              }, 1000);
            }
          } catch (e) {
            // Not JSON
          }
        }
      }
    });

    server.stderr.on('data', (data) => {
      console.log('📋 Server:', data.toString().trim());
    });

    server.on('close', (code) => {
      if (!serverReady) {
        console.log('❌ Server failed to start');
        resolve(false);
      }
    });

    setTimeout(() => {
      console.log('⏱️  Test timeout');
      server.kill();
      resolve(false);
    }, 10000);
  });
}

testMinimalServer().then(success => {
  console.log('\n' + '=' .repeat(40));
  if (success) {
    console.log('🎉 Minimal MCP server works!');
    console.log('💡 The issue is likely in the main server code');
    console.log('💡 Claude should be able to use this minimal version');
  } else {
    console.log('❌ Even minimal MCP server fails');
    console.log('💡 This suggests an SDK or environment issue');
  }
}).catch(console.error);
