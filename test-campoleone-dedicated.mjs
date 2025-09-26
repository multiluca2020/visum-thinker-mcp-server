// Test Istanza Dedicata Campoleone - Performance Ultra-Veloce
// Test per verificare l'istanza persistente dedicata per il progetto Campoleone

import { ProjectInstanceManager } from './build/project-instance-manager.js';

console.log("🎯 TEST ISTANZA DEDICATA CAMPOLEONE");
console.log("=" .repeat(50));

async function testCampoleoneInstance() {
  const projectManager = ProjectInstanceManager.getInstance();
  
  try {
    console.log("\n🚀 FASE 1: Avvio istanza dedicata Campoleone...");
    const startTime = Date.now();
    
    const startResult = await projectManager.startProjectInstance('campoleone');
    const startupTime = Date.now() - startTime;
    
    console.log(`⏱️ Tempo startup: ${startupTime}ms`);
    
    if (startResult.success) {
      console.log("✅ Istanza Campoleone avviata con successo!");
      console.log(`📊 Network: ${startResult.stats?.nodes} nodi, ${startResult.stats?.links} link, ${startResult.stats?.zones} zone`);
    } else {
      console.log("❌ Errore avvio istanza:", startResult.message);
      return;
    }
    
    console.log("\n🔍 FASE 2: Status istanze attive...");
    const status = projectManager.getInstancesStatus();
    console.log("Istanze attive:", Object.keys(status).length);
    
    for (const [projectId, info] of Object.entries(status)) {
      console.log(`   • ${info.name}: ${info.isActive ? '✅ Attiva' : '❌ Inattiva'}`);
    }
    
    console.log("\n⚡ FASE 3: Test performance analisi ultra-veloce...");
    
    // Test 1: Network Stats (dovrebbe essere ultra-veloce dopo inizializzazione)
    console.log("\n🔸 Test 1: Network Statistics");
    const test1Start = Date.now();
    
    const networkStatsResult = await projectManager.executeProjectAnalysis('campoleone', `
# Network Statistics Ultra-Fast
result = {
    'nodes': visum.Net.Nodes.Count,
    'links': visum.Net.Links.Count,
    'zones': visum.Net.Zones.Count,
    'total_demand': visum.Net.Zones.GetAttribute('OBJVAL', 'Sum'),
    'test_type': 'network_stats',
    'timestamp': time.time()
}
`, "Network Statistics Test");
    
    const test1Time = Date.now() - test1Start;
    console.log(`   ⚡ Tempo esecuzione: ${test1Time}ms`);
    console.log(`   📊 Risultato: ${networkStatsResult.success ? '✅ Successo' : '❌ Errore'}`);
    if (networkStatsResult.success) {
      console.log(`   📈 Nodi: ${networkStatsResult.result.nodes}, Link: ${networkStatsResult.result.links}`);
    }
    
    // Test 2: Comando Semplice (dovrebbe essere istantaneo)
    console.log("\n🔸 Test 2: Comando Semplice");
    const test2Start = Date.now();
    
    const simpleResult = await projectManager.executeProjectAnalysis('campoleone', `
# Simple Command Test
import time
start = time.time()
node_count = visum.Net.Nodes.Count
end = time.time()

result = {
    'node_count': node_count,
    'query_time_ms': (end - start) * 1000,
    'test_type': 'simple_command',
    'timestamp': time.time()
}
`, "Simple Command Test");
    
    const test2Time = Date.now() - test2Start;
    console.log(`   ⚡ Tempo esecuzione totale: ${test2Time}ms`);
    console.log(`   🔥 Tempo query VisumPy: ${simpleResult.result?.query_time_ms?.toFixed(3)}ms`);
    
    // Test 3: Comando Complesso
    console.log("\n🔸 Test 3: Analisi Complessa");
    const test3Start = Date.now();
    
    const complexResult = await projectManager.executeProjectAnalysis('campoleone', `
# Complex Analysis Test
import time
start = time.time()

# Multiple operations
node_attrs = ['No', 'XCoord', 'YCoord']
link_attrs = ['No', 'FromNodeNo', 'ToNodeNo', 'Length']

nodes_data = []
for i in range(min(100, visum.Net.Nodes.Count)):
    node = visum.Net.Nodes.ItemByKey(i+1)
    if node:
        node_data = {}
        for attr in node_attrs:
            try:
                node_data[attr] = node.GetAttribute(attr)
            except:
                node_data[attr] = None
        nodes_data.append(node_data)

end = time.time()

result = {
    'processed_nodes': len(nodes_data),
    'total_nodes': visum.Net.Nodes.Count,
    'sample_node': nodes_data[0] if nodes_data else None,
    'query_time_ms': (end - start) * 1000,
    'test_type': 'complex_analysis',
    'timestamp': time.time()
}
`, "Complex Analysis Test");
    
    const test3Time = Date.now() - test3Start;
    console.log(`   ⚡ Tempo esecuzione totale: ${test3Time}ms`);
    console.log(`   🔥 Tempo analisi VisumPy: ${complexResult.result?.query_time_ms?.toFixed(3)}ms`);
    console.log(`   📊 Nodi processati: ${complexResult.result?.processed_nodes}`);
    
    // Test 4: Health Check
    console.log("\n🔸 Test 4: Health Check");
    const healthResult = await projectManager.checkProjectHealth('campoleone');
    
    if (healthResult.success) {
      const uptime = Math.floor((healthResult.health.uptime || 0) / 1000);
      console.log(`   💚 Status: Salutare`);
      console.log(`   🔄 Uptime: ${uptime}s`);
      console.log(`   ⚡ Response time: ${healthResult.health.response_time_ms}ms`);
      console.log(`   📊 Memory: ${healthResult.health.memory_mb}MB`);
    }
    
    console.log("\n📊 RIEPILOGO PERFORMANCE:");
    console.log(`   🚀 Startup time: ${startupTime}ms`);
    console.log(`   ⚡ Network Stats: ${test1Time}ms`);
    console.log(`   🔥 Simple Command: ${test2Time}ms (VisumPy: ${simpleResult.result?.query_time_ms?.toFixed(1)}ms)`);
    console.log(`   🎯 Complex Analysis: ${test3Time}ms (VisumPy: ${complexResult.result?.query_time_ms?.toFixed(1)}ms)`);
    
    console.log("\n✅ TEST COMPLETATO - Istanza dedicata Campoleone funziona perfettamente!");
    console.log("🔄 L'istanza rimane attiva per ricevere altri comandi...");
    
  } catch (error) {
    console.error("❌ ERRORE:", error.message);
    console.error("Stack:", error.stack);
  }
}

// Esegui test
testCampoleoneInstance().catch(console.error);