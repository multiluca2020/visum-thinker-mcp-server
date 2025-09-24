# Test connessione forzata all'istanza admin con progetto caricato
import sys
import time
sys.path.append(r"H:\Program Files\PTV Vision\PTV Visum 2025\Exe")

print("=== CONNESSIONE FORZATA ISTANZA ADMIN ===")
print("ISTRUZIONI: Carica il progetto Campoleone in Visum admin prima di continuare")

try:
    import win32com.client
    import pythoncom
    
    pythoncom.CoInitialize()
    
    # Aspetta che l'utente carichi il progetto
    print("\n⏳ Aspetto 10 secondi per il caricamento del progetto...")
    time.sleep(10)
    
    print("\n🔍 Tentativo connessione post-caricamento progetto...")
    
    # METODO 1: GetActiveObject (ora dovrebbe funzionare)
    try:
        print("Test GetActiveObject...")
        visum = win32com.client.GetActiveObject("Visum.Visum")
        
        nodes = visum.Net.Nodes.Count
        links = visum.Net.Links.Count
        
        print(f"✅ GetActiveObject SUCCESS!")
        print(f"   Nodi: {nodes:,}, Link: {links:,}")
        
        if nodes > 0:
            print("🎉 PROGETTO CARICATO E ACCESSIBILE!")
            
            # Salva il successo
            import json
            success_data = {
                "timestamp": time.time(),
                "method": "GetActiveObject",
                "nodes": nodes,
                "links": links,
                "status": "SUCCESS - Full access to loaded project"
            }
            
            with open(r"H:\visum-thinker-mcp-server\final_success.json", 'w') as f:
                json.dump(success_data, f, indent=2)
            
            print("💾 Successo salvato in final_success.json")
            
    except Exception as e:
        print(f"❌ GetActiveObject failed: {e}")
        
        # METODO 2: Dispatch con retry
        print("\nTest Dispatch con retry...")
        
        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                visum = win32com.client.Dispatch("Visum.Visum")
                nodes = visum.Net.Nodes.Count
                
                print(f"   Tentativo {attempt + 1}: {nodes:,} nodi")
                
                if nodes > 0:
                    print(f"✅ DISPATCH SUCCESS al tentativo {attempt + 1}!")
                    
                    links = visum.Net.Links.Count
                    zones = visum.Net.Zones.Count
                    
                    print(f"   Link: {links:,}, Zone: {zones:,}")
                    
                    # Test completo funzionalità
                    link_attrs = visum.Net.Links.GetMultipleAttributes(['No', 'Length'])
                    print(f"   ✅ Attributi link accessibili: {len(link_attrs)}")
                    
                    # Salva successo
                    import json
                    success_data = {
                        "timestamp": time.time(),
                        "method": f"Dispatch_Attempt_{attempt + 1}",
                        "nodes": nodes,
                        "links": links,
                        "zones": zones,
                        "status": "SUCCESS - Dispatch with loaded project"
                    }
                    
                    with open(r"H:\visum-thinker-mcp-server\final_success.json", 'w') as f:
                        json.dump(success_data, f, indent=2)
                    
                    print("🎉 SUCCESSO TOTALE! MCP può ora funzionare!")
                    break
                    
                elif attempt < max_attempts - 1:
                    print(f"   Rete vuota, aspetto 3 secondi...")
                    time.sleep(3)
                    
            except Exception as e:
                print(f"   Tentativo {attempt + 1} fallito: {e}")
                if attempt < max_attempts - 1:
                    time.sleep(2)
        else:
            print("❌ Tutti i tentativi Dispatch falliti")
    
    # METODO 3: ROT con progetto caricato
    print(f"\n🔍 Test ROT con progetto caricato...")
    try:
        rot = pythoncom.GetRunningObjectTable()
        enum_moniker = rot.EnumRunning()
        
        print("Scansione oggetti COM...")
        count = 0
        
        while True:
            try:
                monikers = enum_moniker.Next(1)
                if not monikers:
                    break
                
                moniker = monikers[0]
                name = moniker.GetDisplayName(None, None)
                
                # Mostra tutti gli oggetti per debug
                if count < 10:  # Prime 10 per debug
                    print(f"   {count}: {name}")
                
                if any(keyword in name.lower() for keyword in ['visum', 'ptv']):
                    print(f"🎯 TROVATO VISUM IN ROT: {name}")
                    
                    try:
                        obj = rot.GetObject(moniker)
                        nodes = obj.Net.Nodes.Count
                        
                        if nodes > 0:
                            print(f"🎉 ROT SUCCESS: {nodes:,} nodi!")
                            
                            import json
                            success_data = {
                                "timestamp": time.time(),
                                "method": "ROT",
                                "moniker": name,
                                "nodes": nodes,
                                "status": "SUCCESS - ROT with loaded project"
                            }
                            
                            with open(r"H:\visum-thinker-mcp-server\final_success.json", 'w') as f:
                                json.dump(success_data, f, indent=2)
                            
                    except Exception as obj_e:
                        print(f"   Oggetto non accessibile: {obj_e}")
                
                count += 1
                if count > 50:  # Limita scansione
                    break
                    
            except:
                break
        
        print(f"ROT scan completata: {count} oggetti")
        
    except Exception as e:
        print(f"❌ ROT test failed: {e}")
    
    pythoncom.CoUninitialize()

except ImportError:
    print("❌ win32com non disponibile")
except Exception as e:
    print(f"❌ Errore generale: {e}")

print(f"\n=== ISTRUZIONI FINALI ===")
print("1. 📂 Carica il progetto Campoleone in Visum admin")
print("2. 🔄 Ri-esegui questo script")
print("3. ✅ Dovrebbe trovare il progetto e accedervi")
print("4. 🚀 Poi implementiamo nell'MCP server!")

print(f"\n=== TEST COMPLETATO ===")
print("Controlla final_success.json se il test ha avuto successo")