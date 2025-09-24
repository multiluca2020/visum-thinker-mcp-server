# SCRIPT 1: Inizializzazione DirectVisumManager
# Questo script crea l'istanza e carica il progetto

import sys
import os
import time
import json

print("=== SCRIPT 1: INIZIALIZZAZIONE DIRECTVISUMMANAGER ===")

# Setup VisumPy paths
visum_path = r"H:\Program Files\PTV Vision\PTV Visum 2025\Exe"
python_path = os.path.join(visum_path, "Python")

if visum_path not in sys.path:
    sys.path.insert(0, visum_path)
if python_path not in sys.path:
    sys.path.insert(0, python_path)

# Import e create DirectVisumManager
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
                
                print("🚀 Creating VisumPy instance...")
                self.visum_instance = vh.CreateVisum(250)
                
                # Load default project
                project_path = r"H:\go\italferr2025\Campoleone\100625_Versione_base_v0.3_sub_ok_priv.ver"
                print(f"📂 Loading project: {os.path.basename(project_path)}")
                self.visum_instance.LoadVersion(project_path)
                self.project_loaded = project_path
                
                self.initialization_time = time.time() - init_start
                
                nodes = self.visum_instance.Net.Nodes.Count
                links = self.visum_instance.Net.Links.Count
                zones = self.visum_instance.Net.Zones.Count
                
                print(f"✅ Initialized in {self.initialization_time:.3f}s:")
                print(f"   📊 {nodes:,} nodes")
                print(f"   🔗 {links:,} links") 
                print(f"   🏠 {zones:,} zones")
                
                # Save instance status for other scripts
                status = {
                    "initialized": True,
                    "creation_timestamp": self.creation_timestamp,
                    "initialization_time": self.initialization_time,
                    "project_path": project_path,
                    "network_summary": {
                        "nodes": nodes,
                        "links": links,
                        "zones": zones
                    },
                    "instance_id": id(self.visum_instance),
                    "script": "script1_init"
                }
                
                with open(r"H:\visum-thinker-mcp-server\visum_instance_status.json", 'w') as f:
                    json.dump(status, f, indent=2)
                
                return True
                
            except Exception as e:
                print(f"❌ Initialization failed: {e}")
                import traceback
                traceback.print_exc()
                return False
        else:
            print("✅ VisumPy instance already exists")
            return True
    
    def get_instance_info(self):
        """Get current instance information"""
        if self.visum_instance:
            try:
                return {
                    "active": True,
                    "nodes": self.visum_instance.Net.Nodes.Count,
                    "links": self.visum_instance.Net.Links.Count,
                    "zones": self.visum_instance.Net.Zones.Count,
                    "project": self.project_loaded,
                    "initialization_time": self.initialization_time,
                    "creation_timestamp": self.creation_timestamp,
                    "instance_id": id(self.visum_instance)
                }
            except Exception as e:
                return {"active": False, "error": f"Instance not accessible: {e}"}
        return {"active": False, "error": "Instance not created"}

# MAIN SCRIPT 1 EXECUTION
try:
    print(f"⏰ Script 1 started at: {time.strftime('%H:%M:%S')}")
    
    # Create and initialize manager
    manager = DirectVisumManager()
    success = manager.initialize_visum()
    
    if success:
        print(f"\n🎉 SCRIPT 1 COMPLETED SUCCESSFULLY!")
        
        # Get detailed info
        info = manager.get_instance_info()
        print(f"📋 Instance Info:")
        for key, value in info.items():
            if key == "nodes":
                print(f"   {key}: {value:,}")
            elif key == "links":
                print(f"   {key}: {value:,}")
            elif key == "zones":
                print(f"   {key}: {value:,}")
            else:
                print(f"   {key}: {value}")
        
        # Keep reference alive for a moment
        print(f"\n⏳ Keeping instance alive for 10 seconds...")
        print(f"   During this time, other scripts can access the same instance")
        
        start_time = time.time()
        while time.time() - start_time < 10:
            # Periodically check instance is still alive
            try:
                current_nodes = manager.visum_instance.Net.Nodes.Count
                elapsed = time.time() - start_time
                print(f"   ⏰ {elapsed:.1f}s - Instance alive: {current_nodes:,} nodes")
                time.sleep(2)
            except Exception as e:
                print(f"   ❌ Instance died: {e}")
                break
        
        print(f"\n✅ Script 1 finished - instance should remain in memory")
        
        # Final status update
        final_status = manager.get_instance_info()
        final_status["script1_completed"] = True
        final_status["script1_end_time"] = time.time()
        
        with open(r"H:\visum-thinker-mcp-server\visum_instance_status.json", 'w') as f:
            json.dump(final_status, f, indent=2)
            
    else:
        print(f"❌ SCRIPT 1 FAILED!")

except Exception as e:
    print(f"❌ Script 1 error: {e}")
    import traceback
    traceback.print_exc()

print(f"=== SCRIPT 1 TERMINATO ===")
print(f"Ora puoi eseguire Script 2 per testare la persistenza...")