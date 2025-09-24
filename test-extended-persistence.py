# ORCHESTRATORE: Esegue tutti i test in sequenza per testare la persistenza
# Simula chiamate MCP multiple separate nel tempo

import subprocess
import time
import json
import os

print("=== TEST ESTESO PERSISTENZA DIRECTVISUMMANAGER ===")
print("Scenario: 3 script separati che dovrebbero condividere istanza VisumPy")

PYTHON_EXE = r"H:\Program Files\PTV Vision\PTV Visum 2025\Exe\Python\python.exe"
BASE_DIR = r"H:\visum-thinker-mcp-server"

def run_script(script_name, description, wait_after=0):
    """Esegue uno script Python e restituisce il risultato"""
    print(f"\n{'='*60}")
    print(f"🚀 EXECUTING: {description}")
    print(f"Script: {script_name}")
    print(f"Time: {time.strftime('%H:%M:%S')}")
    print(f"{'='*60}")
    
    script_path = os.path.join(BASE_DIR, script_name)
    
    try:
        # Esegui script
        start_time = time.time()
        result = subprocess.run([PYTHON_EXE, script_path], 
                              capture_output=True, 
                              text=True, 
                              timeout=60)  # 60 second timeout
        execution_time = time.time() - start_time
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)
        
        print(f"\n📊 Execution completed:")
        print(f"   Return code: {result.returncode}")
        print(f"   Execution time: {execution_time:.3f}s")
        
        success = result.returncode == 0
        print(f"   Status: {'✅ SUCCESS' if success else '❌ FAILED'}")
        
        # Attendi se richiesto
        if wait_after > 0:
            print(f"\n⏳ Waiting {wait_after} seconds before next script...")
            time.sleep(wait_after)
        
        return {
            "script": script_name,
            "success": success,
            "return_code": result.returncode,
            "execution_time": execution_time,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
        
    except subprocess.TimeoutExpired:
        print(f"❌ TIMEOUT: Script exceeded 60 seconds")
        return {
            "script": script_name,
            "success": False,
            "error": "timeout",
            "execution_time": 60
        }
    except Exception as e:
        print(f"❌ ERROR executing script: {e}")
        return {
            "script": script_name,
            "success": False,
            "error": str(e)
        }

def analyze_results():
    """Analizza i risultati dei 3 script per verificare persistenza"""
    print(f"\n{'='*60}")
    print(f"📊 ANALYZING PERSISTENCE RESULTS")
    print(f"{'='*60}")
    
    results_analysis = {
        "timestamp": time.time(),
        "test_type": "DirectVisumManager_Persistence_Test"
    }
    
    # Script 1 results
    status_file = os.path.join(BASE_DIR, "visum_instance_status.json")
    if os.path.exists(status_file):
        with open(status_file, 'r') as f:
            script1_data = json.load(f)
        
        results_analysis["script1"] = {
            "found_status": True,
            "initialized": script1_data.get("initialized", False),
            "nodes": script1_data.get("network_summary", {}).get("nodes", 0),
            "instance_id": script1_data.get("instance_id"),
            "init_time": script1_data.get("initialization_time", 0)
        }
        
        print(f"📋 Script 1 Analysis:")
        print(f"   Initialized: {results_analysis['script1']['initialized']}")
        print(f"   Nodes: {results_analysis['script1']['nodes']:,}")
        print(f"   Instance ID: {results_analysis['script1']['instance_id']}")
        print(f"   Init time: {results_analysis['script1']['init_time']:.3f}s")
    else:
        results_analysis["script1"] = {"found_status": False}
        print(f"❌ Script 1 status not found")
    
    # Script 2 results
    script2_file = os.path.join(BASE_DIR, "script2_results.json")
    if os.path.exists(script2_file):
        with open(script2_file, 'r') as f:
            script2_data = json.load(f)
        
        results_analysis["script2"] = {
            "found_results": True,
            "completed": script2_data.get("script2_completed", False),
            "instance_reused": script2_data.get("instance_reused", False),
            "current_instance_id": script2_data.get("current_instance_id"),
            "nodes": script2_data.get("basic_counts", {}).get("nodes", 0),
            "analysis_time": script2_data.get("analysis_time_ms", 0)
        }
        
        print(f"\n📋 Script 2 Analysis:")
        print(f"   Completed: {results_analysis['script2']['completed']}")
        print(f"   Instance reused: {results_analysis['script2']['instance_reused']}")
        print(f"   Instance ID: {results_analysis['script2']['current_instance_id']}")
        print(f"   Nodes: {results_analysis['script2']['nodes']:,}")
        print(f"   Analysis time: {results_analysis['script2']['analysis_time']:.3f}ms")
    else:
        results_analysis["script2"] = {"found_results": False}
        print(f"❌ Script 2 results not found")
    
    # Script 3 results
    script3_file = os.path.join(BASE_DIR, "script3_results.json")
    if os.path.exists(script3_file):
        with open(script3_file, 'r') as f:
            script3_data = json.load(f)
        
        adv_analysis = script3_data.get("advanced_node_analysis", {})
        perf_test = script3_data.get("performance_test", {})
        
        results_analysis["script3"] = {
            "found_results": True,
            "current_instance_id": script3_data.get("current_instance_id"),
            "nodes_analyzed": adv_analysis.get("total_nodes", 0),
            "analysis_time": adv_analysis.get("analysis_time_ms", 0),
            "performance_avg_ms": perf_test.get("average_time_ms", 0),
            "data_consistency": perf_test.get("data_consistency", False)
        }
        
        print(f"\n📋 Script 3 Analysis:")
        print(f"   Instance ID: {results_analysis['script3']['current_instance_id']}")
        print(f"   Nodes analyzed: {results_analysis['script3']['nodes_analyzed']:,}")
        print(f"   Analysis time: {results_analysis['script3']['analysis_time']:.3f}ms")
        print(f"   Performance avg: {results_analysis['script3']['performance_avg_ms']:.3f}ms")
        print(f"   Data consistency: {results_analysis['script3']['data_consistency']}")
    else:
        results_analysis["script3"] = {"found_results": False}
        print(f"❌ Script 3 results not found")
    
    # OVERALL ANALYSIS
    print(f"\n🎯 OVERALL PERSISTENCE ANALYSIS:")
    
    # Check instance ID consistency
    script1_id = results_analysis.get("script1", {}).get("instance_id")
    script2_id = results_analysis.get("script2", {}).get("current_instance_id")
    script3_id = results_analysis.get("script3", {}).get("current_instance_id")
    
    instance_ids = [id for id in [script1_id, script2_id, script3_id] if id is not None]
    
    if len(instance_ids) > 0:
        same_instance = len(set(instance_ids)) == 1
        results_analysis["instance_persistence"] = {
            "same_instance_across_scripts": same_instance,
            "unique_instances": len(set(instance_ids)),
            "instance_ids": instance_ids
        }
        
        print(f"   Instance persistence: {'✅ SAME INSTANCE' if same_instance else '❌ DIFFERENT INSTANCES'}")
        print(f"   Unique instances: {len(set(instance_ids))}")
        print(f"   Instance IDs: {instance_ids}")
    else:
        results_analysis["instance_persistence"] = {"error": "No instance IDs found"}
        print(f"   ❌ No instance IDs found to compare")
    
    # Check data consistency
    script1_nodes = results_analysis.get("script1", {}).get("nodes", 0)
    script2_nodes = results_analysis.get("script2", {}).get("nodes", 0)
    script3_nodes = results_analysis.get("script3", {}).get("nodes_analyzed", 0)
    
    node_counts = [nodes for nodes in [script1_nodes, script2_nodes, script3_nodes] if nodes > 0]
    
    if len(node_counts) > 0:
        data_consistent = len(set(node_counts)) == 1
        results_analysis["data_consistency"] = {
            "consistent_across_scripts": data_consistent,
            "node_counts": node_counts
        }
        
        print(f"   Data consistency: {'✅ CONSISTENT' if data_consistent else '❌ INCONSISTENT'}")
        print(f"   Node counts: {node_counts}")
    else:
        results_analysis["data_consistency"] = {"error": "No node counts found"}
        print(f"   ❌ No node counts found to compare")
    
    # Performance analysis
    script2_time = results_analysis.get("script2", {}).get("analysis_time", 0)
    script3_time = results_analysis.get("script3", {}).get("analysis_time", 0)
    script3_perf = results_analysis.get("script3", {}).get("performance_avg_ms", 0)
    
    if script2_time > 0 or script3_time > 0 or script3_perf > 0:
        results_analysis["performance_analysis"] = {
            "script2_analysis_ms": script2_time,
            "script3_analysis_ms": script3_time,
            "script3_performance_avg_ms": script3_perf,
            "ultra_fast_calls": script3_perf < 10  # Less than 10ms is ultra-fast
        }
        
        print(f"   Performance:")
        if script2_time > 0:
            print(f"     Script 2 analysis: {script2_time:.3f}ms")
        if script3_time > 0:
            print(f"     Script 3 analysis: {script3_time:.3f}ms")
        if script3_perf > 0:
            print(f"     Script 3 avg calls: {script3_perf:.3f}ms {'✅ ULTRA-FAST' if script3_perf < 10 else '⚠️ SLOW'}")
    
    # Save complete analysis
    with open(os.path.join(BASE_DIR, "persistence_test_analysis.json"), 'w') as f:
        json.dump(results_analysis, f, indent=2)
    
    print(f"\n💾 Complete analysis saved to persistence_test_analysis.json")
    
    return results_analysis

# MAIN ORCHESTRATOR EXECUTION
try:
    print(f"🎬 Starting extended DirectVisumManager persistence test")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Cleanup previous results
    for filename in ["visum_instance_status.json", "script2_results.json", "script3_results.json"]:
        filepath = os.path.join(BASE_DIR, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"🗑️ Removed previous result: {filename}")
    
    # Execute scripts in sequence
    script_results = []
    
    # Script 1: Initialization
    result1 = run_script("test-script1-init.py", "Script 1 - Initialize DirectVisumManager", wait_after=2)
    script_results.append(result1)
    
    # Script 2: Network Analysis (should reuse instance)
    result2 = run_script("test-script2-network.py", "Script 2 - Network Analysis (test reuse)", wait_after=2)
    script_results.append(result2)
    
    # Script 3: Advanced Analysis (should reuse instance)  
    result3 = run_script("test-script3-advanced.py", "Script 3 - Advanced Node Analysis (test reuse)", wait_after=0)
    script_results.append(result3)
    
    # Analyze results
    analysis = analyze_results()
    
    # Final summary
    print(f"\n{'='*60}")
    print(f"🏁 FINAL TEST SUMMARY")
    print(f"{'='*60}")
    
    successful_scripts = sum(1 for r in script_results if r.get("success", False))
    print(f"📊 Scripts executed: {len(script_results)}")
    print(f"✅ Successful: {successful_scripts}")
    print(f"❌ Failed: {len(script_results) - successful_scripts}")
    
    if successful_scripts == 3:
        print(f"🎉 ALL SCRIPTS SUCCESSFUL!")
        
        # Check key persistence indicators
        instance_persistent = analysis.get("instance_persistence", {}).get("same_instance_across_scripts", False)
        data_consistent = analysis.get("data_consistency", {}).get("consistent_across_scripts", False)
        
        print(f"🔍 Persistence Results:")
        print(f"   Instance persistence: {'✅ SUCCESS' if instance_persistent else '❌ FAILED'}")
        print(f"   Data consistency: {'✅ SUCCESS' if data_consistent else '❌ FAILED'}")
        
        if instance_persistent and data_consistent:
            print(f"\n🚀 PERSISTENCE TEST: ✅ COMPLETE SUCCESS!")
            print(f"DirectVisumManager successfully maintains same instance across multiple scripts!")
        else:
            print(f"\n⚠️ PERSISTENCE TEST: ❌ PARTIAL SUCCESS")
            print(f"Instance persistence works but some issues detected")
    else:
        print(f"❌ Some scripts failed - persistence test incomplete")
    
    # Save orchestrator results
    orchestrator_results = {
        "test_timestamp": time.time(),
        "test_type": "Extended DirectVisumManager Persistence Test",
        "script_results": script_results,
        "analysis": analysis,
        "summary": {
            "total_scripts": len(script_results),
            "successful_scripts": successful_scripts,
            "all_successful": successful_scripts == 3,
            "instance_persistent": analysis.get("instance_persistence", {}).get("same_instance_across_scripts", False),
            "data_consistent": analysis.get("data_consistency", {}).get("consistent_across_scripts", False)
        }
    }
    
    with open(os.path.join(BASE_DIR, "orchestrator_results.json"), 'w') as f:
        json.dump(orchestrator_results, f, indent=2)
    
    print(f"\n💾 Complete orchestrator results saved to orchestrator_results.json")

except Exception as e:
    print(f"❌ Orchestrator error: {e}")
    import traceback
    traceback.print_exc()

print(f"\n=== ORCHESTRATOR TERMINATO ===")
print(f"Test esteso di persistenza DirectVisumManager completato!")
print(f"Controlla i file JSON generati per i risultati dettagliati.")