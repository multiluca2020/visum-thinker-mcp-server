# ANALISI RETE VISUM CON PYTHON
# Script per interfacciarsi direttamente con Visum tramite VisumPy
# Progetto: Campoleone Italferr 2025

import sys
import os
import json
from datetime import datetime

# Aggiungi il path di Visum per VisumPy
visum_path = "H:/Program Files/PTV Vision/PTV Visum 2025/Exe"
if visum_path not in sys.path:
    sys.path.append(visum_path)

print("🐍 ANALISI RETE VISUM CON PYTHON")
print("=" * 50)
print("📊 Estrazione dati rete tramite VisumPy")
print("🚄 Progetto: Campoleone Italferr 2025")
print("=" * 50)

def connect_to_visum():
    """Connette a Visum usando VisumPy"""
    try:
        print("🔗 Tentativo connessione a Visum...")
        import VisumPy
        
        # Connetti all'istanza Visum attiva
        visum = VisumPy.Visum()
        print("✅ Connessione VisumPy riuscita!")
        return visum
        
    except ImportError as e:
        print(f"❌ Errore import VisumPy: {e}")
        return None
    except Exception as e:
        print(f"❌ Errore connessione Visum: {e}")
        return None

def get_network_overview(visum):
    """Ottiene panoramica generale della rete"""
    try:
        print("\n📊 PANORAMICA RETE:")
        print("-" * 30)
        
        # Contatori base
        node_count = visum.Net.Nodes.CountActive
        link_count = visum.Net.Links.CountActive
        zone_count = visum.Net.Zones.CountActive
        
        print(f"   • Nodi attivi: {node_count:,}")
        print(f"   • Link attivi: {link_count:,}")
        print(f"   • Zone attive: {zone_count:,}")
        
        # Tipi di link
        try:
            linktype_count = visum.Net.LinkTypes.Count
            print(f"   • Tipi di link: {linktype_count}")
        except:
            print("   • Tipi di link: N/A")
        
        # Funzioni volume-capacità
        try:
            volcap_count = visum.Net.VolCapFormulas.Count
            print(f"   • Funzioni V-C: {volcap_count}")
        except:
            print("   • Funzioni V-C: N/A")
        
        return {
            "nodes": node_count,
            "links": link_count,
            "zones": zone_count,
            "link_types": linktype_count if 'linktype_count' in locals() else 0,
            "volcap_formulas": volcap_count if 'volcap_count' in locals() else 0
        }
        
    except Exception as e:
        print(f"❌ Errore panoramica rete: {e}")
        return None

def analyze_nodes(visum, sample_size=10):
    """Analizza i nodi della rete"""
    try:
        print(f"\n🔵 ANALISI NODI (campione di {sample_size}):")
        print("-" * 40)
        
        nodes = visum.Net.Nodes
        total_nodes = nodes.CountActive
        
        if total_nodes == 0:
            print("   ❌ Nessun nodo trovato!")
            return []
        
        # Analizza campione di nodi
        node_data = []
        sample_count = min(sample_size, total_nodes)
        
        print(f"   Analizzando {sample_count} di {total_nodes:,} nodi...")
        
        # Itera sui primi nodi
        node_iterator = nodes.Iterator
        count = 0
        
        while node_iterator.Valid and count < sample_size:
            node = node_iterator.Item
            try:
                node_info = {
                    "id": node.AttValue("No"),
                    "x": round(node.AttValue("XCoord"), 2),
                    "y": round(node.AttValue("YCoord"), 2),
                    "type": node.AttValue("NodeType") if node.AttValue("NodeType") else "N/A"
                }
                node_data.append(node_info)
                
                if count < 5:  # Mostra primi 5
                    print(f"   Nodo {node_info['id']}: ({node_info['x']}, {node_info['y']}) Tipo: {node_info['type']}")
                
            except Exception as e:
                print(f"   ⚠️ Errore nodo {count+1}: {e}")
            
            node_iterator.Next()
            count += 1
        
        print(f"   ✅ {len(node_data)} nodi analizzati con successo")
        return node_data
        
    except Exception as e:
        print(f"❌ Errore analisi nodi: {e}")
        return []

