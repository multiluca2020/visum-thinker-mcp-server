import sys
import win32com.client

try:
    print("🔍 Tentativo connessione a Visum...")
    
    # Prova GetActiveObject
    try:
        visum = win32com.client.GetActiveObject("Visum.Visum")
        print("✅ GetActiveObject riuscito!")
    except Exception as e:
        print(f"❌ GetActiveObject fallito: {e}")
        
        # Prova DispatchEx
        try:
            visum = win32com.client.DispatchEx("Visum.Visum")
            print("✅ DispatchEx riuscito!")
        except Exception as e2:
            print(f"❌ DispatchEx fallito: {e2}")
            sys.exit(1)
    
    # Testa la connessione
    print(f"🔢 Nodi: {visum.Net.Nodes.Count}")
    print(f"🔗 Link: {visum.Net.Links.Count}")
    print(f"🏭 Zone: {visum.Net.Zones.Count}")
    
    if visum.Net.Nodes.Count > 0:
        print("🎯 Rete attiva!")
    else:
        print("⚠️ Rete vuota - nessun progetto caricato?")
        
except Exception as e:
    print(f"❌ Errore generale: {e}")
