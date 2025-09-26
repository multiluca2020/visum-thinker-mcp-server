// CLIENT VISUM
// Si connette al server permanente per eseguire comandi

import { PersistentVisumController } from './build/persistent-visum-controller.js';
import { existsSync, readFileSync } from 'fs';

console.log('🔌 VISUM CLIENT');
console.log('=' .repeat(30));

const SERVER_INFO_FILE = 'visum-server-info.json';

async function connectToServer() {
  try {
    // Controlla se il server è attivo
    if (!existsSync(SERVER_INFO_FILE)) {
      console.log('❌ Server non trovato!');
      console.log('💡 Avvia prima il server con: node visum-server.mjs');
      return;
    }
    
    const serverInfo = JSON.parse(readFileSync(SERVER_INFO_FILE, 'utf8'));
    console.log(`📋 Server trovato:`);
    console.log(`   • PID: ${serverInfo.pid}`);
    console.log(`   • Avviato: ${serverInfo.startTimeString}`);
    console.log(`   • Status: ${serverInfo.status}`);
    console.log(`   • Progetto: ${serverInfo.project}`);
    console.log(`   • Network: ${serverInfo.nodes} nodi, ${serverInfo.links} link, ${serverInfo.zones} zone`);
    
    if (serverInfo.status !== 'active') {
      console.log(`⚠️ Server non attivo (status: ${serverInfo.status})`);
      return;
    }
    
    console.log('\\n🔗 Connessione al server...');
    
    // Crea controller client
    const client = PersistentVisumController.getInstance();
    
    // Connetti al server (dovrebbe rilevare istanza esistente)
    const connectResult = await client.startPersistentVisumProcess();
    
    if (connectResult.success) {
      console.log('✅ Client connesso al server!');
      console.log(`📊 Network confermata: ${connectResult.nodes} nodi, ${connectResult.links} link, ${connectResult.zones} zone`);
      
      // Test comando dal client
      console.log('\\n⚡ Esecuzione comandi di test...');
      
      // Test 1: Query semplice
      console.log('📋 Test 1: Query nodi e link');
      const testStart1 = Date.now();
      
      const test1 = await client.executeCustomCode(`
import time
start_time = time.time()

result = {
    'test_type': 'basic_query',
    'nodes': visum.Net.Nodes.Count,
    'links': visum.Net.Links.Count,
    'zones': visum.Net.Zones.Count,
    'query_time_ms': (time.time() - start_time) * 1000,
    'client_id': 'test_client_1'
}
`, 'Basic Query Test');

      const totalTime1 = Date.now() - testStart1;
      
      if (test1.success) {
        console.log(`   ✅ Completato in ${totalTime1}ms`);
        console.log(`   ⚡ VisumPy query: ${test1.result.query_time_ms.toFixed(3)}ms`);
        console.log(`   📊 ${test1.result.nodes} nodi, ${test1.result.links} link, ${test1.result.zones} zone`);
      } else {
        console.log(`   ❌ Fallito: ${test1.error}`);
      }
      
      // Test 2: Query zone 
      console.log('\\n📋 Test 2: Query dettagli zone');
      const testStart2 = Date.now();
      
      const test2 = await client.executeCustomCode(`
import time
start_time = time.time()

# Query su prime 5 zone
zone_details = []
for zone_num in list(visum.Net.Zones.Keys)[:5]:
    zone = visum.Net.Zones.ItemByKey(zone_num)
    zone_details.append({
        'zone_id': zone_num,
        'name': zone.AttValue('Name') if zone.AttValue('Name') else f'Zone_{zone_num}'
    })

result = {
    'test_type': 'zone_details',
    'total_zones': visum.Net.Zones.Count,
    'sample_zones': zone_details,
    'query_time_ms': (time.time() - start_time) * 1000,
    'client_id': 'test_client_2'
}
`, 'Zone Details Test');

      const totalTime2 = Date.now() - testStart2;
      
      if (test2.success) {
        console.log(`   ✅ Completato in ${totalTime2}ms`);
        console.log(`   ⚡ VisumPy query: ${test2.result.query_time_ms.toFixed(3)}ms`);
        console.log(`   📊 ${test2.result.total_zones} zone totali`);
        console.log(`   📋 Campione zone:`, test2.result.sample_zones);
      } else {
        console.log(`   ❌ Fallito: ${test2.error}`);
      }
      
      // Test 3: Test performance multipli
      console.log('\\n📋 Test 3: Performance test (5 query veloci)');
      const performanceResults = [];
      
      for (let i = 1; i <= 5; i++) {
        const fastStart = Date.now();
        const fastTest = await client.executeCustomCode(`
result = {
    'performance_test': ${i},
    'nodes': visum.Net.Nodes.Count,
    'timestamp': time.time()
}
`, `Performance Test ${i}`);
        const fastTime = Date.now() - fastStart;
        
        if (fastTest.success) {
          performanceResults.push(fastTime);
          console.log(`   ⚡ Test ${i}: ${fastTime}ms`);
        } else {
          console.log(`   ❌ Test ${i} fallito: ${fastTest.error}`);
        }
      }
      
      if (performanceResults.length > 0) {
        const avgTime = performanceResults.reduce((a, b) => a + b, 0) / performanceResults.length;
        const minTime = Math.min(...performanceResults);
        const maxTime = Math.max(...performanceResults);
        
        console.log(`\\n📊 Risultati performance:`);
        console.log(`   • Media: ${avgTime.toFixed(1)}ms`);
        console.log(`   • Min: ${minTime}ms`);
        console.log(`   • Max: ${maxTime}ms`);
      }
      
      console.log('\\n🎉 TUTTI I TEST CLIENT COMPLETATI!');
      
    } else {
      console.log(`❌ Connessione fallita: ${connectResult.message}`);
      console.log('💡 Assicurati che il server sia in esecuzione');
    }
    
  } catch (error) {
    console.error('❌ Errore client:', error.message);
  }
}

connectToServer();