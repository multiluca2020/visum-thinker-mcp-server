// Test dedicato per istanza persistente progetto Campoleone
// Dimostra l'avvio e l'utilizzo dell'istanza dedicata

import { ProjectInstanceManager } from './build/project-instance-manager.js';

async function testCampoleoneInstance() {
    console.log("🚀 Test Istanza Dedicata Progetto Campoleone");
    console.log("=" .repeat(60));
    
    const projectManager = ProjectInstanceManager.getInstance();
    
    try {
        // 1. Avvia istanza dedicata per Campoleone
        console.log("\n📋 Step 1: Avvio istanza dedicata Campoleone...");
        const startResult = await projectManager.startProjectInstance('campoleone');
        
        if (startResult.success) {
            console.log(`✅ ${startResult.message}`);
            console.log(`📊 Network: ${startResult.stats?.nodes} nodi, ${startResult.stats?.links} link, ${startResult.stats?.zones} zone`);
        } else {
            console.log(`❌ Errore: ${startResult.message}`);
            return;
        }
        
        // 2. Check status istanze
        console.log("\n📋 Step 2: Verifica status istanze...");
        const status = projectManager.getInstancesStatus();
        console.log("Status istanze attive:");
        for (const [id, info] of Object.entries(status)) {
            console.log(`  • ${id}: ${info.name} - ${info.isActive ? 'ATTIVA' : 'INATTIVA'}`);
        }
        
        // 3. Health check istanza Campoleone
        console.log("\n📋 Step 3: Health check Campoleone...");
        const healthResult = await projectManager.checkProjectHealth('campoleone');
        
        if (healthResult.success) {
            const health = healthResult.health;
            console.log("✅ Istanza Campoleone è salutare:");
            console.log(`   • Uptime: ${Math.floor((health.uptime || 0) / 1000)}s`);
            console.log(`   • Response time: ${health.response_time_ms}ms`);
            console.log(`   • Progetto caricato: ${health.project_loaded ? '✅' : '❌'}`);
        } else {
            console.log(`❌ Health check fallito: ${healthResult.error}`);
        }
        
        // 4. Test analisi veloce - Statistiche di base
        console.log("\n📋 Step 4: Test analisi veloce - Statistiche di base...");
        const analysisStart = Date.now();
        
        const basicStatsResult = await projectManager.executeProjectAnalysis(
            'campoleone',
            `
# Analisi veloce delle statistiche di rete
result = {
    'timestamp': time.time(),
    'network_stats': {
        'total_nodes': visum.Net.Nodes.Count,
        'total_links': visum.Net.Links.Count,
        'total_zones': visum.Net.Zones.Count,
        'total_stops': visum.Net.Stops.Count if hasattr(visum.Net, 'Stops') else 0
    },
    'analysis_type': 'basic_network_stats'
}
`,
            "Statistiche di rete di base"
        );
        
        const analysisTime = Date.now() - analysisStart;
        
        if (basicStatsResult.success) {
            console.log(`✅ Analisi completata in ${basicStatsResult.executionTimeMs}ms (totale: ${analysisTime}ms)`);
            console.log("📊 Risultati:");
            console.log(JSON.stringify(basicStatsResult.result, null, 2));
        } else {
            console.log(`❌ Errore analisi: ${basicStatsResult.error}`);
        }
        
        // 5. Test analisi più complessa - Analisi link
        console.log("\n📋 Step 5: Test analisi complessa - Analisi link...");
        const complexAnalysisStart = Date.now();
        
        const linkAnalysisResult = await projectManager.executeProjectAnalysis(
            'campoleone',
            `
# Analisi più complessa dei link della rete
link_lengths = []
link_types = {}

for link in visum.Net.Links:
    length = link.GetAttValue('Length')
    link_type = link.GetAttValue('TypeNo') if hasattr(link, 'TypeNo') else 'Unknown'
    
    link_lengths.append(length)
    
    if link_type in link_types:
        link_types[link_type] += 1
    else:
        link_types[link_type] = 1
    
    # Limite per performance
    if len(link_lengths) >= 1000:
        break

# Calcola statistiche
import statistics
avg_length = statistics.mean(link_lengths) if link_lengths else 0
max_length = max(link_lengths) if link_lengths else 0
min_length = min(link_lengths) if link_lengths else 0

result = {
    'timestamp': time.time(),
    'link_analysis': {
        'sample_size': len(link_lengths),
        'avg_length_km': round(avg_length, 3),
        'max_length_km': round(max_length, 3),
        'min_length_km': round(min_length, 3),
        'link_types_distribution': link_types
    },
    'analysis_type': 'complex_link_analysis'
}
`,
            "Analisi complessa dei link di rete"
        );
        
        const complexAnalysisTime = Date.now() - complexAnalysisStart;
        
        if (linkAnalysisResult.success) {
            console.log(`✅ Analisi complessa completata in ${linkAnalysisResult.executionTimeMs}ms (totale: ${complexAnalysisTime}ms)`);
            console.log("📊 Risultati analisi link:");
            console.log(JSON.stringify(linkAnalysisResult.result, null, 2));
        } else {
            console.log(`❌ Errore analisi complessa: ${linkAnalysisResult.error}`);
        }
        
        // 6. Test performance - Esecuzione multipla rapida
        console.log("\n📋 Step 6: Test performance - 3 esecuzioni consecutive...");
        
        for (let i = 1; i <= 3; i++) {
            const quickStart = Date.now();
            
            const quickResult = await projectManager.executeProjectAnalysis(
                'campoleone',
                `
# Test performance veloce ${i}
result = {
    'test_number': ${i},
    'timestamp': time.time(),
    'node_count': visum.Net.Nodes.Count,
    'quick_calculation': ${i} * visum.Net.Links.Count,
    'analysis_type': 'performance_test'
}
`,
                `Performance test ${i}`
            );
            
            const quickTime = Date.now() - quickStart;
            
            if (quickResult.success) {
                console.log(`⚡ Test ${i}: ${quickResult.executionTimeMs}ms (totale: ${quickTime}ms)`);
            } else {
                console.log(`❌ Test ${i} fallito: ${quickResult.error}`);
            }
        }
        
        console.log("\n🎉 Test completato! L'istanza Campoleone rimane attiva per ulteriori comandi.");
        console.log("💡 Per terminare l'istanza: projectManager.shutdownProjectInstance('campoleone')");
        
    } catch (error) {
        console.error(`❌ Errore durante il test: ${error.message}`);
    }
}

// Avvia il test
testCampoleoneInstance().catch(console.error);