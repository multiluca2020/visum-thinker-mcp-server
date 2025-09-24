import sys
sys.path.append(r"H:\Program Files\PTV Vision\PTV Visum 2025\Exe")

try:
    import win32com.client
    print("Python MCP Test")
    print("=" * 20)
    
    # Prova connessione
    try:
        visum = win32com.client.GetActiveObject("Visum.Visum")
        print("OK GetActiveObject")
    except:
        print("GetActiveObject fallito, provo DispatchEx...")
        visum = win32com.client.DispatchEx("Visum.Visum") 
        print("OK DispatchEx")
    
    # Test rete
    nodes = visum.Net.Nodes.Count
    links = visum.Net.Links.Count
    
    print(f"Nodi: {nodes}")
    print(f"Link: {links}")
    
    if nodes == 0:
        print("Carico progetto...")
        try:
            visum.LoadNet(r"H:\go\italferr2025\Campoleone\100625_Versione_base_v0.3_sub_ok_priv.ver")
            nodes2 = visum.Net.Nodes.Count
            links2 = visum.Net.Links.Count
            print(f"Nodi (dopo caricamento): {nodes2}")
            print(f"Link (dopo caricamento): {links2}")
            
            if nodes2 > 0:
                print("SUCCESSO! Progetto caricato via COM")
                
                # Test accesso dati
                if links2 > 0:
                    print("Test accesso primo link...")
                    try:
                        first_link = visum.Net.Links.ItemByKey(1, 1)  # From node 1, To node 1
                        length = first_link.GetAttValue("Length")
                        print(f"Primo link - Lunghezza: {length}")
                    except:
                        print("Errore accesso primo link")
                        # Prova approccio alternativo
                        try:
                            all_links = visum.Net.Links
                            print(f"Collezione links accessibile: {all_links}")
                        except Exception as e2:
                            print(f"Errore collezione links: {e2}")
            else:
                print("Progetto non caricato o vuoto")
        except Exception as load_error:
            print(f"Errore caricamento: {load_error}")
    else:
        print("Rete gia' presente!")
    
    print("\nTest MCP completato!")
    
except Exception as e:
    print(f"Errore MCP: {e}")
    import traceback
    traceback.print_exc()
