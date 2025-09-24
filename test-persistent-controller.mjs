// Test del nuovo Persistent Visum Controller
import { PersistentVisumController } from './persistent-visum-controller.js';

async function testPersistentController() {
  console.log("=== TEST PERSISTENT VISUM CONTROLLER ===");
  
  const controller = PersistentVisumController.getInstance();
  
  // Test 1: Initialize persistent instance
  console.log("\n🚀 Test 1: Initialize persistent instance");
  const initResult = await controller.initializePersistentInstance();
  console.log("Init result:", initResult);
  
  if (!initResult.success) {
    console.error("❌ Initialization failed, stopping tests");
    return;
  }
  
  // Test 2: Get network stats (should be fast)
  console.log("\n📊 Test 2: Get network statistics");
  const start1 = Date.now();
  const statsResult = await controller.getNetworkStats();
  const time1 = Date.now() - start1;
  console.log(`Stats result (${time1}ms):`, statsResult);
  
  // Test 3: Analyze nodes (should reuse instance)
  console.log("\n🔍 Test 3: Analyze nodes");
  const start2 = Date.now();
  const nodesResult = await controller.analyzeNodes();
  const time2 = Date.now() - start2;
  console.log(`Nodes result (${time2}ms):`, nodesResult);
  
  // Test 4: Multiple rapid calls (should be ultra-fast)
  console.log("\n⚡ Test 4: Multiple rapid calls");
  for (let i = 1; i <= 5; i++) {
    const start = Date.now();
    const rapidResult = await controller.getNetworkStats();
    const time = Date.now() - start;
    console.log(`  Call ${i} (${time}ms): ${rapidResult.success ? rapidResult.nodes + ' nodes' : 'Failed'}`);
  }
  
  // Test 5: Custom Python execution
  console.log("\n🐍 Test 5: Custom Python code");
  const customCode = `
# Custom analysis using the global visum instance
nodes = visum.Net.Nodes.Count
links = visum.Net.Links.Count
print(f"Custom analysis: {nodes:,} nodes, {links:,} links")

# Try to get zone count
try:
    zones = visum.Net.Zones.Count
    print(f"Zones: {zones:,}")
except Exception as e:
    print(f"Zone error: {e}")
`;
  
  const customResult = await controller.executeCustomPython(customCode);
  console.log("Custom Python result:", customResult);
  
  // Test 6: Instance health check
  console.log("\n🏥 Test 6: Instance health check");
  const healthResult = await controller.checkInstanceHealth();
  console.log("Health check:", healthResult);
  
  console.log("\n✅ All tests completed!");
}

// Run the test
testPersistentController().catch(console.error);