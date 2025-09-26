#!/usr/bin/env node

/**
 * Test Logging MCP - Verifica se Claude chiama effettivamente project_open
 */

import { spawn } from 'child_process';

console.log('🔍 TEST LOGGING - Verifica chiamate Claude');

// Avvia il server MCP
const mcp = spawn('node', ['build/index.js'], {
    stdio: ['pipe', 'pipe', 'pipe'],
    cwd: process.cwd()
});

// Mostra TUTTI i log stderr (include i nostri log di debug)
mcp.stderr.on('data', (data) => {
    const logLine = data.toString().trim();
    if (logLine.includes('PROJECT_OPEN') || logLine.includes('🚀') || logLine.includes('⏰') || logLine.includes('🔄')) {
        console.log('🎯 DEBUG LOG:', logLine);
    } else {
        console.log('🔧 LOG:', logLine);
    }
});

// Aspetta avvio MCP
setTimeout(() => {
    console.log('\n🚀 SIMULO CHIAMATA CLAUDE project_open...');
    
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
    
    // Termina dopo 2 minuti
    setTimeout(() => {
        console.log('\n⏰ Test logging completato');
        mcp.kill();
        process.exit(0);
    }, 120000);
    
}, 3000);

console.log('👀 Monitoraggio chiamate project_open...');