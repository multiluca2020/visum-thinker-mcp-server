// Test connessione a istanza condivisa
// Questo script deve connettersi all'istanza esistente invece di crearne una nuova

import { PersistentVisumController } from './build/persistent-visum-controller.js';

console.log('🔗 TEST CONNESSIONE ISTANZA CONDIVISA');
console.log('=' .repeat(50));

const controller = PersistentVisumController.getInstance();

async function testSharedConnection() {
  try {
    console.log('🔍 Tentativo di connessione all\'istanza esistente...');
    
    // Questo dovrebbe connettersi all'istanza esistente
    const result = await controller.startPersistentVisumProcess();
    
    if (result.success) {
      console.log(`✅ ${result.message}`);
      console.log(`📊 Network: ${result.nodes} nodi, ${result.links} link, ${result.zones} zone`);
      
      // Test veloce per confermare la connessione
      console.log('\n⚡ Test veloce connessione...');
      const testStart = Date.now();
      
      const quickTest = await controller.executeCustomCode(`
import time
start_time = time.time()

result = {
    'connection_test': True,
    'nodes': visum.Net.Nodes.Count,
    'query_time_ms': (time.time() - start_time) * 1000,
    'timestamp': time.time()
}
`, 'Quick Connection Test');

      const totalTime = Date.now() - testStart;
      
      if (quickTest.success) {
        console.log(`🔥 Connessione confermata! Tempo totale: ${totalTime}ms`);
        console.log(`⚡ VisumPy query: ${quickTest.result.query_time_ms.toFixed(3)}ms`);
        console.log(`📊 Nodi confermati: ${quickTest.result.nodes}`);
      } else {
        console.log(`❌ Test connessione fallito: ${quickTest.error}`);
      }
      
    } else {
      console.log(`❌ Connessione fallita: ${result.message}`);
    }
    
  } catch (error) {
    console.error('❌ Errore durante test:', error.message);
  }
}

testSharedConnection().catch(console.error);