// Simple test for Claude's Visum access
import { spawn } from 'child_process';

console.log('🧪 Testing Claude\'s Access to Visum via MCP');
console.log('=' .repeat(50));

async function testClaudeVisumAccess() {
  return new Promise((resolve) => {
    console.log('📡 Starting MCP server and testing tool call...');
    
    const mcp = spawn('node', ['build/index.js'], {
      stdio: ['pipe', 'pipe', 'pipe'],
      cwd: process.cwd()
    });

    let serverReady = false;
    let testComplete = false;

    mcp.stdout.on('data', (data) => {
      const text = data.toString();
      
      // Check if server is ready
      if (text.includes('running on stdio') && !serverReady) {
        serverReady = true;
        console.log('✅ MCP server started successfully');
        
        // Send a test request using the correct tool name
        const request = {
          jsonrpc: "2.0",
          id: 1,
          method: "tools/call",
          params: {
            name: "check_visum", // Correct tool name
            arguments: {}
          }
        };
        
        console.log('📤 Sending check_visum request...');
        mcp.stdin.write(JSON.stringify(request) + '\n');
      }
      
      // Look for response
      const lines = text.split('\n');
      for (const line of lines) {
        if (line.trim().startsWith('{') && line.includes('"jsonrpc"')) {
          try {
            const response = JSON.parse(line.trim());
            if (response.result && !testComplete) {
              testComplete = true;
              console.log('✅ SUCCESS: MCP tool responded correctly!');
              console.log('📋 Response preview:');
              
              // Extract the text content from the result
              if (response.result.content && response.result.content[0] && response.result.content[0].text) {
                const responseText = response.result.content[0].text;
                const firstLines = responseText.split('\n').slice(0, 5).join('\n');
                console.log(firstLines + '\n...');
                
                if (responseText.includes('✅ **Visum Available**')) {
                  console.log('🎉 VISUM IS WORKING! Claude should be able to access it now.');
                } else if (responseText.includes('❌ **Visum Not Found**')) {
                  console.log('⚠️  Visum not detected, but MCP tool is working correctly.');
                }
              }
              
              setTimeout(() => {
                mcp.kill();
                resolve(true);
              }, 1000);
            } else if (response.error && !testComplete) {
              testComplete = true;
              console.log('❌ Error response from MCP tool:');
              console.log(JSON.stringify(response.error, null, 2));
              setTimeout(() => {
                mcp.kill();
                resolve(false);
              }, 1000);
            }
          } catch (e) {
            // Not valid JSON, continue
          }
        }
      }
    });

    mcp.stderr.on('data', (data) => {
      const errorText = data.toString();
      console.log('📋 Server log:', errorText.trim());
    });

    mcp.on('close', (code) => {
      if (!testComplete) {
        console.log(`❌ Test incomplete (server closed with code: ${code})`);
        resolve(false);
      }
    });

    // Timeout if no response
    setTimeout(() => {
      if (!testComplete) {
        console.log('⏱️  Timeout - no response received');
        mcp.kill();
        resolve(false);
      }
    }, 10000);
  });
}

// Also verify Visum is directly accessible
async function testDirectVisum() {
  console.log('\n🔧 Direct Visum Test (for comparison)');
  console.log('=' .repeat(30));
  
  return new Promise((resolve) => {
    const script = `
      try {
        $visum = New-Object -ComObject "Visum.Visum"
        $version = $visum.VersionNumber
        Write-Host "✅ Visum accessible, version: $version"
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($visum) | Out-Null
      } catch {
        Write-Host "❌ Visum not accessible: $($_.Exception.Message)"
        exit 1
      }
    `;

    const powershell = spawn('powershell', ['-ExecutionPolicy', 'Bypass', '-Command', script]);

    let output = '';
    powershell.stdout.on('data', (data) => {
      output += data.toString();
    });

    powershell.on('close', (code) => {
      console.log('📋 Direct test result:', output.trim());
      resolve(code === 0);
    });
  });
}

async function runTest() {
  console.log('🚀 Running Claude Visum Access Test\n');
  
  const directResult = await testDirectVisum();
  const mcpResult = await testClaudeVisumAccess();
  
  console.log('\n' + '=' .repeat(50));
  console.log('📊 TEST RESULTS');
  console.log('=' .repeat(50));
  console.log(`Direct Visum Access: ${directResult ? '✅ PASS' : '❌ FAIL'}`);
  console.log(`MCP Tool Response: ${mcpResult ? '✅ PASS' : '❌ FAIL'}`);
  
  if (directResult && mcpResult) {
    console.log('\n🎉 SUCCESS! Claude should be able to access Visum via MCP');
    console.log('\n💡 Try asking Claude to:');
    console.log('   • Check if Visum is available');
    console.log('   • Initialize Visum');
    console.log('   • Get Visum status');
  } else if (directResult && !mcpResult) {
    console.log('\n⚠️  Visum works directly but MCP has issues');
    console.log('   The server might need debugging');
  } else {
    console.log('\n❌ Visum access issues detected');
    console.log('   Check Visum installation and COM registration');
  }
}

runTest().catch(console.error);
