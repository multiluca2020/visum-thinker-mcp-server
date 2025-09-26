#!/usr/bin/env node

import { spawn } from 'child_process';

console.log('🎯 === COMPLETE MCP WORKFLOW TEST ===\n');

const serverProcess = spawn('node', ['build/index.js'], {
  stdio: ['pipe', 'pipe', 'pipe']
});

let responseBuffer = '';
let testStep = 0;

const steps = [
  'initialize',
  'tools/list', 
  'visum_health_check'
];

serverProcess.stdout.on('data', (data) => {
  responseBuffer += data.toString();
  
  // Check for complete JSON response
  const lines = responseBuffer.split('\n');
  for (let i = 0; i < lines.length - 1; i++) {
    const line = lines[i].trim();
    if (line) {
      try {
        const response = JSON.parse(line);
        console.log(`✅ Step ${testStep + 1} (${steps[testStep]}) Response:`, JSON.stringify(response, null, 2));
        
        // Move to next step
        testStep++;
        if (testStep < steps.length) {
          setTimeout(() => sendNextRequest(), 1000);
        } else {
          console.log('\n🎉 === ALL TESTS COMPLETED SUCCESSFULLY ===');
          serverProcess.kill();
        }
        
        // Remove processed line
        responseBuffer = lines.slice(i + 1).join('\n');
        break;
      } catch (e) {
        // Not a complete JSON yet
      }
    }
  }
});

serverProcess.stderr.on('data', (data) => {
  const logMessage = data.toString();
  console.log('📢 Server:', logMessage.trim());
  
  if (logMessage.includes('🚀') && testStep === 0) {
    setTimeout(() => sendNextRequest(), 1000);
  }
});

function sendNextRequest() {
  let payload;
  
  switch (steps[testStep]) {
    case 'initialize':
      payload = {
        jsonrpc: "2.0",
        id: testStep + 1,
        method: "initialize",
        params: {
          protocolVersion: "2024-11-05",
          capabilities: {},
          clientInfo: { name: "test-client", version: "1.0.0" }
        }
      };
      break;
      
    case 'tools/list':
      payload = {
        jsonrpc: "2.0",
        id: testStep + 1,
        method: "tools/list",
        params: {}
      };
      break;
      
    case 'visum_health_check':
      payload = {
        jsonrpc: "2.0", 
        id: testStep + 1,
        method: "tools/call",
        params: {
          name: "visum_health_check",
          arguments: {}
        }
      };
      break;
  }
  
  console.log(`\n📨 Sending ${steps[testStep]} request...`);
  serverProcess.stdin.write(JSON.stringify(payload) + '\n');
}

serverProcess.on('exit', (code) => {
  console.log('\n🔚 Complete test finished with exit code:', code);
});