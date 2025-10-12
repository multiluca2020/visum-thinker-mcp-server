#!/usr/bin/env node
/**
 * MCP Quick Call - Invia un singolo comando MCP e termina
 * Uso: node mcp-quick-call.js <tool_name> <json_args>
 * 
 * Esempio:
 *   node mcp-quick-call.js visum_list_demand_segments '{"projectId":"..."}'
 */

import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const args = process.argv.slice(2);

if (args.length < 2) {
  console.error('❌ Usage: node mcp-quick-call.js <tool_name> <json_args>');
  console.error('');
  console.error('Example:');
  console.error('  node mcp-quick-call.js visum_list_demand_segments \'{"projectId":"100625_Versione_base_v0.3_sub_ok_priv_10176442"}\'');
  process.exit(1);
}

const toolName = args[0];
const argsJson = args[1];

let argsObj;
try {
  argsObj = JSON.parse(argsJson);
} catch (e) {
  console.error('❌ Invalid JSON arguments:', e.message);
  process.exit(1);
}

const mcpRequest = {
  jsonrpc: "2.0",
  id: Math.floor(Math.random() * 1000000),
  method: "tools/call",
  params: {
    name: toolName,
    arguments: argsObj
  }
};

console.error(`📤 Calling tool: ${toolName}`);
console.error(`📋 Arguments:`, argsObj);
console.error('');

const mcpServer = spawn('node', [join(__dirname, 'build', 'index.js')], {
  stdio: ['pipe', 'pipe', 'inherit']
});

let responseData = '';
let hasResponse = false;

mcpServer.stdout.on('data', (data) => {
  responseData += data.toString();
  
  // Cerca una risposta JSON completa
  try {
    const lines = responseData.split('\n');
    for (const line of lines) {
      if (line.trim().startsWith('{')) {
        const response = JSON.parse(line);
        if (response.id === mcpRequest.id) {
          hasResponse = true;
          console.log('📥 Response:');
          console.log(JSON.stringify(response, null, 2));
          
          // Termina il server dopo la risposta
          setTimeout(() => {
            mcpServer.kill('SIGTERM');
            setTimeout(() => {
              if (!mcpServer.killed) {
                mcpServer.kill('SIGKILL');
              }
              process.exit(0);
            }, 500);
          }, 100);
        }
      }
    }
  } catch (e) {
    // Ignora errori di parsing parziale
  }
});

mcpServer.on('error', (err) => {
  console.error('❌ Error:', err.message);
  process.exit(1);
});

mcpServer.on('exit', (code) => {
  if (!hasResponse) {
    console.error('❌ Server exited without response. Exit code:', code);
    process.exit(1);
  }
});

// Invia il comando
mcpServer.stdin.write(JSON.stringify(mcpRequest) + '\n');
mcpServer.stdin.end();

// Timeout di sicurezza
setTimeout(() => {
  if (!hasResponse) {
    console.error('⏱️ Timeout - no response after 30 seconds');
    mcpServer.kill('SIGKILL');
    process.exit(1);
  }
}, 30000);
