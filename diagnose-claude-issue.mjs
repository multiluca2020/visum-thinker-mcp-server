// Test the Visum MCP server tools that Claude would use
import { spawn } from 'child_process';
import fs from 'fs';

console.log('🔍 CLAUDE VISUM INTERACTION DIAGNOSTIC');
console.log('=' .repeat(50));

// Create a test that simulates what Claude would do
async function testClaudeVisumInteraction() {
  console.log('\n📋 Simulating Claude\'s Visum requests...\n');

  // Test 1: Check Visum availability (what Claude would ask first)
  await testMCPTool('check_visum_availability', {});
  
  // Test 2: Get Visum status
  await testMCPTool('get_visum_status', {});
  
  // Test 3: Try to initialize Visum 
  await testMCPTool('initialize_visum', {});
  
  // Test 4: Check if we can get memory/status after init
  await testMCPTool('get_visum_memory', {});
}

async function testMCPTool(toolName, args) {
  return new Promise((resolve) => {
    console.log(`🧪 Testing: ${toolName}`);
    console.log(`📝 Args: ${JSON.stringify(args)}`);
    
    const mcp = spawn('node', ['build/index.js'], {
      stdio: ['pipe', 'pipe', 'pipe'],
      cwd: process.cwd()
    });

    let output = '';
    let errorOutput = '';
    let responseReceived = false;

    mcp.stdout.on('data', (data) => {
      const text = data.toString();
      output += text;
      
      // Look for JSON responses
      const lines = text.split('\n');
      for (const line of lines) {
        if (line.trim().startsWith('{') && line.includes('"jsonrpc"')) {
          try {
            const response = JSON.parse(line.trim());
            if (response.result) {
              console.log(`✅ Response received:`);
              console.log(JSON.stringify(response.result, null, 2));
              responseReceived = true;
            } else if (response.error) {
              console.log(`❌ Error response:`);
              console.log(JSON.stringify(response.error, null, 2));
              responseReceived = true;
            }
          } catch (e) {
            // Not JSON, continue
          }
        }
      }
    });

    mcp.stderr.on('data', (data) => {
      errorOutput += data.toString();
    });

    mcp.on('close', (code) => {
      if (!responseReceived) {
        console.log(`❌ No response received (exit code: ${code})`);
        if (errorOutput) {
          console.log(`📋 Error output: ${errorOutput.trim()}`);
        }
      }
      console.log('─'.repeat(40));
      resolve();
    });

    // Wait for server to start
    setTimeout(() => {
      if (output.includes('running on stdio')) {
        // Send the test request
        const request = {
          jsonrpc: "2.0",
          id: Math.floor(Math.random() * 1000),
          method: "tools/call",
          params: {
            name: toolName,
            arguments: args
          }
        };
        
        console.log(`📤 Sending request...`);
        mcp.stdin.write(JSON.stringify(request) + '\n');
        
        // Wait for response
        setTimeout(() => {
          if (!responseReceived) {
            console.log(`⏱️  Timeout waiting for response`);
            mcp.kill();
          }
        }, 5000);
      } else {
        console.log(`❌ Server failed to start properly`);
        mcp.kill();
      }
    }, 2000);
  });
}

// Also test the direct PowerShell approach that should work
async function testDirectPowerShellVisum() {
  console.log('\n🔧 DIRECT POWERSHELL TEST (What actually works)');
  console.log('=' .repeat(50));
  
  return new Promise((resolve) => {
    const script = `
      try {
        Write-Host "Testing direct Visum COM access..."
        $visum = New-Object -ComObject "Visum.Visum"
        Write-Host "✅ COM object created successfully"
        
        $version = $visum.VersionNumber
        Write-Host "✅ Version: $version"
        
        $net = $visum.Net
        Write-Host "✅ Net object: $($net -ne $null)"
        
        # Test basic functionality
        Write-Host "✅ Visum is accessible and working"
        
        # Clean up
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($visum) | Out-Null
        Write-Host "✅ COM object released"
        
      } catch {
        Write-Host "❌ Error: $($_.Exception.Message)"
        exit 1
      }
    `;

    const powershell = spawn('powershell', ['-ExecutionPolicy', 'Bypass', '-Command', script], {
      stdio: ['pipe', 'pipe', 'pipe']
    });

    let output = '';
    let errorOutput = '';

    powershell.stdout.on('data', (data) => {
      output += data.toString();
    });

    powershell.stderr.on('data', (data) => {
      errorOutput += data.toString();
    });

    powershell.on('close', (code) => {
      console.log('📋 Direct PowerShell Result:');
      console.log(output.trim());
      
      if (errorOutput) {
        console.log('📋 Errors:');
        console.log(errorOutput.trim());
      }
      
      if (code === 0) {
        console.log('✅ Direct PowerShell test PASSED');
      } else {
        console.log('❌ Direct PowerShell test FAILED');
      }
      
      resolve();
    });
  });
}

// Check the MCP server configuration
function checkMCPConfiguration() {
  console.log('\n⚙️  MCP SERVER CONFIGURATION CHECK');
  console.log('=' .repeat(50));
  
  // Check if tools are properly registered
  try {
    const indexPath = './build/index.js';
    if (fs.existsSync(indexPath)) {
      const indexContent = fs.readFileSync(indexPath, 'utf8');
      
      const tools = [
        'check_visum_availability',
        'initialize_visum', 
        'get_visum_status',
        'get_visum_memory'
      ];
      
      console.log('📋 Checking tool registration...');
      for (const tool of tools) {
        const isRegistered = indexContent.includes(tool);
        console.log(`   ${isRegistered ? '✅' : '❌'} ${tool}`);
      }
      
      // Check if Visum controller is imported
      const hasVisumController = indexContent.includes('VisumController');
      console.log(`   ${hasVisumController ? '✅' : '❌'} VisumController imported`);
      
    } else {
      console.log('❌ Build artifacts not found');
    }
  } catch (error) {
    console.log(`❌ Configuration check failed: ${error.message}`);
  }
}

// Main execution
async function runDiagnostic() {
  checkMCPConfiguration();
  await testDirectPowerShellVisum();
  await testClaudeVisumInteraction();
  
  console.log('\n🎯 DIAGNOSTIC SUMMARY');
  console.log('=' .repeat(50));
  console.log('1. If Direct PowerShell works but MCP tools fail,');
  console.log('   the issue is in the MCP server implementation');
  console.log('2. If both fail, the issue is with Visum COM registration');
  console.log('3. Claude needs the MCP tools to work correctly');
  console.log('\n💡 Check the MCP tool responses above to identify the issue');
}

runDiagnostic().catch(console.error);
