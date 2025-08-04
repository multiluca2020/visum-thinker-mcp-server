#!/usr/bin/env node

// Ultra-simple STDIO test - just echo back what we receive
import { createInterface } from 'readline';

console.error("Simple STDIO Echo Server running");

const rl = createInterface({
  input: process.stdin,
  output: process.stdout,
  terminal: false
});

rl.on('line', (line) => {
  try {
    console.error(`Received: ${line}`);
    
    // Try to parse as JSON
    const request = JSON.parse(line);
    
    // Send back a simple response
    const response = {
      jsonrpc: "2.0",
      id: request.id,
      result: {
        message: "Echo server is working",
        received: request
      }
    };
    
    console.log(JSON.stringify(response));
    console.error(`Sent response for ID: ${request.id}`);
    
  } catch (error) {
    console.error(`Error processing line: ${error.message}`);
  }
});

rl.on('close', () => {
  console.error('STDIO closed');
  process.exit(0);
});
