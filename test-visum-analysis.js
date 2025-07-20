#!/usr/bin/env node

/**
 * Quick test of sequential thinking with the loaded Visum knowledge
 */

import { spawn } from 'child_process';

async function testVisumAnalysis() {
  console.log('🧠 Testing Visum Analysis with Loaded Knowledge...\n');

  const request = {
    jsonrpc: "2.0",
    id: 2,
    method: "tools/call",
    params: {
      name: "sequential_thinking",
      arguments: {
        query: "Plan a complete workflow for creating a public transport model in PTV Visum, including network setup, demand modeling, and calibration steps"
      }
    }
  };

  const serverProcess = spawn('node', ['build/index.js'], {
    cwd: '/Users/uovo/sequential_thinking',
    stdio: ['pipe', 'pipe', 'pipe']
  });

  return new Promise((resolve) => {
    let stdout = '';
    let stderr = '';

    serverProcess.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    serverProcess.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    serverProcess.on('close', () => {
      console.log('📖 Sequential Thinking Analysis:');
      console.log('=================================');
      
      if (stdout) {
        try {
          const responses = stdout.trim().split('\n').filter(line => line.trim());
          responses.forEach((response) => {
            if (response.startsWith('{')) {
              const parsed = JSON.parse(response);
              if (parsed.result && parsed.result.content) {
                console.log(parsed.result.content[0].text);
              }
            }
          });
        } catch (parseError) {
          console.log('Raw analysis output:', stdout);
        }
      }
      
      console.log('\n✅ Visum analysis completed');
      resolve(0);
    });

    // Send the request
    serverProcess.stdin.write(JSON.stringify(request) + '\n');
    serverProcess.stdin.end();
  });
}

// Run the test
console.log('🚀 Testing your comprehensive Visum knowledge base...');
testVisumAnalysis().catch(console.error);
