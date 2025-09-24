# SCRIPT 2: Test persistenza istanza - Analisi di rete
# Questo script deve accedere all'istanza creata da Script 1

import sys
import os
import time
import json

print("=== SCRIPT 2: TEST PERSISTENZA - ANALISI RETE ===")

# Setup VisumPy paths
visum_path = r"H:\Program Files\PTV Vision\PTV Visum 2025\Exe"
python_path = os.path.join(visum_path, "Python")

if visum_path not in sys.path:
    sys.path.insert(0, visum_path)
if python_path not in sys.path:
    sys.path.insert(0, python_path)

# Stesso DirectVisumManager - dovrebbe recuperare istanza esistente
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
                
                print("🆕 Creating NEW VisumPy instance (Script 1 instance not found)...")
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
    
    def execute_network_analysis(self):
        """Execute detailed network analysis"""
        if not self.initialize_visum():
            return {"error": "Failed to initialize Visum"}
        
        try:
            analysis_start = time.time()
            
            print("🔍 Executing network analysis...")
            
            # Basic network info
            nodes = self.visum_instance.Net.Nodes.Count
            links = self.visum_instance.Net.Links.Count
            zones = self.visum_instance.Net.Zones.Count
            
            # Try to get some detailed info
            network_details = {
                "basic_counts": {
                    "nodes": nodes,
                    "links": links,  
                    "zones": zones
                },
                "analysis_timestamp": time.time(),
                "script": "script2_network_analysis"
            }
            
            # Try to get sample node data
            try:
                node_container = self.visum_instance.Net.Nodes
                if node_container.Count > 0:
                    sample_nodes = node_container.GetMultiAttValues('No')[:5]
                    network_details["sample_nodes"] = sample_nodes
                    print(f"📊 Sample nodes: {sample_nodes}")
            except Exception as e:
                network_details["sample_nodes_error"] = str(e)
                print(f"⚠️ Could not get sample nodes: {e}")
            
            # Try to get zone info
            try:
                zone_container = self.visum_instance.Net.Zones
                if zone_container.Count > 0:
                    sample_zones = zone_container.GetMultiAttValues('No')[:3]
                    network_details["sample_zones"] = sample_zones
                    print(f"🏠 Sample zones: {sample_zones}")
            except Exception as e:
                network_details["sample_zones_error"] = str(e)
                print(f"⚠️ Could not get sample zones: {e}")
            
            analysis_time = time.time() - analysis_start
            network_details["analysis_time_ms"] = round(analysis_time * 1000, 3)
            
            print(f"✅ Network analysis completed in {analysis_time*1000:.3f}ms")
            print(f"📊 Results: {nodes:,} nodes, {links:,} links, {zones:,} zones")
            
            return network_details
            
        except Exception as e:
            error_result = {
                "error": f"Network analysis failed: {str(e)}",
                "script": "script2_network_analysis"
            }
            print(f"❌ Network analysis failed: {e}")
            return error_result

# MAIN SCRIPT 2 EXECUTION  
try:
    print(f"⏰ Script 2 started at: {time.strftime('%H:%M:%S')}")
    
    # Check if Script 1 left status info
    status_file = r"H:\visum-thinker-mcp-server\visum_instance_status.json"
    if os.path.exists(status_file):
        with open(status_file, 'r') as f:
            script1_status = json.load(f)
        print(f"📋 Found Script 1 status:")
        print(f"   Initialized: {script1_status.get('initialized', 'Unknown')}")
        print(f"   Nodes from Script 1: {script1_status.get('network_summary', {}).get('nodes', 'Unknown'):,}")
        print(f"   Instance ID: {script1_status.get('instance_id', 'Unknown')}")
    else:
        print("⚠️ No Script 1 status found")
    
    # Try to access DirectVisumManager
    print(f"\n🔄 Attempting to access DirectVisumManager...")
    manager = DirectVisumManager()
    
    # Execute network analysis
    result = manager.execute_network_analysis()
    
    print(f"\n📊 SCRIPT 2 RESULTS:")
    print(json.dumps(result, indent=2))
    
    # Check if instance was reused or recreated
    current_instance_id = id(manager.visum_instance) if manager.visum_instance else None
    script1_instance_id = script1_status.get('instance_id') if 'script1_status' in locals() else None
    
    if current_instance_id and script1_instance_id:
        if current_instance_id == script1_instance_id:
            print(f"\n🎉 SUCCESS: Same instance reused from Script 1!")
            print(f"   Instance ID match: {current_instance_id}")
        else:
            print(f"\n⚠️ Different instance created:")
            print(f"   Script 1 ID: {script1_instance_id}")
            print(f"   Script 2 ID: {current_instance_id}")
    
    # Save Script 2 results
    script2_status = result.copy()
    script2_status.update({
        "script2_completed": True,
        "script2_timestamp": time.time(),
        "current_instance_id": current_instance_id,
        "instance_reused": current_instance_id == script1_instance_id if script1_instance_id else False
    })
    
    with open(r"H:\visum-thinker-mcp-server\script2_results.json", 'w') as f:
        json.dump(script2_status, f, indent=2)
    
    print(f"\n✅ SCRIPT 2 COMPLETED!")

except Exception as e:
    print(f"❌ Script 2 error: {e}")
    import traceback
    traceback.print_exc()

print(f"=== SCRIPT 2 TERMINATO ===")
print(f"Ora puoi eseguire Script 3 per ulteriori test...")