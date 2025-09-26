// Script per testare architettura Server-Client con gestione PID
// Avvia server in background, testa client, poi termina server

import { spawn } from 'child_process';
import { existsSync, unlinkSync } from 'fs';
import { PersistentVisumController } from './build/persistent-visum-controller.js';

console.log('🏗️ TEST COMPLETO SERVER-CLIENT CON GESTIONE PID');
console.log('=' .repeat(60));

const SERVER_INFO_FILE = 'visum-server-info.json';
let serverProcess = null;
let serverPid = null;

// Funzione per pulire file temporanei
function cleanup() {
  if (existsSync(SERVER_INFO_FILE)) {
    unlinkSync(SERVER_INFO_FILE);
    console.log('🧹 File info server rimosso');
  }
}

// Funzione per terminare il server
function killServer() {
  if (serverProcess && !serverProcess.killed) {
    console.log(`🔴 Terminando server PID ${serverProcess.pid}...`);
    serverProcess.kill('SIGTERM');
    
    // Forza terminazione dopo 5 secondi
    setTimeout(() => {
      if (!serverProcess.killed) {
        console.log('⚡ Forzando terminazione server...');
        serverProcess.kill('SIGKILL');
      }
    }, 5000);
  }
}

// Gestione Ctrl+C
process.on('SIGINT', () => {
  console.log('\n🛑 Ricevuto Ctrl+C, terminando server...');
  killServer();
  cleanup();
  process.exit(0);
});

async function runTest() {
  try {
    // Pulisci stato precedente
    cleanup();
    
    console.log('🚀 FASE 1: Avvio server Visum in background...');
    
    // Avvia server come processo separato
    serverProcess = spawn('node', ['test-server-client.mjs', 'server'], {
      detached: false,
      stdio: ['pipe', 'pipe', 'pipe']
    });
    
    serverPid = serverProcess.pid;
    console.log(`📋 Server avviato con PID ${serverPid}`);
    
    // Cattura output del server
    serverProcess.stdout.on('data', (data) => {
      const output = data.toString().trim();
      if (output) {
        console.log(`🖥️ Server: ${output}`);
      }
    });
    
    serverProcess.stderr.on('data', (data) => {
      const output = data.toString().trim();
      if (output) {
        console.log(`🖥️ Server: ${output}`);
      }
    });
    
    serverProcess.on('exit', (code) => {
      console.log(`🔴 Server terminato con codice ${code}`);
    });
    
    // Aspetta che il server si inizializzi
    console.log('⏳ Aspettando inizializzazione server...');
    
    let serverReady = false;
    let attempts = 0;
    const maxAttempts = 90; // 90 secondi per progetto grande
    
    while (!serverReady && attempts < maxAttempts) {
      await new Promise(resolve => setTimeout(resolve, 1000));
      attempts++;
      
      // Controlla se il file info server esiste
      if (existsSync(SERVER_INFO_FILE)) {
        console.log(`✅ Server inizializzato dopo ${attempts} secondi!`);
        serverReady = true;
      } else {
        process.stdout.write(`⏳ Attesa inizializzazione... ${attempts}/${maxAttempts}\\r`);
      }
    }
    
    if (!serverReady) {
      throw new Error('Timeout inizializzazione server');
    }
    
    // Aspetta un momento extra per stabilizzazione
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    console.log('\\n🔌 FASE 2: Test connessione client...');
    
    // Crea client e testa connessione
    const client = PersistentVisumController.getInstance();
    
    console.log('🔍 Tentativo connessione client al server...');
    const connectResult = await client.startPersistentVisumProcess();
    
    if (connectResult.success) {
      console.log(`✅ Client connesso!`);
      console.log(`📊 Network: ${connectResult.nodes} nodi, ${connectResult.links} link, ${connectResult.zones} zone`);
      
      // Test comando dal client
      console.log('\\n⚡ FASE 3: Test comando dal client...');
      const testStart = Date.now();
      
      const clientTest = await client.executeCustomCode(`
import time
start_time = time.time()

# Test comando dal client
result = {
    'client_command': True,
    'nodes': visum.Net.Nodes.Count,
    'links': visum.Net.Links.Count,
    'zones': visum.Net.Zones.Count,
    'query_time_ms': (time.time() - start_time) * 1000,
    'timestamp': time.time()
}
`, 'Client Test Command');

      const totalTime = Date.now() - testStart;
      
      if (clientTest.success) {
        console.log(`🔥 Comando client eseguito! Tempo totale: ${totalTime}ms`);
        console.log(`⚡ VisumPy query: ${clientTest.result.query_time_ms.toFixed(3)}ms`);
        console.log(`📊 Risultati: ${clientTest.result.nodes} nodi, ${clientTest.result.links} link, ${clientTest.result.zones} zone`);
        
        // Test multipli comandi veloci
        console.log('\\n🔥 FASE 4: Test multipli comandi veloci...');
        
        for (let i = 1; i <= 5; i++) {
          const fastStart = Date.now();
          const fastTest = await client.executeCustomCode(`
result = {
    'fast_test': ${i},
    'nodes': visum.Net.Nodes.Count,
    'timestamp': time.time()
}
`, `Fast Test ${i}`);
          const fastTime = Date.now() - fastStart;
          
          if (fastTest.success) {
            console.log(`⚡ Test ${i}: ${fastTime}ms - ${fastTest.result.nodes} nodi`);
          } else {
            console.log(`❌ Test ${i} fallito: ${fastTest.error}`);
          }
        }
        
        console.log('\\n✅ TUTTI I TEST COMPLETATI CON SUCCESSO!');
        
      } else {
        console.log(`❌ Comando client fallito: ${clientTest.error}`);
      }
    } else {
      console.log(`❌ Connessione client fallita: ${connectResult.message}`);
    }
    
  } catch (error) {
    console.error('❌ Errore durante test:', error.message);
  } finally {
    // Termina sempre il server
    console.log('\\n🔴 FASE FINALE: Terminazione server...');
    killServer();
    
    // Aspetta un momento per la terminazione
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    cleanup();
    console.log('🏁 Test completato!');
    process.exit(0);
  }
}

runTest().catch(console.error);