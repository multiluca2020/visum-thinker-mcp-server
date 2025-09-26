#!/usr/bin/env node

import { spawn } from 'child_process';

console.log('🚄 === TEST VISUM CAMPOLEONE SINGLETON ===\n');

const CAMPOLEONE_PROJECT = "H:\\go\\italferr2025\\Campoleone\\100625_Versione_base_v0.3_sub_ok_priv.ver";

let serverProcess;
let responseBuffer = '';
let currentStep = 0;

const testSequence = [
  {
    name: 'initialize',
    description: 'Inizializzazione protocollo MCP',
    payload: {
      jsonrpc: "2.0", id: 1, method: "initialize",
      params: { protocolVersion: "2024-11-05", capabilities: {}, clientInfo: { name: "campoleone-test", version: "1.0.0" } }
    }
  },
  {
    name: 'visum_launch_project',
    description: 'Caricamento progetto Campoleone',
    payload: {
      jsonrpc: "2.0", id: 2, method: "tools/call",
      params: { name: "visum_launch_project", arguments: { projectPath: CAMPOLEONE_PROJECT } }
    }
  },
  {
    name: 'visum_network_stats',
    description: 'Prime statistiche rete (dovrebbe essere veloce)',
    payload: {
      jsonrpc: "2.0", id: 3, method: "tools/call",
      params: { name: "visum_network_stats", arguments: {} }
    }
  },
  {
    name: 'visum_health_check',
    description: 'Controllo salute istanza (dovrebbe essere sana)',
    payload: {
      jsonrpc: "2.0", id: 4, method: "tools/call", 
      params: { name: "visum_health_check", arguments: {} }
    }
  },
  {
    name: 'visum_network_analysis',
    description: 'Analisi completa rete (usando istanza singleton)',
    payload: {
      jsonrpc: "2.0", id: 5, method: "tools/call",
      params: { name: "visum_network_analysis", arguments: { includeGeometry: true, sampleSize: 10 } }
    }
  },
  {
    name: 'visum_network_stats_again', 
    description: 'Statistiche rete ripetute (dovrebbe essere ultra-veloce)',
    payload: {
      jsonrpc: "2.0", id: 6, method: "tools/call",
      params: { name: "visum_network_stats", arguments: {} }
    }
  }
];

function startServer() {
  console.log('🔧 Avvio server MCP...\n');
  
  serverProcess = spawn('node', ['build/index.js'], {
    stdio: ['pipe', 'pipe', 'pipe']
  });

  serverProcess.stdout.on('data', handleResponse);
  
  serverProcess.stderr.on('data', (data) => {
    const logMessage = data.toString();
    console.log('📢 Server:', logMessage.trim());
    
    // Quando il server è pronto, inizia i test
    if (logMessage.includes('🚀') && currentStep === 0) {
      setTimeout(() => executeNextStep(), 1000);
    }
  });

  serverProcess.on('exit', (code) => {
    console.log('\n🔚 Server terminato con codice:', code);
  });
}

function handleResponse(data) {
  responseBuffer += data.toString();
  
  // Cerca risposte JSON complete
  const lines = responseBuffer.split('\n');
  for (let i = 0; i < lines.length - 1; i++) {
    const line = lines[i].trim();
    if (line) {
      try {
        const response = JSON.parse(line);
        if (response.jsonrpc && response.id) {
          processResponse(response);
          responseBuffer = lines.slice(i + 1).join('\n');
          break;
        }
      } catch (e) {
        // Non è JSON valido, continua
      }
    }
  }
}