def analyze_links(visum, sample_size=10):
    """Analizza i link della rete"""
    try:
        print(f"\n🔗 ANALISI LINK (campione di {sample_size}):")
        print("-" * 40)
        
        links = visum.Net.Links
        total_links = links.CountActive
        
        if total_links == 0:
            print("   ❌ Nessun link trovato!")
            return []
        
        # Analizza campione di link
        link_data = []
        sample_count = min(sample_size, total_links)
        
        print(f"   Analizzando {sample_count} di {total_links:,} link...")
        
        # Itera sui primi link
        link_iterator = links.Iterator
        count = 0
        
        while link_iterator.Valid and count < sample_size:
            link = link_iterator.Item
            try:
                link_info = {
                    "id": link.AttValue("No"),
                    "from_node": link.AttValue("FromNodeNo"),
                    "to_node": link.AttValue("ToNodeNo"),
                    "length": round(link.AttValue("Length"), 1),
                    "type": link.AttValue("TypeNo"),
                    "v0_prt": round(link.AttValue("V0_PrT"), 1) if link.AttValue("V0_PrT") else 0,
                    "capacity": link.AttValue("VolCapPrT") if link.AttValue("VolCapPrT") else 0
                }
                link_data.append(link_info)
                
                if count < 5:  # Mostra primi 5
                    print(f"   Link {link_info['id']}: {link_info['from_node']}→{link_info['to_node']}")
                    print(f"      Lung: {link_info['length']}m, V0: {link_info['v0_prt']}km/h, Cap: {link_info['capacity']}")
                
            except Exception as e:
                print(f"   ⚠️ Errore link {count+1}: {e}")
            
            link_iterator.Next()
            count += 1
        
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
        
        type_data = []
        type_iterator = link_types.Iterator
        
        while type_iterator.Valid:
            link_type = type_iterator.Item
            try:
                type_info = {
                    "id": link_type.AttValue("No"),
                    "name": link_type.AttValue("Name"),
                    "vmax": link_type.AttValue("VMax") if link_type.AttValue("VMax") else 0,
                    "default_v0": link_type.AttValue("DefaultV0_PrT") if link_type.AttValue("DefaultV0_PrT") else 0
                }
                type_data.append(type_info)
                
                print(f"   Tipo {type_info['id']}: {type_info['name']}")
                print(f"      VMax: {type_info['vmax']}km/h, V0 default: {type_info['default_v0']}km/h")
                
            except Exception as e:
                print(f"   ⚠️ Errore tipo link: {e}")
            
            type_iterator.Next()
        
        print(f"   ✅ {len(type_data)} tipi di link analizzati")
        return type_data
        
    except Exception as e:
        print(f"❌ Errore analisi tipi link: {e}")
        return []

def save_results(network_data, node_data, link_data, type_data):
    """Salva i risultati in file JSON"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"visum_analysis_python_{timestamp}.json"
        
        results = {
            "timestamp": timestamp,
            "project": "Campoleone Italferr 2025",
            "method": "VisumPy Python API",
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
        print("❌ Impossibile connettersi a Visum. Assicurati che sia aperto con il progetto.")
        return
    
    # Analisi completa
    print("\n🚀 Inizio analisi completa della rete...")
    
    # Panoramica rete
    network_data = get_network_overview(visum)
    
    # Analisi dettagliata
    node_data = analyze_nodes(visum, sample_size=20)
    link_data = analyze_links(visum, sample_size=20)
    type_data = analyze_link_types(visum)
    
    # Salva risultati
    filename = save_results(network_data, node_data, link_data, type_data)
    
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
    
    print("\n🐍 Analisi Python completata!")

if __name__ == "__main__":
    main()
