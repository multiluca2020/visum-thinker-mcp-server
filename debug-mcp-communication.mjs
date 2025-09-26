#!/usr/bin/env node

import { spawn } from 'child_process';

console.log('🐛 === DEBUG MCP SERVER COMMUNICATION ===\n');

const testPayload = {
  jsonrpc: "2.0",
  id: 1,
  method: "tools/call",
  params: {
    name: "visum_health_check",
    arguments: {}
  }
};

console.log('📋 Test payload:', JSON.stringify(testPayload, null, 2));
console.log('⏳ Starting server and monitoring all output...\n');

const serverProcess = spawn('node', ['build/index.js'], {
  stdio: ['pipe', 'pipe', 'pipe']
});

let stdoutData = '';
let stderrData = '';

serverProcess.stdout.on('data', (data) => {
  const chunk = data.toString();
  stdoutData += chunk;
  console.log('📤 STDOUT:', chunk.trim());
});

serverProcess.stderr.on('data', (data) => {
  const chunk = data.toString();
  stderrData += chunk;
  console.log('📢 STDERR:', chunk.trim());
});

serverProcess.on('error', (error) => {
  console.log('❌ Process error:', error.message);
});

// Wait for server to start, then send request
setTimeout(() => {
  console.log('\n📨 Sending request...');
  const payload = JSON.stringify(testPayload) + '\n';
  console.log('📨 Payload length:', payload.length);
  serverProcess.stdin.write(payload);
  
  // Wait for response
  setTimeout(() => {
    console.log('\n📊 === FINAL RESULTS ===');
    console.log('📤 Total STDOUT length:', stdoutData.length);
    console.log('📢 Total STDERR length:', stderrData.length);
    
    if (stdoutData.trim()) {
      console.log('📤 STDOUT content:', stdoutData);
      
      // Try to parse JSON response
      try {
        const lines = stdoutData.split('\n').filter(line => line.trim());
        for (const line of lines) {
          try {
            const parsed = JSON.parse(line);
            if (parsed.jsonrpc) {
              console.log('✅ Found JSON-RPC response:', JSON.stringify(parsed, null, 2));
              break;
            }
          } catch (e) {
            // Not JSON, continue
          }
        }
      } catch (error) {
        console.log('❌ No valid JSON-RPC found in STDOUT');
      }
    } else {
      console.log('❌ No STDOUT received');
    }
    
    serverProcess.kill();
  }, 5000);
  
}, 2000);

serverProcess.on('exit', (code) => {
  console.log('\n🔚 Process exited with code:', code);
});