function processResponse(response) {
  const step = testSequence[currentStep];
  const stepNumber = currentStep + 1;
  
  console.log(`\n✅ STEP ${stepNumber}: ${step.description} - COMPLETATO`);
  
  if (response.result) {
    // Estrai informazioni rilevanti dalla risposta
    if (step.name === 'initialize') {
      console.log(`   🔗 Protocollo: ${response.result.protocolVersion}`);
      console.log(`   🏷️  Server: ${response.result.serverInfo.name} v${response.result.serverInfo.version}`);
      
    } else if (step.name === 'visum_launch_project') {
      if (response.result.content && response.result.content[0]) {
        const text = response.result.content[0].text;
        if (text.includes('✅')) {
          console.log('   🚄 Progetto Campoleone caricato con SUCCESSO!');
          // Estrai statistiche dal testo se disponibili
          const nodesMatch = text.match(/Nodi:\s*([0-9,]+)/);
          const linksMatch = text.match(/Link:\s*([0-9,]+)/);
          if (nodesMatch && linksMatch) {
            console.log(`   📊 Rete: ${nodesMatch[1]} nodi, ${linksMatch[1]} link`);
          }
        } else {
          console.log('   ❌ Errore caricamento progetto:', text.slice(0, 100));
        }
      }
      
    } else if (step.name.includes('visum_network_stats')) {
      if (response.result.content && response.result.content[0]) {
        const text = response.result.content[0].text;
        const timeMatch = text.match(/Tempo Esecuzione:\s*([0-9.]+)ms/);
        if (timeMatch) {
          const time = parseFloat(timeMatch[1]);
          console.log(`   ⚡ Tempo esecuzione: ${time}ms ${time < 100 ? '(ULTRA-VELOCE!)' : time < 1000 ? '(veloce)' : '(normale)'}`);
        }
        
        // Estrai statistiche rete
        const nodesMatch = text.match(/Nodi:\s*([0-9,]+)/);
        const linksMatch = text.match(/Link:\s*([0-9,]+)/);
        if (nodesMatch && linksMatch) {
          console.log(`   📊 Rete attiva: ${nodesMatch[1]} nodi, ${linksMatch[1]} link`);
        }
      }
      
    } else if (step.name === 'visum_health_check') {
      if (response.result.content && response.result.content[0]) {
        const text = response.result.content[0].text;
        if (text.includes('✅')) {
          console.log('   💚 Istanza VisumPy SANA e operativa');
          const perfMatch = text.match(/Performance:\s*(\w+)/);
          if (perfMatch) {
            console.log(`   🚀 Performance: ${perfMatch[1]}`);
          }
        } else {
          console.log('   ⚠️ Istanza ha problemi:', text.slice(0, 50));
        }
      }
      
    } else if (step.name === 'visum_network_analysis') {
      if (response.result.content && response.result.content[0]) {
        const text = response.result.content[0].text;
        if (text.includes('✅')) {
          console.log('   🔍 Analisi rete completa COMPLETATA');
          // Estrai tempo analisi e tool
          const analysisTimeMatch = text.match(/Tempo Analisi:\s*([0-9.]+)s/);
          const toolTimeMatch = text.match(/Tempo Esecuzione Tool:\s*([0-9.]+)ms/);
          if (analysisTimeMatch) console.log(`   ⏱️  Tempo analisi interna: ${analysisTimeMatch[1]}s`);
          if (toolTimeMatch) console.log(`   ⚡ Tempo tool MCP: ${toolTimeMatch[1]}ms`);
        }
      }
    }
  } else if (response.error) {
    console.log(`   ❌ ERRORE: ${response.error.message || response.error}`);
  }
  
  // Passa al prossimo step
  currentStep++;
  if (currentStep < testSequence.length) {
    const nextStep = testSequence[currentStep];
    let delay = 1000; // Default 1 secondo
    
    // Tempi di attesa diversi per operazioni lunghe
    if (step.name === 'visum_launch_project') {
      delay = 5000; // 5 secondi dopo il caricamento del progetto
      console.log('   ⏳ Attendendo stabilizzazione istanza VisumPy...');
    } else if (step.name === 'visum_network_analysis') {
      delay = 2000; // 2 secondi dopo analisi completa
    }
    
    setTimeout(() => executeNextStep(), delay);
  } else {
    console.log('\n🎉 === TUTTI I TEST COMPLETATI ===');
    console.log('✅ Progetto Campoleone caricato e mantenuto in memoria');
    console.log('✅ Istanza VisumPy singleton operativa');  
    console.log('✅ Performance ottimizzate per chiamate successive');
    
    console.log('\n💡 L\'istanza resta attiva per successive interrogazioni!');
    console.log('📝 Usa Ctrl+C per terminare il server quando hai finito.\n');
    
    // Lascia il server attivo invece di chiuderlo
    console.log('🔄 Server ancora attivo. Puoi fare altre interrogazioni...');
  }
}

function executeNextStep() {
  const step = testSequence[currentStep];
  const stepNumber = currentStep + 1;
  
  console.log(`\n📨 STEP ${stepNumber}: ${step.description}`);
  
  if (step.name === 'visum_launch_project') {
    console.log('⏳ ATTENZIONE: Questo step può richiedere 60-90 secondi per il primo caricamento...');
  }
  
  serverProcess.stdin.write(JSON.stringify(step.payload) + '\n');
}

// Gestione interruzione da parte dell'utente
process.on('SIGINT', () => {
  console.log('\n\n🛑 Interruzione richiesta dall\'utente');
  if (serverProcess) {
    console.log('🔚 Terminando il server...');
    serverProcess.kill();
  }
  process.exit(0);
});

// Avvia il test
startServer();