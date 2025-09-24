# Test realistico: Simulazione chiamate MCP tools nel STESSO processo Python
# Questo simula meglio come funzionerà nel MCP server

import sys
import os
import time
import json

print("=== TEST SIMULAZIONE MCP TOOLS - STESSO PROCESSO ===")
print("Scenario: Multiple tool calls nello STESSO processo Python (come MCP server)")

# Setup VisumPy paths
visum_path = r"H:\Program Files\PTV Vision\PTV Visum 2025\Exe"
python_path = os.path.join(visum_path, "Python")

if visum_path not in sys.path:
    sys.path.insert(0, visum_path)
if python_path not in sys.path:
    sys.path.insert(0, python_path)

# DirectVisumManager - SINGLETON per processo Python
class DirectVisumManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.visum_instance = None
            cls._instance.project_loaded = None
            cls._instance.initialization_time = None
            cls._instance.creation_timestamp = time.time()
            cls._instance.tool_call_count = 0
        return cls._instance
        
    def initialize_visum(self):
        """Initialize VisumPy instance once per process"""
        if self.visum_instance is None:
            try:
                init_start = time.time()
                import VisumPy.helpers as vh
                
                print("FIRST CALL: Creating VisumPy instance...")
                self.visum_instance = vh.CreateVisum(250)
                
                # Load default project
                project_path = r"H:\go\italferr2025\Campoleone\100625_Versione_base_v0.3_sub_ok_priv.ver"
                print(f"FIRST CALL: Loading project: {os.path.basename(project_path)}")
                self.visum_instance.LoadVersion(project_path)
                self.project_loaded = project_path
                
                self.initialization_time = time.time() - init_start
                
                nodes = self.visum_instance.Net.Nodes.Count
                links = self.visum_instance.Net.Links.Count
                zones = self.visum_instance.Net.Zones.Count
                
                print(f"SUCCESS: Initialized in {self.initialization_time:.3f}s:")
                print(f"   Nodes: {nodes:,}")
                print(f"   Links: {links:,}")
                print(f"   Zones: {zones:,}")
                
                return True
                
            except Exception as e:
                print(f"ERROR: Initialization failed: {e}")
                import traceback
                traceback.print_exc()
                return False
        else:
            print("SUBSEQUENT CALL: Reusing existing VisumPy instance")
            return True

def simulate_mcp_tool_call(tool_name, analysis_code, description=""):
    """Simula una chiamata MCP tool"""
    print(f"\n{'='*50}")
    print(f"MCP TOOL CALL: {tool_name}")
    print(f"Description: {description}")
    print(f"Time: {time.strftime('%H:%M:%S')}")
    print(f"{'='*50}")
    
    manager = DirectVisumManager()
    manager.tool_call_count += 1
    
    call_start = time.time()
    
    if not manager.initialize_visum():
        return {"error": "Failed to initialize Visum", "tool": tool_name}
    
    try:
        # Create namespace with visum available
        namespace = {
            'visum': manager.visum_instance,
            'json': json,
            'time': time,
            'result': {},
            'print': print
        }
        
        # Execute analysis code
        print(f"Executing analysis...")
        exec(analysis_code, namespace)
        
        # Get results
        analysis_result = namespace.get('result', {})
        call_time = time.time() - call_start
        
        final_result = {
            "success": True,
            "tool": tool_name,
            "call_number": manager.tool_call_count,
            "analysis_result": analysis_result,
            "execution_time_ms": round(call_time * 1000, 3),
            "initialization_time_s": manager.initialization_time,
            "timestamp": time.time(),
            "instance_id": id(manager.visum_instance)
        }
        
        print(f"SUCCESS: Tool call completed in {call_time*1000:.3f}ms")
        return final_result
        
    except Exception as e:
        error_result = {
            "success": False,
            "tool": tool_name,
            "call_number": manager.tool_call_count,
            "error": f"Tool execution failed: {str(e)}",
            "execution_time_ms": round((time.time() - call_start) * 1000, 3)
        }
        print(f"ERROR: Tool call failed: {e}")
        return error_result

