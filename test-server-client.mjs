// Test architettura Server-Client per Visum
// 1. Avvia un server Visum in background
// 2. I client si connettono al server per eseguire comandi

import { PersistentVisumController } from './build/persistent-visum-controller.js';
import { spawn } from 'child_process';
import { existsSync, writeFileSync, readFileSync } from 'fs';
import { join } from 'path';

console.log('🏗️ TEST ARCHITETTURA SERVER-CLIENT');
console.log('=' .repeat(60));

const VISUM_SERVER_PORT = 7891;
const SERVER_INFO_FILE = 'visum-server-info.json';

// Funzione per avviare il server Visum
async function startVisumServer() {
  console.log('🚀 Avvio server Visum in background...');
  
  const controller = PersistentVisumController.getInstance();
  
  try {
    // Avvia l'istanza Visum persistente
    const result = await controller.startPersistentVisumProcess();
    
    if (result.success) {
      console.log(`✅ Server Visum avviato!`);
      console.log(`📊 Network: ${result.nodes} nodi, ${result.links} link, ${result.zones} zone`);
      
      // Salva info del server per i client
      const serverInfo = {
        pid: process.pid,
        startTime: Date.now(),
        nodes: result.nodes,
        links: result.links,
        zones: result.zones,
        status: 'active'
      };
      
      writeFileSync(SERVER_INFO_FILE, JSON.stringify(serverInfo, null, 2));
      console.log(`📝 Info server salvate in ${SERVER_INFO_FILE}`);
      
      // Mantieni il server attivo
      console.log('🔄 Server in ascolto di comandi...');
      console.log('   - Usa Ctrl+C per fermare il server');
      console.log('   - Usa altri script per inviare comandi');
      
      // Test periodici per mantenere viva la connessione
      setInterval(async () => {
        try {
          const pingResult = await controller.executeCustomCode(`
result = {
    'ping': True,
    'nodes': visum.Net.Nodes.Count,
    'timestamp': time.time()
}
`, 'Server Ping');
          
          if (pingResult.success) {
            console.log(`🔔 Server attivo - ${pingResult.result.nodes} nodi - ${new Date().toLocaleTimeString()}`);
          }
        } catch (error) {
          console.error('⚠️ Errore ping server:', error.message);
        }
      }, 30000); // Ping ogni 30 secondi
      
    } else {
      console.log(`❌ Errore avvio server: ${result.message}`);
      process.exit(1);
    }
  } catch (error) {
    console.error('❌ Errore critico:', error.message);
    process.exit(1);
  }
}

// Funzione per testare il client
async function testClient() {
  console.log('🔌 Test client - connessione al server...');
  
  // Controlla se il server è attivo
  if (!existsSync(SERVER_INFO_FILE)) {
    console.log('❌ Server non trovato! Avvia prima il server.');
    return;
  }
  
  const serverInfo = JSON.parse(readFileSync(SERVER_INFO_FILE, 'utf8'));
  console.log(`📋 Server trovato: PID ${serverInfo.pid}, avviato ${new Date(serverInfo.startTime).toLocaleString()}`);
  
  // Crea un nuovo controller per il client
  const clientController = PersistentVisumController.getInstance();
  
  try {
    // Il client dovrebbe connettersi al server esistente
    const connectResult = await clientController.startPersistentVisumProcess();
    
    if (connectResult.success) {
      console.log(`✅ Client connesso al server!`);
      console.log(`📊 Network: ${connectResult.nodes} nodi, ${connectResult.links} link, ${connectResult.zones} zone`);
      
      // Test comando dal client
      console.log('\n⚡ Esecuzione comando dal client...');
      const testStart = Date.now();
      
      const clientTest = await clientController.executeCustomCode(`
import time
start_time = time.time()

# Comando di test dal client
result = {
    'client_test': True,
    'nodes': visum.Net.Nodes.Count,
    'links': visum.Net.Links.Count,
    'zones': visum.Net.Zones.Count,
    'query_time_ms': (time.time() - start_time) * 1000,
    'client_timestamp': time.time()
}
`, 'Client Command Test');

      const totalTime = Date.now() - testStart;
      
      if (clientTest.success) {
        console.log(`🔥 Comando eseguito! Tempo totale: ${totalTime}ms`);
        console.log(`⚡ VisumPy query: ${clientTest.result.query_time_ms.toFixed(3)}ms`);
        console.log(`📊 Risultati: ${clientTest.result.nodes} nodi, ${clientTest.result.links} link`);
      } else {
        console.log(`❌ Comando fallito: ${clientTest.error}`);
      }
    } else {
      console.log(`❌ Connessione client fallita: ${connectResult.message}`);
    }
  } catch (error) {
    console.error('❌ Errore client:', error.message);
  }
}

// Gestione argomenti comando
const args = process.argv.slice(2);

if (args[0] === 'server') {
  startVisumServer();
} else if (args[0] === 'client') {
  testClient();
} else {
  console.log('Uso:');
  console.log('  node test-server-client.mjs server    # Avvia server Visum');
  console.log('  node test-server-client.mjs client    # Testa client');
}