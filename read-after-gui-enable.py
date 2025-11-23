# -*- coding: ascii -*-
"""
Leggi lo stato della fermata 370 DOPO che l'hai abilitata MANUALMENTE dalla GUI
"""

try:
    print("=" * 80)
    print("LETTURA STATO DOPO ABILITAZIONE MANUALE DALLA GUI")
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
            print("\nTimeProfile: %s" % tp.AttValue("Name"))
            
            # Cerca fermata 370
            print("\n" + "=" * 80)
            print("RICERCA FERMATA 370 NEL TIMEPROFILE:")
            print("=" * 80)
            
            found_370 = False
            for tpi in tp.TimeProfileItems:
                stop_no = tpi.AttValue("StopPointNo")
                if stop_no and int(stop_no) == 370:
                    found_370 = True
                    
                    print("\nFERMATA 370 TROVATA!")
                    print("-" * 80)
                    
                    # Leggi TUTTI gli attributi
                    attrs = ["Arr", "Dep", "StopTime", "PreRunTime", "PostRunTime", 
                             "AccumRunTime", "Index", "StopPointNo"]
                    
                    for attr in attrs:
                        try:
                            value = tpi.AttValue(attr)
                            print("  %-20s : %s" % (attr, value))
                        except:
                            pass
                    
                    # Analisi
                    arr = tpi.AttValue("Arr")
                    dep = tpi.AttValue("Dep")
                    stoptime = tpi.AttValue("StopTime")
                    
                    print("\n" + "-" * 80)
                    print("ANALISI:")
                    print("  Arr:              %s" % arr)
                    print("  Dep:              %s" % dep)
                    print("  Dep - Arr:        %s" % (dep - arr))
                    print("  StopTime (attr):  %s" % stoptime)
                    
                    if stoptime == 0:
                        print("\n  >>> StopTime = 0 (GUI mostra questo!)")
                        print("  >>> Arr = Dep (nessun tempo di sosta)")
                        print("\n  CONCLUSIONE: Quando abiliti dalla GUI senza impostare")
                        print("               lo StopTime, Visum crea il TimeProfileItem")
                        print("               con Arr = Dep (quindi StopTime = 0)")
                    elif abs(stoptime - (dep - arr)) < 0.01:
                        print("\n  >>> StopTime coerente con Arr/Dep")
                    
                    break
            
            if not found_370:
                print("\nFERMATA 370 NON TROVATA nel TimeProfile!")
                print("\nPossibili cause:")
                print("  1. Non hai ancora salvato/applicato nella GUI")
                print("  2. La GUI non ha ancora sincronizzato con il database")
                print("  3. Hai modificato un altro TimeProfile")
            
            # Mostra anche IsRoutePoint del LineRouteItem
            print("\n" + "=" * 80)
            print("VERIFICA LINEROUTE ITEM:")
            print("=" * 80)
            
            for lri in lr.LineRouteItems:
                stop_no = lri.AttValue("StopPointNo")
                if stop_no and int(stop_no) == 370:
                    is_rp = lri.AttValue("IsRoutePoint")
                    idx = lri.AttValue("Index")
                    print("\nLineRouteItem 370:")
                    print("  IsRoutePoint: %s" % is_rp)
                    print("  Index:        %s" % idx)
                    
                    if is_rp:
                        print("\n  OK: IsRoutePoint = True (fermata abilitata)")
                    else:
                        print("\n  PROBLEMA: IsRoutePoint = False (fermata NON abilitata)")
                    break

except Exception as e:
    print("\nERRORE: %s" % str(e))
    import traceback
    traceback.print_exc()
