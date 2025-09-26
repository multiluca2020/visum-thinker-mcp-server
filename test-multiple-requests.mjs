// Script per testare richieste multiple all'istanza persistente
// Questo script invia comandi sequenziali per testare performance e stabilità

import { PersistentVisumController } from './build/persistent-visum-controller.js';

console.log('🚀 TEST RICHIESTE MULTIPLE - Istanza Persistente');
console.log('=' .repeat(60));

const controller = PersistentVisumController.getInstance();

async function testMultipleRequests() {
  try {
    console.log('🔗 Connessione all\'istanza persistente...');
    
    // Connetti all'istanza esistente
    const connection = await controller.startPersistentVisumProcess();
    
    if (!connection.success) {
      console.log(`❌ Connessione fallita: ${connection.message}`);
      return;
    }
    
    console.log(`✅ Connesso! ${connection.nodes} nodi disponibili`);
    console.log('\n🎯 Iniziando test richieste multiple...\n');
    
    // Array di test da eseguire
    const tests = [
      {
        name: 'Network Count',
        code: `result = {'nodes': visum.Net.Nodes.Count, 'test': 'count_nodes'}`,
        description: 'Count Nodes Test'
      },
      {
        name: 'Links Count', 
        code: `result = {'links': visum.Net.Links.Count, 'test': 'count_links'}`,
        description: 'Count Links Test'
      },
      {
        name: 'Zones Count',
        code: `result = {'zones': visum.Net.Zones.Count, 'test': 'count_zones'}`,
        description: 'Count Zones Test'
      },
      {
        name: 'Network Stats',
        code: `
import time
start = time.time()
nodes = visum.Net.Nodes.Count
links = visum.Net.Links.Count
zones = visum.Net.Zones.Count
end = time.time()
result = {
    'nodes': nodes,
    'links': links, 
    'zones': zones,
    'visum_query_time_ms': (end - start) * 1000,
    'test': 'full_network_stats'
}`,
        description: 'Full Network Statistics'
      },
      {
        name: 'Sample Node Data',
        code: `
# Get first 3 nodes data
nodes_data = []
count = 0
for node in visum.Net.Nodes:
    if count >= 3:
        break
    try:
        nodes_data.append({
            'no': node.GetAttribute('No'),
            'x': node.GetAttribute('XCoord'),
            'y': node.GetAttribute('YCoord')
        })
        count += 1
    except:
        continue

result = {
    'sample_nodes': nodes_data,
    'sampled_count': len(nodes_data),
    'test': 'sample_nodes'
}`,
        description: 'Sample Node Data'
      }
    ];
    
    // Esegui tutti i test in sequenza
    for (let i = 0; i < tests.length; i++) {
      const test = tests[i];
      
      console.log(`🔸 Test ${i+1}/${tests.length}: ${test.name}`);
      const startTime = Date.now();
      
      try {
        const result = await controller.executeCustomCode(test.code, test.description);
        const totalTime = Date.now() - startTime;
        
        if (result.success) {
          console.log(`   ✅ Successo! Tempo: ${totalTime}ms (VisumPy: ${result.executionTimeMs}ms)`);
          
          // Log risultati specifici
          if (result.result.nodes) console.log(`   📊 Nodi: ${result.result.nodes}`);
          if (result.result.links) console.log(`   🔗 Link: ${result.result.links}`);
          if (result.result.zones) console.log(`   🗺️  Zone: ${result.result.zones}`);
          if (result.result.sample_nodes) console.log(`   📍 Campioni nodi: ${result.result.sampled_count}`);
          if (result.result.visum_query_time_ms) console.log(`   ⚡ Query interna: ${result.result.visum_query_time_ms.toFixed(3)}ms`);
        } else {
          console.log(`   ❌ Errore: ${result.error} (Tempo: ${totalTime}ms)`);
        }
        
      } catch (error) {
        const totalTime = Date.now() - startTime;
        console.log(`   💥 Eccezione: ${error.message} (Tempo: ${totalTime}ms)`);
      }
      
      console.log(''); // Spazio tra test
      
      // Pausa breve tra richieste
      await new Promise(resolve => setTimeout(resolve, 500));
    }
    
    // Test finale - Health check
    console.log('🏥 Test finale: Health Check');
    const healthStart = Date.now();
    
    try {
      const health = await controller.checkInstanceHealth();
      const healthTime = Date.now() - healthStart;
      
      if (health.success) {
        console.log(`✅ Health Check OK! Tempo: ${healthTime}ms`);
        console.log(`   💚 Istanza attiva e stabile`);
        console.log(`   📊 Memory: ${health.result.memory_mb}MB`);
        console.log(`   ⚡ Response time: ${health.result.response_time_ms}ms`);
      } else {
        console.log(`❌ Health Check fallito: ${health.error}`);
      }
      
    } catch (error) {
      console.log(`💥 Health Check eccezione: ${error.message}`);
    }
    
    console.log('\n✅ TEST RICHIESTE MULTIPLE COMPLETATO');
    console.log('🔄 Istanza rimane attiva per altre operazioni...');
    
  } catch (error) {
    console.error('❌ Errore generale:', error.message);
  }
}

testMultipleRequests().catch(console.error);