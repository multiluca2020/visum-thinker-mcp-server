#!/usr/bin/env node

import { spawn } from 'child_process';

console.log('🧪 === QUICK MCP HEALTH CHECK ===');

const testPayload = {
  jsonrpc: "2.0",
  id: 1,
  method: "tools/call",
  params: {
    name: "visum_health_check",
    arguments: {}
  }
};

console.log('⏳ Testing visum_health_check tool...\n');

const serverProcess = spawn('node', ['build/index.js'], {
  stdio: ['pipe', 'pipe', 'pipe']
});

let responseData = '';

serverProcess.stdout.on('data', (data) => {
  responseData += data.toString();
});

serverProcess.stderr.on('data', (data) => {
  const logMessage = data.toString();
  if (logMessage.includes('🚀') || logMessage.includes('📋')) {
    console.log('🔧 Server:', logMessage.trim());
  }
});

// Send the test request
serverProcess.stdin.write(JSON.stringify(testPayload) + '\n');

// Wait for response
setTimeout(() => {
  try {
    const response = JSON.parse(responseData);
    if (response.result && response.result.content && response.result.content[0]) {
      console.log('\n✅ === HEALTH CHECK RESPONSE ===');
      console.log(response.result.content[0].text);
    } else {
      console.log('\n❌ === UNEXPECTED RESPONSE ===');
      console.log(responseData);
    }
  } catch (error) {
    console.log('\n❌ === PARSE ERROR ===');
    console.log('Raw response:', responseData);
  }
  
  serverProcess.kill();
}, 15000); // Wait 15 seconds for health check

serverProcess.on('exit', () => {
  console.log('\n🔚 Quick test completed');
});