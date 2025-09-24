import sys
import time
sys.path.append(r"H:\Program Files\PTV Vision\PTV Visum 2025\Exe")

print("=== TEST CONNESSIONE A VISUM GUI APERTO ===")
print(f"Timestamp: {time.strftime('%H:%M:%S')}")

try:
    import win32com.client
    
    print("\n🔍 TENTATIVO 1: GetActiveObject('Visum.Visum')")
    try:
        visum = win32com.client.GetActiveObject("Visum.Visum")
        print("✅ CONNESSIONE RIUSCITA!")
        
        # Test accesso immediato alla rete
        nodes = visum.Net.Nodes.Count
        links = visum.Net.Links.Count
        zones = visum.Net.Zones.Count
        
        print(f"📊 DATI RETE:")
        print(f"   Nodi: {nodes:,}")
        print(f"   Link: {links:,}")  
        print(f"   Zone: {zones:,}")
        
        if nodes > 0:
            print("🎯 SUCCESSO COMPLETO! GUI Visum accessibile con progetto caricato")
            
            # Test analisi veloce
            print("\n🚀 TEST ANALISI SU ISTANZA GUI:")
            start_time = time.time()
            
            # Analisi link
            link_set = visum.Net.Links
            attrs = link_set.GetMultipleAttributes(['No', 'Length', 'NumLanes'])
            sample = attrs[:5]
            
            total_length = sum([attr[1] for attr in sample])
            avg_length = total_length / len(sample)
            
            end_time = time.time()
            
            print(f"   Campione 5 link analizzati in {end_time - start_time:.3f}s")
            print(f"   Lunghezza media: {avg_length:.3f} km")
            
            # Test disconnessione e riconnessione
            print("\n🔄 TEST DISCONNESSIONE/RICONNESSIONE:")
            
            # "Disconnessione" (elimina riferimento)
            del visum
            print("   ✅ Riferimento COM eliminato")
            
            time.sleep(2)
            
            # Riconnessione
            visum2 = win32com.client.GetActiveObject("Visum.Visum")
            nodes2 = visum2.Net.Nodes.Count
            print(f"   ✅ Riconnesso! Nodi: {nodes2:,}")
            
            if nodes2 == nodes:
                print("   🎯 PERFETTO! Stessa istanza, stessi dati")
                
                print("\n" + "="*50)
                print("🎉 WORKFLOW CONFERMATO FUNZIONANTE!")
                print("="*50)
                print("✅ 1. Utente apre Visum GUI ✓")
                print("✅ 2. Progetto caricato visibile ✓")
                print("✅ 3. MCP si connette via GetActiveObject ✓")
                print("✅ 4. Analisi completata ✓")
                print("✅ 5. Disconnessione pulita ✓") 
                print("✅ 6. Riconnessione immediata ✓")
                print("\n💡 IL WORKFLOW RICHIESTO È POSSIBILE!")
                
            else:
                print("   ⚠️ Dati diversi dopo riconnessione")
        else:
            print("⚠️ Connesso ma progetto non caricato nell'istanza GUI")
            
    except Exception as e:
        print(f"❌ GetActiveObject fallito: {e}")
        print("   Possibili cause:")
        print("   - Visum non ancora completamente avviato")
        print("   - Problema registrazione COM")
        print("   - Visum 2025 non supporta GetActiveObject")
        
        print("\n🔍 TENTATIVO 2: Verifica processo Visum")
        try:
            import psutil
            visum_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if 'visum' in proc.info['name'].lower():
                    visum_processes.append(proc.info)
            
            if visum_processes:
                print(f"✅ Trovati {len(visum_processes)} processi Visum:")
                for proc in visum_processes:
                    print(f"   PID: {proc['pid']}, Nome: {proc['name']}")
                print("   → Visum è in esecuzione ma non accessibile via COM")
            else:
                print("❌ Nessun processo Visum trovato")
                
        except ImportError:
            print("   (psutil non disponibile per verifica processi)")
        except Exception as proc_error:
            print(f"   Errore verifica processi: {proc_error}")

except Exception as e:
    print(f"❌ ERRORE GENERALE: {e}")
    import traceback
    traceback.print_exc()

print(f"\n=== TEST COMPLETATO {time.strftime('%H:%M:%S')} ===")