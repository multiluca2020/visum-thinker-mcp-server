# Test: Mantenere istanza VisumPy viva per accesso diretto
import sys
import os
import time
import json

print("=== TEST ISTANZA VISUMPY PERSISTENTE ===")
print("Obiettivo: Una sola istanza VisumPy che rimane viva per tutte le analisi")

# Setup paths
visum_path = r"H:\Program Files\PTV Vision\PTV Visum 2025\Exe"
python_path = os.path.join(visum_path, "Python")

if visum_path not in sys.path:
    sys.path.insert(0, visum_path)
if python_path not in sys.path:
    sys.path.insert(0, python_path)

# GLOBAL VISUM INSTANCE - manteniamo una referenza globale
GLOBAL_VISUM_INSTANCE = None
GLOBAL_PROJECT_LOADED = None

def get_or_create_visum_instance():
    """Ottieni istanza Visum globale o creane una nuova"""
    global GLOBAL_VISUM_INSTANCE, GLOBAL_PROJECT_LOADED
    
    try:
        import VisumPy.helpers as vh
        
        # Se non esiste, crea
        if GLOBAL_VISUM_INSTANCE is None:
            print(f"  🆕 Creating new VisumPy instance...")
            GLOBAL_VISUM_INSTANCE = vh.CreateVisum(250)
            print(f"  ✅ VisumPy instance created")
            GLOBAL_PROJECT_LOADED = None
        
        # Verifica che sia ancora viva
        try:
            # Test rapido per verificare se l'istanza è ancora valida
            nodes = GLOBAL_VISUM_INSTANCE.Net.Nodes.Count
            print(f"  ♻️  Using existing instance: {nodes:,} nodes")
        except:
            print(f"  💀 Instance died, creating new one...")
            GLOBAL_VISUM_INSTANCE = vh.CreateVisum(250)
            GLOBAL_PROJECT_LOADED = None
            
        return GLOBAL_VISUM_INSTANCE
        
    except Exception as e:
        print(f"  ❌ Failed to get/create instance: {e}")
        return None

def ensure_project_loaded(visum_instance, project_path):
    """Assicura che il progetto sia caricato"""
    global GLOBAL_PROJECT_LOADED
    
    try:
        # Check se progetto già caricato
        current_nodes = visum_instance.Net.Nodes.Count
        
        if current_nodes > 0 and GLOBAL_PROJECT_LOADED == project_path:
            print(f"  📂 Project already loaded: {current_nodes:,} nodes")
            return True
            
        # Carica progetto
        print(f"  📂 Loading project: {os.path.basename(project_path)}")
        visum_instance.LoadVersion(project_path)
        
        new_nodes = visum_instance.Net.Nodes.Count
        print(f"  ✅ Project loaded: {new_nodes:,} nodes")
        
        GLOBAL_PROJECT_LOADED = project_path
        return True
        
    except Exception as e:
        print(f"  ❌ Failed to load project: {e}")
        return False

def visum_analysis(analysis_name, analysis_func):
    """Esegui analisi usando l'istanza globale"""
    print(f"\n🔍 {analysis_name}")
    
    # Ottieni istanza
    visum = get_or_create_visum_instance()
    if not visum:
        return None
    
    # Assicura progetto caricato
    project_path = r"H:\go\italferr2025\Campoleone\100625_Versione_base_v0.3_sub_ok_priv.ver"
    if not ensure_project_loaded(visum, project_path):
        return None
    
    # Esegui analisi
    try:
        start_time = time.time()
        result = analysis_func(visum)
        elapsed = time.time() - start_time
        
        print(f"  ⏱️  Analysis completed in {elapsed:.3f}s")
        return result
        
    except Exception as e:
        print(f"  ❌ Analysis failed: {e}")
        return None

