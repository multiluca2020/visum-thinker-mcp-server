// Test diretto sull'istanza esistente - APPROCCIO SEMPLICE
// Bypassa il sistema di connessione condivisa e usa l'istanza attiva

import { PersistentVisumController } from './build/persistent-visum-controller.js';

console.log('🎯 TEST DIRETTO ISTANZA ESISTENTE');
console.log('=' .repeat(50));

async function testDirectConnection() {
  try {
    // Crea un controller completamente nuovo ma usa l'istanza già attiva
    const controller = new PersistentVisumController();
    
    console.log('🔧 Tentativo connessione diretta...');
    
    // Test comando semplice per verificare se l'istanza è raggiungibile
    console.log('⚡ Test comando veloce...');
    const testResult = await controller.executeCustomCode(`
import time
start = time.time()

# Test veloce - solo conta nodi
nodes = visum.Net.Nodes.Count

result = {
    'test_type': 'direct_connection',
    'nodes': nodes,
    'query_time_ms': (time.time() - start) * 1000,
    'timestamp': time.time()
}
`, 'Direct Connection Test');

    if (testResult.success) {
      console.log('✅ Connessione diretta riuscita!');
      console.log(`📊 Nodi: ${testResult.result.nodes}`);
      console.log(`⚡ Tempo query: ${testResult.result.query_time_ms.toFixed(3)}ms`);
      console.log(`🔥 Execution time: ${testResult.executionTimeMs}ms`);
      
      // Test aggiuntivo - network stats completo
      console.log('\n📊 Test network stats completo...');
      const fullTest = await controller.executeCustomCode(`
import time
start = time.time()

nodes = visum.Net.Nodes.Count
links = visum.Net.Links.Count
zones = visum.Net.Zones.Count

result = {
    'test_type': 'full_network_stats',
    'network': {
        'nodes': nodes,
        'links': links,
        'zones': zones
    },
    'query_time_ms': (time.time() - start) * 1000,
    'timestamp': time.time()
}
`, 'Full Network Stats Test');

      if (fullTest.success) {
        console.log('✅ Test completo riuscito!');
        console.log(`📊 Network completo: ${fullTest.result.network.nodes} nodi, ${fullTest.result.network.links} link, ${fullTest.result.network.zones} zone`);
        console.log(`⚡ Tempo query interna: ${fullTest.result.query_time_ms.toFixed(3)}ms`);
        console.log(`🔥 Tempo totale execution: ${fullTest.executionTimeMs}ms`);
      }
      
    } else {
      console.log('❌ Connessione diretta fallita:', testResult.error);
    }
    
  } catch (error) {
    console.error('❌ Errore test diretto:', error.message);
  }
}

testDirectConnection().catch(console.error);