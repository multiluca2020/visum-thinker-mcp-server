import sys
sys.path.append(r"H:\Program Files\PTV Vision\PTV Visum 2025\Exe")

try:
    import win32com.client
    print("=== TEST CONNESSIONE VISUM ===")
    
    # Test 1: GetActiveObject
    print("\n1. Test GetActiveObject:")
    try:
        visum = win32com.client.GetActiveObject("Visum.Visum")
        print("   SUCCESSO - GetActiveObject connesso!")
        
        nodes = visum.Net.Nodes.Count
        links = visum.Net.Links.Count
        print(f"   Nodi: {nodes}, Link: {links}")
        
        if nodes > 0:
            print("   OTTIMO! Rete con dati disponibile via GetActiveObject")
            exit(0)  # Successo totale
        else:
            print("   Connesso ma rete vuota")
            
    except Exception as e:
        print(f"   FALLITO: {e}")
    
    # Test 2: Dispatch (crea istanza)
    print("\n2. Test Dispatch (nuova istanza):")
    try:
        visum = win32com.client.Dispatch("Visum.Visum")
        print("   SUCCESSO - Dispatch connesso!")
        
        nodes = visum.Net.Nodes.Count
        links = visum.Net.Links.Count
        print(f"   Nodi: {nodes}, Link: {links}")
        
    except Exception as e:
        print(f"   FALLITO: {e}")
    
    # Test 3: DispatchEx (crea istanza fuori processo)
    print("\n3. Test DispatchEx (fuori processo):")
    try:
        visum = win32com.client.DispatchEx("Visum.Visum")
        print("   SUCCESSO - DispatchEx connesso!")
        
        nodes = visum.Net.Nodes.Count
        links = visum.Net.Links.Count
        print(f"   Nodi: {nodes}, Link: {links}")
        
    except Exception as e:
        print(f"   FALLITO: {e}")
    
    print("\n=== CONCLUSIONE ===")
    print("Visum COM disponibile ma probabilmente senza progetto caricato automaticamente")
    print("Soluzione: lanciare Visum con progetto, poi usare GetActiveObject")
    
except Exception as e:
    print(f"Errore generale: {e}")
    import traceback
    traceback.print_exc()
