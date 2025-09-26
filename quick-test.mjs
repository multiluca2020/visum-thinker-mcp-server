// Script veloce per testare l'istanza Visum attiva
// Uso: node quick-test.mjs

import { PersistentVisumController } from './build/persistent-visum-controller.js';

console.log('⚡ QUICK TEST - Istanza Visum Attiva');
console.log('=' .repeat(40));

const controller = PersistentVisumController.getInstance();

async function quickTest() {
  try {
    console.log('🔍 Testing network stats...');
    const start = Date.now();
    
    const result = await controller.executeCustomCode(`
# Quick Network Stats
import time
start_time = time.time()

result = {
    'nodes': visum.Net.Nodes.Count,
    'links': visum.Net.Links.Count, 
    'zones': visum.Net.Zones.Count,
    'query_time_ms': (time.time() - start_time) * 1000,
    'timestamp': time.time()
}
`, 'Quick Network Test');

    const totalTime = Date.now() - start;
    
    if (result.success) {
      console.log(`✅ Success! Total time: ${totalTime}ms`);
      console.log(`� VisumPy query time: ${result.result.query_time_ms.toFixed(3)}ms`);
      console.log(`📊 Network: ${result.result.nodes} nodes, ${result.result.links} links, ${result.result.zones} zones`);
    } else {
      console.log(`❌ Error: ${result.error}`);
    }
    
  } catch (error) {
    console.error('❌ Exception:', error.message);
  }
}

quickTest().catch(console.error);
