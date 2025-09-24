import sys
import time
sys.path.append(r"H:\Program Files\PTV Vision\PTV Visum 2025\Exe")

def test_connection_to_running_visum():
    """
    Test se possiamo connetterci a Visum già in esecuzione
    """
    print("=== TEST CONNESSIONE A VISUM GIÀ APERTO ===")
    
    try:
        import win32com.client
        
        print("🔍 Tentativo 1: GetActiveObject (standard)")
        try:
            visum = win32com.client.GetActiveObject("Visum.Visum")
            print("✅ SUCCESSO! Connesso a istanza attiva con GetActiveObject")
            
            # Test accesso dati
            nodes = visum.Net.Nodes.Count
            links = visum.Net.Links.Count
            print(f"   Rete: {nodes:,} nodi, {links:,} link")
            
            if nodes > 0:
                print("✅ Progetto caricato e accessibile!")
                return True, "GetActiveObject"
            else:
                print("⚠️ Connesso ma rete vuota")
                return False, "GetActiveObject - empty"
                
        except Exception as e:
            print(f"❌ GetActiveObject fallito: {e}")
        
        print("\n🔍 Tentativo 2: GetActiveObject con ProgID alternativo")
        try:
            visum = win32com.client.GetActiveObject("Visum.Application")
            print("✅ Connesso con Visum.Application")
            nodes = visum.Net.Nodes.Count
            print(f"   Nodi: {nodes:,}")
            return True, "Visum.Application"
        except Exception as e:
            print(f"❌ Visum.Application fallito: {e}")
            
        print("\n🔍 Tentativo 3: Dispatch con istanza esistente")
        try:
            visum = win32com.client.Dispatch("Visum.Visum")
            print("✅ Dispatch riuscito")
            nodes = visum.Net.Nodes.Count
            print(f"   Nodi: {nodes:,}")
            if nodes > 0:
                return True, "Dispatch - existing"
            else:
                return False, "Dispatch - new instance"
        except Exception as e:
            print(f"❌ Dispatch fallito: {e}")
            
        print("\n🔍 Tentativo 4: Enumerazione processi COM")
        try:
            import pythoncom
            pythoncom.CoInitialize()
            
            # Prova a enumerare oggetti COM attivi
            rot = pythoncom.GetRunningObjectTable()
            print("✅ Running Object Table accessibile")
            
            # Enumera oggetti
            enum = rot.EnumRunning()
            count = 0
            while True:
                try:
                    monikers = enum.Next(1)
                    if not monikers:
                        break
                    
                    moniker = monikers[0]
                    name = moniker.GetDisplayName(None, None)
                    print(f"   Oggetto COM: {name}")
                    
                    if "visum" in name.lower():
                        print(f"   🎯 Trovato oggetto Visum: {name}")
                        try:
                            obj = rot.GetObject(moniker)
                            print("   ✅ Oggetto acquisito!")
                            return True, f"ROT - {name}"
                        except:
                            print("   ❌ Non riesco ad acquisire l'oggetto")
                    
                    count += 1
                    if count > 20:  # Limita la ricerca
                        break
                        
                except:
                    break
                    
            print(f"   Enumerati {count} oggetti COM, nessun Visum trovato")
            
        except Exception as e:
            print(f"❌ Enumerazione ROT fallita: {e}")
            
        return False, "All methods failed"
        
    except Exception as e:
        print(f"❌ ERRORE GENERALE: {e}")
        return False, f"Error: {e}"

def test_workflow_simulation():
    """
    Simula il workflow: apri -> connetti -> disconnetti -> riconnetti
    """
    print("\n" + "="*60)
    print("SIMULAZIONE WORKFLOW UTENTE")
    print("="*60)
    
    print("📋 ISTRUZIONI PER L'UTENTE:")
    print("1. Apri Visum manualmente")
    print("2. Carica il progetto Campoleone nella GUI")
    print("3. Premi INVIO qui per testare la connessione")
    
    input("\n⏳ Premi INVIO quando Visum è aperto con progetto caricato...")
    
    # Test connessione
    success, method = test_connection_to_running_visum()
    
    if success:
        print(f"\n🎯 SUCCESSO! Connessione riuscita con metodo: {method}")
        print("\n📋 WORKFLOW POSSIBILE:")
        print("✅ 1. Utente apre Visum GUI")
        print("✅ 2. Utente carica progetto")
        print("✅ 3. Claude si connette per analisi")
        print("✅ 4. Claude chiude connessione")
        print("✅ 5. Claude si riconnette per analisi successive")
        
    else:
        print(f"\n❌ FALLITO: {method}")
        print("\n📋 ALTERNATIVA NECESSARIA:")
        print("🔄 1. Claude crea istanza COM propria")
        print("🔄 2. Claude carica progetto via codice")
        print("🔄 3. Claude mantiene istanza persistente")
        print("🔄 4. Utente può comunque vedere Visum se visibile=True")

if __name__ == "__main__":
    # Prima test senza GUI aperta
    print("FASE 1: Test senza Visum aperto")
    success, method = test_connection_to_running_visum()
    
    if not success:
        print("\n" + "="*50)
        print("COME PREVISTO: Nessuna istanza attiva da acquisire")
        print("="*50)
        
        # Ora simula workflow con GUI
        test_workflow_simulation()
    else:
        print(f"\nSORPRESA! Connessione riuscita anche senza GUI: {method}")