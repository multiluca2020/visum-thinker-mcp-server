# Step 1: Launch Visum with project
# Questo script carica il progetto direttamente

import sys
import json
import time
import os

print("=== VISUM STEP 1: LAUNCH WITH PROJECT ===")
print(f"Timestamp: {time.strftime('%H:%M:%S')}")

try:
    # Il progetto sarà caricato automaticamente se passato come argomento
    # Ma possiamo anche caricarlo via script
    
    # Accesso oggetto Visum (diversi metodi)
    visum = None
    
    # Prova accesso diretto (variabile globale in Visum)
    try:
        if 'Visum' in globals():
            visum = globals()['Visum']
            print("✅ Visum accessed via globals")
    except:
        pass
    
    # Prova import Visum module
    if not visum:
        try:
            import Visum as VisumModule
            visum = VisumModule
            print("✅ Visum accessed via module import")
        except ImportError:
            pass
    
    # Prova COM dispatch interno
    if not visum:
        try:
            import win32com.client
            # In script Visum, questo dovrebbe funzionare
            visum = win32com.client.Dispatch("Visum.Visum")
            print("✅ Visum accessed via COM dispatch")
        except:
            pass
    
    # Se ancora non trovato, prova GetActiveObject
    if not visum:
        try:
            import win32com.client
            visum = win32com.client.GetActiveObject("Visum.Visum")
            print("✅ Visum accessed via GetActiveObject")
        except Exception as e:
            print(f"❌ GetActiveObject failed: {e}")
    
    if visum:
        print("🎯 Visum object acquired successfully!")
        
        # Carica progetto
        project_path = r"H:\go\italferr2025\Campoleone\100625_Versione_base_v0.3_sub_ok_priv.ver"
        
        if os.path.exists(project_path):
            print(f"📂 Loading project: {os.path.basename(project_path)}")
            
            # Carica versione
            visum.LoadVersion(project_path)
            print("✅ Project loaded successfully!")
            
            # Verifica caricamento
            nodes = visum.Net.Nodes.Count
            links = visum.Net.Links.Count
            zones = visum.Net.Zones.Count
            
            print(f"📊 Network loaded:")
            print(f"   Nodes: {nodes:,}")
            print(f"   Links: {links:,}")  
            print(f"   Zones: {zones:,}")
            
            # Salva stato per step successivi
            status = {
                "timestamp": time.time(),
                "step": "1_launch_project",
                "success": True,
                "project_loaded": True,
                "project_path": project_path,
                "network": {
                    "nodes": nodes,
                    "links": links,
                    "zones": zones
                }
            }
            
        else:
            print(f"❌ Project file not found: {project_path}")
            status = {
                "timestamp": time.time(),
                "step": "1_launch_project", 
                "success": False,
                "error": f"Project file not found: {project_path}"
            }
            
    else:
        print("❌ Could not access Visum object")
        status = {
            "timestamp": time.time(),
            "step": "1_launch_project",
            "success": False,
            "error": "Could not access Visum COM object"
        }
    
    # Salva risultato step 1
    output_file = r"H:\visum-thinker-mcp-server\step1_result.json"
    with open(output_file, 'w') as f:
        json.dump(status, f, indent=2)
    
    print(f"💾 Step 1 results saved to: {output_file}")
    
except Exception as e:
    print(f"❌ Step 1 error: {e}")
    import traceback
    traceback.print_exc()
    
    # Salva errore
    error_status = {
        "timestamp": time.time(),
        "step": "1_launch_project",
        "success": False,
        "error": str(e),
        "traceback": traceback.format_exc()
    }
    
    output_file = r"H:\visum-thinker-mcp-server\step1_result.json"  
    with open(output_file, 'w') as f:
        json.dump(error_status, f, indent=2)

print("=== STEP 1 COMPLETED ===")