# Test COM con Visum avviato come amministratore
import sys
import time
sys.path.append(r"H:\Program Files\PTV Vision\PTV Visum 2025\Exe")

print("=== TEST COM CON VISUM AMMINISTRATORE ===")
print(f"Timestamp: {time.strftime('%H:%M:%S')}")

try:
    import win32com.client
    import pythoncom
    
    # Inizializza COM
    pythoncom.CoInitialize()
    print("✅ COM inizializzato")
    
    print("\n🔍 TEST 1: GetActiveObject")
    try:
        visum = win32com.client.GetActiveObject("Visum.Visum")
        print("🎉 SUCCESSO! GetActiveObject funziona con admin!")
        
        # Test immediato accesso rete
        nodes = visum.Net.Nodes.Count
        links = visum.Net.Links.Count
        zones = visum.Net.Zones.Count
        
        print(f"📊 RETE ACCESSIBILE:")
        print(f"   Nodi: {nodes:,}")
        print(f"   Link: {links:,}")
        print(f"   Zone: {zones:,}")
        
        if nodes > 0:
            print("🎯 PERFETTO! Visum admin ha progetto caricato!")
            
            # Test analisi veloce per confermare piena funzionalità
            print("\n🚀 TEST FUNZIONALITÀ COMPLETE:")
            
            # Accesso attributi link
            link_set = visum.Net.Links
            attrs = link_set.GetMultipleAttributes(['No', 'Length', 'NumLanes'])
            
            print(f"✅ Link attributes accessibili: {len(attrs)} link")
            
            # Sample di primi 3 link
            for i, (no, length, lanes) in enumerate(attrs[:3]):
                print(f"   Link {int(no)}: {length:.3f} km, {int(lanes)} corsie")
            
            # Accesso nodi
            node_set = visum.Net.Nodes
            node_attrs = node_set.GetMultipleAttributes(['No', 'XCoord', 'YCoord'])
            
            print(f"✅ Node attributes accessibili: {len(node_attrs)} nodi")
            
            # Sample coordinate primi 3 nodi
            for i, (no, x, y) in enumerate(node_attrs[:3]):
                print(f"   Nodo {int(no)}: ({x:.3f}, {y:.3f})")
            
            # Zone
            zone_set = visum.Net.Zones
            zone_attrs = zone_set.GetMultipleAttributes(['No', 'XCoord', 'YCoord'])
            
            print(f"✅ Zone attributes accessibili: {len(zone_attrs)} zone")
            
            # Statistiche rapide
            lengths = [attr[1] for attr in attrs[:100]]  # Prime 100
            avg_length = sum(lengths) / len(lengths)
            max_length = max(lengths)
            min_length = min(lengths)
            
            print(f"\n📈 ANALISI STATISTICA:")
            print(f"   Lunghezza media link: {avg_length:.3f} km")
            print(f"   Link più lungo: {max_length:.3f} km") 
            print(f"   Link più corto: {min_length:.3f} km")
            
            # Connettività
            connectivity = links / nodes
            print(f"   Connettività: {connectivity:.2f} link/nodo")
            
            # SUCCESSO TOTALE!
            result = {
                "timestamp": time.time(),
                "success": True,
                "method": "GetActiveObject_Admin",
                "network": {
                    "nodes": nodes,
                    "links": links,
                    "zones": zones
                },
                "statistics": {
                    "avg_length": avg_length,
                    "max_length": max_length,
                    "min_length": min_length,
                    "connectivity": connectivity
                },
                "sample_links": [
                    {"no": int(attr[0]), "length": float(attr[1]), "lanes": int(attr[2])}
                    for attr in attrs[:5]
                ]
            }
            
            import json
            with open(r"H:\visum-thinker-mcp-server\visum_admin_success.json", 'w') as f:
                json.dump(result, f, indent=2)
            
            print(f"\n🎉 RISULTATO SALVATO! GetActiveObject funziona con admin!")
            
        else:
            print("⚠️ Visum connesso ma progetto non caricato")
            
    except Exception as e:
        print(f"❌ GetActiveObject ancora fallito: {e}")
        
        # Prova altri metodi anche se GetActiveObject fallisce
        print(f"\n🔍 TEST 2: Dispatch con admin")
        try:
            visum = win32com.client.Dispatch("Visum.Visum")
            nodes = visum.Net.Nodes.Count
            print(f"✅ Dispatch funziona: {nodes:,} nodi")
            
            if nodes > 0:
                print("🎯 Dispatch ha accesso ai dati!")
        except Exception as e2:
            print(f"❌ Anche Dispatch fallito: {e2}")
    
    # Test ROT con admin
    print(f"\n🔍 TEST 3: Running Object Table con admin")
    try:
        rot = pythoncom.GetRunningObjectTable()
        enum_moniker = rot.EnumRunning()
        
        visum_found = False
        count = 0
        
        while True:
            try:
                monikers = enum_moniker.Next(1)
                if not monikers:
                    break
                    
                moniker = monikers[0]
                name = moniker.GetDisplayName(None, None)
                
                if 'visum' in name.lower() or 'ptv' in name.lower():
                    print(f"🎯 ROT Visum object: {name}")
                    try:
                        obj = rot.GetObject(moniker)
                        nodes = obj.Net.Nodes.Count
                        print(f"✅ ROT access success: {nodes:,} nodi")
                        visum_found = True
                    except:
                        print(f"❌ ROT object not accessible")
                
                count += 1
                if count > 20:  # Limita ricerca
                    break
                    
            except:
                break
        
        if visum_found:
            print("✅ ROT method works with admin!")
        else:
            print(f"❌ Nessun oggetto Visum in ROT (scansionati {count})")
    
    except Exception as e:
        print(f"❌ ROT test failed: {e}")
    
    pythoncom.CoUninitialize()
    
except ImportError:
    print("❌ win32com.client non disponibile")
except Exception as e:
    print(f"❌ Errore generale: {e}")

print(f"\n=== TEST COMPLETATO ===")
print("Controlla visum_admin_success.json per conferma!")