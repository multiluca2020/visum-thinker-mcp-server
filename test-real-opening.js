/**
 * 🔍 TEST APERTURA REALE CAMPOLEONE
 * Test da zero senza server già attivi
 */

import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

console.log('🚀 TEST APERTURA REALE - Campoleone da zero');
console.log('📍 Progetto: H:\\go\\italferr2025\\Campoleone\\100625_Versione_base_v0.3_sub_ok_priv.ver');
console.log('⏰ Inizio:', new Date().toISOString());
console.log('');

const mcpServer = spawn('node', ['build/index.js'], {
    cwd: __dirname,
    stdio: ['pipe', 'pipe', 'pipe']
});

let initialized = false;

mcpServer.stdout.on('data', (data) => {
    const message = data.toString().trim();
    if (message) {
        console.log('📥 RISPOSTA:', message);
        
        // Dopo l'inizializzazione, chiama project_open
        if (!initialized && message.includes('"serverInfo"')) {
            initialized = true;
            console.log('');
            console.log('🔄 Server inizializzato, chiamo project_open...');
            
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
            
            setTimeout(() => {
                console.log('📤 INVIO project_open...');
                mcpServer.stdin.write(JSON.stringify(request) + '\n');
            }, 500);
        }
    }
});

mcpServer.stderr.on('data', (data) => {
    const logMessage = data.toString().trim();
    console.log('🔧 LOG:', logMessage);
});

mcpServer.on('close', (code) => {
    console.log(`\n🏁 Test completato (codice: ${code})`);
    console.log('⏰ Fine:', new Date().toISOString());
});

// Inizializzazione
const initRequest = {
    jsonrpc: "2.0",
    id: 0,
    method: "initialize",
    params: {
        protocolVersion: "2024-11-05",
        capabilities: { tools: {} },
        clientInfo: { name: "test-real", version: "1.0.0" }
    }
};

console.log('🔄 Invio inizializzazione...');
mcpServer.stdin.write(JSON.stringify(initRequest) + '\n');

// Timeout di 2 minuti per vedere il caricamento completo
setTimeout(() => {
    console.log('\n⏰ Timeout 2 minuti - chiusura test');
    mcpServer.kill();
}, 120000);