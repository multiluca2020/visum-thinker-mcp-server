#!/usr/bin/env node

/**
 * Test MCP Client - Simula i comandi che Claude invierebbe all'MCP
 * Testa l'apertura del progetto Campoleone
 */

import { spawn } from 'child_process';
import { createReadStream, createWriteStream } from 'fs';
import { setTimeout } from 'timers/promises';

class MCPTestClient {
    constructor() {
        this.requestId = 1;
        this.mcpProcess = null;
    }

    async startMCPServer() {
        console.log('🚀 Avviando server MCP...');
        
        this.mcpProcess = spawn('node', ['build/index.js'], {
            stdio: ['pipe', 'pipe', 'pipe'],
            cwd: process.cwd()
        });

        // Gestisce stderr per i log del server
        this.mcpProcess.stderr.on('data', (data) => {
            console.log('📋 MCP Log:', data.toString().trim());
        });

        await setTimeout(2000); // Aspetta che il server si avvii
        console.log('✅ Server MCP avviato');
    }

    async sendRequest(method, params = {}) {
        const request = {
            jsonrpc: "2.0",
            id: this.requestId++,
            method: method,
            params: params
        };

        console.log(`\n🔄 Invio richiesta: ${method}`);
        console.log('📤 Payload:', JSON.stringify(request, null, 2));

        return new Promise((resolve, reject) => {
            let responseData = '';
            
            const onData = (data) => {
                responseData += data.toString();
                
                // Cerca una risposta JSON completa
                const lines = responseData.split('\n');
                for (const line of lines) {
                    if (line.trim()) {
                        try {
                            const response = JSON.parse(line.trim());
                            if (response.id === request.id) {
                                this.mcpProcess.stdout.off('data', onData);
                                resolve(response);
                                return;
                            }
                        } catch (e) {
                            // Continua a cercare
                        }
                    }
                }
            };

            this.mcpProcess.stdout.on('data', onData);
            
            // Invia la richiesta
            this.mcpProcess.stdin.write(JSON.stringify(request) + '\n');
            
            // Timeout
            const timeoutId = setTimeout(() => {
                this.mcpProcess.stdout.off('data', onData);
                reject(new Error('Timeout: Nessuna risposta dal server MCP'));
            }, 10000);
        });
    }

    async testWorkflow() {
        try {
            await this.startMCPServer();

            // 1. Lista tools disponibili
            console.log('\n' + '='.repeat(50));
            console.log('📋 STEP 1: Lista tools disponibili');
            const toolsResponse = await this.sendRequest('tools/list');
            console.log('📥 Risposta:', JSON.stringify(toolsResponse, null, 2));

            // 2. Apri progetto Campoleone
            console.log('\n' + '='.repeat(50));
            console.log('🏗️ STEP 2: Apertura progetto Campoleone');
            const projectPath = 'H:\\go\\italferr2025\\Campoleone\\100625_Versione_base_v0.3_sub_ok_priv.ver';
            
            const openResponse = await this.sendRequest('tools/call', {
                name: 'project_open',
                arguments: {
                    projectPath: projectPath
                }
            });
            console.log('📥 Risposta apertura:', JSON.stringify(openResponse, null, 2));

            // 3. Controlla status
            console.log('\n' + '='.repeat(50));
            console.log('📊 STEP 3: Controllo status progetti');
            const statusResponse = await this.sendRequest('tools/call', {
                name: 'project_status',
                arguments: {}
            });
            console.log('📥 Risposta status:', JSON.stringify(statusResponse, null, 2));

        } catch (error) {
            console.error('❌ Errore nel test:', error);
        } finally {
            if (this.mcpProcess) {
                console.log('\n🔚 Terminando server MCP...');
                this.mcpProcess.kill();
            }
        }
    }
}

// Avvia il test
const client = new MCPTestClient();
client.testWorkflow().then(() => {
    console.log('✅ Test completato');
    process.exit(0);
}).catch((error) => {
    console.error('❌ Test fallito:', error);
    process.exit(1);
});