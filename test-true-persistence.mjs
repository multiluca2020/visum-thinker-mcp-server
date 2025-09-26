// Test TRUE PERSISTENT VisumPy Controller
// This test validates that the VisumPy instance truly persists across multiple calls

import { PersistentVisumController } from "./build/persistent-visum-controller.js";

console.log("🚀 TESTING TRUE PERSISTENT VisumPy Controller");
console.log("=" .repeat(60));

const controller = PersistentVisumController.getInstance();

async function runTruePersistenceTest() {
  try {
    console.log("\n1️⃣ Starting persistent VisumPy process...");
    const startTime = Date.now();
    
    const initResult = await controller.startPersistentVisumProcess();
    const initTime = Date.now() - startTime;
    
    console.log(`   Result: ${initResult.success ? '✅ SUCCESS' : '❌ FAILED'}`);
    console.log(`   Message: ${initResult.message}`);
    if (initResult.success) {
      console.log(`   Nodes: ${initResult.nodes?.toLocaleString()}`);
      console.log(`   Links: ${initResult.links?.toLocaleString()}`);
      console.log(`   Zones: ${initResult.zones?.toLocaleString()}`);
    }
    console.log(`   Init Time: ${initTime}ms`);
    
    if (!initResult.success) {
      console.error("❌ Cannot continue without persistent process");
      return;
    }
    
    console.log("\n2️⃣ Testing rapid successive calls (TRUE PERSISTENCE)...");
    
    // Perform multiple rapid calls to test persistence
    const rapidTests = [
      { name: "Network Stats #1", test: () => controller.getNetworkStats() },
      { name: "Node Analysis #1", test: () => controller.analyzeNodes(5) },
      { name: "Network Stats #2", test: () => controller.getNetworkStats() },
      { name: "Node Analysis #2", test: () => controller.analyzeNodes(3) },
      { name: "Health Check", test: () => controller.checkInstanceHealth() },
      { name: "Network Stats #3", test: () => controller.getNetworkStats() },
      { name: "Custom Analysis", test: () => controller.executeCustomCode(`
# Custom persistent analysis
result = {
    'test_type': 'custom',
    'visum_available': visum is not None,
    'nodes_count': visum.Net.Nodes.Count if visum else 0,
    'persistent_test': 'SUCCESS'
}
      `, "Custom persistence test") }
    ];
    
    console.log(`   Executing ${rapidTests.length} rapid tests...`);
    
    const testResults = [];
    const overallStartTime = Date.now();
    
    for (let i = 0; i < rapidTests.length; i++) {
      const test = rapidTests[i];
      console.log(`\n   📊 Test ${i+1}/${rapidTests.length}: ${test.name}`);
      
      const testStartTime = Date.now();
      const result = await test.test();
      const testTime = Date.now() - testStartTime;
      
      testResults.push({
        name: test.name,
        success: result.success,
        time: testTime,
        isPersistent: result.result?.persistent === true,
        error: result.error
      });
      
      console.log(`      Result: ${result.success ? '✅' : '❌'} (${testTime}ms)`);
      if (result.success && result.result?.persistent) {
        console.log(`      🚀 PERSISTENT: ${result.result.persistent ? 'YES' : 'NO'}`);
      }
      if (result.error) {
        console.log(`      ❌ Error: ${result.error}`);
      }
      
      // Small delay to show responsiveness
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    
    const overallTime = Date.now() - overallStartTime;
    
    console.log("\n3️⃣ Test Results Analysis:");
    console.log("   " + "=".repeat(50));
    
    const successfulTests = testResults.filter(t => t.success);
    const persistentTests = testResults.filter(t => t.isPersistent);
    const averageTime = testResults.reduce((sum, t) => sum + t.time, 0) / testResults.length;
    const maxTime = Math.max(...testResults.map(t => t.time));
    const minTime = Math.min(...testResults.map(t => t.time));
    
    console.log(`   📊 Tests Executed: ${testResults.length}`);
    console.log(`   ✅ Successful: ${successfulTests.length}/${testResults.length}`);
    console.log(`   🚀 Truly Persistent: ${persistentTests.length}/${testResults.length}`);
    console.log(`   ⏱️  Average Time: ${averageTime.toFixed(1)}ms`);
    console.log(`   ⚡ Fastest: ${minTime}ms`);
    console.log(`   🐌 Slowest: ${maxTime}ms`);
    console.log(`   🕒 Total Time: ${overallTime}ms`);
    
    // Performance analysis
    console.log("\n4️⃣ Performance Analysis:");
    console.log("   " + "=".repeat(50));
    
    const ultraFastTests = testResults.filter(t => t.success && t.time < 100);
    const fastTests = testResults.filter(t => t.success && t.time < 500);
    
    console.log(`   🚀 Ultra-Fast (<100ms): ${ultraFastTests.length}/${successfulTests.length}`);
    console.log(`   ⚡ Fast (<500ms): ${fastTests.length}/${successfulTests.length}`);
    
    if (persistentTests.length === successfulTests.length) {
      console.log("   🎯 PERSISTENCE VERIFIED: All tests used persistent instance!");
    } else {
      console.log("   ⚠️  PERSISTENCE ISSUE: Some tests didn't use persistent instance");
    }
    
    // Final persistence validation
    console.log("\n5️⃣ Final Persistence Validation...");
    const finalHealthCheck = await controller.checkInstanceHealth();
    
    if (finalHealthCheck.success) {
      const requestCount = finalHealthCheck.result?.requestCount || 0;
      console.log(`   ✅ Persistent process still alive`);
      console.log(`   📊 Total requests processed: ${requestCount}`);
      console.log(`   🎯 Process persistence: CONFIRMED`);
    } else {
      console.log(`   ❌ Persistence check failed: ${finalHealthCheck.error}`);
    }
    
    console.log("\n6️⃣ Cleanup...");
    await controller.shutdown();
    console.log("   🔚 Persistent process shutdown completed");
    
    // Summary
    console.log("\n" + "=".repeat(60));
    console.log("🏁 TEST SUMMARY");
    console.log("=".repeat(60));
    
    const allSuccessful = successfulTests.length === testResults.length;
    const allPersistent = persistentTests.length === successfulTests.length;
    const performanceExcellent = averageTime < 200;
    
    console.log(`✅ All Tests Passed: ${allSuccessful ? 'YES 🎉' : 'NO ❌'}`);
    console.log(`🚀 True Persistence: ${allPersistent ? 'YES 🎉' : 'NO ❌'}`);
    console.log(`⚡ Performance: ${performanceExcellent ? 'EXCELLENT 🚀' : 'NEEDS IMPROVEMENT ⚠️'}`);
    
    if (allSuccessful && allPersistent && performanceExcellent) {
      console.log("\n🎉 TRUE PERSISTENCE SUCCESS!");
      console.log("   The VisumPy instance truly persists across calls");
      console.log("   Ultra-fast responses achieved");
      console.log("   Ready for production use!");
    } else {
      console.log("\n⚠️  Issues detected that need resolution");
    }
    
  } catch (error) {
    console.error("💀 CRITICAL TEST ERROR:");
    console.error(error);
  }
}

// Run the test
runTruePersistenceTest().then(() => {
  console.log("\n🔚 Test completed");
  process.exit(0);
}).catch(error => {
  console.error("💀 Test failed:", error);
  process.exit(1);
});