// DIAGNOSI: Test della comunicazione JSON con il processo Python persistente

import { PersistentVisumController } from "./build/persistent-visum-controller.js";

console.log("🔍 DIAGNOSI: Comunicazione JSON Process Python");
console.log("=".repeat(60));

const controller = PersistentVisumController.getInstance();

async function diagnosisTest() {
  try {
    console.log("\n1️⃣ Avviando processo persistente...");
    const startResult = await controller.startPersistentVisumProcess();
    
    if (!startResult.success) {
      console.error("❌ Impossibile avviare processo:", startResult.message);
      return;
    }
    
    console.log(`✅ Processo avviato con ${startResult.nodes} nodi`);
    
    console.log("\n2️⃣ Test comunicazione JSON semplice...");
    
    // Test 1: Network Stats (è riuscito prima)
    console.log("   📊 Test Network Stats...");
    const statsStart = Date.now();
    const statsResult = await controller.getNetworkStats();
    const statsTime = Date.now() - statsStart;
    
    console.log(`   Risultato: ${statsResult.success ? '✅' : '❌'} (${statsTime}ms)`);
    if (statsResult.success) {
      console.log(`   Nodi: ${statsResult.result?.nodes}`);
      console.log(`   Persistente: ${statsResult.result?.persistent}`);
    } else {
      console.log(`   Errore: ${statsResult.error}`);
    }
    
    // Test 2: Comando semplice personalizzato
    console.log("\n   🧪 Test comando semplice...");
    const simpleStart = Date.now();
    const simpleResult = await controller.executeCustomCode(`
# Test semplice per diagnosi
result = {
    'test': 'simple',
    'success': True,
    'nodes': visum.Net.Nodes.Count,
    'timestamp': time.time()
}
`, "Test semplice");
    const simpleTime = Date.now() - simpleStart;
    
    console.log(`   Risultato: ${simpleResult.success ? '✅' : '❌'} (${simpleTime}ms)`);
    if (simpleResult.success) {
      console.log(`   Test: ${simpleResult.result?.test}`);
      console.log(`   Nodi: ${simpleResult.result?.nodes}`);
    } else {
      console.log(`   Errore: ${simpleResult.error}`);
    }
    
    // Test 3: Comando che potrebbe causare problemi
    console.log("\n   ⚠️  Test comando complesso...");
    const complexStart = Date.now();
    const complexResult = await controller.executeCustomCode(`
# Test complesso - potrebbe causare timeout
try:
    # Operazione che potrebbe bloccarsi
    nodes = visum.Net.Nodes
    count = nodes.Count
    
    # Test iterazione semplice
    result = {
        'test': 'complex',
        'success': True,
        'totalNodes': count,
        'sample': [],  # Non facciamo iterazioni complesse
        'method': 'count_only'
    }
except Exception as e:
    result = {
        'test': 'complex',
        'success': False,
        'error': str(e)
    }
`, "Test complesso");
    const complexTime = Date.now() - complexStart;
    
    console.log(`   Risultato: ${complexResult.success ? '✅' : '❌'} (${complexTime}ms)`);
    if (complexResult.success) {
      console.log(`   Test: ${complexResult.result?.test}`);
      console.log(`   Metodo: ${complexResult.result?.method}`);
    } else {
      console.log(`   Errore: ${complexResult.error}`);
    }
    
    // Test 4: Health check
    console.log("\n   🩺 Test health check...");
    const healthStart = Date.now();
    const healthResult = await controller.checkInstanceHealth();
    const healthTime = Date.now() - healthStart;
    
    console.log(`   Risultato: ${healthResult.success ? '✅' : '❌'} (${healthTime}ms)`);
    if (healthResult.success) {
      console.log(`   Richieste: ${healthResult.result?.requestCount}`);
      console.log(`   Progetto: ${healthResult.result?.projectLoaded ? 'SÌ' : 'NO'}`);
    } else {
      console.log(`   Errore: ${healthResult.error}`);
    }
    
    console.log("\n3️⃣ Analisi problemi comunicazione:");
    console.log("   " + "=".repeat(50));
    
    const tests = [
      { name: "Network Stats", result: statsResult, time: statsTime },
      { name: "Comando Semplice", result: simpleResult, time: simpleTime },
      { name: "Comando Complesso", result: complexResult, time: complexTime },
      { name: "Health Check", result: healthResult, time: healthTime }
    ];
    
    let successCount = 0;
    let timeoutCount = 0;
    
    tests.forEach((test, i) => {
      const status = test.result.success ? '✅' : '❌';
      const timeStatus = test.time < 1000 ? '⚡' : test.time > 30000 ? '🐌' : '⏳';
      
      console.log(`   ${i+1}. ${test.name}: ${status} ${timeStatus} (${test.time}ms)`);
      
      if (test.result.success) successCount++;
      if (test.time > 30000) timeoutCount++;
      
      if (!test.result.success && test.result.error?.includes('timeout')) {
        console.log(`      🚨 TIMEOUT: ${test.result.error}`);
      }
    });
    
    console.log(`\n   📊 Successi: ${successCount}/${tests.length}`);
    console.log(`   ⏰ Timeout: ${timeoutCount}/${tests.length}`);
    
    if (timeoutCount > 0) {
      console.log("\n🚨 PROBLEMA IDENTIFICATO:");
      console.log("   - Comunicazione JSON si blocca dopo primo comando");
      console.log("   - Possibile problema nel parsing delle risposte");
      console.log("   - Il processo Python non risponde correttamente");
    } else if (successCount === tests.length) {
      console.log("\n✅ COMUNICAZIONE FUNZIONANTE:");
      console.log("   - Tutti i test sono passati");
      console.log("   - La comunicazione JSON è robusta");
    }
    
    await controller.shutdown();
    console.log("\n🔚 Processo terminato per diagnosi");
    
  } catch (error) {
    console.error("\n💀 ERRORE CRITICO nella diagnosi:");
    console.error(error);
  }
}

// Esegui diagnosi
diagnosisTest().then(() => {
  console.log("\n🔍 Diagnosi completata");
  process.exit(0);
}).catch(error => {
  console.error("💀 Diagnosi fallita:", error);
  process.exit(1);
});