# Test script per Visum - da eseguire DENTRO l'istanza Visum
# Questo script avrà accesso diretto ai dati via COM interno

import sys
import json
import time
import os

print("=== VISUM INTERNAL SCRIPT START ===")
print(f"Python version: {sys.version}")
print(f"Script path: {__file__}")

try:
    # In Visum, l'oggetto COM è disponibile come variabile globale
    # Diversi modi per accedere a seconda della versione
    visum_obj = None
    
    # Metodo 1: Variabile globale Visum
    try:
        visum_obj = Visum
        print("✅ Visum object found via global variable")
    except NameError:
        pass
    
    # Metodo 2: Modulo Visum
    if not visum_obj:
        try:
            import Visum
            visum_obj = Visum
            print("✅ Visum object found via import")
        except ImportError:
            pass
    
    # Metodo 3: COM interno
    if not visum_obj:
        try:
            import win32com.client
            visum_obj = win32com.client.GetActiveObject("Visum.Visum")
            print("✅ Visum object found via COM internal")
        except:
            pass
    
    if visum_obj:
        # Accesso ai dati rete
        nodes_count = visum_obj.Net.Nodes.Count
        links_count = visum_obj.Net.Links.Count  
        zones_count = visum_obj.Net.Zones.Count
        
        print(f"📊 Network Statistics:")
        print(f"   Nodes: {nodes_count:,}")
        print(f"   Links: {links_count:,}")
        print(f"   Zones: {zones_count:,}")
        
        # Raccolta dati dettagliati
        analysis_data = {
            "timestamp": time.time(),
            "success": True,
            "network": {
                "nodes": nodes_count,
                "links": links_count,
                "zones": zones_count
            }
        }
        
        # Sample link data se disponibile
        if links_count > 0:
            try:
                print("🔍 Collecting sample link data...")
                link_set = visum_obj.Net.Links
                attrs = link_set.GetMultipleAttributes(['No', 'Length', 'NumLanes'])
                
                sample_links = []
                for i, (no, length, lanes) in enumerate(attrs[:5]):  # Prime 5
                    sample_links.append({
                        "no": int(no),
                        "length": float(length),
                        "lanes": int(lanes)
                    })
                
                analysis_data["sample_links"] = sample_links
                print(f"✅ Collected {len(sample_links)} sample links")
                
            except Exception as e:
                print(f"⚠️ Link data collection failed: {e}")
                analysis_data["sample_links"] = []
        
        # Export risultati
        output_file = r"H:\visum-thinker-mcp-server\visum_analysis_result.json"
        with open(output_file, 'w') as f:
            json.dump(analysis_data, f, indent=2)
        
        print(f"✅ Results exported to: {output_file}")
        
        # Segnale di completamento
        flag_file = r"H:\visum-thinker-mcp-server\analysis_complete.flag"
        with open(flag_file, 'w') as f:
            f.write(f"COMPLETE_{time.time()}")
        
        print("🎯 Analysis completed successfully!")
        
    else:
        print("❌ Could not access Visum object")
        # Export error result
        error_data = {
            "timestamp": time.time(),
            "success": False,
            "error": "Could not access Visum COM object"
        }
        
        output_file = r"H:\visum-thinker-mcp-server\visum_analysis_result.json"
        with open(output_file, 'w') as f:
            json.dump(error_data, f, indent=2)

except Exception as e:
    print(f"❌ Script error: {e}")
    import traceback
    traceback.print_exc()
    
    # Export error result
    error_data = {
        "timestamp": time.time(),
        "success": False,
        "error": str(e),
        "traceback": traceback.format_exc()
    }
    
    output_file = r"H:\visum-thinker-mcp-server\visum_analysis_result.json"
    with open(output_file, 'w') as f:
        json.dump(error_data, f, indent=2)

print("=== VISUM INTERNAL SCRIPT END ===")