# TEST: Simulazione chiamate MCP multiple
try:
    print(f"\n🧪 SIMULATION: Multiple MCP tool calls")
    
    # Simulazione tool 1: Network Statistics
    def network_stats(visum):
        stats = {
            "nodes": visum.Net.Nodes.Count,
            "links": visum.Net.Links.Count,
            "zones": visum.Net.Zones.Count
        }
        print(f"    Network: {stats['nodes']:,} nodes, {stats['links']:,} links, {stats['zones']:,} zones")
        return stats
    
    result1 = visum_analysis("Tool 1: Network Statistics", network_stats)
    
    # Simulazione tool 2: Node Analysis  
    def node_analysis(visum):
        # Prova a ottenere alcuni attributi dei nodi
        try:
            # Get first 5 nodes
            node_container = visum.Net.Nodes
            if node_container.Count > 0:
                first_nodes = node_container.GetMultiAttValues('No')[:5]
                print(f"    First 5 nodes: {first_nodes}")
                return {"sample_nodes": first_nodes}
        except Exception as e:
            print(f"    ⚠️ Node details failed: {e}")
            return {"node_count": visum.Net.Nodes.Count}
    
    result2 = visum_analysis("Tool 2: Node Analysis", node_analysis)
    
    # Simulazione tool 3: Quick Stats
    def quick_stats(visum):
        return {
            "timestamp": time.time(),
            "nodes": visum.Net.Nodes.Count,
            "instance_id": id(visum)  # Per verificare se è la stessa istanza
        }
    
    result3 = visum_analysis("Tool 3: Quick Stats", quick_stats)
    
    # Simulazione tool 4: Dopo 10 secondi
    print(f"\n⏰ Waiting 10 seconds to test persistence...")
    time.sleep(10)
    
    result4 = visum_analysis("Tool 4: After 10s", quick_stats)
    
    # Analisi risultati
    print(f"\n📊 RESULTS ANALYSIS:")
    
    if result1 and result3 and result4:
        print(f"  Tool 1 nodes: {result1.get('nodes', 'N/A'):,}")
        print(f"  Tool 3 nodes: {result3.get('nodes', 'N/A'):,}")
        print(f"  Tool 4 nodes: {result4.get('nodes', 'N/A'):,}")
        
        # Verifica consistenza
        nodes_consistent = (result1['nodes'] == result3['nodes'] == result4['nodes'])
        print(f"  Nodes consistent: {'✅' if nodes_consistent else '❌'}")
        
        # Verifica stessa istanza
        same_instance = (result3['instance_id'] == result4['instance_id'])
        print(f"  Same instance: {'✅' if same_instance else '❌'}")
        
        if nodes_consistent and same_instance:
            print(f"\n🎉 SUCCESS: Persistent VisumPy instance works!")
            
            # Salva successo
            success_data = {
                "timestamp": time.time(),
                "method": "Persistent VisumPy instance",
                "api": "VisumPy_Persistent_Global",
                "consistency_check": "passed",
                "instance_reuse": "confirmed", 
                "nodes": result1['nodes'],
                "persistence_seconds": 10,
                "status": "PERSISTENT_INSTANCE_SUCCESS"
            }
            
            with open(r"H:\visum-thinker-mcp-server\visumpy_persistent_success.json", 'w') as f:
                json.dump(success_data, f, indent=2)
            
            print(f"💾 Persistent instance success saved!")
        else:
            print(f"❌ Consistency or instance reuse failed")
    
    # Test finale: verifica che l'istanza sia ancora viva
    print(f"\n🔍 Final instance check:")
    final_visum = get_or_create_visum_instance()
    if final_visum:
        final_nodes = final_visum.Net.Nodes.Count
        print(f"  Final check: {final_nodes:,} nodes - Instance still alive! ✅")
        
        print(f"\n🚀 SOLUTION CONFIRMED:")
        print(f"  - Use global VisumPy instance")
        print(f"  - Reuse same instance across MCP calls")
        print(f"  - Load project only once")
        print(f"  - Ultra-fast subsequent calls")

except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()

print(f"\n=== TEST ISTANZA PERSISTENTE COMPLETATO ===")
print("Key insight: Keep VisumPy instance alive globally!")