#!/usr/bin/env node

/**
 * Test Debug rapido - Testa apertura Campoleone con logging dettagliato
 */

import { spawn } from 'child_process';

console.log('🔍 TEST DEBUG RAPIDO - Campoleone');
console.log('📁 Progetto:', 'H:\\go\\italferr2025\\Campoleone\\100625_Versione_base_v0.3_sub_ok_priv.ver');
console.log('📊 Dimensione:', '196 MB (file molto grande)');

// Avvia il server MCP
const mcp = spawn('node', ['build/index.js'], {
    stdio: ['pipe', 'pipe', 'pipe'],
    cwd: process.cwd()
});

// Mostra TUTTI i log in tempo reale
mcp.stderr.on('data', (data) => {
    console.log('🔧 STDERR:', data.toString().trim());
});

mcp.stdout.on('data', (data) => {
    const responses = data.toString().split('\n');
    for (const response of responses) {
        if (response.trim()) {
            try {
                const parsed = JSON.parse(response.trim());
                console.log('📥 JSON Response:', JSON.stringify(parsed, null, 2));
            } catch (e) {
                console.log('📄 STDOUT:', response.trim());
            }
        }
    }
});

// Aspetta avvio MCP
setTimeout(() => {
    console.log('\n🚀 INVIO COMANDO project_open...');
    
    const openRequest = {
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
    
    mcp.stdin.write(JSON.stringify(openRequest) + '\n');
    
    // Termina dopo 3 minuti per debug rapido
    setTimeout(() => {
        console.log('\n⏰ TIMEOUT DEBUG - Terminando per analisi...');
        mcp.kill();
        process.exit(0);
    }, 180000); // 3 minuti
    
}, 3000);

mcp.on('error', (error) => {
    console.error('❌ Errore MCP:', error);
});

mcp.on('exit', (code) => {
    console.log(`🔚 Test debug completato (exit code: ${code})`);
});

console.log('⏰ Test configurato con timeout di 3 minuti per debug rapido...');