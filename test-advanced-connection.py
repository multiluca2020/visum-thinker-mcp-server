import sys
import time
import os
sys.path.append(r"H:\Program Files\PTV Vision\PTV Visum 2025\Exe")

print("=== RICERCA SOLUZIONI ALTERNATIVE GETACTIVEOBJECT ===")
print("Visum 2025 - Test metodi avanzati di connessione\n")

try:
    import win32com.client
    
    # METODO 1: ROT (Running Object Table) diretto
    print("🔍 METODO 1: Running Object Table (ROT)")
    try:
        import pythoncom
        pythoncom.CoInitialize()
        
        rot = pythoncom.GetRunningObjectTable()
        enum = rot.EnumRunning()
        
        found_visum = False
        while True:
            try:
                monikers = enum.Next(1)
                if not monikers:
                    break
                
                moniker = monikers[0]
                name = moniker.GetDisplayName(None, None)
                print(f"   ROT Object: {name}")
                
                # Cerca oggetti Visum
                if any(keyword in name.lower() for keyword in ['visum', 'ptv']):
                    print(f"   🎯 Possibile oggetto Visum: {name}")
                    try:
                        obj = rot.GetObject(moniker)
                        print(f"   ✅ Oggetto acquisito: {type(obj)}")
                        
                        # Test se è Visum
                        if hasattr(obj, 'Net'):
                            visum = obj
                            nodes = visum.Net.Nodes.Count
                            print(f"   🎉 VISUM TROVATO! Nodi: {nodes:,}")
                            found_visum = True
                            break
                    except Exception as e:
                        print(f"   ❌ Errore accesso oggetto: {e}")
                        
            except:
                break
                
        if not found_visum:
            print("   ❌ Nessun oggetto Visum trovato in ROT")
            
    except Exception as e:
        print(f"   ❌ ROT fallito: {e}")
    
    # METODO 2: CLSID diretti
    print(f"\n🔍 METODO 2: CLSID Visum diretti")
    clsids_to_try = [
        "{B86F87C1-D586-11D3-B6BB-0050DAB88A76}",  # Visum.Application
        "{B86F87C0-D586-11D3-B6BB-0050DAB88A76}",  # Visum.Visum possibile
        "{9B3F8CE0-4C8C-11D4-B6C4-0050DAB88A76}",  # Alternative
    ]
    
    for clsid in clsids_to_try:
        try:
            print(f"   Tentativo CLSID: {clsid}")
            visum = win32com.client.GetActiveObject(clsid)
            nodes = visum.Net.Nodes.Count
            print(f"   🎉 SUCCESSO! Nodi: {nodes:,}")
            break
        except Exception as e:
            print(f"   ❌ Fallito: {e}")
    
    # METODO 3: ProgID alternativi
    print(f"\n🔍 METODO 3: ProgID alternativi")
    progids = [
        "Visum.Application",
        "PTV.Visum",
        "PTVVisum.Application", 
        "Visum.Visum.25",
        "Visum.Document",
    ]
    
    for progid in progids:
        try:
            print(f"   Tentativo ProgID: {progid}")
            visum = win32com.client.GetActiveObject(progid)
            nodes = visum.Net.Nodes.Count
            print(f"   🎉 SUCCESSO! Nodi: {nodes:,}")
            break
        except Exception as e:
            print(f"   ❌ {progid} fallito: {e}")
    
    # METODO 4: COM Interface diretta
    print(f"\n🔍 METODO 4: Interface COM diretta")
    try:
        import win32api
        import win32gui
        
        # Trova finestra Visum
        def enum_windows_proc(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                if 'visum' in window_text.lower():
                    windows.append((hwnd, window_text))
            return True
            
        windows = []
        win32gui.EnumWindows(enum_windows_proc, windows)
        
        for hwnd, title in windows:
            print(f"   Finestra Visum: {title} (HWND: {hwnd})")
            
            # Prova ad ottenere oggetto COM dalla finestra
            try:
                # Metodo AccessibleObjectFromWindow (se disponibile)
                pass
            except:
                pass
                
        if not windows:
            print("   ❌ Nessuna finestra Visum trovata")
            
    except Exception as e:
        print(f"   ❌ Interface diretta fallita: {e}")
    
    # METODO 5: DDE (Dynamic Data Exchange)
    print(f"\n🔍 METODO 5: DDE Communication")
    try:
        # Visum potrebbe supportare DDE
        import win32ui
        import dde
        print("   DDE disponibile per test...")
        # Test DDE connection to Visum
    except ImportError:
        print("   ❌ DDE non disponibile (win32ui/dde)")
    except Exception as e:
        print(f"   ❌ DDE fallito: {e}")
    
    # METODO 6: Named Pipes/Memory Mapped Files
    print(f"\n🔍 METODO 6: Communication alternatives")
    
    # Controlla se Visum crea named pipes
    import glob
    pipes = glob.glob(r"\\.\pipe\*visum*", recursive=False)
    if pipes:
        print(f"   🎯 Named pipes Visum trovati: {pipes}")
    else:
        print("   ❌ Nessun named pipe Visum")
    
    # METODO 7: Reflection/Registry
    print(f"\n🔍 METODO 7: Registry inspection")
    try:
        import winreg
        
        # Cerca chiavi Visum nel registry
        key_paths = [
            r"SOFTWARE\Classes\Visum.Visum",
            r"SOFTWARE\Classes\Visum.Application", 
            r"SOFTWARE\PTV Group",
            r"SOFTWARE\Wow6432Node\PTV Group",
        ]
        
        for key_path in key_paths:
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
                print(f"   ✅ Chiave trovata: {key_path}")
                
                # Enumera sottochiavi
                i = 0
                while True:
                    try:
                        subkey = winreg.EnumKey(key, i)
                        print(f"      Sottochiave: {subkey}")
                        i += 1
                        if i > 5:  # Limita output
                            break
                    except WindowsError:
                        break
                winreg.CloseKey(key)
                
            except WindowsError:
                print(f"   ❌ Chiave non trovata: {key_path}")
                
    except Exception as e:
        print(f"   ❌ Registry inspection fallita: {e}")

    print(f"\n" + "="*60)
    print("🤔 ALTERNATIVE SE GETACTIVEOBJECT NON FUNZIONA:")
    print("="*60)
    print("1. 🔄 File Watcher - Monitor modifiche file progetto")
    print("2. 📡 IPC - Comunicazione inter-processo custom")
    print("3. 🗂️ Temp Export - Visum esporta, MCP legge")
    print("4. 📋 Clipboard - Trasferimento dati via clipboard") 
    print("5. 🖥️ Screen Scraping - OCR dati da GUI")
    print("6. 🔌 Plugin Visum - Estensione VAL custom")
    print("7. 🌐 HTTP API - Server locale in Visum")

except Exception as e:
    print(f"❌ ERRORE GENERALE: {e}")
    import traceback
    traceback.print_exc()

print(f"\n=== RICERCA COMPLETATA ===")
print("Determiniamo la migliore alternativa possibile...")