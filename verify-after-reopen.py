# -*- coding: ascii -*-
"""
Test: Verifica se il salvataggio persiste le modifiche
"""

try:
    print("=" * 80)
    print("VERIFICA STATO FERMATA 370 - TEST SALVATAGGIO")
    print("=" * 80)
    
    # Trova LineRoute
    lr = None
    for lineroute in Visum.Net.LineRoutes:
        name = lineroute.AttValue("Name")
        if name == "R17_2":
            lr = lineroute
            break
    
    if not lr:
        print("\nERRORE: LineRoute non trovato!")
    else:
        # TimeProfile
        tp = None
        for time_profile in lr.TimeProfiles:
            tp = time_profile
            break
        
        if not tp:
            print("\nERRORE: TimeProfile non trovato!")
        else:
            # Conta TimeProfileItems
            total = 0
            has_370 = False
            stop_370_data = None
            
            for tpi in tp.TimeProfileItems:
                total += 1
                stop_no = tpi.AttValue("StopPointNo")
                if stop_no and int(stop_no) == 370:
                    has_370 = True
                    stop_370_data = {
                        'arr': tpi.AttValue("Arr"),
                        'dep': tpi.AttValue("Dep"),
                        'stoptime': tpi.AttValue("StopTime"),
                        'index': tpi.AttValue("Index")
                    }
            
            print("\nSTATO ATTUALE NEL DATABASE:")
            print("-" * 80)
            print("  Totale TimeProfileItems: %d" % total)
            print("  Fermata 370 presente:    %s" % has_370)
            
            if has_370:
                print("\n  Dati fermata 370:")
                print("    Index:    %s" % stop_370_data['index'])
                print("    Arr:      %s" % stop_370_data['arr'])
                print("    Dep:      %s" % stop_370_data['dep'])
                print("    StopTime: %s" % stop_370_data['stoptime'])
            
            # Verifica IsRoutePoint
            print("\n" + "-" * 80)
            print("VERIFICA LINEROUTE:")
            print("-" * 80)
            
            for lri in lr.LineRouteItems:
                stop_no = lri.AttValue("StopPointNo")
                if stop_no and int(stop_no) == 370:
                    is_rp = lri.AttValue("IsRoutePoint")
                    print("  Fermata 370 IsRoutePoint: %s" % is_rp)
                    break
            
            print("\n" + "=" * 80)
            print("ISTRUZIONI PER IL TEST:")
            print("=" * 80)
            print("\n1. SALVA il progetto: File > Save (Ctrl+S)")
            print("2. Verifica nella GUI se vedi la fermata 370:")
            print("   - Apri Edit > Time Profiles")
            print("   - Seleziona R17_2, TimeProfile 'R17'")
            print("   - Guarda se c'e' la fermata 370")
            print("\n3. CHIUDI Visum completamente")
            print("4. RIAPRI il file di progetto")
            print("5. RIESEGUI questo script")
            print("\nCOMANDO:")
            print("exec(open(r\"h:\\visum-thinker-mcp-server\\verify-after-reopen.py\").read())")
            print("\nE dimmi:")
            print("  A) Dopo il salvataggio, vedi la 370 nella GUI?")
            print("  B) Dopo chiusura/riapertura, lo script trova ancora la 370?")
            print("  C) Dopo chiusura/riapertura, vedi la 370 nella GUI?")

except Exception as e:
    print("\nERRORE: %s" % str(e))
    import traceback
    traceback.print_exc()
