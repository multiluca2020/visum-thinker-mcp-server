// Ultra-simple MCP test to verify basic communication
import { spawn } from 'child_process';

console.log('🔍 MCP Basic Communication Test');
console.log('=' .repeat(40));

async function testBasicMCP() {
  return new Promise((resolve) => {
    console.log('📡 Testing basic MCP protocol...');
    
    const mcp = spawn('node', ['build/index.js'], {
      stdio: ['pipe', 'pipe', 'pipe'],
      cwd: process.cwd()
    });

    let output = '';
    
    mcp.stdout.on('data', (data) => {
      const text = data.toString();
      output += text;
      
      // Check for server ready message
      if (text.includes('running on stdio')) {
        console.log('✅ Server started');
        
        // Try a basic tools/list request first
        const listRequest = {
          jsonrpc: "2.0",
          id: 1,
          method: "tools/list",
          params: {}
        };
        
        console.log('📤 Requesting tools list...');
        mcp.stdin.write(JSON.stringify(listRequest) + '\n');
      }
      
      // Check for any JSON responses
      const lines = text.split('\n');
      for (const line of lines) {
        if (line.trim().startsWith('{') && line.includes('"jsonrpc"')) {
          try {
            const response = JSON.parse(line.trim());
            console.log('📥 Response received:');
            
            if (response.result && response.result.tools) {
              console.log(`✅ Tools list: ${response.result.tools.length} tools found`);
              
              // Look for Visum tools
              const visumTools = response.result.tools.filter(tool => 
                tool.name.includes('visum') || tool.name.includes('check')
              );
              
              console.log(`🔧 Visum-related tools: ${visumTools.length}`);
              visumTools.forEach(tool => {
                console.log(`   • ${tool.name}: ${tool.description}`);
              });
              
              if (visumTools.length > 0) {
                console.log('✅ MCP communication working!');
                console.log('✅ Visum tools are registered!');
                resolve(true);
              } else {
                console.log('⚠️  No Visum tools found');
                resolve(false);
              }
            } else {
              console.log('📋 Other response:', JSON.stringify(response, null, 2));
            }
            
            setTimeout(() => mcp.kill(), 2000);
          } catch (e) {
            // Not valid JSON
          }
        }
      }
    });

    mcp.stderr.on('data', (data) => {
      console.log('📋 Server log:', data.toString().trim());
    });

    mcp.on('close', (code) => {
      console.log(`📋 Server closed with code: ${code}`);
      resolve(false);
    });

    // Timeout
    setTimeout(() => {
      console.log('⏱️  Timeout');
      mcp.kill();
      resolve(false);
    }, 8000);
  });
}

testBasicMCP().then(success => {
  console.log('\n' + '=' .repeat(40));
  if (success) {
    console.log('🎉 MCP communication is working!');
    console.log('💡 The issue might be with the specific tool execution');
    console.log('💡 Claude should be able to see and use the Visum tools');
  } else {
    console.log('❌ MCP communication issue detected');
    console.log('💡 This explains why Claude cannot access Visum');
  }
}).catch(console.error);
