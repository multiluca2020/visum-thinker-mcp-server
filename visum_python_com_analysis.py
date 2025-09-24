# ANALISI RETE VISUM CON PYTHON - VERSIONE CORRETTA
# Script per interfacciarsi con Visum tramite win32com e VisumPy helpers
# Progetto: Campoleone Italferr 2025

import sys
import os
import json
from datetime import datetime
import win32com.client

print("🐍 ANALISI RETE VISUM CON PYTHON (win32com)")
print("=" * 50)
print("📊 Estrazione dati rete tramite COM Automation")
print("🚄 Progetto: Campoleone Italferr 2025")
print("=" * 50)

def connect_to_visum():
    """Connette a Visum usando win32com"""
    try:
        print("🔗 Tentativo connessione a Visum tramite COM...")
        
        # Prova GetActiveObject
        try:
            visum = win32com.client.GetActiveObject("Visum.Visum.250")
            print("✅ Connesso a istanza Visum attiva!")
            return visum
        except:
            print("⚠️ GetActiveObject fallito, provo Dispatch...")
            
        # Se fallisce, prova Dispatch
        visum = win32com.client.Dispatch("Visum.Visum.250")
        print("✅ Nuova connessione COM creata!")
        return visum
        
    except Exception as e:
        print(f"❌ Errore connessione COM: {e}")
        return None

def get_project_info(visum):
    """Ottiene info base del progetto"""
    try:
        print("\n📋 INFORMAZIONI PROGETTO:")
        print("-" * 30)
        
        # Info progetto
        try:
            version_file = visum.GetPath(1)  # VER file path
            print(f"   • File progetto: {os.path.basename(version_file) if version_file else 'N/A'}")
        except:
            print("   • File progetto: N/A")
        
        # Nome applicazione
        try:
            app_name = visum.GetApplicationName()
            print(f"   • Applicazione: {app_name}")
        except:
            print("   • Applicazione: N/A")
        
        # Versione
        try:
            version = visum.GetVersion()
            print(f"   • Versione: {version}")
        except:
            print("   • Versione: N/A")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore info progetto: {e}")
        return False

def get_network_overview(visum):
    """Ottiene panoramica generale della rete"""
    try:
        print("\n📊 PANORAMICA RETE:")
        print("-" * 30)
        
        net = visum.Net
        
        # Contatori base
        node_count = net.Nodes.CountActive
        link_count = net.Links.CountActive
        zone_count = net.Zones.CountActive
        
        print(f"   • Nodi attivi: {node_count:,}")
        print(f"   • Link attivi: {link_count:,}")
        print(f"   • Zone attive: {zone_count:,}")
        
        # Altri elementi
        try:
            linktype_count = net.LinkTypes.Count
            print(f"   • Tipi di link: {linktype_count}")
        except:
            print("   • Tipi di link: N/A")
        
        try:
            system_count = net.TSystems.Count
            print(f"   • Sistemi di trasporto: {system_count}")
        except:
            print("   • Sistemi di trasporto: N/A")
        
        # Funzioni volume-capacità
        try:
            volcap_count = net.VolCapFormulas.Count
            print(f"   • Funzioni V-C: {volcap_count}")
        except:
            print("   • Funzioni V-C: N/A")
        
        return {
            "nodes": node_count,
            "links": link_count,
            "zones": zone_count,
            "link_types": linktype_count if 'linktype_count' in locals() else 0,
            "transport_systems": system_count if 'system_count' in locals() else 0,
            "volcap_formulas": volcap_count if 'volcap_count' in locals() else 0
        }
        
    except Exception as e:
        print(f"❌ Errore panoramica rete: {e}")
        return None

def analyze_nodes_sample(visum, sample_size=10):
    """Analizza campione di nodi"""
    try:
        print(f"\n🔵 ANALISI NODI (campione di {sample_size}):")
        print("-" * 40)
        
        nodes = visum.Net.Nodes
        total_nodes = nodes.CountActive
        
        if total_nodes == 0:
            print("   ❌ Nessun nodo trovato!")
            return []
        
        print(f"   Analizzando {min(sample_size, total_nodes)} di {total_nodes:,} nodi...")
        
        # Ottieni attributi con GetMultiAttValues
        node_nos = nodes.GetMultiAttValues('No')
        x_coords = nodes.GetMultiAttValues('XCoord')
        y_coords = nodes.GetMultiAttValues('YCoord')
        
        node_data = []
        count = 0
        
        for i, (node_id_row, x_row, y_row) in enumerate(zip(node_nos, x_coords, y_coords)):
            if count >= sample_size:
                break
                
            try:
                node_id = node_id_row[1]  # [0] è l'indice, [1] è il valore
                x_coord = round(x_row[1], 2)
                y_coord = round(y_row[1], 2)
                
                node_info = {
                    "id": node_id,
                    "x": x_coord,
                    "y": y_coord
                }
                node_data.append(node_info)
                
                if count < 5:  # Mostra primi 5
                    print(f"   Nodo {node_id}: ({x_coord}, {y_coord})")
                
                count += 1
                
            except Exception as e:
                print(f"   ⚠️ Errore nodo {i}: {e}")
                continue
        
        print(f"   ✅ {len(node_data)} nodi analizzati con successo")
        return node_data
        
    except Exception as e:
        print(f"❌ Errore analisi nodi: {e}")
        return []

