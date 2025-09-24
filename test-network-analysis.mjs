#!/usr/bin/env node

// Test rapido analisi rete con Visum già caricato
import { spawn } from 'child_process';

console.log('🔍 TEST ANALISI RETE - Visum già caricato');
console.log('═'.repeat(45));

async function testNetworkAnalysis() {
  // Avvia server MCP
  const server = spawn('node', ['build/index.js'], {
    stdio: ['pipe', 'pipe', 'pipe'],
    cwd: process.cwd()
  });
  
  let serverReady = false;
  
  server.stderr.on('data', (data) => {
    if (data.toString().includes('running')) {
      console.log('✅ Server MCP pronto');
      serverReady = true;
      runAnalysis();
    }
  });
  
  server.stdout.on('data', (data) => {
    const output = data.toString().trim();
    if (output) {
      try {
        const response = JSON.parse(output);
        handleResponse(response);
      } catch (e) {
        console.log('📨 Raw:', output.substring(0, 200) + '...');
      }
    }
  });
  
  function runAnalysis() {
    console.log('🔧 Inizializzazione MCP...');
    
    // 1. Inizializza
    const initRequest = {
      jsonrpc: "2.0",
      id: 1,
      method: "initialize",
      params: {
        protocolVersion: "2024-11-05",
        capabilities: {},
        clientInfo: { name: "network-test", version: "1.0.0" }
      }
    };
    
    server.stdin.write(JSON.stringify(initRequest) + '\n');
    
    // 2. Dopo 2 secondi, test analisi rete
    setTimeout(() => {
      console.log('📊 TEST: visum_network_analysis con Visum caricato');
      
      const analysisRequest = {
        jsonrpc: "2.0",
        id: 2,
        method: "tools/call",
        params: {
          name: "visum_network_analysis",
          arguments: {
            analysisType: "detailed",
            exportPath: "C:\\temp\\mcp_test_analysis"
          }
        }
      };
      
      server.stdin.write(JSON.stringify(analysisRequest) + '\n');
      
      // 3. Chiudi dopo 15 secondi per vedere l'output completo
      setTimeout(() => {
        console.log('\n🔄 Test completato, chiusura server...');
        server.kill();
      }, 15000);
      
    }, 2000);
  }
  
  function handleResponse(response) {
    console.log('\n📨 RISPOSTA MCP:');
    console.log('═'.repeat(20));
    
    if (response.id === 1) {
      console.log('✅ Inizializzazione completata');
    } else if (response.id === 2) {
      console.log('📊 RISULTATO ANALISI RETE:');
      
      if (response.result && response.result.content) {
        response.result.content.forEach(content => {
          if (content.type === 'text') {
            console.log(content.text);
          }
        });
      } else if (response.error) {
        console.log('❌ ERRORE ANALISI:', response.error.message);
        if (response.error.data) {
          console.log('📋 Dettagli errore:', response.error.data);
        }
      }
    }
    
    console.log('═'.repeat(20));
  }
  
  server.on('close', (code) => {
    console.log(`\n🏁 Test terminato con codice: ${code}`);
    console.log('\n📋 ANALISI DEL TEST:');
    console.log('✅ Se hai visto "Connected to active Visum instance" → COM funziona');
    console.log('✅ Se hai visto statistiche rete → Analisi riuscita');
    console.log('❌ Se hai visto errori Python → Problema con ambiente Visum');
    console.log('❌ Se hai visto "Network appears empty" → Progetto non caricato in COM');
  });
}

testNetworkAnalysis().catch(console.error);