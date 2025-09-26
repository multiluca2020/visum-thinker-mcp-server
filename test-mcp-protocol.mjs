#!/usr/bin/env node

import { spawn } from 'child_process';

console.log('🔧 === TESTING MCP PROTOCOL HANDSHAKE ===\n');

// First test: initialize protocol
const initPayload = {
  jsonrpc: "2.0",
  id: 1,
  method: "initialize",
  params: {
    protocolVersion: "2024-11-05",
    capabilities: {},
    clientInfo: {
      name: "test-client",
      version: "1.0.0"
    }
  }
};

console.log('📋 Testing MCP initialize handshake...');
console.log('📨 Init payload:', JSON.stringify(initPayload, null, 2));

const serverProcess = spawn('node', ['build/index.js'], {
  stdio: ['pipe', 'pipe', 'pipe']
});

let responseData = '';
let serverReady = false;

serverProcess.stdout.on('data', (data) => {
  const chunk = data.toString();
  responseData += chunk;
  console.log('📤 Response chunk:', chunk.trim());
});

serverProcess.stderr.on('data', (data) => {
  const logMessage = data.toString();
  console.log('📢 Server log:', logMessage.trim());
  
  // Wait for server ready message
  if (logMessage.includes('🚀') && logMessage.includes('running on stdio')) {
    serverReady = true;
    console.log('\n✅ Server ready, sending initialize...');
    
    setTimeout(() => {
      const payload = JSON.stringify(initPayload) + '\n';
      console.log('📨 Sending payload of length:', payload.length);
      serverProcess.stdin.write(payload);
      
      // Wait for response
      setTimeout(() => {
        console.log('\n📊 === RESPONSE ANALYSIS ===');
        console.log('📤 Total response length:', responseData.length);
        
        if (responseData.trim()) {
          console.log('📤 Raw response:\n' + responseData);
          
          // Try parsing each line as JSON
          const lines = responseData.split('\n').filter(line => line.trim());
          console.log('📄 Response lines count:', lines.length);
          
          for (let i = 0; i < lines.length; i++) {
            const line = lines[i].trim();
            if (line) {
              try {
                const parsed = JSON.parse(line);
                console.log(`✅ Line ${i + 1} is valid JSON:`, JSON.stringify(parsed, null, 2));
              } catch (e) {
                console.log(`❌ Line ${i + 1} is not JSON:`, line);
              }
            }
          }
        } else {
          console.log('❌ No response received on stdout');
        }
        
        serverProcess.kill();
      }, 3000);
    }, 1000);
  }
});

serverProcess.on('exit', (code) => {
  console.log('\n🔚 Test completed with exit code:', code);
});