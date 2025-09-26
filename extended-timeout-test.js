#!/usr/bin/env node

/**
 * Test MCP Timeout Extended - Testa apertura Campoleone con timeout esteso
 */

import { spawn } from 'child_process';

console.log('🚀 Test MCP Timeout Extended - Progetto Campoleone');

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
    console.log('\n🏗️ APERTURA PROGETTO CAMPOLEONE (TIMEOUT ESTESO)...');
    
    // Invia richiesta apertura progetto con timeout esteso
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
    
    console.log('📤 Invio richiesta apertura...');
    mcp.stdin.write(JSON.stringify(openRequest) + '\n');
    
    // Aspetta più a lungo per progetto grande
    setTimeout(() => {
        console.log('\n📊 CONTROLLO STATUS DOPO 4 MINUTI...');
        
        // Invia richiesta status
        const statusRequest = {
            jsonrpc: "2.0",
            id: 2,
            method: "tools/call",
            params: {
                name: "project_status",
                arguments: {}
            }
        };
        
        mcp.stdin.write(JSON.stringify(statusRequest) + '\n');
        
        // Termina dopo altri 2 minuti
        setTimeout(() => {
            console.log('\n🔚 Terminando test timeout esteso...');
            mcp.kill();
            process.exit(0);
        }, 120000); // Altri 2 minuti
        
    }, 240000); // 4 minuti per il caricamento
    
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
    console.log(`✅ Test timeout esteso completato (exit code: ${code})`);
});

console.log('⏰ Test configurato con timeout di 5 minuti per inizializzazione...');
console.log('📊 Monitoraggio per 6 minuti totali...');