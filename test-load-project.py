import sys
import os
sys.path.append(r"H:\Program Files\PTV Vision\PTV Visum 2025\Exe")

# Percorso del progetto Campoleone
PROJECT_PATH = r"H:\go\italferr2025\Campoleone\100625_Versione_base_v0.3_sub_ok_priv.ver"

try:
    print("=== CARICAMENTO PROGETTO VISUM VIA PYTHON ===")
    
    import win32com.client
    
    # Usa DispatchEx per creare nuova istanza
    print("🔄 Creazione istanza Visum...")
    visum = win32com.client.DispatchEx("Visum.Visum")
    print("✅ Istanza creata")
    
    # Verifica esistenza file progetto
    if os.path.exists(PROJECT_PATH):
        print(f"✅ File progetto trovato: {os.path.basename(PROJECT_PATH)}")
        file_size = os.path.getsize(PROJECT_PATH) / (1024 * 1024)
        print(f"   Dimensione: {file_size:.1f} MB")
        
        # Carica il progetto
        print("📂 Caricamento progetto in corso...")
        visum.LoadVersion(PROJECT_PATH)
        print("✅ Progetto caricato!")
        
        # Verifica dati rete
        nodes = visum.Net.Nodes.Count
        links = visum.Net.Links.Count  
        zones = visum.Net.Zones.Count
        
        print(f"\n📊 STATISTICHE RETE CAMPOLEONE:")
        print(f"   Nodi: {nodes:,}")
        print(f"   Link: {links:,}")
        print(f"   Zone: {zones:,}")
        
        if nodes > 0 and links > 0:
            print("\n🎯 SUCCESSO! Rete caricata correttamente")
            
            # Test analisi veloce
            print("🔍 Test analisi dettagli rete...")
            
            # Statistiche tipi nodi
            node_types = {}
            for i in range(1, min(nodes, 100) + 1):  # Test primi 100 nodi
                try:
                    node = visum.Net.Nodes.ItemByKey(i)
                    node_type = node.GetAttValue("NodeTypeNo")
                    node_types[node_type] = node_types.get(node_type, 0) + 1
                except:
                    continue
            
            print(f"   Tipi nodi (campione): {node_types}")
            
            # Statistiche link base
            print("📈 Analisi link base...")
            total_length = 0
            link_count_sample = 0
            
            for i in range(1, min(links, 1000) + 1):  # Test primi 1000 link
                try:
                    link = visum.Net.Links.ItemByKey(1, i)  # From=1, To=i (approx)
                    length = link.GetAttValue("Length")
                    total_length += length
                    link_count_sample += 1
                except:
                    continue
                
                if link_count_sample >= 100:  # Ferma dopo 100 link validi
                    break
            
            if link_count_sample > 0:
                avg_length = total_length / link_count_sample
                print(f"   Link analizzati: {link_count_sample}")
                print(f"   Lunghezza media: {avg_length:.2f} km")
            
            print("\n✅ ANALISI COMPLETATA - MCP DOVREBBE FUNZIONARE!")
            
        else:
            print("❌ Rete vuota dopo caricamento")
            
    else:
        print(f"❌ File progetto non trovato: {PROJECT_PATH}")

except Exception as e:
    print(f"❌ ERRORE: {e}")
    import traceback
    traceback.print_exc()

print("\n=== TEST COMPLETATO ===")