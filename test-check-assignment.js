#!/usr/bin/env node

/**
 * Test Script for visum_check_assignment Tool
 * 
 * Usage:
 *   node test-check-assignment.js <projectId> [analysisPeriod]
 * 
 * Examples:
 *   node test-check-assignment.js S000009result_1278407893
 *   node test-check-assignment.js S000009result_1278407893 AM
 */

import { spawn } from 'child_process';
import * as readline from 'readline';

// Parse command line arguments
const args = process.argv.slice(2);
if (args.length === 0) {
  console.error('❌ Error: Missing projectId argument');
  console.error('\nUsage:');
  console.error('  node test-check-assignment.js <projectId> [analysisPeriod]');
  console.error('\nExamples:');
  console.error('  node test-check-assignment.js S000009result_1278407893');
  console.error('  node test-check-assignment.js S000009result_1278407893 AM');
  process.exit(1);
}

const projectId = args[0];
const analysisPeriod = args[1] || 'AP';

console.log('🔍 Testing visum_check_assignment Tool');
console.log(`📊 Project ID: ${projectId}`);
console.log(`🕐 Analysis Period: ${analysisPeriod}`);
console.log('═'.repeat(60));

// Build MCP request
const request = {
  jsonrpc: "2.0",
  id: 1,
  method: "tools/call",
  params: {
    name: "visum_check_assignment",
    arguments: {
      projectId: projectId,
      analysisPeriod: analysisPeriod
    }
  }
};

const requestJson = JSON.stringify(request);

console.log('\n📤 Sending request:');
console.log(JSON.stringify(request, null, 2));
console.log('═'.repeat(60));

// Spawn MCP server process
const mcpProcess = spawn('node', ['build/index.js'], {
  stdio: ['pipe', 'pipe', 'inherit'],
  shell: false
});

let responseData = '';
let hasReceivedResponse = false;

// Handle stdout (MCP responses)
const rl = readline.createInterface({
  input: mcpProcess.stdout,
  crlfDelay: Infinity
});

rl.on('line', (line) => {
  if (!line.trim()) return;
  
  try {
    const parsed = JSON.parse(line);
    
    if (parsed.id === 1 && parsed.result) {
      hasReceivedResponse = true;
      console.log('\n📥 Response received:');
      console.log('═'.repeat(60));
      
      const content = parsed.result.content;
      if (content && content[0] && content[0].text) {
        console.log(content[0].text);
      } else {
        console.log(JSON.stringify(parsed.result, null, 2));
      }
      
      console.log('═'.repeat(60));
      console.log('✅ Test completed successfully');
      
      // Terminate process
      mcpProcess.stdin.end();
      setTimeout(() => {
        mcpProcess.kill();
        process.exit(0);
      }, 500);
    }
  } catch (e) {
    // Ignore non-JSON lines (initialization messages)
  }
});

// Handle process errors
mcpProcess.on('error', (error) => {
  console.error('❌ Failed to start MCP server:', error);
  process.exit(1);
});

mcpProcess.on('exit', (code) => {
  if (!hasReceivedResponse) {
    console.error('\n❌ No response received from MCP server');
    process.exit(1);
  }
});

// Send request after short delay to allow server initialization
setTimeout(() => {
  mcpProcess.stdin.write(requestJson + '\n');
}, 1000);

// Timeout after 30 seconds
setTimeout(() => {
  if (!hasReceivedResponse) {
    console.error('\n❌ Timeout: No response after 30 seconds');
    mcpProcess.kill();
    process.exit(1);
  }
}, 30000);
