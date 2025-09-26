// Script per operazioni specifiche su istanza Campoleone attiva
// Usa l'istanza persistente già avviata per analisi rapide

import { ProjectInstanceManager } from './build/project-instance-manager.js';

console.log("⚡ OPERAZIONI SU ISTANZA CAMPOLEONE ATTIVA");
console.log("=" .repeat(45));

const projectManager = ProjectInstanceManager.getInstance();

// Operazione 1: Statistiche di rete rapide
async function networkQuickStats() {
  console.log("\n📊 1. STATISTICHE RETE RAPIDE");
  const start = Date.now();
  
  try {
    const result = await projectManager.executeProjectAnalysis('campoleone', `
result = {
    'nodes': visum.Net.Nodes.Count,
    'links': visum.Net.Links.Count,
    'zones': visum.Net.Zones.Count,
    'analysis_type': 'quick_stats'
}
`, "Quick Network Stats");
    
    const time = Date.now() - start;
    console.log(`✅ Completato in ${time}ms`);
    console.log(`📈 Nodi: ${result.result.nodes}, Link: ${result.result.links}, Zone: ${result.result.zones}`);
    
  } catch (error) {
    console.error("❌ Errore:", error.message);
  }
}

// Operazione 2: Analisi domanda di trasporto
async function demandAnalysis() {
  console.log("\n🚌 2. ANALISI DOMANDA TRASPORTO");
  const start = Date.now();
  
  try {
    const result = await projectManager.executeProjectAnalysis('campoleone', `
# Analisi domanda di trasporto
zones = visum.Net.Zones
demand_data = []

for zone in zones:
    zone_data = {
        'zone_no': zone.GetAttribute('No'),
        'demand_origin': zone.GetAttribute('DemOrig') if hasattr(zone, 'GetAttribute') else 0,
        'demand_dest': zone.GetAttribute('DemDest') if hasattr(zone, 'GetAttribute') else 0
    }
    demand_data.append(zone_data)
    if len(demand_data) >= 10:  # Limitiamo a 10 zone per test rapido
        break

total_zones = zones.Count
        
result = {
    'total_zones': total_zones,
    'sample_zones': len(demand_data),
    'zone_data': demand_data[:5],  # Prime 5 zone
    'analysis_type': 'demand_analysis'
}
`, "Transport Demand Analysis");
    
    const time = Date.now() - start;
    console.log(`✅ Completato in ${time}ms`);
    console.log(`🎯 Zone totali: ${result.result.total_zones}`);
    console.log(`📊 Zone campione analizzate: ${result.result.sample_zones}`);
    
  } catch (error) {
    console.error("❌ Errore:", error.message);
  }
}

// Operazione 3: Analisi collegamenti più lunghi
async function longestLinksAnalysis() {
  console.log("\n🛤️ 3. ANALISI COLLEGAMENTI PIÙ LUNGHI");
  const start = Date.now();
  
  try {
    const result = await projectManager.executeProjectAnalysis('campoleone', `
# Trova i collegamenti più lunghi
links = visum.Net.Links
link_lengths = []

# Raccogli lunghezze di tutti i link (limitiamo per performance)
count = 0
for link in links:
    if count >= 1000:  # Limitiamo a 1000 link per test rapido
        break
    try:
        length = link.GetAttribute('Length')
        from_node = link.GetAttribute('FromNodeNo')
        to_node = link.GetAttribute('ToNodeNo')
        
        link_lengths.append({
            'from_node': from_node,
            'to_node': to_node,
            'length': length
        })
        count += 1
    except:
        continue

# Ordina per lunghezza
link_lengths.sort(key=lambda x: x['length'], reverse=True)

result = {
    'total_links_analyzed': len(link_lengths),
    'total_links_in_network': links.Count,
    'longest_links': link_lengths[:5],  # Top 5 collegamenti più lunghi
    'shortest_links': link_lengths[-5:],  # Top 5 collegamenti più corti
    'average_length': sum(l['length'] for l in link_lengths) / len(link_lengths) if link_lengths else 0,
    'analysis_type': 'longest_links'
}
`, "Longest Links Analysis");
    
    const time = Date.now() - start;
    console.log(`✅ Completato in ${time}ms`);
    console.log(`🔗 Link analizzati: ${result.result.total_links_analyzed}/${result.result.total_links_in_network}`);
    console.log(`📏 Lunghezza media: ${result.result.average_length.toFixed(2)}m`);
    
    if (result.result.longest_links.length > 0) {
      const longest = result.result.longest_links[0];
      console.log(`🥇 Link più lungo: ${longest.from_node} → ${longest.to_node} (${longest.length.toFixed(2)}m)`);
    }
    
  } catch (error) {
    console.error("❌ Errore:", error.message);
  }
}

// Operazione 4: Health check rapido
async function quickHealthCheck() {
  console.log("\n💚 4. HEALTH CHECK ISTANZA");
  
  try {
    const health = await projectManager.checkProjectHealth('campoleone');
    
    if (health.success) {
      const uptime = Math.floor((health.health.uptime || 0) / 1000);
      console.log(`✅ Istanza Salutare`);
      console.log(`⏰ Uptime: ${uptime}s`);
      console.log(`⚡ Response time: ${health.health.response_time_ms}ms`);
      console.log(`💾 Memoria: ${health.health.memory_mb}MB`);
    } else {
      console.log(`❌ Health check fallito: ${health.error}`);
    }
    
  } catch (error) {
    console.error("❌ Errore health check:", error.message);
  }
}

// Esegui tutte le operazioni in sequenza
async function executeAllOperations() {
  console.log("🚀 Inizio operazioni su istanza Campoleone...\n");
  
  const totalStart = Date.now();
  
  await networkQuickStats();
  await demandAnalysis();
  await longestLinksAnalysis();
  await quickHealthCheck();
  
  const totalTime = Date.now() - totalStart;
  
  console.log("\n" + "=" .repeat(45));
  console.log(`🎯 TUTTE LE OPERAZIONI COMPLETATE in ${totalTime}ms`);
  console.log("🔄 Istanza rimane attiva per altre operazioni...");
}

// Esegui script
executeAllOperations().catch(console.error);