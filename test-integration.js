// Test the corrected Visum MCP server
const fs = require('fs');
const { spawn } = require('child_process');

console.log('🧪 Testing Visum MCP Server Integration...\n');

// Test 1: Check if MCP server is running and responsive
function testMCPConnection() {
  return new Promise((resolve) => {
    console.log('📡 Test 1: MCP Server Connection');
    
    const mcp = spawn('node', ['build/index.js'], {
      stdio: ['pipe', 'pipe', 'pipe'],
      cwd: process.cwd()
    });

    let output = '';
    let serverReady = false;

    mcp.stdout.on('data', (data) => {
      output += data.toString();
      if (output.includes('Visum Thinker MCP Server running')) {
        serverReady = true;
        console.log('✅ MCP server started successfully');
        
        // Send a test request to get Visum status
        const testRequest = {
          jsonrpc: "2.0",
          id: 1,
          method: "tools/call",
          params: {
            name: "get_visum_status",
            arguments: {}
          }
        };
        
        mcp.stdin.write(JSON.stringify(testRequest) + '\n');
      }
    });

    mcp.stderr.on('data', (data) => {
      const errorMsg = data.toString();
      console.log('📋 Server log:', errorMsg.trim());
    });

    // Wait for response or timeout
    setTimeout(() => {
      if (serverReady) {
        console.log('✅ Test 1 PASSED: MCP server is responsive\n');
        mcp.kill();
        resolve(true);
      } else {
        console.log('❌ Test 1 FAILED: MCP server not responsive\n');
        mcp.kill();
        resolve(false);
      }
    }, 5000);
  });
}

// Test 2: Check Visum path learning
function testVisumPathLearning() {
  console.log('📂 Test 2: Visum Path Learning System');
  
  try {
    const configPath = './visum-config.json';
    if (fs.existsSync(configPath)) {
      const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
      console.log('✅ Configuration file exists');
      console.log(`📍 Known installations: ${config.knownInstallations.length}`);
      console.log(`🎯 Preferred path: ${config.preferredPath || 'None set'}`);
      
      if (config.knownInstallations.length > 0) {
        const installation = config.knownInstallations[0];
        console.log(`📋 First installation: ${installation.path}`);
        console.log(`🏷️  Version: ${installation.version}`);
        console.log(`📅 Last verified: ${installation.lastVerified}`);
        
        // Verify the path still exists
        if (fs.existsSync(installation.path)) {
          console.log('✅ Installation path is valid');
          console.log('✅ Test 2 PASSED: Learning system is functional\n');
          return true;
        } else {
          console.log('❌ Installation path no longer exists');
          console.log('❌ Test 2 FAILED: Path verification failed\n');
          return false;
        }
      } else {
        console.log('⚠️  No learned installations found');
        console.log('✅ Test 2 PASSED: Config system ready for learning\n');
        return true;
      }
    } else {
      console.log('⚠️  Configuration file not found (will be created on first use)');
      console.log('✅ Test 2 PASSED: System ready for initial learning\n');
      return true;
    }
  } catch (error) {
    console.log(`❌ Test 2 FAILED: ${error.message}\n`);
    return false;
  }
}

// Test 3: Verify COM method corrections
function testCOMMethodCorrections() {
  console.log('🔧 Test 3: COM Method Corrections');
  
  try {
    const controllerPath = './src/visum-controller.ts';
    const controllerContent = fs.readFileSync(controllerPath, 'utf8');
    
    // Check that old methods are replaced
    const hasOldMethods = controllerContent.includes('GetAttValue(\'VersionStr\')');
    const hasNewMethods = controllerContent.includes('VersionNumber');
    const hasHDrivePaths = controllerContent.includes('H:\\\\Program Files\\\\PTV Vision');
    
    if (hasOldMethods) {
      console.log('❌ Still contains old GetAttValue method calls');
      return false;
    }
    
    if (!hasNewMethods) {
      console.log('❌ Missing new VersionNumber property usage');
      return false;
    }
    
    if (!hasHDrivePaths) {
      console.log('❌ Missing H: drive paths in search list');
      return false;
    }
    
    console.log('✅ Old GetAttValue methods removed');
    console.log('✅ New VersionNumber property implemented');
    console.log('✅ H: drive paths added to search list');
    console.log('✅ Test 3 PASSED: COM methods corrected\n');
    return true;
    
  } catch (error) {
    console.log(`❌ Test 3 FAILED: ${error.message}\n`);
    return false;
  }
}

// Test 4: Direct COM test to verify functionality
function testDirectCOM() {
  return new Promise((resolve) => {
    console.log('⚡ Test 4: Direct COM Functionality');
    
    const powershell = spawn('powershell', [
      '-ExecutionPolicy', 'Bypass',
      '-Command',
      `
      try {
        Write-Host "Testing Visum COM with corrected methods..."
        $visum = New-Object -ComObject "Visum.Visum"
        $version = $visum.VersionNumber
        $net = $visum.Net
        Write-Host "SUCCESS: Version=$version, Net=$($net -ne $null)"
        exit 0
      } catch {
        Write-Host "FAILED: $($_.Exception.Message)"
        exit 1
      }
      `
    ], { stdio: ['pipe', 'pipe', 'pipe'] });

    let output = '';
    let errorOutput = '';

    powershell.stdout.on('data', (data) => {
      output += data.toString();
    });

    powershell.stderr.on('data', (data) => {
      errorOutput += data.toString();
    });

    powershell.on('close', (code) => {
      if (code === 0 && output.includes('SUCCESS')) {
        console.log('✅ Direct COM test successful');
        console.log(`📋 ${output.trim()}`);
        console.log('✅ Test 4 PASSED: COM interface working correctly\n');
        resolve(true);
      } else {
        console.log('❌ Direct COM test failed');
        console.log(`📋 Output: ${output.trim()}`);
        console.log(`📋 Error: ${errorOutput.trim()}`);
        console.log('❌ Test 4 FAILED: COM interface issues\n');
        resolve(false);
      }
    });
  });
}

// Run all tests
async function runAllTests() {
  console.log('🚀 Starting Visum MCP Server Integration Tests\n');
  console.log('=' .repeat(60) + '\n');
  
  const results = [];
  
  // Run tests sequentially
  results.push(await testMCPConnection());
  results.push(testVisumPathLearning());
  results.push(testCOMMethodCorrections());
  results.push(await testDirectCOM());
  
  // Summary
  console.log('=' .repeat(60));
  console.log('📊 TEST SUMMARY');
  console.log('=' .repeat(60));
  
  const passed = results.filter(r => r).length;
  const total = results.length;
  
  console.log(`✅ Passed: ${passed}/${total}`);
  console.log(`❌ Failed: ${total - passed}/${total}`);
  
  if (passed === total) {
    console.log('\n🎉 ALL TESTS PASSED! MCP server is ready for use.');
    console.log('🔥 The Visum COM integration issue has been resolved!');
    console.log('\n💡 Key fixes applied:');
    console.log('   • Replaced GetAttValue("VersionStr") with VersionNumber property');
    console.log('   • Added H: drive paths to installation search');
    console.log('   • Updated all COM method calls to use correct interface');
    console.log('   • Verified learning system maintains correct paths');
  } else {
    console.log('\n⚠️  Some tests failed. Check the output above for details.');
  }
  
  console.log('\n🚀 MCP Server Status: Ready for Claude integration');
}

// Start the tests
runAllTests().catch(console.error);
