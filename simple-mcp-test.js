#!/usr/bin/env node

/**
 * Test MCP semplice - Simula apertura progetto Campoleone
 */

import { spawn } from 'child_process';

console.log('🚀 Test MCP Server - Apertura Progetto Campoleone');

// Avvia il server MCP
const mcp = spawn('node', ['build/index.js'], {
    stdio: ['pipe', 'pipe', 'pipe'],
    cwd: process.cwd()
});

// Mostra i log del server
mcp.stderr.on('data', (data) => {
    console.log('🔧 MCP:', data.toString().trim());
});

// Aspetta che il server si avvii
setTimeout(() => {
    console.log('\n📋 STEP 1: Lista tools...');
    
    // Invia richiesta lista tools
    const toolsRequest = {
        jsonrpc: "2.0",
        id: 1,
        method: "tools/list",
        params: {}
    };
    
    mcp.stdin.write(JSON.stringify(toolsRequest) + '\n');
    
    // Aspetta risposta tools
    setTimeout(() => {
        console.log('\n🏗️ STEP 2: Apertura progetto Campoleone...');
        
        // Invia richiesta apertura progetto
        const openRequest = {
            jsonrpc: "2.0",
            id: 2,
            method: "tools/call",
            params: {
                name: "project_open",
                arguments: {
                    projectPath: "H:\\go\\italferr2025\\Campoleone\\100625_Versione_base_v0.3_sub_ok_priv.ver"
                }
            }
        };
        
        mcp.stdin.write(JSON.stringify(openRequest) + '\n');
        
        // Aspetta risposta apertura
        setTimeout(() => {
            console.log('\n📊 STEP 3: Status progetti...');
            
            // Invia richiesta status
            const statusRequest = {
                jsonrpc: "2.0",
                id: 3,
                method: "tools/call",
                params: {
                    name: "project_status",
                    arguments: {}
                }
            };
            
            mcp.stdin.write(JSON.stringify(statusRequest) + '\n');
            
            // Termina dopo 15 secondi
            setTimeout(() => {
                console.log('\n🔚 Terminando test...');
                mcp.kill();
                process.exit(0);
            }, 15000);
            
        }, 5000);
    }, 5000);
}, 3000);

// Mostra tutte le risposte dal server
mcp.stdout.on('data', (data) => {
    const responses = data.toString().split('\n');
    for (const response of responses) {
        if (response.trim()) {
            try {
                const parsed = JSON.parse(response.trim());
                console.log('📥 Risposta MCP:', JSON.stringify(parsed, null, 2));
            } catch (e) {
                console.log('📄 Output MCP:', response.trim());
            }
        }
    }
});

// Gestione errori
mcp.on('error', (error) => {
    console.error('❌ Errore MCP:', error);
});

mcp.on('exit', (code) => {
    console.log(`✅ Test completato (exit code: ${code})`);
});