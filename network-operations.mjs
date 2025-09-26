// Operazioni di modifica sulla rete Campoleone
// Script per modifiche e test sulla rete ferroviaria

import { PersistentVisumController } from './build/persistent-visum-controller.js';

console.log('🔧 OPERAZIONI RETE CAMPOLEONE');
console.log('=' .repeat(50));

const controller = PersistentVisumController.getInstance();

async function networkOperations() {
  try {
    // 1. Backup stato corrente
    console.log('💾 1. Creazione backup stato...');
    const backup = await controller.executeCustomCode(`
import time
start_time = time.time()

# Salva stato attuale per backup
current_state = {
    'timestamp': time.time(),
    'nodes_count': visum.Net.Nodes.Count,
    'links_count': visum.Net.Links.Count,
    'zones_count': visum.Net.Zones.Count
}

# Esempio: crea copia di alcuni attributi chiave
sample_nodes = []
node_count = 0
for node in visum.Net.Nodes:
    if node_count >= 5:
        break
    try:
        sample_nodes.append({
            'no': node.GetAttribute('No'),
            'x': node.GetAttribute('XCoord'),
            'y': node.GetAttribute('YCoord')
        })
        node_count += 1
    except:
        continue

result = {
    'backup_created': True,
    'state': current_state,
    'sample_nodes_backup': sample_nodes,
    'backup_time_ms': (time.time() - start_time) * 1000
}
`, 'Create Network Backup');

    if (backup.success) {
      console.log(`   ✅ Backup creato - ${backup.result.state.nodes_count} nodi, ${backup.result.state.links_count} collegamenti`);
      console.log(`   ⚡ Tempo backup: ${backup.result.backup_time_ms.toFixed(1)}ms`);
    }

    // 2. Test query veloci
    console.log('\n⚡ 2. Test query ultra-veloci...');
    
    const queries = [
      'visum.Net.Nodes.Count',
      'visum.Net.Links.Count', 
      'visum.Net.Zones.Count'
    ];

    for (let i = 0; i < queries.length; i++) {
      const query = queries[i];
      const testResult = await controller.executeCustomCode(`
import time
start_time = time.time()

result_value = ${query}
query_time = (time.time() - start_time) * 1000

result = {
    'query': '${query}',
    'value': result_value,
    'query_time_ms': query_time
}
`, `Quick Query ${i+1}`);

      if (testResult.success) {
        console.log(`   🔥 ${query}: ${testResult.result.value} (${testResult.result.query_time_ms.toFixed(3)}ms)`);
      }
    }

    // 3. Analisi collegamenti specifici
    console.log('\n🔗 3. Analisi collegamenti...');
    const linksAnalysis = await controller.executeCustomCode(`
import time
start_time = time.time()

# Analizza collegamenti per lunghezza
link_stats = {
    'total_links': 0,
    'total_length_km': 0,
    'min_length': float('inf'),
    'max_length': 0,
    'avg_length': 0
}

lengths = []
for link in visum.Net.Links:
    try:
        length = link.GetAttribute('Length')
        lengths.append(length)
        
        link_stats['total_links'] += 1
        link_stats['total_length_km'] += length / 1000
        
        if length < link_stats['min_length']:
            link_stats['min_length'] = length
        if length > link_stats['max_length']:
            link_stats['max_length'] = length
            
    except:
        continue

if lengths:
    link_stats['avg_length'] = sum(lengths) / len(lengths)
    link_stats['min_length'] = link_stats['min_length'] if link_stats['min_length'] != float('inf') else 0

result = {
    'link_statistics': link_stats,
    'analysis_time_ms': (time.time() - start_time) * 1000
}
`, 'Links Analysis');

    if (linksAnalysis.success) {
      const stats = linksAnalysis.result.link_statistics;
      console.log(`   📊 Collegamenti totali: ${stats.total_links}`);
      console.log(`   📏 Lunghezza totale: ${stats.total_length_km.toFixed(2)} km`);
      console.log(`   📐 Lunghezza media: ${(stats.avg_length/1000).toFixed(2)} km`);
      console.log(`   ⚡ Tempo analisi: ${linksAnalysis.result.analysis_time_ms.toFixed(1)}ms`);
    }

    // 4. Test performance finale
    console.log('\n🎯 4. Test performance finale...');
    const perfTest = await controller.executeCustomCode(`
import time

# Test multiple queries rapide
start_total = time.time()

tests = []

# Test 1: Count operations
start = time.time()
nodes = visum.Net.Nodes.Count
test1_time = (time.time() - start) * 1000
tests.append({'test': 'nodes_count', 'time_ms': test1_time, 'result': nodes})

# Test 2: Links count
start = time.time()
links = visum.Net.Links.Count
test2_time = (time.time() - start) * 1000
tests.append({'test': 'links_count', 'time_ms': test2_time, 'result': links})

# Test 3: Zones count  
start = time.time()
zones = visum.Net.Zones.Count
test3_time = (time.time() - start) * 1000
tests.append({'test': 'zones_count', 'time_ms': test3_time, 'result': zones})

total_time = (time.time() - start_total) * 1000

result = {
    'performance_tests': tests,
    'total_time_ms': total_time,
    'avg_query_time_ms': total_time / len(tests)
}
`, 'Performance Final Test');

    if (perfTest.success) {
      console.log(`   🚀 Test completati in ${perfTest.result.total_time_ms.toFixed(1)}ms`);
      console.log(`   ⚡ Tempo medio query: ${perfTest.result.avg_query_time_ms.toFixed(3)}ms`);
      
      perfTest.result.performance_tests.forEach(test => {
        console.log(`   🔥 ${test.test}: ${test.result} (${test.time_ms.toFixed(3)}ms)`);
      });
    }
    
    console.log('\n✅ OPERAZIONI COMPLETATE - Istanza rimane attiva e pronta');
    
  } catch (error) {
    console.error('❌ Errore durante operazioni:', error.message);
  }
}

networkOperations().catch(console.error);