// Script per monitoraggio continuo istanza Campoleone
// Monitora performance e stato dell'istanza attiva

import { ProjectInstanceManager } from './build/project-instance-manager.js';

console.log("📊 MONITORAGGIO ISTANZA CAMPOLEONE");
console.log("=" .repeat(42));

const projectManager = ProjectInstanceManager.getInstance();

// Funzione di monitoraggio singolo
async function singleMonitorCheck() {
  const timestamp = new Date().toLocaleTimeString();
  
  try {
    // Test velocità con comando semplice
    const start = Date.now();
    
    const result = await projectManager.executeProjectAnalysis('campoleone', `
import time
test_start = time.time()
node_count = visum.Net.Nodes.Count
link_count = visum.Net.Links.Count
test_end = time.time()

result = {
    'timestamp': time.time(),
    'nodes': node_count,
    'links': link_count,
    'visum_query_time_ms': (test_end - test_start) * 1000,
    'check_type': 'speed_monitor'
}
`, "Speed Monitor Check");
    
    const totalTime = Date.now() - start;
    
    if (result.success) {
      console.log(`[${timestamp}] ✅ Risposta in ${totalTime}ms (VisumPy: ${result.result.visum_query_time_ms.toFixed(1)}ms)`);
      return { success: true, totalTime, visumTime: result.result.visum_query_time_ms };
    } else {
      console.log(`[${timestamp}] ❌ Errore: ${result.error}`);
      return { success: false, error: result.error };
    }
    
  } catch (error) {
    console.log(`[${timestamp}] ❌ Exception: ${error.message}`);
    return { success: false, error: error.message };
  }
}

// Monitoraggio continuo con intervalli
async function continuousMonitoring(intervalSeconds = 5, maxChecks = 10) {
  console.log(`🔄 Avvio monitoraggio continuo (ogni ${intervalSeconds}s, ${maxChecks} check)`);
  console.log("");
  
  const stats = {
    totalChecks: 0,
    successfulChecks: 0,
    failedChecks: 0,
    totalTimes: [],
    visumTimes: []
  };
  
  for (let i = 0; i < maxChecks; i++) {
    const result = await singleMonitorCheck();
    stats.totalChecks++;
    
    if (result.success) {
      stats.successfulChecks++;
      stats.totalTimes.push(result.totalTime);
      stats.visumTimes.push(result.visumTime);
    } else {
      stats.failedChecks++;
    }
    
    // Attendi prima del prossimo check (tranne l'ultimo)
    if (i < maxChecks - 1) {
      await new Promise(resolve => setTimeout(resolve, intervalSeconds * 1000));
    }
  }
  
  // Statistiche finali
  console.log("\n" + "=" .repeat(42));
  console.log("📊 STATISTICHE MONITORAGGIO:");
  console.log(`✅ Check riusciti: ${stats.successfulChecks}/${stats.totalChecks}`);
  console.log(`❌ Check falliti: ${stats.failedChecks}`);
  
  if (stats.totalTimes.length > 0) {
    const avgTotal = stats.totalTimes.reduce((a, b) => a + b, 0) / stats.totalTimes.length;
    const avgVisum = stats.visumTimes.reduce((a, b) => a + b, 0) / stats.visumTimes.length;
    const minTotal = Math.min(...stats.totalTimes);
    const maxTotal = Math.max(...stats.totalTimes);
    const minVisum = Math.min(...stats.visumTimes);
    const maxVisum = Math.max(...stats.visumTimes);
    
    console.log(`⚡ Tempo totale medio: ${avgTotal.toFixed(1)}ms`);
    console.log(`🔥 Tempo VisumPy medio: ${avgVisum.toFixed(1)}ms`);
    console.log(`📈 Range totale: ${minTotal}ms - ${maxTotal}ms`);
    console.log(`📈 Range VisumPy: ${minVisum.toFixed(1)}ms - ${maxVisum.toFixed(1)}ms`);
    
    // Valutazione performance
    if (avgVisum < 20) {
      console.log("🚀 PERFORMANCE: ECCELLENTE (< 20ms)");
    } else if (avgVisum < 50) {
      console.log("⚡ PERFORMANCE: OTTIMA (< 50ms)");
    } else if (avgVisum < 100) {
      console.log("✅ PERFORMANCE: BUONA (< 100ms)");
    } else {
      console.log("⚠️ PERFORMANCE: ACCETTABILE (> 100ms)");
    }
  }
  
  console.log("🔄 Istanza continua a essere attiva...");
}

// Health check dettagliato
async function detailedHealthCheck() {
  console.log("\n💚 HEALTH CHECK DETTAGLIATO");
  
  try {
    const health = await projectManager.checkProjectHealth('campoleone');
    
    if (health.success) {
      const uptime = Math.floor((health.health.uptime || 0) / 1000);
      const minutes = Math.floor(uptime / 60);
      const seconds = uptime % 60;
      
      console.log("✅ Stato istanza: SALUTARE");
      console.log(`⏰ Uptime: ${minutes}m ${seconds}s`);
      console.log(`⚡ Response time: ${health.health.response_time_ms}ms`);
      console.log(`💾 Memoria: ${health.health.memory_mb}MB`);
      console.log(`📂 Progetto: ${health.health.project_loaded ? '✅ Caricato' : '❌ Non caricato'}`);
      console.log(`🔗 Network: ${health.health.network_ready ? '✅ Pronto' : '❌ Non pronto'}`);
    } else {
      console.log(`❌ Health check fallito: ${health.error}`);
    }
    
  } catch (error) {
    console.error("❌ Errore health check:", error.message);
  }
}

// Status istanze
async function instancesStatus() {
  console.log("\n📋 STATUS ISTANZE ATTIVE");
  
  try {
    const status = projectManager.getInstancesStatus();
    const count = Object.keys(status).length;
    
    console.log(`🎯 Istanze attive: ${count}`);
    
    for (const [projectId, info] of Object.entries(status)) {
      const uptime = Math.floor((info.uptime || 0) / 1000);
      const lastUsed = info.lastUsed ? Math.floor((Date.now() - info.lastUsed) / 1000) : 'Mai';
      
      console.log(`\n🔧 ${info.name}:`);
      console.log(`   • ID: ${projectId}`);
      console.log(`   • Status: ${info.isActive ? '✅ Attiva' : '❌ Inattiva'}`);
      console.log(`   • Uptime: ${uptime}s`);
      console.log(`   • Ultimo uso: ${lastUsed}s fa`);
      console.log(`   • Network: ${info.stats?.nodes} nodi, ${info.stats?.links} link`);
    }
    
  } catch (error) {
    console.error("❌ Errore status:", error.message);
  }
}

// Script principale
async function runMonitoring() {
  console.log("🚀 Avvio script monitoraggio Campoleone...\n");
  
  // 1. Health check iniziale
  await detailedHealthCheck();
  
  // 2. Status istanze
  await instancesStatus();
  
  // 3. Monitoraggio continuo (5 check ogni 3 secondi)
  await continuousMonitoring(3, 5);
  
  console.log("\n🎯 MONITORAGGIO COMPLETATO");
  console.log("L'istanza Campoleone rimane attiva e pronta!");
}

// Esegui monitoraggio
runMonitoring().catch(console.error);