import sys
sys.path.append(r"H:\Program Files\PTV Vision\PTV Visum 2025\Exe")

try:
    print("=== TEST DIRETTO PYTHON VISUM ===")
    print("Tentativo connessione a Visum attivo...")
    
    import win32com.client
    
    # Test GetActiveObject (dovrebbe funzionare se Visum è già aperto)
    try:
        visum = win32com.client.GetActiveObject("Visum.Visum")
        print("✅ CONNESSO a istanza Visum attiva!")
        
        # Test accesso dati rete
        nodes = visum.Net.Nodes.Count
        links = visum.Net.Links.Count  
        zones = visum.Net.Zones.Count
        
        print(f"📊 STATISTICHE RETE:")
        print(f"   Nodi: {nodes:,}")
        print(f"   Link: {links:,}")
        print(f"   Zone: {zones:,}")
        
        if nodes > 0:
            print("🎯 SUCCESSO! Rete attiva con dati")
            
            # Test accesso dettagli link
            if links > 0:
                print("🔍 Test accesso primo link...")
                try:
                    # Prova diversi metodi di accesso
                    first_link = visum.Net.Links.ItemByKey(1, 1)  # From-To node
                    print("✅ ItemByKey funziona")
                except:
                    try:
                        link_collection = visum.Net.Links
                        print(f"✅ Collezione Links accessibile: {link_collection}")
                    except Exception as e:
                        print(f"❌ Errore accesso link: {e}")
        else:
            print("⚠️ Rete vuota - progetto non caricato in COM")
            
    except Exception as active_error:
        print(f"❌ GetActiveObject fallito: {active_error}")
        
        # Fallback: DispatchEx
        try:
            print("🔄 Tentativo DispatchEx...")
            visum = win32com.client.DispatchEx("Visum.Visum")
            print("✅ DispatchEx riuscito (nuova istanza)")
            
            nodes = visum.Net.Nodes.Count
            links = visum.Net.Links.Count
            print(f"   Nodi: {nodes}, Link: {links}")
            
        except Exception as dispatch_error:
            print(f"❌ Anche DispatchEx fallito: {dispatch_error}")

except Exception as e:
    print(f"❌ ERRORE GENERALE: {e}")
    import traceback
    traceback.print_exc()

print("\n=== TEST COMPLETATO ===")