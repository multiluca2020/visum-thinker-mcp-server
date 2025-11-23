# -*- coding: ascii -*-
"""
Prova a salvare e fare refresh
"""

try:
    print("=" * 80)
    print("SALVATAGGIO E REFRESH")
    print("=" * 80)
    
    # 1. SaveVersion
    print("\n1. Tentativo SaveVersion()...")
    try:
        Visum.SaveVersion()
        print("   OK - SaveVersion completato")
    except Exception as e:
        print("   ERRORE: %s" % str(e))
    
    # 2. Cerca metodi Refresh
    print("\n2. Metodi Refresh disponibili:")
    print("-" * 80)
    
    refresh_methods = []
    for attr in dir(Visum):
        if 'refresh' in attr.lower():
            refresh_methods.append(attr)
    
    if refresh_methods:
        for method in refresh_methods:
            print("  - %s" % method)
            try:
                func = getattr(Visum, method)
                if callable(func):
                    print("    Tentativo chiamata...")
                    func()
                    print("    OK")
            except Exception as e:
                print("    ERRORE: %s" % str(e))
    else:
        print("  Nessun metodo Refresh trovato")
    
    # 3. Verifica Graphics
    print("\n3. Metodi su Visum.Graphics:")
    print("-" * 80)
    
    if hasattr(Visum, 'Graphics'):
        graphics_methods = []
        for attr in dir(Visum.Graphics):
            if 'refresh' in attr.lower():
                graphics_methods.append(attr)
        
        if graphics_methods:
            for method in graphics_methods:
                print("  - %s" % method)
                try:
                    func = getattr(Visum.Graphics, method)
                    if callable(func):
                        print("    Tentativo chiamata...")
                        func()
                        print("    OK")
                except Exception as e:
                    print("    ERRORE: %s" % str(e))
        else:
            print("  Nessun metodo Refresh trovato")
    else:
        print("  Visum.Graphics non disponibile")
    
    # 4. Verifica stato finale
    print("\n4. Verifica stato fermata 328:")
    print("-" * 80)
    
    lr = None
    for lineroute in Visum.Net.LineRoutes:
        name = lineroute.AttValue("Name")
        if name == "R17_2":
            lr = lineroute
            break
    
    if lr:
        # Verifica nel TimeProfile
        tp = None
        for time_profile in lr.TimeProfiles:
            tp = time_profile
            break
        
        if tp:
            found_328 = False
            for tpi in tp.TimeProfileItems:
                stop_no = tpi.AttValue("StopPointNo")
                if stop_no == 328:
                    found_328 = True
                    print("  Fermata 328 PRESENTE nel TimeProfile")
                    print("  Arr: %s" % tpi.AttValue("Arr"))
                    print("  Dep: %s" % tpi.AttValue("Dep"))
                    break
            
            if not found_328:
                print("  Fermata 328 NON presente nel TimeProfile")
    
    print("\n" + "=" * 80)
    print("COMPLETATO")
    print("=" * 80)
    print("\nSe la fermata 328 e' presente nel TimeProfile ma non visibile")
    print("nell'interfaccia, prova a:")
    print("  1. Chiudere e riaprire il Time Profile Editor")
    print("  2. Cliccare su Refresh/Update nel menu di Visum")
    print("  3. Salvare il progetto (Ctrl+S) e ricaricarlo")
    print("=" * 80)

except Exception as e:
    print("\nERRORE GENERALE: %s" % str(e))
    import traceback
    traceback.print_exc()
