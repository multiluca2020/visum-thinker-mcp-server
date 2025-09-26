// Script per analisi avanzate su Campoleone
// Operazioni più complesse sull'istanza persistente

import { ProjectInstanceManager } from './build/project-instance-manager.js';

console.log("🔬 ANALISI AVANZATE CAMPOLEONE");
console.log("=" .repeat(40));

const projectManager = ProjectInstanceManager.getInstance();

// Analisi 1: Matrice origine-destinazione campione
async function odMatrixSample() {
  console.log("\n🗺️ 1. CAMPIONE MATRICE O-D");
  const start = Date.now();
  
  try {
    const result = await projectManager.executeProjectAnalysis('campoleone', `
# Analisi matrice origine-destinazione
zones = visum.Net.Zones
zone_list = []

# Prendiamo prime 5 zone per test rapido
count = 0
for zone in zones:
    if count >= 5:
        break
    zone_no = zone.GetAttribute('No')
    zone_list.append(zone_no)
    count += 1

od_sample = []
for origin in zone_list:
    for dest in zone_list:
        if origin != dest:
            # Simuliamo valore domanda (in un vero scenario leggeresti dalla matrice)
            od_sample.append({
                'origin': origin,
                'destination': dest,
                'demand': origin * dest * 10  # Valore simulato
            })

result = {
    'total_zones': zones.Count,
    'sample_zones': zone_list,
    'od_pairs': len(od_sample),
    'od_sample': od_sample[:10],  # Prime 10 coppie O-D
    'analysis_type': 'od_matrix_sample'
}
`, "O-D Matrix Sample");
    
    const time = Date.now() - start;
    console.log(`✅ Completato in ${time}ms`);
    console.log(`🎯 Zone campione: ${result.result.sample_zones.join(', ')}`);
    console.log(`🔗 Coppie O-D analizzate: ${result.result.od_pairs}`);
    
  } catch (error) {
    console.error("❌ Errore:", error.message);
  }
}

// Analisi 2: Analisi topologia rete
async function networkTopology() {
  console.log("\n🌐 2. TOPOLOGIA RETE");
  const start = Date.now();
  
  try {
    const result = await projectManager.executeProjectAnalysis('campoleone', `
# Analisi topologia della rete
nodes = visum.Net.Nodes
links = visum.Net.Links

# Analisi gradi dei nodi (limitata per performance)
node_degrees = {}
link_count = 0

for link in links:
    if link_count >= 1000:  # Limitiamo per performance
        break
    try:
        from_node = link.GetAttribute('FromNodeNo')
        to_node = link.GetAttribute('ToNodeNo')
        
        # Conta gradi (connessioni) per ogni nodo
        node_degrees[from_node] = node_degrees.get(from_node, 0) + 1
        node_degrees[to_node] = node_degrees.get(to_node, 0) + 1
        link_count += 1
    except:
        continue

# Trova nodi con più connessioni
if node_degrees:
    max_degree = max(node_degrees.values())
    max_degree_nodes = [node for node, degree in node_degrees.items() if degree == max_degree]
    
    # Statistiche
    avg_degree = sum(node_degrees.values()) / len(node_degrees)
    
    result = {
        'total_nodes': nodes.Count,
        'total_links': links.Count,
        'analyzed_links': link_count,
        'nodes_analyzed': len(node_degrees),
        'max_degree': max_degree,
        'max_degree_nodes': max_degree_nodes[:5],
        'average_degree': round(avg_degree, 2),
        'analysis_type': 'network_topology'
    }
else:
    result = {
        'error': 'Nessun dato topologico raccolto',
        'analysis_type': 'network_topology'
    }
`, "Network Topology Analysis");
    
    const time = Date.now() - start;
    console.log(`✅ Completato in ${time}ms`);
    
    if (!result.result.error) {
      console.log(`🌟 Nodo con più connessioni: ${result.result.max_degree_nodes[0]} (${result.result.max_degree} connessioni)`);
      console.log(`📊 Grado medio: ${result.result.average_degree}`);
      console.log(`🔗 Link analizzati: ${result.result.analyzed_links}/${result.result.total_links}`);
    } else {
      console.log(`❌ ${result.result.error}`);
    }
    
  } catch (error) {
    console.error("❌ Errore:", error.message);
  }
}

// Analisi 3: Simulazione path finding
async function pathFindingSample() {
  console.log("\n🛣️ 3. SIMULAZIONE PATH FINDING");
  const start = Date.now();
  
  try {
    const result = await projectManager.executeProjectAnalysis('campoleone', `
# Simulazione path finding tra nodi casuali
nodes = visum.Net.Nodes
node_list = []

# Raccogliamo primi 10 nodi per test
count = 0
for node in nodes:
    if count >= 10:
        break
    node_no = node.GetAttribute('No')
    try:
        x_coord = node.GetAttribute('XCoord')
        y_coord = node.GetAttribute('YCoord')
        node_list.append({
            'node_no': node_no,
            'x': x_coord,
            'y': y_coord
        })
        count += 1
    except:
        continue

# Calcola distanze euclidee tra primi 3 nodi
path_samples = []
if len(node_list) >= 3:
    for i in range(3):
        for j in range(i+1, 3):
            node1 = node_list[i]
            node2 = node_list[j]
            
            # Distanza euclidea
            distance = ((node2['x'] - node1['x'])**2 + (node2['y'] - node1['y'])**2)**0.5
            
            path_samples.append({
                'from_node': node1['node_no'],
                'to_node': node2['node_no'],
                'euclidean_distance': round(distance, 2),
                'from_coords': [node1['x'], node1['y']],
                'to_coords': [node2['x'], node2['y']]
            })

result = {
    'total_nodes': nodes.Count,
    'sample_nodes': len(node_list),
    'path_samples': path_samples,
    'analysis_type': 'path_finding_sample'
}
`, "Path Finding Sample");
    
    const time = Date.now() - start;
    console.log(`✅ Completato in ${time}ms`);
    console.log(`🎯 Nodi campione: ${result.result.sample_nodes}`);
    console.log(`🛣️ Path simulati: ${result.result.path_samples.length}`);
    
    if (result.result.path_samples.length > 0) {
      const sample = result.result.path_samples[0];
      console.log(`📏 Esempio: Nodo ${sample.from_node} → ${sample.to_node} (${sample.euclidean_distance}m)`);
    }
    
  } catch (error) {
    console.error("❌ Errore:", error.message);
  }
}

// Esegui analisi avanzate
async function executeAdvancedAnalysis() {
  console.log("🔬 Inizio analisi avanzate Campoleone...\n");
  
  const totalStart = Date.now();
  
  await odMatrixSample();
  await networkTopology();
  await pathFindingSample();
  
  const totalTime = Date.now() - totalStart;
  
  console.log("\n" + "=" .repeat(40));
  console.log(`🎯 ANALISI AVANZATE COMPLETATE in ${totalTime}ms`);
  console.log("⚡ Tutte le operazioni sono state ultra-rapide!");
  console.log("🔄 Istanza rimane attiva...");
}

// Esegui script
executeAdvancedAnalysis().catch(console.error);