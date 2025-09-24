# Test CreateVisum con parametri corretti
import sys
import os
import time
import json

print("=== TEST CREATEVISUM WITH PARAMETERS ===")

# Setup paths
visum_path = r"H:\Program Files\PTV Vision\PTV Visum 2025\Exe"
python_path = os.path.join(visum_path, "Python")

if visum_path not in sys.path:
    sys.path.insert(0, visum_path)
if python_path not in sys.path:
    sys.path.insert(0, python_path)

try:
    import VisumPy.helpers as vh
    
    print("✅ VisumPy.helpers imported")
    print(f"CreateVisum signature: {vh.CreateVisum.__doc__ or 'No docstring'}")
    
    # Prova diversi parametri per CreateVisum
    print(f"\n🔍 Testing CreateVisum with different parameters:")
    
    test_params = [
        # Parametri comuni per CreateVisum
        ([], "no parameters"),
        ([250], "version 250"),
        ([2025], "version 2025"), 
        ([25.0], "version 25.0"),
        ([250, True], "version + visible"),
        ([250, False], "version + hidden"),
        ([None], "None parameter"),
        (["250"], "string version"),
        ([250, True, True], "version + visible + license"),
        ([250, False, False], "version + hidden + no license")
    ]
    
    visum_instance = None
    successful_params = None
    
    for params, description in test_params:
        try:
            print(f"  Trying CreateVisum({params}) - {description}...")
            
            if not params:
                visum_instance = vh.CreateVisum()
            else:
                visum_instance = vh.CreateVisum(*params)
                
            print(f"  ✅ SUCCESS! CreateVisum({params})")
            print(f"    Instance type: {type(visum_instance)}")
            
            # Test se ha Net
            if hasattr(visum_instance, 'Net'):
                print(f"    ✅ Has Net attribute")
                nodes = visum_instance.Net.Nodes.Count
                links = visum_instance.Net.Links.Count
                print(f"    📊 Empty network - Nodes: {nodes:,}, Links: {links:,}")
                successful_params = params
                break
            else:
                print(f"    ❌ No Net attribute")
                
        except Exception as e:
            print(f"  ❌ CreateVisum({params}) failed: {e}")
    
    if visum_instance and successful_params is not None:
        print(f"\n🎉 VisumPy.helpers.CreateVisum works!")
        print(f"Successful parameters: {successful_params}")
        
        # Ora proviamo a caricare il progetto Campoleone
        project_path = r"H:\go\italferr2025\Campoleone\100625_Versione_base_v0.3_sub_ok_priv.ver"
        
        print(f"\n📂 Attempting to load project: {os.path.basename(project_path)}")
        
        try:
            print(f"  Loading version file...")
            visum_instance.LoadVersion(project_path)
            print(f"  ✅ Project loaded!")
            
            # Verifica dati caricati
            nodes = visum_instance.Net.Nodes.Count
            links = visum_instance.Net.Links.Count
            zones = visum_instance.Net.Zones.Count if hasattr(visum_instance.Net, 'Zones') else 0
            
            print(f"  📊 Project data:")
            print(f"    Nodes: {nodes:,}")
            print(f"    Links: {links:,}")
            print(f"    Zones: {zones:,}")
            
            if nodes > 0:
                print(f"\n🎉 VISUMPY SUCCESS! Connected to active project!")
                
                # Test analisi di base
                print(f"\n🔍 Basic network analysis:")
                
                # Sample di nodi
                if nodes > 0:
                    first_nodes = visum_instance.Net.Nodes.GetMultiAttValues('No', '', 10 if nodes > 10 else nodes)
                    print(f"    First nodes IDs: {first_nodes[:5] if len(first_nodes) > 5 else first_nodes}")
                
                # Salva successo completo
                success_data = {
                    "timestamp": time.time(),
                    "method": f"VisumPy.helpers.CreateVisum({successful_params})",
                    "api": "VisumPy_Official",
                    "project": project_path,
                    "nodes": nodes,
                    "links": links,
                    "zones": zones,
                    "status": "PROJECT_LOADED_SUCCESS"
                }
                
                with open(r"H:\visum-thinker-mcp-server\visumpy_project_success.json", 'w') as f:
                    json.dump(success_data, f, indent=2)
                
                print(f"\n💾 Complete success saved to visumpy_project_success.json")
                print(f"🚀 VisumPy is the SOLUTION!")
                
            else:
                print(f"  ❌ Project loaded but no data found")
                
        except Exception as load_e:
            print(f"  ❌ Project loading failed: {load_e}")
            
            # Salva successo parziale (istanza creata)
            partial_success = {
                "timestamp": time.time(),
                "method": f"VisumPy.helpers.CreateVisum({successful_params})",
                "api": "VisumPy_Official", 
                "project": "NONE",
                "nodes": 0,
                "links": 0,
                "status": "INSTANCE_CREATED_SUCCESS"
            }
            
            with open(r"H:\visum-thinker-mcp-server\visumpy_partial_success.json", 'w') as f:
                json.dump(partial_success, f, indent=2)
                
            print(f"💾 Partial success saved - VisumPy creates instances!")
            
    else:
        print(f"\n❌ No working CreateVisum parameters found")

    # Prova anche: direct import del COM object
    print(f"\n🔍 Alternative: Direct Visum COM via VisumPy environment")
    
    try:
        import win32com.client as win32
        
        # Con l'ambiente VisumPy, potrebbero essere disponibili altri ProgID
        visum_com = win32.Dispatch("Visum.Visum.250")
        print(f"✅ Direct COM Dispatch worked: {type(visum_com)}")
        
        if hasattr(visum_com, 'LoadVersion'):
            project_path = r"H:\go\italferr2025\Campoleone\100625_Versione_base_v0.3_sub_ok_priv.ver"
            visum_com.LoadVersion(project_path)
            nodes = visum_com.Net.Nodes.Count
            print(f"🎉 Direct COM + Project: {nodes:,} nodes!")
            
    except Exception as com_e:
        print(f"❌ Direct COM failed: {com_e}")

except ImportError as e:
    print(f"❌ VisumPy.helpers import failed: {e}")

print(f"\n=== CREATEVISUM TEST COMPLETED ===")