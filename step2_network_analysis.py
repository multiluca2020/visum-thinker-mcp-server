# Step 2: Network Analysis on loaded project
# Analisi dettagliata della rete già caricata

import sys
import json
import time
import os

print("=== VISUM STEP 2: NETWORK ANALYSIS ===")
print(f"Timestamp: {time.strftime('%H:%M:%S')}")

try:
    # Accesso a Visum (il progetto dovrebbe già essere caricato)
    visum = None
    
    # Prova tutti i metodi di accesso
    access_methods = []
    
    # Metodo 1: Variabile globale
    try:
        if 'Visum' in dir():
            visum = Visum
            access_methods.append("Global variable")
    except:
        pass
    
    # Metodo 2: COM Dispatch
    if not visum:
        try:
            import win32com.client
            visum = win32com.client.Dispatch("Visum.Visum")
            access_methods.append("COM Dispatch")
        except Exception as e:
            print(f"COM Dispatch failed: {e}")
    
    # Metodo 3: GetActiveObject  
    if not visum:
        try:
            import win32com.client
            visum = win32com.client.GetActiveObject("Visum.Visum")
            access_methods.append("GetActiveObject")
        except Exception as e:
            print(f"GetActiveObject failed: {e}")
    
    if visum:
        print(f"✅ Visum accessed via: {', '.join(access_methods)}")
        
        # Verifica che il progetto sia caricato
        nodes = visum.Net.Nodes.Count
        links = visum.Net.Links.Count
        zones = visum.Net.Zones.Count
        
        print(f"📊 Current network state:")
        print(f"   Nodes: {nodes:,}")
        print(f"   Links: {links:,}")
        print(f"   Zones: {zones:,}")
        
        if nodes > 0 and links > 0:
            print("🎯 Project confirmed loaded - starting detailed analysis...")
            
            # ANALISI DETTAGLIATA
            analysis_start = time.time()
            
            # 1. Link Analysis
            print("🔍 Analyzing links...")
            link_set = visum.Net.Links
            link_attrs = link_set.GetMultipleAttributes(['No', 'Length', 'NumLanes', 'FromNodeNo', 'ToNodeNo'])
            
            # Statistiche link
            lengths = [attr[1] for attr in link_attrs]
            lanes = [attr[2] for attr in link_attrs]
            
            total_length = sum(lengths)
            avg_length = total_length / len(lengths)
            max_length = max(lengths)
            min_length = min(lengths)
            
            avg_lanes = sum(lanes) / len(lanes)
            max_lanes = max(lanes)
            
            print(f"   📏 Total network length: {total_length:.2f} km")
            print(f"   📐 Average link length: {avg_length:.3f} km")
            print(f"   🛣️ Average lanes: {avg_lanes:.1f}")
            
            # 2. Node Analysis
            print("🔍 Analyzing nodes...")
            node_set = visum.Net.Nodes
            node_attrs = node_set.GetMultipleAttributes(['No', 'XCoord', 'YCoord'])
            
            # Bounding box della rete
            x_coords = [attr[1] for attr in node_attrs]
            y_coords = [attr[2] for attr in node_attrs]
            
            min_x, max_x = min(x_coords), max(x_coords)
            min_y, max_y = min(y_coords), max(y_coords)
            
            network_width = max_x - min_x
            network_height = max_y - min_y
            
            print(f"   🗺️ Network bounds: ({min_x:.3f},{min_y:.3f}) to ({max_x:.3f},{max_y:.3f})")
            print(f"   📐 Dimensions: {network_width:.3f} x {network_height:.3f}")
            
            # 3. Zone Analysis  
            print("🔍 Analyzing zones...")
            zone_set = visum.Net.Zones
            zone_attrs = zone_set.GetMultipleAttributes(['No', 'XCoord', 'YCoord'])
            
            zone_x = [attr[1] for attr in zone_attrs]
            zone_y = [attr[2] for attr in zone_attrs]
            
            center_x = sum(zone_x) / len(zone_x)
            center_y = sum(zone_y) / len(zone_y)
            
            print(f"   🎯 Network center: ({center_x:.3f}, {center_y:.3f})")
            
            # 4. Connectivity Analysis
            print("🔍 Analyzing connectivity...")
            connectivity_ratio = links / nodes
            density = nodes / (network_width * network_height) if network_width > 0 and network_height > 0 else 0
            
            print(f"   🔗 Connectivity ratio: {connectivity_ratio:.2f} links per node")
            print(f"   🏢 Node density: {density:.2f} nodes per unit²")
            
            analysis_end = time.time()
            analysis_time = analysis_end - analysis_start
            
            print(f"⏱️ Analysis completed in {analysis_time:.2f} seconds")
            
            # Risultati finali
            results = {
                "timestamp": time.time(),
                "step": "2_network_analysis",
                "success": True,
                "analysis_time": analysis_time,
                "network_statistics": {
                    "nodes": nodes,
                    "links": links, 
                    "zones": zones,
                    "total_length_km": total_length,
                    "avg_length_km": avg_length,
                    "max_length_km": max_length,
                    "min_length_km": min_length,
                    "avg_lanes": avg_lanes,
                    "max_lanes": max_lanes,
                    "connectivity_ratio": connectivity_ratio,
                    "node_density": density
                },
                "network_bounds": {
                    "min_x": min_x,
                    "max_x": max_x,
                    "min_y": min_y,
                    "max_y": max_y,
                    "width": network_width,
                    "height": network_height,
                    "center_x": center_x,
                    "center_y": center_y
                },
                "sample_links": [
                    {
                        "no": int(attr[0]),
                        "length": float(attr[1]),
                        "lanes": int(attr[2]),
                        "from_node": int(attr[3]),
                        "to_node": int(attr[4])
                    }
                    for attr in link_attrs[:10]  # Prime 10 links
                ]
            }
            
        else:
            print("❌ No project loaded or empty network")
            results = {
                "timestamp": time.time(),
                "step": "2_network_analysis",
                "success": False,
                "error": "No project loaded or empty network"
            }
            
    else:
        print("❌ Could not access Visum object")
        results = {
            "timestamp": time.time(),
            "step": "2_network_analysis", 
            "success": False,
            "error": "Could not access Visum COM object"
        }
    
    # Salva risultati
    output_file = r"H:\visum-thinker-mcp-server\step2_analysis_result.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"💾 Step 2 results saved to: {output_file}")
    
except Exception as e:
    print(f"❌ Step 2 error: {e}")
    import traceback
    traceback.print_exc()
    
    error_results = {
        "timestamp": time.time(),
        "step": "2_network_analysis",
        "success": False,
        "error": str(e),
        "traceback": traceback.format_exc()
    }
    
    output_file = r"H:\visum-thinker-mcp-server\step2_analysis_result.json"
    with open(output_file, 'w') as f:
        json.dump(error_results, f, indent=2)

print("=== STEP 2 COMPLETED ===")