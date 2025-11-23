# -*- coding: ascii -*-
"""
Verifica StopTime di tutte le fermate nel TimeProfile
"""

try:
    print("=" * 80)
    print("VERIFICA STOPTIME DI TUTTE LE FERMATE")
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
        # Accedi al TimeProfile
        tp = None
        for time_profile in lr.TimeProfiles:
            tp = time_profile
            break
        
        if not tp:
            print("\nERRORE: TimeProfile non trovato!")
        else:
            print("\nTimeProfile: %s" % tp.AttValue("Name"))
            print("")
            print("TUTTE LE FERMATE CON STOPTIME:")
            print("=" * 80)
            print("Idx | Stop | Arr     | Dep     | StopTime | PreRun  | PostRun")
            print("-" * 80)
            
            idx = 0
            stops_with_zero_stoptime = []
            
            for tpi in tp.TimeProfileItems:
                stop_no = tpi.AttValue("StopPointNo")
                arr = tpi.AttValue("Arr")
                dep = tpi.AttValue("Dep")
                stop_time = tpi.AttValue("StopTime")
                pre_run = tpi.AttValue("PreRunTime")
                post_run = tpi.AttValue("PostRunTime")
                
                marker = ""
                if int(stop_no) in [328, 370]:
                    marker = " <--- TEST"
                
                if stop_time == 0.0:
                    stops_with_zero_stoptime.append(int(stop_no))
                    marker = " <--- STOPTIME = 0!"
                
                print("%3d | %4d | %7.1f | %7.1f | %8.1f | %7.1f | %7.1f%s" % 
                      (idx, int(stop_no), arr, dep, stop_time, pre_run, post_run, marker))
                idx += 1
            
            print("\n" + "=" * 80)
            print("ANALISI:")
            print("=" * 80)
            
            if stops_with_zero_stoptime:
                print("\nFermate con StopTime = 0:")
                for stop in stops_with_zero_stoptime:
                    print("  - Stop %d" % stop)
                
                print("\nNOTA: Arr = Dep per queste fermate (nessun tempo di sosta)")
                print("\nQuando abiliti manualmente una fermata dall'interfaccia,")
                print("Visum NON imposta automaticamente un tempo di sosta.")
                print("Devi impostarlo manualmente o con lo script.")
            else:
                print("\nTutte le fermate hanno StopTime > 0")
            
            # Verifica specifica per 370
            print("\n" + "=" * 80)
            print("VERIFICA FERMATA 370:")
            print("=" * 80)
            
            found_370 = False
            for tpi in tp.TimeProfileItems:
                stop_no = tpi.AttValue("StopPointNo")
                if int(stop_no) == 370:
                    found_370 = True
                    arr = tpi.AttValue("Arr")
                    dep = tpi.AttValue("Dep")
                    stop_time = tpi.AttValue("StopTime")
                    
                    print("\nFermata 370 nel TimeProfile:")
                    print("  Arr:      %s" % arr)
                    print("  Dep:      %s" % dep)
                    print("  StopTime: %s" % stop_time)
                    print("  Calcolo:  Dep - Arr = %s" % (dep - arr))
                    
                    if stop_time == 0.0:
                        print("\n  PROBLEMA: StopTime = 0!")
                        print("  Questo significa che Arr = Dep")
                        print("  La fermata e' nel TimeProfile ma senza tempo di sosta")
                    elif stop_time == 60.0:
                        print("\n  OK: StopTime = 60s (come configurato nello script)")
                    else:
                        print("\n  StopTime = %s (valore diverso da quello atteso: 60)" % stop_time)
                    
                    break
            
            if not found_370:
                print("\nFermata 370 NON presente nel TimeProfile")

except Exception as e:
    print("\nERRORE: %s" % str(e))
    import traceback
    traceback.print_exc()
