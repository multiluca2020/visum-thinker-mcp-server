#!/usr/bin/env node

/**
 * Test script to import comprehensive knowledge base into MCP server
 */

import { spawn } from 'child_process';
import fs from 'fs';
import path from 'path';

async function testImportKnowledge() {
  console.log('🧠 Testing comprehensive knowledge base import...\n');

  const knowledgePath = '/Users/uovo/sequential_thinking/visum-complete-knowledge.json';
  
  // Check if knowledge base exists
  if (!fs.existsSync(knowledgePath)) {
    console.error('❌ Knowledge base not found at:', knowledgePath);
    return;
  }

  console.log('✅ Found knowledge base at:', knowledgePath);
  
  // Read knowledge base info
  const knowledge = JSON.parse(fs.readFileSync(knowledgePath, 'utf8'));
  console.log(`📊 Knowledge Base Stats:`);
  console.log(`   - Files: ${knowledge.files?.length || 0}`);
  console.log(`   - Total Pages: ${knowledge.totalPages?.toLocaleString() || 'Unknown'}`);
  console.log(`   - Size: ${knowledge.totalSizeMB?.toFixed(2) || 'Unknown'} MB`);
  console.log(`   - Content Length: ${knowledge.content?.length?.toLocaleString() || 'Unknown'} chars\n`);

  // Create JSON-RPC request
  const request = {
    jsonrpc: "2.0",
    id: 1,
    method: "tools/call",
    params: {
      name: "import_knowledge",
      arguments: {
        importPath: knowledgePath
      }
    }
  };

  console.log('📤 Sending import request to MCP server...');

  // Spawn MCP server
  const serverProcess = spawn('node', ['build/index.js'], {
    cwd: '/Users/uovo/sequential_thinking',
    stdio: ['pipe', 'pipe', 'pipe']
  });

  return new Promise((resolve, reject) => {
    let stdout = '';
    let stderr = '';

    serverProcess.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    serverProcess.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    serverProcess.on('close', (code) => {
      console.log('📥 MCP Server Response:');
      console.log('=======================');
      
      if (stderr) {
        console.log('Server Log:', stderr.trim());
      }
      
      if (stdout) {
        try {
          const responses = stdout.trim().split('\n').filter(line => line.trim());
          responses.forEach((response, index) => {
            if (response.startsWith('{')) {
              const parsed = JSON.parse(response);
              console.log(`Response ${index + 1}:`, JSON.stringify(parsed, null, 2));
              
              if (parsed.result && parsed.result.content) {
                console.log('\n📖 Import Result:');
                console.log(parsed.result.content[0].text);
              }
            }
          });
        } catch (parseError) {
          console.log('Raw output:', stdout);
        }
      }
      
      console.log('\n✅ Test completed');
      resolve(code);
    });

    serverProcess.on('error', (error) => {
      console.error('❌ Error spawning server:', error);
      reject(error);
    });

    // Send the request
    serverProcess.stdin.write(JSON.stringify(request) + '\n');
    serverProcess.stdin.end();
  });
}

// Run the test
testImportKnowledge().catch(console.error);
