# SCRIPT 3: Test persistenza istanza - Analisi nodi avanzata
# Questo script deve accedere all'istanza esistente per analisi dettagliata

import sys
import os
import time
import json

print("=== SCRIPT 3: ANALISI NODI AVANZATA ===")

# Setup VisumPy paths
visum_path = r"H:\Program Files\PTV Vision\PTV Visum 2025\Exe"
python_path = os.path.join(visum_path, "Python")

if visum_path not in sys.path:
    sys.path.insert(0, visum_path)
if python_path not in sys.path:
    sys.path.insert(0, python_path)

# Stesso DirectVisumManager - test finale di persistenza
class DirectVisumManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.visum_instance = None
            cls._instance.project_loaded = None
            cls._instance.initialization_time = None
            cls._instance.creation_timestamp = time.time()
        return cls._instance
        
    def initialize_visum(self):
        """Initialize VisumPy instance once"""
        if self.visum_instance is None:
            try:
                init_start = time.time()
                import VisumPy.helpers as vh
                
                print("🆕 Creating NEW VisumPy instance (previous instances not in memory)...")
                self.visum_instance = vh.CreateVisum(250)
                
                # Load default project
                project_path = r"H:\go\italferr2025\Campoleone\100625_Versione_base_v0.3_sub_ok_priv.ver"
                print(f"📂 Loading project: {os.path.basename(project_path)}")
                self.visum_instance.LoadVersion(project_path)
                self.project_loaded = project_path
                
                self.initialization_time = time.time() - init_start
                
                nodes = self.visum_instance.Net.Nodes.Count
                print(f"✅ NEW instance initialized in {self.initialization_time:.3f}s: {nodes:,} nodes")
                return True
                
            except Exception as e:
                print(f"❌ Initialization failed: {e}")
                import traceback
                traceback.print_exc()
                return False
        else:
            print("♻️  REUSING existing VisumPy instance from memory!")
            return True
    
    def execute_advanced_node_analysis(self):
        """Execute advanced node analysis"""
        if not self.initialize_visum():
            return {"error": "Failed to initialize Visum"}
        
        try:
            analysis_start = time.time()
            
            print("🔬 Executing advanced node analysis...")
            
            node_container = self.visum_instance.Net.Nodes
            total_nodes = node_container.Count
            
            advanced_analysis = {
                "total_nodes": total_nodes,
                "analysis_timestamp": time.time(),
                "script": "script3_advanced_nodes"
            }
            
            if total_nodes > 0:
                print(f"🔍 Analyzing {total_nodes:,} nodes...")
                
                # Get detailed node sample
                try:
                    sample_size = min(20, total_nodes)
                    node_ids = node_container.GetMultiAttValues('No')[:sample_size]
                    advanced_analysis["detailed_sample"] = node_ids
                    advanced_analysis["sample_size"] = len(node_ids)
                    print(f"📊 Got {len(node_ids)} node IDs for detailed analysis")
                    
                    # Try to get node positions if available
                    try:
                        x_coords = node_container.GetMultiAttValues('XCoord')[:sample_size]
                        y_coords = node_container.GetMultiAttValues('YCoord')[:sample_size]
                        
                        # Create coordinate pairs
                        coordinates = list(zip(node_ids, x_coords, y_coords))
                        advanced_analysis["node_coordinates"] = coordinates[:5]  # First 5 for brevity
                        
                        print(f"📍 Sample coordinates: {coordinates[:3]}")
                        
                    except Exception as coord_e:
                        advanced_analysis["coordinate_error"] = str(coord_e)
                        print(f"⚠️ Could not get coordinates: {coord_e}")
                        
                except Exception as sample_e:
                    advanced_analysis["sample_error"] = str(sample_e)
                    print(f"⚠️ Could not get node sample: {sample_e}")
                
                # Try to get network statistics
                try:
                    link_container = self.visum_instance.Net.Links
                    total_links = link_container.Count
                    
                    advanced_analysis["network_connectivity"] = {
                        "nodes": total_nodes,
                        "links": total_links,
                        "avg_connections_per_node": round(total_links * 2 / total_nodes, 2) if total_nodes > 0 else 0
                    }
                    
                    print(f"🔗 Network connectivity: {total_links:,} links, avg {advanced_analysis['network_connectivity']['avg_connections_per_node']} connections/node")
                    
                except Exception as link_e:
                    advanced_analysis["connectivity_error"] = str(link_e)
                    print(f"⚠️ Could not analyze connectivity: {link_e}")
            
            analysis_time = time.time() - analysis_start
            advanced_analysis["analysis_time_ms"] = round(analysis_time * 1000, 3)
            
            print(f"✅ Advanced node analysis completed in {analysis_time*1000:.3f}ms")
            
            return advanced_analysis
            
        except Exception as e:
            error_result = {
                "error": f"Advanced node analysis failed: {str(e)}",
                "script": "script3_advanced_nodes"
            }
            print(f"❌ Advanced analysis failed: {e}")
            return error_result
    
    def performance_test(self, iterations=5):
        """Test performance with multiple rapid calls"""
        if not self.initialize_visum():
            return {"error": "Failed to initialize Visum"}
        
        print(f"⚡ Performance test: {iterations} rapid calls...")
        
        performance_results = []
        
        for i in range(iterations):
            start_time = time.time()
            
            try:
                nodes = self.visum_instance.Net.Nodes.Count
                links = self.visum_instance.Net.Links.Count
                call_time = time.time() - start_time
                
                performance_results.append({
                    "iteration": i + 1,
                    "time_ms": round(call_time * 1000, 3),
                    "nodes": nodes,
                    "links": links
                })
                
                print(f"  Call {i+1}: {call_time*1000:.3f}ms - {nodes:,} nodes")
                
            except Exception as e:
                performance_results.append({
                    "iteration": i + 1,
                    "error": str(e)
                })
        
        # Calculate averages
        successful_calls = [r for r in performance_results if "error" not in r]
        if successful_calls:
            avg_time = sum(r["time_ms"] for r in successful_calls) / len(successful_calls)
            consistency_check = len(set(r["nodes"] for r in successful_calls)) == 1
            
            performance_summary = {
                "total_iterations": iterations,
                "successful_calls": len(successful_calls),
                "average_time_ms": round(avg_time, 3),
                "min_time_ms": min(r["time_ms"] for r in successful_calls),
                "max_time_ms": max(r["time_ms"] for r in successful_calls),
                "data_consistency": consistency_check,
                "results": performance_results
            }
            
            print(f"📈 Performance summary: {avg_time:.3f}ms avg, consistency: {'✅' if consistency_check else '❌'}")
            return performance_summary
        
        return {"error": "All performance test calls failed", "results": performance_results}

