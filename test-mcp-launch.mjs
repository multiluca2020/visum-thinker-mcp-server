#!/usr/bin/env node

import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

console.log('🧪 === TESTING MCP VISUM LAUNCH TOOL ===');

const projectPath = "H:\\go\\italferr2025\\Campoleone\\100625_Versione_base_v0.3_sub_ok_priv.ver";

const testPayload = {
  jsonrpc: "2.0",
  id: 1,
  method: "tools/call",
  params: {
    name: "visum_launch_project",
    arguments: {
      projectPath: projectPath
    }
  }
};

console.log('📋 Testing project launch with:', projectPath);
console.log('⏳ Starting MCP server and sending request...\n');

const serverProcess = spawn('node', [join(__dirname, 'build', 'index.js')], {
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

// Wait for response and then kill server
setTimeout(() => {
  try {
    const response = JSON.parse(responseData);
    if (response.result && response.result.content && response.result.content[0]) {
      console.log('\n✅ === TOOL RESPONSE ===');
      console.log(response.result.content[0].text);
    } else {
      console.log('\n❌ === UNEXPECTED RESPONSE ===');
      console.log(responseData);
    }
  } catch (error) {
    console.log('\n❌ === PARSE ERROR ===');
    console.log('Raw response:', responseData);
    console.log('Error:', error.message);
  }
  
  serverProcess.kill();
}, 90000); // Wait 90 seconds for Visum to load

serverProcess.on('exit', (code) => {
  console.log('\n🔚 Test completed with exit code:', code);
});