def analyze_links_sample(visum, sample_size=10):
    """Analizza campione di link"""
    try:
        print(f"\n🔗 ANALISI LINK (campione di {sample_size}):")
        print("-" * 40)
        
        links = visum.Net.Links
        total_links = links.CountActive
        
        if total_links == 0:
            print("   ❌ Nessun link trovato!")
            return []
        
        print(f"   Analizzando {min(sample_size, total_links)} di {total_links:,} link...")
        
        # Ottieni attributi multipli
        link_nos = links.GetMultiAttValues('No')
        from_nodes = links.GetMultiAttValues('FromNodeNo')
        to_nodes = links.GetMultiAttValues('ToNodeNo')
        lengths = links.GetMultiAttValues('Length')
        type_nos = links.GetMultiAttValues('TypeNo')
        
        # Prova ad ottenere velocità e capacità (potrebbero non esistere)
        try:
            v0_values = links.GetMultiAttValues('V0_PrT')
        except:
            v0_values = [[0, 0] for _ in range(len(link_nos))]
        
        try:
            cap_values = links.GetMultiAttValues('VolCapPrT')
        except:
            cap_values = [[0, 0] for _ in range(len(link_nos))]
        
        link_data = []
        count = 0
        
        for i, (link_no, from_node, to_node, length, type_no, v0, cap) in enumerate(
            zip(link_nos, from_nodes, to_nodes, lengths, type_nos, v0_values, cap_values)):
            
            if count >= sample_size:
                break
                
            try:
                link_info = {
                    "id": link_no[1],
                    "from_node": from_node[1],
                    "to_node": to_node[1],
                    "length": round(length[1], 1),
                    "type": type_no[1],
                    "v0_prt": round(v0[1], 1) if v0[1] else 0,
                    "capacity": cap[1] if cap[1] else 0
                }
                link_data.append(link_info)
                
                if count < 5:  # Mostra primi 5
                    print(f"   Link {link_info['id']}: {link_info['from_node']}→{link_info['to_node']}")
                    print(f"      Lung: {link_info['length']}m, Tipo: {link_info['type']}, V0: {link_info['v0_prt']}km/h")
                
                count += 1
                
            except Exception as e:
                print(f"   ⚠️ Errore link {i}: {e}")
                continue
        
        print(f"   ✅ {len(link_data)} link analizzati con successo")
        
        # Statistiche riassuntive
        if link_data:
            lengths = [l["length"] for l in link_data if l["length"] > 0]
            speeds = [l["v0_prt"] for l in link_data if l["v0_prt"] > 0]
            
            if lengths:
                print(f"   📊 Lunghezza media: {sum(lengths)/len(lengths):.1f}m")
            if speeds:
                print(f"   📊 Velocità media: {sum(speeds)/len(speeds):.1f}km/h")
        
        return link_data
        
    except Exception as e:
        print(f"❌ Errore analisi link: {e}")
        return []

def analyze_link_types(visum):
    """Analizza i tipi di link"""
    try:
        print(f"\n🏷️ ANALISI TIPI DI LINK:")
        print("-" * 30)
        
        link_types = visum.Net.LinkTypes
        total_types = link_types.Count
        
        if total_types == 0:
            print("   ❌ Nessun tipo di link trovato!")
            return []
        
        # Ottieni attributi multipli
        type_nos = link_types.GetMultiAttValues('No')
        type_names = link_types.GetMultiAttValues('Name')
        
        type_data = []
        
        for type_no, type_name in zip(type_nos, type_names):
            try:
                type_info = {
                    "id": type_no[1],
                    "name": type_name[1]
                }
                type_data.append(type_info)
                
                print(f"   Tipo {type_info['id']}: {type_info['name']}")
                
            except Exception as e:
                print(f"   ⚠️ Errore tipo link: {e}")
        
        print(f"   ✅ {len(type_data)} tipi di link analizzati")
        return type_data
        
    except Exception as e:
        print(f"❌ Errore analisi tipi link: {e}")
        return []

def save_results(project_info, network_data, node_data, link_data, type_data):
    """Salva i risultati in file JSON"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"visum_analysis_com_{timestamp}.json"
        
        results = {
            "timestamp": timestamp,
            "project": "Campoleone Italferr 2025",
            "method": "win32com Python API",
            "project_info": project_info,
            "network_overview": network_data,
            "sample_nodes": node_data,
            "sample_links": link_data,
            "link_types": type_data,
            "summary": {
                "total_nodes_analyzed": len(node_data),
                "total_links_analyzed": len(link_data),
                "total_link_types": len(type_data),
                "analysis_successful": True
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Risultati salvati in: {filename}")
        return filename
        
    except Exception as e:
        print(f"❌ Errore salvataggio: {e}")
        return None

def main():
    """Funzione principale"""
    # Connetti a Visum
    visum = connect_to_visum()
    if not visum:
        print("❌ Impossibile connettersi a Visum. Assicurati che sia aperto.")
        return
    
    # Analisi completa
    print("\n🚀 Inizio analisi completa della rete...")
    
    # Info progetto
    project_ok = get_project_info(visum)
    
    # Panoramica rete
    network_data = get_network_overview(visum)
    
    # Analisi dettagliata
    node_data = analyze_nodes_sample(visum, sample_size=20)
    link_data = analyze_links_sample(visum, sample_size=20)
    type_data = analyze_link_types(visum)
    
    # Salva risultati
    filename = save_results(project_ok, network_data, node_data, link_data, type_data)
    
    # Riepilogo finale
    print("\n" + "=" * 50)
    print("🎯 ANALISI COMPLETATA!")
    print("=" * 50)
    
    if network_data:
        print(f"✅ Rete con {network_data['nodes']:,} nodi e {network_data['links']:,} link")
        print(f"✅ {len(node_data)} nodi campione analizzati")
        print(f"✅ {len(link_data)} link campione analizzati")
        print(f"✅ {len(type_data)} tipi di link identificati")
        
        if filename:
            print(f"💾 Dati esportati in: {filename}")
    else:
        print("❌ Analisi fallita - verifica che il progetto sia caricato")
    
    print("\n🐍 Analisi Python/COM completata!")

if __name__ == "__main__":
    main()