# MAIN SCRIPT 3 EXECUTION  
try:
    print(f"⏰ Script 3 started at: {time.strftime('%H:%M:%S')}")
    
    # Check previous scripts status
    for script_num, filename in [(1, "visum_instance_status.json"), (2, "script2_results.json")]:
        filepath = f"H:\\visum-thinker-mcp-server\\{filename}"
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                prev_status = json.load(f)
            print(f"📋 Script {script_num} status found:")
            if script_num == 1:
                print(f"   Nodes: {prev_status.get('network_summary', {}).get('nodes', 'Unknown'):,}")
                print(f"   Instance ID: {prev_status.get('instance_id', 'Unknown')}")
            else:
                print(f"   Completed: {prev_status.get('script2_completed', 'Unknown')}")
                print(f"   Instance reused: {prev_status.get('instance_reused', 'Unknown')}")
        else:
            print(f"⚠️ No Script {script_num} status found")
    
    # Access DirectVisumManager
    print(f"\n🔄 Attempting to access DirectVisumManager for advanced analysis...")
    manager = DirectVisumManager()
    
    # Execute advanced node analysis
    print(f"\n🔬 Running advanced node analysis...")
    node_result = manager.execute_advanced_node_analysis()
    
    # Execute performance test
    print(f"\n⚡ Running performance test...")
    perf_result = manager.performance_test(5)
    
    # Combine results
    final_results = {
        "script3_timestamp": time.time(),
        "advanced_node_analysis": node_result,
        "performance_test": perf_result,
        "current_instance_id": id(manager.visum_instance) if manager.visum_instance else None
    }
    
    print(f"\n📊 SCRIPT 3 FINAL RESULTS:")
    print(f"🔬 Advanced Analysis: {node_result.get('total_nodes', 'N/A'):,} nodes analyzed")
    if "analysis_time_ms" in node_result:
        print(f"   Analysis time: {node_result['analysis_time_ms']:.3f}ms")
    
    if "average_time_ms" in perf_result:
        print(f"⚡ Performance Test: {perf_result['average_time_ms']:.3f}ms average")
        print(f"   Data consistency: {'✅' if perf_result.get('data_consistency') else '❌'}")
    
    # Save Script 3 results
    with open(r"H:\visum-thinker-mcp-server\script3_results.json", 'w') as f:
        json.dump(final_results, f, indent=2)
    
    print(f"\n✅ SCRIPT 3 COMPLETED!")
    print(f"💾 Results saved to script3_results.json")

except Exception as e:
    print(f"❌ Script 3 error: {e}")
    import traceback
    traceback.print_exc()

print(f"=== SCRIPT 3 TERMINATO ===")
print(f"Tutti i test di persistenza completati!")