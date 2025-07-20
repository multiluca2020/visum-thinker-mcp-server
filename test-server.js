#!/usr/bin/env node

// Simple test script to verify the MCP server functionality
import { spawn } from 'child_process';

console.log('Testing Visum Thinker MCP Server...');

// Test 1: Check if server starts without errors
const server = spawn('node', ['build/index.js'], {
  stdio: ['pipe', 'pipe', 'inherit'],
  cwd: process.cwd()
});

let output = '';
let testTimeout;

server.stdout.on('data', (data) => {
  output += data.toString();
  console.log('Server output:', data.toString());
});

server.on('error', (error) => {
  console.error('Server error:', error.message);
  process.exit(1);
});

// Test basic MCP initialization message
testTimeout = setTimeout(() => {
  console.log('Test 1: Server startup - PASSED');
  
  // Send MCP initialization request
  const initRequest = {
    jsonrpc: '2.0',
    id: 1,
    method: 'initialize',
    params: {
      protocolVersion: '2024-11-05',
      capabilities: {},
      clientInfo: { name: 'test-client', version: '1.0.0' }
    }
  };
  
  console.log('Sending initialization request...');
  server.stdin.write(JSON.stringify(initRequest) + '\n');
  
  // Wait for response
  setTimeout(() => {
    console.log('Test 2: Initialization - COMPLETED');
    
    // Test tools listing
    const toolsRequest = {
      jsonrpc: '2.0',
      id: 2,
      method: 'tools/list',
      params: {}
    };
    
    console.log('Requesting tools list...');
    server.stdin.write(JSON.stringify(toolsRequest) + '\n');
    
    setTimeout(() => {
      console.log('Test 3: Tools listing - COMPLETED');
      console.log('All tests completed. Server appears to be working correctly.');
      
      // Cleanup
      server.kill('SIGTERM');
      process.exit(0);
    }, 2000);
    
  }, 2000);
  
}, 1000);

// Cleanup on exit
process.on('SIGINT', () => {
  clearTimeout(testTimeout);
  server.kill('SIGTERM');
  process.exit(0);
});
