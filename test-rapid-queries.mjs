#!/usr/bin/env node

import { spawn } from 'child_process';

console.log('⚡ === TEST INTERROGAZIONI RAPIDE SU ISTANZA ATTIVA ===\n');

// Questo script presuppone che un'istanza VisumPy con Campoleone sia già attiva
const quickTests = [
  {
    name: 'visum_health_check',
    description: 'Verifica stato istanza'
  },
  {
    name: 'visum_network_stats', 
    description: 'Statistiche rapide #1'
  },
  {
    name: 'visum_network_stats',
    description: 'Statistiche rapide #2'
  },
  {
    name: 'visum_network_stats',
    description: 'Statistiche rapide #3'
  },
  {
    name: 'visum_custom_analysis',
    description: 'Analisi custom veloce',
    arguments: {
      pythonCode: `
# Test veloce su istanza attiva
import time
start = time.time()
node_count = visum.Net.Nodes.Count
link_count = visum.Net.Links.Count
zone_count = visum.Net.Zones.Count
elapsed = time.time() - start

result = {
  'test_type': 'quick_stats',
  'execution_time_ms': round(elapsed * 1000, 2),
  'network': {
    'nodes': node_count,
    'links': link_count, 
    'zones': zone_count
  },
  'status': 'singleton_working'
}`,
      description: 'Test velocità istanza singleton'
    }
  }
];

let currentTest = 0;
let serverProcess;
let responseBuffer = '';
let testTimes = [];

function startQuickTest() {
  console.log('🚀 Avvio server per test velocità...\n');
  
  serverProcess = spawn('node', ['build/index.js'], {
    stdio: ['pipe', 'pipe', 'pipe']
  });

  serverProcess.stdout.on('data', handleResponse);
  
  serverProcess.stderr.on('data', (data) => {
    const logMessage = data.toString();
    if (logMessage.includes('🚀')) {
      console.log('✅ Server pronto, inizializzazione protocollo...\n');
      
      // Prima inizializza il protocollo
      const initPayload = {
        jsonrpc: "2.0", id: 0, method: "initialize",
        params: { protocolVersion: "2024-11-05", capabilities: {}, clientInfo: { name: "quick-test", version: "1.0.0" } }
      };
      
      setTimeout(() => {
        serverProcess.stdin.write(JSON.stringify(initPayload) + '\n');
      }, 1000);
    }
  });
}

function handleResponse(data) {
  responseBuffer += data.toString();
  
  const lines = responseBuffer.split('\n');
  for (let i = 0; i < lines.length - 1; i++) {
    const line = lines[i].trim();
    if (line) {
      try {
        const response = JSON.parse(line);
        if (response.jsonrpc && response.id !== undefined) {
          
          if (response.id === 0) {
            // Inizializzazione completata, inizia i test
            console.log('🔧 Protocollo inizializzato, avvio test velocità...\n');
            setTimeout(() => executeQuickTest(), 500);
          } else {
            processQuickResponse(response);
          }
          
          responseBuffer = lines.slice(i + 1).join('\n');
          break;
        }
      } catch (e) {
        // Non è JSON valido
      }
    }
  }
}

function processQuickResponse(response) {
  const test = quickTests[currentTest - 1]; // currentTest è già incrementato
  const testNumber = currentTest;
  
  const endTime = Date.now();
  const executionTime = endTime - testTimes[currentTest - 1];
  
  console.log(`✅ TEST ${testNumber}: ${test.description} - ${executionTime}ms`);
  
  if (response.result && response.result.content && response.result.content[0]) {
    const text = response.result.content[0].text;
    
    // Estrai tempo di esecuzione interno se disponibile
    const internalTimeMatch = text.match(/Tempo Esecuzione:\s*([0-9.]+)ms/);
    if (internalTimeMatch) {
      const internalTime = parseFloat(internalTimeMatch[1]);
      console.log(`   ⚡ Tempo interno: ${internalTime}ms`);
      
      if (internalTime < 100) {
        console.log('   🚀 ULTRA-VELOCE - Istanza singleton funziona perfettamente!');
      }
    }
    
    // Per il custom analysis, mostra i risultati
    if (test.name === 'visum_custom_analysis' && text.includes('json')) {
      console.log('   📊 Analisi custom completata');
    }
  }
  
  // Prossimo test
  if (currentTest < quickTests.length) {
    setTimeout(() => executeQuickTest(), 200); // Test ravvicinati
  } else {
    console.log('\n🏁 === RISULTATI TEST VELOCITÀ ===');
    testTimes.forEach((startTime, index) => {
      if (index > 0) { // Skip initialization time
        const test = quickTests[index - 1];
        const totalTime = Date.now() - startTime; // This won't be accurate, but we have individual times
        console.log(`   ${test.description}: Test completato`);
      }
    });
    
    console.log('\n💡 CONCLUSIONI:');
    console.log('✅ Se i tempi sono <100ms, l\'istanza singleton funziona perfettamente');
    console.log('✅ Chiamate successive dovrebbero essere ultra-veloci');
    console.log('✅ Il progetto Campoleone rimane caricato in memoria\n');
    
    serverProcess.kill();
  }
}

function executeQuickTest() {
  const test = quickTests[currentTest];
  testTimes[currentTest] = Date.now();
  
  console.log(`📨 Eseguendo: ${test.description}...`);
  
  const payload = {
    jsonrpc: "2.0",
    id: currentTest + 1,
    method: "tools/call", 
    params: {
      name: test.name,
      arguments: test.arguments || {}
    }
  };
  
  currentTest++;
  serverProcess.stdin.write(JSON.stringify(payload) + '\n');
}

// Avvia i test
startQuickTest();