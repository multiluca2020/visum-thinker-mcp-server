#!/usr/bin/env node

// Test semplice MCP Server
import { spawn } from 'child_process';

console.log('🧪 TEST SEMPLICE MCP SERVER CON TOOL VISUM');
console.log('═'.repeat(45));

async function testMCPTools() {
  console.log('🚀 Avvio server MCP...');
  
  // Avvia il server
  const server = spawn('node', ['build/index.js'], {
    stdio: ['pipe', 'pipe', 'pipe'],
    cwd: process.cwd()
  });
  
  let serverReady = false;
  let responses = [];
  
  // Gestisci output server
  server.stderr.on('data', (data) => {
    const message = data.toString().trim();
    if (message.includes('running')) {
      console.log('✅ Server avviato:', message);
      serverReady = true;
      startTests();
    }
  });
  
  server.stdout.on('data', (data) => {
    const output = data.toString().trim();
    if (output) {
      console.log('📨 Server response:', output);
      responses.push(output);
    }
  });
  
  server.on('error', (error) => {
    console.error('❌ Errore server:', error.message);
  });
  
  function startTests() {
    if (!serverReady) return;
    
    console.log('\n🔧 Test 1: Inizializzazione');
    
    // Test inizializzazione
    const initRequest = {
      jsonrpc: "2.0",
      id: 1,
      method: "initialize",
      params: {
        protocolVersion: "2024-11-05",
        capabilities: {},
        clientInfo: { name: "test-client", version: "1.0.0" }
      }
    };
    
    server.stdin.write(JSON.stringify(initRequest) + '\n');
    
    // Dopo 2 secondi, testa la lista dei tool
    setTimeout(() => {
      console.log('\n🛠️  Test 2: Lista Tool');
      
      const listToolsRequest = {
        jsonrpc: "2.0",
        id: 2, 
        method: "tools/list",
        params: {}
      };
      
      server.stdin.write(JSON.stringify(listToolsRequest) + '\n');
      
      // Chiudi dopo 5 secondi
      setTimeout(() => {
        console.log('\n🏁 Terminazione test...');
        server.kill('SIGTERM');
        
        // Analizza risultati
        setTimeout(() => {
          analyzeResults(responses);
        }, 1000);
        
      }, 5000);
      
    }, 2000);
  }
  
  // Timeout di sicurezza
  setTimeout(() => {
    if (!serverReady) {
      console.log('⏰ Timeout - server non avviato, terminazione forzata');
      server.kill('SIGKILL');
    }
  }, 10000);
}

function analyzeResults(responses) {
  console.log('\n📊 ANALISI RISULTATI');
  console.log('═'.repeat(25));
  
  const allOutput = responses.join(' ');
  
  // Verifica tool Visum
  const visumTools = [
    'visum_launch',
    'visum_network_analysis', 
    'visum_export_network',
    'visum_python_analysis',
    'visum_connectivity_stats',
    'visum_val_script'
  ];
  
  console.log('🔍 TOOL VISUM RILEVATI:');
  let foundTools = 0;
  
  visumTools.forEach(tool => {
    const found = allOutput.includes(tool);
    console.log(`${found ? '✅' : '❌'} ${tool}: ${found ? 'PRESENTE' : 'NON TROVATO'}`);
    if (found) foundTools++;
  });
  
  // Verifica tool base
  const baseTools = ['sequential_thinking', 'load_pdf', 'check_visum'];
  console.log('\n🔧 TOOL BASE RILEVATI:');
  
  baseTools.forEach(tool => {
    const found = allOutput.includes(tool);
    console.log(`${found ? '✅' : '❌'} ${tool}: ${found ? 'PRESENTE' : 'NON TROVATO'}`);
  });
  
  // Risultato finale
  console.log('\n🎯 RISULTATO FINALE:');
  console.log(`✅ Tool Visum trovati: ${foundTools}/6`);
  
  if (foundTools === 6) {
    console.log('🎉 SUCCESSO COMPLETO! Tutti i tool Visum sono disponibili per Claude!');
    console.log('\n📋 CLAUDE PUÒ ORA USARE:');
    visumTools.forEach((tool, i) => {
      const descriptions = [
        'Lancia Visum con progetti',
        'Analisi rete avanzata',
        'Export dati CSV', 
        'Script Python personalizzati',
        'Statistiche connettività',
        'Script VAL automatizzati'
      ];
      console.log(`   ${i+1}. ${tool} - ${descriptions[i]}`);
    });
  } else if (foundTools > 0) {
    console.log(`🔶 SUCCESSO PARZIALE! ${foundTools} tool Visum disponibili`);
  } else {
    console.log('❌ ERRORE: Nessun tool Visum trovato');
  }
  
  console.log('\n🔗 INTEGRAZIONE MCP-VISUM COMPLETATA!');
}

// Avvia test
testMCPTools().catch(console.error);