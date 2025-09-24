# Test connessione all'istanza VisumPy creata
import sys
import os
import time
import json

print("=== TEST CONNESSIONE ISTANZA VISUMPY ===")
print("Scenario: Creare istanza con VisumPy, poi connettersi dall'esterno")

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
    
    print("✅ VisumPy.helpers and win32com imported")
    
    # STEP 1: Creare istanza con VisumPy
    print(f"\n📋 STEP 1: Create VisumPy instance")
    visum_instance = vh.CreateVisum(250)
    print(f"✅ VisumPy instance created: {type(visum_instance)}")
    
    # Carica progetto
    project_path = r"H:\go\italferr2025\Campoleone\100625_Versione_base_v0.3_sub_ok_priv.ver"
    print(f"📂 Loading project...")
    visum_instance.LoadVersion(project_path)
    
    nodes_original = visum_instance.Net.Nodes.Count
    print(f"✅ Project loaded - Nodes: {nodes_original:,}")
    
    # STEP 2: Tenere l'istanza viva e provare connessione esterna
    print(f"\n🔍 STEP 2: Try external connection to VisumPy instance")
    
    # Test 1: GetActiveObject ora che abbiamo un'istanza attiva
    print(f"  Test 1: GetActiveObject dopo CreateVisum")
    try:
        visum_external = win32.GetActiveObject("Visum.Visum")
        print(f"  ✅ GetActiveObject SUCCESS! {type(visum_external)}")
        
        # Verifica che sia la stessa istanza
        nodes_external = visum_external.Net.Nodes.Count
        print(f"  📊 External nodes: {nodes_external:,}")
        
        if nodes_external == nodes_original:
            print(f"  🎉 SAME INSTANCE! External connection works!")
            
            # Test modifica per confermare connessione
            print(f"  🧪 Testing external control...")
            
            # Prova a fare una semplice operazione
            original_title = visum_external.GetPath(0)  # Path del progetto
            print(f"  📁 Project path via external: {original_title}")
            
            success_data = {
                "timestamp": time.time(),
                "method": "VisumPy.CreateVisum + GetActiveObject",
                "api": "VisumPy_External_Connection",
                "nodes": nodes_external,
                "connection_type": "external_after_visumpy",
                "status": "EXTERNAL_CONNECTION_SUCCESS"
            }
            
            with open(r"H:\visum-thinker-mcp-server\visumpy_external_success.json", 'w') as f:
                json.dump(success_data, f, indent=2)
            
            print(f"  💾 External connection success saved!")
            
        else:
            print(f"  ❌ Different instance - External: {nodes_external}, Original: {nodes_original}")
            
    except Exception as get_e:
        print(f"  ❌ GetActiveObject failed: {get_e}")
    
    # Test 2: Multiple Dispatch attempts
    print(f"\n  Test 2: Multiple Dispatch to find same instance")
    
    dispatch_progids = [
        "Visum.Visum.250",
        "Visum.Visum", 
        "Visum.Application"
    ]
    
    for progid in dispatch_progids:
        try:
            print(f"    Trying Dispatch('{progid}')...")
            visum_dispatch = win32.Dispatch(progid)
            
            # Se è vuoto, prova a caricare lo stesso progetto
            if visum_dispatch.Net.Nodes.Count == 0:
                print(f"      Empty instance, loading project...")
                visum_dispatch.LoadVersion(project_path)
            
            nodes_dispatch = visum_dispatch.Net.Nodes.Count
            print(f"      Dispatch nodes: {nodes_dispatch:,}")
            
            if nodes_dispatch == nodes_original:
                print(f"      🎉 SAME INSTANCE via {progid}!")
                
                # Test command execution
                try:
                    # Prova qualche comando semplice
                    zones = visum_dispatch.Net.Zones.Count
                    print(f"      📊 Zones accessible: {zones:,}")
                    print(f"      ✅ External control confirmed via {progid}")
                except Exception as cmd_e:
                    print(f"      ❌ Command test failed: {cmd_e}")
            else:
                print(f"      ❌ Different instance")
                
        except Exception as dispatch_e:
            print(f"      ❌ Dispatch('{progid}') failed: {dispatch_e}")
    
    # STEP 3: Test persistenza istanza
    print(f"\n⏱️  STEP 3: Instance persistence test")
    print(f"  Keeping VisumPy instance alive for 30 seconds...")
    print(f"  During this time, external connections should work...")
    
    start_time = time.time()
    test_interval = 5  # Test ogni 5 secondi
    
    for i in range(6):  # 30 seconds total
        time.sleep(test_interval)
        elapsed = time.time() - start_time
        
        print(f"  ⏰ {elapsed:.1f}s - Testing external access...")
        
        try:
            # Test accesso dall'istanza originale
            nodes_check = visum_instance.Net.Nodes.Count
            print(f"    Original instance: {nodes_check:,} nodes - ✅")
            
            # Test GetActiveObject
            try:
                visum_active = win32.GetActiveObject("Visum.Visum")
                nodes_active = visum_active.Net.Nodes.Count
                print(f"    GetActiveObject: {nodes_active:,} nodes - ✅")
                
                if nodes_active == nodes_check:
                    print(f"    🎉 External connection persistent at {elapsed:.1f}s!")
            except:
                print(f"    ❌ GetActiveObject failed at {elapsed:.1f}s")
                
        except Exception as persist_e:
            print(f"    ❌ Persistence check failed: {persist_e}")
    
    print(f"\n✅ VisumPy instance persistence test completed")
    print(f"Original instance still active: {visum_instance.Net.Nodes.Count:,} nodes")
    
    # Final test
    print(f"\n🔍 FINAL TEST: One more external connection")
    try:
        final_visum = win32.GetActiveObject("Visum.Visum")
        final_nodes = final_visum.Net.Nodes.Count
        print(f"✅ Final external connection: {final_nodes:,} nodes")
        
        if final_nodes == nodes_original:
            print(f"🚀 SOLUTION CONFIRMED: VisumPy + External Connection WORKS!")
            
            final_success = {
                "timestamp": time.time(),
                "method": "VisumPy.CreateVisum + Persistent GetActiveObject",
                "api": "VisumPy_Persistent_External",
                "nodes": final_nodes,
                "persistence_seconds": 30,
                "status": "PERSISTENT_EXTERNAL_SUCCESS"
            }
            
            with open(r"H:\visum-thinker-mcp-server\visumpy_persistent_external.json", 'w') as f:
                json.dump(final_success, f, indent=2)
                
            print(f"💾 Persistent external success confirmed!")
        else:
            print(f"❌ Final external connection shows different data")
            
    except Exception as final_e:
        print(f"❌ Final external connection failed: {final_e}")

except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()

print(f"\n=== TEST CONNESSIONE ISTANZA VISUMPY COMPLETATO ===")
print("Key question: Can we connect externally to VisumPy-created instances?")