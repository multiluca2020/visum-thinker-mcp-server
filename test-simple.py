# Test semplice e diretto - concentrato sull'accesso base
import sys
import time

print("=== TEST SEMPLICE ACCESSO VISUM ===")

# Prova il metodo più diretto possibile
try:
    # METODO A: Variabile globale Visum (dovrebbe esistere negli script Visum)
    print("Test A: Variabile globale Visum")
    try:
        visum_app = Visum
        print(f"✅ TROVATO! Tipo: {type(visum_app)}")
        
        # Test accesso rete
        nodes = visum_app.Net.Nodes.Count
        links = visum_app.Net.Links.Count
        
        print(f"📊 RETE:")
        print(f"   Nodi: {nodes:,}")  
        print(f"   Link: {links:,}")
        
        if nodes > 0:
            print("🎉 SUCCESSO COMPLETO!")
            
            # Salva conferma
            with open("visum_success.txt", "w") as f:
                f.write(f"SUCCESS: {nodes} nodes, {links} links")
                
        else:
            print("⚠️ Visum trovato ma rete vuota")
            with open("visum_empty.txt", "w") as f:
                f.write("Visum found but empty network")
                
    except NameError:
        print("❌ Variabile 'Visum' non trovata")
        
    except Exception as e:
        print(f"❌ Errore accesso Visum: {e}")

except Exception as e:
    print(f"❌ Errore generale: {e}")

# METODO B: COM come fallback
try:
    print("\nTest B: COM fallback")
    import win32com.client
    
    visum_com = win32com.client.Dispatch("Visum.Visum")
    nodes_com = visum_com.Net.Nodes.Count
    
    print(f"COM - Nodi: {nodes_com:,}")
    
    if nodes_com > 0:
        print("✅ COM con dati!")
        with open("visum_com_success.txt", "w") as f:
            f.write(f"COM SUCCESS: {nodes_com} nodes")
    else:
        print("⚠️ COM senza dati")
        
except Exception as e:
    print(f"❌ COM fallito: {e}")

print("=== TEST COMPLETATO ===")