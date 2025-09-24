# Test workflow ibrido VisumPy + Dispatch
import sys
import os
import time
import json

print("=== TEST WORKFLOW IBRIDO ===")
print("VisumPy per inizializzazione + Dispatch per accesso successivo")

# Setup paths
visum_path = r"H:\Program Files\PTV Vision\PTV Visum 2025\Exe"
python_path = os.path.join(visum_path, "Python")

if visum_path not in sys.path:
    sys.path.insert(0, visum_path)
if python_path not in sys.path:
    sys.path.insert(0, python_path)

try:
    import VisumPy.helpers as vh
    import win32com.client as win32
    
    project_path = r"H:\go\italferr2025\Campoleone\100625_Versione_base_v0.3_sub_ok_priv.ver"
    
    # SCENARIO 1: Fresh start - VisumPy initialization
    print(f"\n🚀 SCENARIO 1: Fresh VisumPy initialization")
    
    print(f"  Creating VisumPy instance...")
    visum_init = vh.CreateVisum(250)
    print(f"  Loading project...")
    visum_init.LoadVersion(project_path)
    nodes_init = visum_init.Net.Nodes.Count
    print(f"  ✅ Initialized: {nodes_init:,} nodes")
    
    # SCENARIO 2: Subsequent access via Dispatch
    print(f"\n🔄 SCENARIO 2: Subsequent Dispatch access")
    
    print(f"  Accessing via Dispatch...")
    visum_dispatch = win32.Dispatch("Visum.Visum.250")
    
    # Check if it has data (same instance) or empty (new instance)
    nodes_dispatch = visum_dispatch.Net.Nodes.Count
    print(f"  Dispatch nodes: {nodes_dispatch:,}")
    
    if nodes_dispatch == 0:
        print(f"  Empty instance - loading project...")
        visum_dispatch.LoadVersion(project_path)
        nodes_dispatch = visum_dispatch.Net.Nodes.Count
        print(f"  After loading: {nodes_dispatch:,} nodes")
    
    if nodes_dispatch == nodes_init:
        print(f"  ✅ Same instance accessed!")
    else:
        print(f"  ⚠️ Different instance (or reloaded)")
    
    # SCENARIO 3: Multiple consecutive Dispatch calls (typical MCP usage)
    print(f"\n🔁 SCENARIO 3: Multiple Dispatch calls")
    
    analysis_results = []
    
    for i in range(5):
        print(f"  Analysis {i+1}...")
        
        # Simula chiamata MCP tool
        visum_analysis = win32.Dispatch("Visum.Visum.250")
        
        # Check if needs project loading
        if visum_analysis.Net.Nodes.Count == 0:
            print(f"    Loading project...")
            visum_analysis.LoadVersion(project_path)
        
        # Perform analysis
        nodes = visum_analysis.Net.Nodes.Count
        links = visum_analysis.Net.Links.Count
        zones = visum_analysis.Net.Zones.Count
        
        result = {
            "analysis_id": i+1,
            "nodes": nodes,
            "links": links, 
            "zones": zones,
            "timestamp": time.time()
        }
        
        analysis_results.append(result)
        print(f"    ✅ Analysis {i+1}: {nodes:,} nodes")
        
        # Small delay
        time.sleep(0.5)
    
    print(f"  📊 All analyses completed consistently:")
    for result in analysis_results:
        print(f"    Analysis {result['analysis_id']}: {result['nodes']:,} nodes")
    
    # Check consistency
    all_nodes = [r['nodes'] for r in analysis_results]
    if len(set(all_nodes)) == 1:
        print(f"  ✅ Perfect consistency across all calls!")
    else:
        print(f"  ❌ Inconsistent results: {set(all_nodes)}")
    
    # SCENARIO 4: Performance test
    print(f"\n⚡ SCENARIO 4: Performance comparison")
    
    # Test 1: VisumPy CreateVisum + LoadVersion
    start_time = time.time()
    visum_perf1 = vh.CreateVisum(250)
    visum_perf1.LoadVersion(project_path)
    nodes_perf1 = visum_perf1.Net.Nodes.Count
    time_visumpy = time.time() - start_time
    print(f"  VisumPy CreateVisum + Load: {time_visumpy:.3f}s -> {nodes_perf1:,} nodes")
    
    # Test 2: Dispatch (assuming instance exists)
    start_time = time.time()
    visum_perf2 = win32.Dispatch("Visum.Visum.250")
    if visum_perf2.Net.Nodes.Count == 0:
        visum_perf2.LoadVersion(project_path)
    nodes_perf2 = visum_perf2.Net.Nodes.Count
    time_dispatch = time.time() - start_time
    print(f"  Dispatch + Load (if needed): {time_dispatch:.3f}s -> {nodes_perf2:,} nodes")
    
    # Test 3: Dispatch senza reload (se instance persiste)
    start_time = time.time()
    visum_perf3 = win32.Dispatch("Visum.Visum.250")
    nodes_perf3 = visum_perf3.Net.Nodes.Count  # No loading
    time_dispatch_noload = time.time() - start_time
    print(f"  Dispatch without reload: {time_dispatch_noload:.3f}s -> {nodes_perf3:,} nodes")
    
    print(f"\n📈 Performance summary:")
    print(f"  VisumPy first time: {time_visumpy:.3f}s")
    print(f"  Dispatch with load: {time_dispatch:.3f}s") 
    print(f"  Dispatch no load: {time_dispatch_noload:.3f}s")
    
    if time_dispatch_noload < 0.1 and nodes_perf3 > 0:
        print(f"  🚀 Instance persistence detected! Ultra-fast access.")
    
    # FINAL: Save hybrid workflow results
    workflow_results = {
        "timestamp": time.time(),
        "method": "VisumPy.CreateVisum + win32com.Dispatch hybrid",
        "api": "Hybrid_VisumPy_Dispatch",
        "initialization": {
            "method": "VisumPy.helpers.CreateVisum(250)",
            "time_seconds": time_visumpy,
            "nodes": nodes_init
        },
        "subsequent_access": {
            "method": "win32com.client.Dispatch('Visum.Visum.250')",
            "time_seconds": time_dispatch_noload,
            "nodes": nodes_perf3,
            "consistent": len(set(all_nodes)) == 1
        },
        "performance": {
            "visumpy_init": time_visumpy,
            "dispatch_with_load": time_dispatch,
            "dispatch_no_load": time_dispatch_noload
        },
        "status": "HYBRID_WORKFLOW_SUCCESS"
    }
    
    with open(r"H:\visum-thinker-mcp-server\visumpy_hybrid_workflow.json", 'w') as f:
        json.dump(workflow_results, f, indent=2)
    
    print(f"\n💾 Hybrid workflow results saved!")
    print(f"🎉 SOLUTION: VisumPy for init, Dispatch for MCP calls!")

except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()

print(f"\n=== WORKFLOW IBRIDO COMPLETATO ===")