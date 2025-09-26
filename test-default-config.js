/**
 * 🔍 TEST CONFIGURAZIONE PREDEFINITA
 * Verifica che project_open sia mostrato come DEFAULT
 */

import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

console.log('🔧 TEST CONFIGURAZIONE PREDEFINITA');
console.log('🎯 Verifica che project_open sia il tool DEFAULT');
console.log('');

const mcpServer = spawn('node', ['build/index.js'], {
    cwd: __dirname,
    stdio: ['pipe', 'pipe', 'pipe']
});

mcpServer.stdout.on('data', (data) => {
    const message = data.toString().trim();
    if (message && message.includes('tools')) {
        console.log('📥 TOOL LIST RESPONSE:', message);
        mcpServer.kill();
    }
});

mcpServer.stderr.on('data', (data) => {
    const logMessage = data.toString().trim();
    if (logMessage.includes('DEFAULT') || logMessage.includes('project_open')) {
        console.log('✅ FOUND DEFAULT:', logMessage);
    }
});

mcpServer.on('close', (code) => {
    console.log('\n🏁 Test configurazione completato');
});

// Richiedi lista tool
const listToolsRequest = {
    jsonrpc: "2.0",
    id: 1,
    method: "tools/list",
    params: {}
};

setTimeout(() => {
    mcpServer.stdin.write(JSON.stringify(listToolsRequest) + '\n');
}, 1000);

setTimeout(() => {
    mcpServer.kill();
}, 5000);