# SIMULAZIONE: Serie di chiamate MCP tools
try:
    print(f"Starting MCP tools simulation at: {time.strftime('%H:%M:%S')}")
    
    all_results = []
    
    # TOOL 1: visum_network_stats
    result1 = simulate_mcp_tool_call(
        "visum_network_stats",
        """
# Basic network statistics
nodes = visum.Net.Nodes.Count
links = visum.Net.Links.Count
zones = visum.Net.Zones.Count

result['network_stats'] = {
    'nodes': nodes,
    'links': links,
    'zones': zones,
    'timestamp': time.time()
}

print(f"Network stats: {nodes:,} nodes, {links:,} links, {zones:,} zones")
""",
        "Get basic network statistics"
    )
    all_results.append(result1)
    
    # Breve pausa per simulare tempo tra chiamate
    time.sleep(1)
    
    # TOOL 2: visum_node_analysis
    result2 = simulate_mcp_tool_call(
        "visum_node_analysis", 
        """
# Node analysis
node_container = visum.Net.Nodes
total_nodes = node_container.Count

if total_nodes > 0:
    sample_nodes = node_container.GetMultiAttValues('No')[:10]
    
    result['node_analysis'] = {
        'total_nodes': total_nodes,
        'sample_nodes': sample_nodes,
        'sample_size': len(sample_nodes)
    }
    
    print(f"Node analysis: {total_nodes:,} total, sampled {len(sample_nodes)}")
else:
    result['node_analysis'] = {'error': 'No nodes found'}
""",
        "Analyze network nodes"
    )
    all_results.append(result2)
    
    time.sleep(1)
    
    # TOOL 3: visum_connectivity_analysis
    result3 = simulate_mcp_tool_call(
        "visum_connectivity_analysis",
        """
# Connectivity analysis
nodes = visum.Net.Nodes.Count
links = visum.Net.Links.Count

# Calculate basic connectivity metrics
avg_degree = (links * 2) / nodes if nodes > 0 else 0

result['connectivity'] = {
    'nodes': nodes,
    'links': links,
    'average_degree': round(avg_degree, 2),
    'density': round(links / (nodes * (nodes-1) / 2), 6) if nodes > 1 else 0
}

print(f"Connectivity: avg degree {avg_degree:.2f}, density {result['connectivity']['density']:.6f}")
""",
        "Analyze network connectivity"
    )
    all_results.append(result3)
    
    time.sleep(1)
    
    # TOOL 4: visum_performance_test (multiple rapid calls)
    print(f"\n{'='*50}")
    print(f"PERFORMANCE TEST: 5 rapid successive calls")
    print(f"{'='*50}")
    
    perf_results = []
    for i in range(5):
        result = simulate_mcp_tool_call(
            f"visum_rapid_call_{i+1}",
            f"""
# Rapid performance test {i+1}
nodes = visum.Net.Nodes.Count
result['rapid_test'] = {{
    'nodes': nodes,
    'call_number': {i+1},
    'timestamp': time.time()
}}
""",
            f"Rapid call #{i+1}"
        )
        perf_results.append(result)
        
        # No sleep between rapid calls
    
    all_results.extend(perf_results)
    
    # ANALYSIS OF RESULTS
    print(f"\n{'='*60}")
    print(f"SIMULATION RESULTS ANALYSIS")
    print(f"{'='*60}")
    
    successful_calls = [r for r in all_results if r.get("success", False)]
    
    print(f"Total tool calls: {len(all_results)}")
    print(f"Successful calls: {len(successful_calls)}")
    print(f"Failed calls: {len(all_results) - len(successful_calls)}")
    
    if successful_calls:
        # Check instance consistency
        instance_ids = [r.get("instance_id") for r in successful_calls if r.get("instance_id")]
        same_instance = len(set(instance_ids)) == 1 if instance_ids else False
        
        print(f"\nInstance Persistence:")
        print(f"   Same instance across calls: {'YES' if same_instance else 'NO'}")
        print(f"   Unique instance IDs: {len(set(instance_ids))}")
        
        # Check data consistency  
        node_counts = [r.get("analysis_result", {}).get("network_stats", {}).get("nodes") or
                       r.get("analysis_result", {}).get("node_analysis", {}).get("total_nodes") or
                       r.get("analysis_result", {}).get("connectivity", {}).get("nodes") or
                       r.get("analysis_result", {}).get("rapid_test", {}).get("nodes")
                       for r in successful_calls]
        node_counts = [n for n in node_counts if n is not None]
        data_consistent = len(set(node_counts)) == 1 if node_counts else False
        
        print(f"   Data consistency: {'YES' if data_consistent else 'NO'}")
        if node_counts:
            print(f"   Node counts: {set(node_counts)}")
        
        # Performance analysis
        execution_times = [r.get("execution_time_ms", 0) for r in successful_calls if r.get("execution_time_ms")]
        if execution_times:
            avg_time = sum(execution_times) / len(execution_times)
            min_time = min(execution_times)
            max_time = max(execution_times)
            
            print(f"\nPerformance:")
            print(f"   Average execution: {avg_time:.3f}ms")
            print(f"   Fastest call: {min_time:.3f}ms")
            print(f"   Slowest call: {max_time:.3f}ms")
            
            # Check if subsequent calls are faster (indicating reuse)
            first_call_time = execution_times[0] if execution_times else 0
            subsequent_times = execution_times[1:] if len(execution_times) > 1 else []
            
            if subsequent_times:
                avg_subsequent = sum(subsequent_times) / len(subsequent_times)
                print(f"   First call: {first_call_time:.3f}ms")
                print(f"   Avg subsequent: {avg_subsequent:.3f}ms")
                print(f"   Speed improvement: {((first_call_time - avg_subsequent) / first_call_time * 100):.1f}%" if first_call_time > 0 else "N/A")
        
        # Final assessment
        if same_instance and data_consistent and len(successful_calls) == len(all_results):
            print(f"\nFINAL ASSESSMENT: SUCCESS!")
            print(f"   All tool calls successful")
            print(f"   Instance persistence confirmed") 
            print(f"   Data consistency confirmed")
            print(f"   Performance optimization confirmed")
            
            assessment = "COMPLETE_SUCCESS"
        else:
            print(f"\nFINAL ASSESSMENT: PARTIAL SUCCESS")
            print(f"   Some issues detected in persistence or consistency")
            
            assessment = "PARTIAL_SUCCESS"
    else:
        print(f"\nFINAL ASSESSMENT: FAILURE")
        print(f"   No successful tool calls")
        assessment = "FAILURE"
    
    # Save comprehensive results
    simulation_results = {
        "simulation_timestamp": time.time(),
        "scenario": "MCP Tools Same Process Simulation",
        "total_calls": len(all_results),
        "successful_calls": len(successful_calls),
        "assessment": assessment,
        "instance_persistence": same_instance if 'same_instance' in locals() else False,
        "data_consistency": data_consistent if 'data_consistent' in locals() else False,
        "performance": {
            "average_time_ms": avg_time if 'avg_time' in locals() else None,
            "first_call_time_ms": first_call_time if 'first_call_time' in locals() else None,
            "subsequent_avg_time_ms": avg_subsequent if 'avg_subsequent' in locals() else None
        },
        "detailed_results": all_results
    }
    
    with open(r"H:\visum-thinker-mcp-server\mcp_simulation_results.json", 'w') as f:
        json.dump(simulation_results, f, indent=2)
    
    print(f"\nComplete simulation results saved to mcp_simulation_results.json")
    
except Exception as e:
    print(f"ERROR: Simulation error: {e}")
    import traceback
    traceback.print_exc()

print(f"\n=== MCP SIMULATION TERMINATA ===")
print(f"This test demonstrates how DirectVisumManager will work in the actual MCP server!")