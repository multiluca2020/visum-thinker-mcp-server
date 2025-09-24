# Test per trovare istanze Visum attive
import sys
import os
sys.path.append(r"H:\Program Files\PTV Vision\PTV Visum 2025\Exe")

print("=== RICERCA ISTANZE VISUM ATTIVE ===")

# METODO 1: psutil per processi
try:
    # Proviamo a installare psutil se non c'è
    try:
        import psutil
        print("✅ psutil disponibile")
    except ImportError:
        print("❌ psutil non disponibile, provo subprocess...")
        import subprocess
        
        # Usa tasklist di Windows
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq Visum250.exe'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            visum_processes = [line for line in lines if 'Visum250.exe' in line]
            
            print(f"📋 Processi Visum trovati:")
            for proc in visum_processes:
                parts = proc.split()
                if len(parts) >= 2:
                    name = parts[0]
                    pid = parts[1]
                    print(f"   {name} - PID: {pid}")
            
            if visum_processes:
                print(f"✅ Trovati {len(visum_processes)} processi Visum")
            else:
                print("❌ Nessun processo Visum250.exe trovato")
        else:
            print("❌ tasklist fallito")

except Exception as e:
    print(f"❌ Errore ricerca processi: {e}")

# METODO 2: Running Object Table (ROT) COM
print(f"\n🔍 METODO 2: Running Object Table COM")
try:
    import win32com.client
    import pythoncom
    
    pythoncom.CoInitialize()
    
    # Get Running Object Table
    rot = pythoncom.GetRunningObjectTable()
    enum_moniker = rot.EnumRunning()
    
    print("📋 Oggetti COM attivi:")
    visum_objects = []
    count = 0
    
    while True:
        try:
            monikers = enum_moniker.Next(1)
            if not monikers:
                break
                
            moniker = monikers[0]
            name = moniker.GetDisplayName(None, None)
            
            print(f"   {count}: {name}")
            
            # Cerca oggetti che potrebbero essere Visum
            if any(keyword in name.lower() for keyword in ['visum', 'ptv']):
                print(f"   🎯 VISUM CANDIDATE: {name}")
                try:
                    obj = rot.GetObject(moniker)
                    visum_objects.append((name, obj))
                    print(f"      ✅ Oggetto acquisito: {type(obj)}")
                    
                    # Test se ha interfaccia Visum
                    if hasattr(obj, 'Net'):
                        nodes = obj.Net.Nodes.Count
                        links = obj.Net.Links.Count
                        print(f"      🎉 VISUM TROVATO! Nodi: {nodes:,}, Link: {links:,}")
                        
                        # Salva questo successo
                        with open(r"H:\visum-thinker-mcp-server\active_visum_found.txt", 'w') as f:
                            f.write(f"FOUND: {name}\nNodes: {nodes}\nLinks: {links}")
                            
                    else:
                        print(f"      ❌ Non ha interfaccia Visum")
                        
                except Exception as obj_e:
                    print(f"      ❌ Errore accesso oggetto: {obj_e}")
            
            count += 1
            if count > 50:  # Limita la ricerca
                print("   ... (limitato a 50 oggetti)")
                break
                
        except:
            break
    
    print(f"📊 Totale oggetti COM: {count}")
    print(f"🎯 Candidati Visum: {len(visum_objects)}")
    
    pythoncom.CoUninitialize()
    
except Exception as e:
    print(f"❌ ROT search failed: {e}")

# METODO 3: Enumerazione finestre Windows
print(f"\n🔍 METODO 3: Windows enumeration")
try:
    import win32gui
    import win32process
    
    visum_windows = []
    
    def enum_windows_callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            window_title = win32gui.GetWindowText(hwnd)
            if window_title and 'visum' in window_title.lower():
                # Ottieni PID del processo
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                windows.append((hwnd, window_title, pid))
        return True
    
    win32gui.EnumWindows(enum_windows_callback, visum_windows)
    
    print(f"📋 Finestre Visum trovate:")
    for hwnd, title, pid in visum_windows:
        print(f"   HWND: {hwnd}, PID: {pid}")
        print(f"   Title: {title}")
        
        # Prova ad ottenere handle processo
        try:
            import win32api
            process_handle = win32api.OpenProcess(0x0400, False, pid)  # PROCESS_QUERY_INFORMATION
            print(f"   ✅ Process handle ottenuto")
            win32api.CloseHandle(process_handle)
        except Exception as proc_e:
            print(f"   ❌ Process handle fallito: {proc_e}")
    
    if visum_windows:
        print(f"✅ Trovate {len(visum_windows)} finestre Visum")
        
        # Salva info finestre
        with open(r"H:\visum-thinker-mcp-server\visum_windows_found.txt", 'w') as f:
            for hwnd, title, pid in visum_windows:
                f.write(f"HWND: {hwnd}, PID: {pid}, Title: {title}\n")
    else:
        print("❌ Nessuna finestra Visum trovata")
        
except Exception as e:
    print(f"❌ Windows enumeration failed: {e}")

# METODO 4: COM GetActiveObject con timeout
print(f"\n🔍 METODO 4: GetActiveObject con retry")
try:
    import win32com.client
    import time
    
    # Lista di ProgID da provare
    progids = [
        "Visum.Visum",
        "Visum.Application",
        "PTV.Visum",
        "VisumApp.Application"
    ]
    
    for progid in progids:
        print(f"   Tentativo: {progid}")
        for attempt in range(3):  # 3 tentativi
            try:
                visum_obj = win32com.client.GetActiveObject(progid)
                print(f"   ✅ {progid} SUCCESSO al tentativo {attempt + 1}!")
                
                # Test funzionalità
                nodes = visum_obj.Net.Nodes.Count
                links = visum_obj.Net.Links.Count
                
                print(f"   📊 Nodi: {nodes:,}, Link: {links:,}")
                
                if nodes > 0:
                    print(f"   🎉 VISUM ATTIVO CON DATI TROVATO!")
                    with open(r"H:\visum-thinker-mcp-server\getactive_success.txt", 'w') as f:
                        f.write(f"SUCCESS: {progid}\nNodes: {nodes}\nLinks: {links}")
                    break
                    
            except Exception as e:
                print(f"   ❌ Tentativo {attempt + 1}: {e}")
                if attempt < 2:  # Non aspettare all'ultimo tentativo
                    time.sleep(1)
        else:
            continue
        break  # Se arriviamo qui, abbiamo trovato qualcosa
    
except Exception as e:
    print(f"❌ GetActiveObject tests failed: {e}")

print(f"\n=== RICERCA COMPLETATA ===")
print("Controlla i file di output per i risultati")