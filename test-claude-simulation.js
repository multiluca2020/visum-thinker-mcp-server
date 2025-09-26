/**
 * 🔍 TEST CLAUDE SIMULATION
 * Simula esattamente quello che Claude dovrebbe fare
 * per aprire il progetto Campoleone
 */

import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

console.log('🤖 CLAUDE SIMULATION - Test completo MCP');
console.log('📍 Progetto: Campoleone');
console.log('⏰ Timestamp:', new Date().toISOString());
console.log('');

// Simula la comunicazione MCP di Claude
const mcpServer = spawn('node', ['build/index.js'], {
    cwd: __dirname,
    stdio: ['pipe', 'pipe', 'pipe']
});

let responseCount = 0;

// Handler per le risposte del server
mcpServer.stdout.on('data', (data) => {
    const message = data.toString().trim();
    if (message) {
        console.log('📥 SERVER RESPONSE:', message);
        responseCount++;
        
        // Dopo aver ricevuto la risposta di inizializzazione, invia la richiesta
        if (responseCount === 1) {
            console.log('');
            console.log('🚀 INVIO RICHIESTA project_open...');
            
            const request = {
                jsonrpc: "2.0",
                id: 1,
                method: "tools/call",
                params: {
                    name: "project_open",
                    arguments: {
                        projectPath: "H:\\go\\italferr2025\\Campoleone\\100625_Versione_base_v0.3_sub_ok_priv.ver"
                    }
                }
            };
            
            console.log('📤 REQUEST:', JSON.stringify(request, null, 2));
            mcpServer.stdin.write(JSON.stringify(request) + '\n');
        }
    }
});

mcpServer.stderr.on('data', (data) => {
    console.log('🔧 SERVER LOG:', data.toString().trim());
});

mcpServer.on('close', (code) => {
    console.log(`\n🏁 Server chiuso con codice: ${code}`);
});

// Inizializzazione MCP
console.log('🔄 Inizializzazione MCP...');
const initRequest = {
    jsonrpc: "2.0",
    id: 0,
    method: "initialize",
    params: {
        protocolVersion: "2024-11-05",
        capabilities: {
            tools: {}
        },
        clientInfo: {
            name: "claude-simulation",
            version: "1.0.0"
        }
    }
};

console.log('📤 INIT REQUEST:', JSON.stringify(initRequest, null, 2));
mcpServer.stdin.write(JSON.stringify(initRequest) + '\n');

// Timeout per il test
setTimeout(() => {
    console.log('\n⏰ Timeout test - chiusura...');
    mcpServer.kill();
}, 10000);