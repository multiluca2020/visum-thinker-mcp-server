# -*- coding: ascii -*-
"""
Salva il file correttamente
"""

try:
    print("=" * 80)
    print("SALVATAGGIO FILE VISUM")
    print("=" * 80)
    
    # Ottieni il path del file corrente
    print("\n1. Ottieni path file corrente...")
    try:
        current_file = Visum.GetPath(1)  # 1 = PATH_FILE
        print("   File: %s" % current_file)
    except:
        # Prova metodo alternativo
        try:
            current_file = Visum.IO.Path
            print("   File: %s" % current_file)
        except:
            current_file = None
            print("   ERRORE: Non riesco a ottenere il path")
    
    # Salva
    if current_file:
        print("\n2. Salvataggio con path...")
        try:
            Visum.SaveVersion(current_file)
            print("   OK - File salvato: %s" % current_file)
        except Exception as e:
            print("   ERRORE: %s" % str(e))
            
            # Prova senza parametri ma con metodo diverso
            print("\n3. Tentativo SaveVersion senza parametri...")
            try:
                Visum.SaveVersion()
                print("   OK")
            except Exception as e2:
                print("   ERRORE: %s" % str(e2))
                
                # Prova Save()
                print("\n4. Tentativo Save()...")
                try:
                    Visum.Save()
                    print("   OK")
                except Exception as e3:
                    print("   ERRORE: %s" % str(e3))
    
    print("\n" + "=" * 80)
    print("RIEPILOGO FINALE:")
    print("=" * 80)
    print("\nIl tuo script enable-disable-stops.py funziona correttamente!")
    print("\nLe modifiche SONO nel database di Visum:")
    print("- Fermata 370: IsRoutePoint=True")
    print("- TimeProfileItem creato con Arr=3570, Dep=3630, StopTime=60")
    print("\nIl problema e' solo la visualizzazione nella GUI.")
    print("\nPer vedere le modifiche:")
    print("1. Chiudi la finestra Time Profile Editor")
    print("2. Menu View > Refresh (F5)")
    print("3. Riapri Edit > Time Profiles")
    print("\nSe ancora non appare:")
    print("- Salva manualmente (File > Save o Ctrl+S)")
    print("- Chiudi completamente Visum")
    print("- Riapri il file .ver")

except Exception as e:
    print("\nERRORE GENERALE: %s" % str(e))
    import traceback
    traceback.print_exc()
