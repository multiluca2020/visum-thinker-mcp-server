// Analisi specifica progetto Campoleone
// Operazioni dettagliate sulla rete ferroviaria

import { PersistentVisumController } from './build/persistent-visum-controller.js';

console.log('🚆 ANALISI PROGETTO CAMPOLEONE');
console.log('=' .repeat(50));

const controller = PersistentVisumController.getInstance();

async function analyzeCampoleone() {
  try {
    // 1. Analisi generale rete
    console.log('📊 1. Analisi generale della rete...');
    const networkAnalysis = await controller.executeCustomCode(`
import time
start_time = time.time()

# Analisi base rete
nodes = visum.Net.Nodes.Count
links = visum.Net.Links.Count
zones = visum.Net.Zones.Count

# Analisi collegamenti ferroviari
rail_links = 0
rail_length = 0
for link in visum.Net.Links:
    # Assume che i collegamenti ferroviari abbiano attributi specifici
    try:
        if hasattr(link, 'GetAttribute'):
            # Controlla se è un collegamento ferroviario
            rail_links += 1
            rail_length += link.GetAttribute('Length')
    except:
        continue

# Statistiche zone
zone_data = []
for zone in visum.Net.Zones:
    try:
        zone_info = {
            'no': zone.GetAttribute('No'),
            'name': zone.GetAttribute('Name') if hasattr(zone, 'Name') else f'Zone_{zone.GetAttribute("No")}',
            'x': zone.GetAttribute('XCoord'),
            'y': zone.GetAttribute('YCoord')
        }
        zone_data.append(zone_info)
    except:
        continue

result = {
    'network_summary': {
        'nodes': nodes,
        'links': links,
        'zones': zones,
        'rail_links': rail_links,
        'total_rail_length_km': round(rail_length / 1000, 2)
    },
    'zones_sample': zone_data[:5],  # Prime 5 zone
    'analysis_time_ms': (time.time() - start_time) * 1000
}
`, 'Network General Analysis');

    if (networkAnalysis.success) {
      const net = networkAnalysis.result.network_summary;
      console.log(`   ✅ Nodi: ${net.nodes}`);
      console.log(`   ✅ Collegamenti: ${net.links}`);
      console.log(`   ✅ Zone: ${net.zones}`);
      console.log(`   🚆 Collegamenti ferroviari: ${net.rail_links}`);
      console.log(`   📏 Lunghezza totale: ${net.total_rail_length_km} km`);
      console.log(`   ⚡ Tempo analisi: ${networkAnalysis.result.analysis_time_ms.toFixed(1)}ms`);
    }

    // 2. Analisi nodi principali
    console.log('\n🔍 2. Analisi nodi principali...');
    const nodesAnalysis = await controller.executeCustomCode(`
import time
start_time = time.time()

# Analizza i primi 10 nodi per connettività
main_nodes = []
node_count = 0

for node in visum.Net.Nodes:
    if node_count >= 10:
        break
    
    try:
        # Conta collegamenti in entrata e uscita
        in_links = 0
        out_links = 0
        
        for link in visum.Net.Links:
            if link.GetAttribute('ToNodeNo') == node.GetAttribute('No'):
                in_links += 1
            if link.GetAttribute('FromNodeNo') == node.GetAttribute('No'):
                out_links += 1
        
        node_info = {
            'node_no': node.GetAttribute('No'),
            'x_coord': node.GetAttribute('XCoord'),
            'y_coord': node.GetAttribute('YCoord'),
            'incoming_links': in_links,
            'outgoing_links': out_links,
            'total_connections': in_links + out_links
        }
        main_nodes.append(node_info)
        node_count += 1
        
    except Exception as e:
        continue

# Ordina per numero di connessioni
main_nodes.sort(key=lambda x: x['total_connections'], reverse=True)

result = {
    'main_nodes': main_nodes,
    'most_connected': main_nodes[0] if main_nodes else None,
    'analysis_time_ms': (time.time() - start_time) * 1000
}
`, 'Main Nodes Analysis');

    if (nodesAnalysis.success) {
      console.log(`   📈 Nodo più connesso: ${nodesAnalysis.result.most_connected?.node_no} (${nodesAnalysis.result.most_connected?.total_connections} connessioni)`);
      console.log(`   ⚡ Tempo analisi: ${nodesAnalysis.result.analysis_time_ms.toFixed(1)}ms`);
    }

    // 3. Health check veloce
    console.log('\n💚 3. Health check istanza...');
    const health = await controller.checkInstanceHealth();
    
    if (health.success) {
      console.log(`   ✅ Istanza operativa`);
      console.log(`   ⚡ Response time: ${health.result.response_time_ms}ms`);
      console.log(`   💾 Memory: ${health.result.memory_mb}MB`);
      console.log(`   🔄 Progetto caricato: ${health.result.project_loaded ? 'Sì' : 'No'}`);
    }
    
    console.log('\n🎯 ANALISI COMPLETATA - Istanza rimane attiva per altri comandi');
    
  } catch (error) {
    console.error('❌ Errore durante analisi:', error.message);
  }
}

analyzeCampoleone().catch(console.error);