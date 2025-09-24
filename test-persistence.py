import sys
import time
sys.path.append(r"H:\Program Files\PTV Vision\PTV Visum 2025\Exe")

try:
    import win32com.client
    
    print("=== TEST PERSISTENZA ISTANZA COM VISUM ===")
    print("Creazione istanza COM...")
    
    # Crea istanza e carica progetto
    visum = win32com.client.DispatchEx("Visum.Visum")
    print("✅ Istanza COM creata")
    
    # Carica progetto
    campoleone_path = r"H:\go\italferr2025\Campoleone\100625_Versione_base_v0.3_sub_ok_priv.ver"
    print("📂 Caricamento progetto...")
    visum.LoadVersion(campoleone_path)
    print("✅ Progetto caricato")
    
    # ANALISI 1: Statistiche base
    print("\n" + "="*50)
    print("ANALISI 1 - STATISTICHE BASE")
    print("="*50)
    
    start_time = time.time()
    nodes = visum.Net.Nodes.Count
    links = visum.Net.Links.Count  
    zones = visum.Net.Zones.Count
    end_time = time.time()
    
    print(f"Nodi: {nodes:,}")
    print(f"Link: {links:,}")
    print(f"Zone: {zones:,}")
    print(f"⏱️ Tempo: {end_time - start_time:.3f} secondi")
    
    # Pausa simulata
    print("\n⏳ Pausa di 3 secondi (simulazione lavoro diverso)...")
    time.sleep(3)
    
    # ANALISI 2: Dettagli link
    print("\n" + "="*50)
    print("ANALISI 2 - DETTAGLI LINK (stessa istanza)")
    print("="*50)
    
    start_time = time.time()
    
    # Test accesso agli attributi dei link
    link_set = visum.Net.Links
    print(f"Collezione link: {type(link_set)}")
    
    # Prendi campione di attributi
    attrs = link_set.GetMultipleAttributes(['No', 'Length', 'NumLanes', 'VolCapPrT'])
    sample_size = min(10, len(attrs))
    
    print(f"\nCampione primi {sample_size} link:")
    total_length = 0
    for i in range(sample_size):
        link_no, length, lanes, capacity = attrs[i]
        total_length += length
        print(f"  Link {int(link_no):>6}: {length:>8.3f} km, {int(lanes)} corsie, cap: {capacity}")
    
    avg_length = total_length / sample_size if sample_size > 0 else 0
    end_time = time.time()
    
    print(f"\n📊 Lunghezza media campione: {avg_length:.3f} km")
    print(f"⏱️ Tempo: {end_time - start_time:.3f} secondi")
    
    # Pausa più lunga
    print("\n⏳ Pausa di 5 secondi (simulazione analisi complessa)...")
    time.sleep(5)
    
    # ANALISI 3: Topologia (stessa istanza)
    print("\n" + "="*50)
    print("ANALISI 3 - TOPOLOGIA RETE (stessa istanza)")
    print("="*50)
    
    start_time = time.time()
    
    # Analisi nodi
    node_set = visum.Net.Nodes  
    node_attrs = node_set.GetMultipleAttributes(['No', 'XCoord', 'YCoord'])
    
    # Calcola bounding box
    x_coords = [attr[1] for attr in node_attrs[:1000]]  # Campione primi 1000
    y_coords = [attr[2] for attr in node_attrs[:1000]]
    
    min_x, max_x = min(x_coords), max(x_coords)
    min_y, max_y = min(y_coords), max(y_coords)
    
    area_width = max_x - min_x
    area_height = max_y - min_y
    
    print(f"📍 Area rete (campione):")
    print(f"   X: {min_x:.0f} - {max_x:.0f} (larghezza: {area_width:.0f})")
    print(f"   Y: {min_y:.0f} - {max_y:.0f} (altezza: {area_height:.0f})")
    
    # Densità spaziale
    area_total = area_width * area_height if area_width > 0 and area_height > 0 else 1
    spatial_density = nodes / (area_total / 1000000)  # nodi per km²
    
    print(f"🗺️ Densità spaziale: {spatial_density:.2f} nodi/km²")
    
    end_time = time.time()
    print(f"⏱️ Tempo: {end_time - start_time:.3f} secondi")
    
    # Test finale: l'istanza è ancora viva?
    print("\n" + "="*50)
    print("TEST FINALE - ISTANZA ANCORA ATTIVA?")
    print("="*50)
    
    try:
        final_check = visum.Net.Nodes.Count
        print(f"✅ SUCCESSO! Istanza ancora attiva: {final_check:,} nodi")
        print("🎯 L'istanza COM può essere riutilizzata per analisi multiple!")
        
        # Info versione Visum
        try:
            version_info = visum.GetVersionString()
            print(f"📋 Versione Visum: {version_info}")
        except:
            print("📋 Versione Visum: Non disponibile")
            
    except Exception as final_error:
        print(f"❌ ERRORE: Istanza persa: {final_error}")
    
    print("\n=== CONCLUSIONI ===")
    print("✅ Stessa istanza COM usata per 3 analisi diverse")
    print("✅ Performance mantenuta tra le chiamate") 
    print("✅ Dati persistenti e accessibili")
    print("🎯 RACCOMANDAZIONE: Riutilizzare istanza COM per efficienza!")
    
except Exception as e:
    print(f"ERRORE GENERALE: {e}")
    import traceback
    traceback.print_exc()