// Test the working MCP server
import { spawn } from 'child_process';

console.log('🎯 Testing Working Visum MCP Server for Claude');
console.log('=' .repeat(50));

async function testWorkingServer() {
  return new Promise((resolve) => {
    const server = spawn('node', ['working-visum-mcp.mjs'], {
      stdio: ['pipe', 'pipe', 'pipe'],
      cwd: process.cwd()
    });

    let tests = {
      serverStart: false,
      toolsList: false,
      checkVisum: false,
      initVisum: false,
      getStatus: false
    };

    server.stdout.on('data', (data) => {
      const text = data.toString();
      
      const lines = text.split('\n');
      for (const line of lines) {
        if (line.trim().startsWith('{')) {
          try {
            const response = JSON.parse(line.trim());
            
            if (response.result?.tools) {
              tests.toolsList = true;
              console.log(`✅ Tools list: ${response.result.tools.length} tools`);
              response.result.tools.forEach(tool => {
                console.log(`   • ${tool.name}: ${tool.description}`);
              });
            }
            
            else if (response.result?.content?.[0]?.text) {
              const text = response.result.content[0].text;
              const firstLine = text.split('\n')[0];
              
              if (text.includes('Visum Available')) {
                tests.checkVisum = true;
                console.log('✅ check_visum: Visum detected as available');
              } else if (text.includes('Initialized Successfully')) {
                tests.initVisum = true;
                console.log('✅ initialize_visum: Initialization successful');
              } else if (text.includes('Current Visum Status')) {
                tests.getStatus = true;
                console.log('✅ get_visum_status: Status retrieved');
              }
              
              console.log(`📋 Response: ${firstLine}`);
            }
          } catch (e) {
            // Not JSON
          }
        }
      }
    });

    server.stderr.on('data', (data) => {
      const text = data.toString().trim();
      console.log('📋 Server:', text);
      
      if (text.includes('ready for Claude')) {
        tests.serverStart = true;
        console.log('✅ Server started successfully');
        
        // Run sequential tests
        setTimeout(runTests, 1000);
      }
    });

    function runTests() {
      // Test 1: Tools list
      const listRequest = {
        jsonrpc: "2.0",
        id: 1,
        method: "tools/list",
        params: {}
      };
      console.log('📤 Testing tools/list...');
      server.stdin.write(JSON.stringify(listRequest) + '\n');
      
      // Test 2: Check Visum
      setTimeout(() => {
        const checkRequest = {
          jsonrpc: "2.0",
          id: 2,
          method: "tools/call",
          params: { name: "check_visum", arguments: {} }
        };
        console.log('📤 Testing check_visum...');
        server.stdin.write(JSON.stringify(checkRequest) + '\n');
      }, 1500);
      
      // Test 3: Initialize Visum
      setTimeout(() => {
        const initRequest = {
          jsonrpc: "2.0",
          id: 3,
          method: "tools/call",
          params: { name: "initialize_visum", arguments: {} }
        };
        console.log('📤 Testing initialize_visum...');
        server.stdin.write(JSON.stringify(initRequest) + '\n');
      }, 3000);
      
      // Test 4: Get Status
      setTimeout(() => {
        const statusRequest = {
          jsonrpc: "2.0",
          id: 4,
          method: "tools/call",
          params: { name: "get_visum_status", arguments: {} }
        };
        console.log('📤 Testing get_visum_status...');
        server.stdin.write(JSON.stringify(statusRequest) + '\n');
      }, 4500);
      
      // Finish test
      setTimeout(() => {
        server.kill();
        resolve(tests);
      }, 6000);
    }

    server.on('close', () => {
      resolve(tests);
    });
  });
}

testWorkingServer().then(results => {
  console.log('\n' + '=' .repeat(50));
  console.log('📊 TEST RESULTS');
  console.log('=' .repeat(50));
  
  const passed = Object.values(results).filter(r => r).length;
  const total = Object.keys(results).length;
  
  console.log(`✅ Passed: ${passed}/${total}`);
  Object.entries(results).forEach(([test, result]) => {
    console.log(`${result ? '✅' : '❌'} ${test}`);
  });
  
  if (passed >= 4) {
    console.log('\n🎉 SUCCESS! Working MCP server is ready for Claude!');
    console.log('\n💡 Instructions for Claude:');
    console.log('1. Stop the current MCP server if running');
    console.log('2. Start: node working-visum-mcp.mjs');
    console.log('3. Claude can now access Visum tools successfully');
    console.log('\n🔧 Available tools for Claude:');
    console.log('   • check_visum - Check Visum availability');
    console.log('   • initialize_visum - Initialize COM connection');
    console.log('   • get_visum_status - Get current status');
  } else {
    console.log('\n⚠️  Some tests failed - debugging needed');
  }
}).catch(console.error);
