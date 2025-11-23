# -*- coding: ascii -*-
"""
Verifica lo stato della fermata 370 nel LineRoute R17_2
"""

try:
    # Trova il LineRoute
    print("Ricerca LineRoute R17_2...")
    lr = None
    for lineroute in Visum.Net.LineRoutes:
        name = lineroute.AttValue("Name")
        if name == "R17_2":
            lr = lineroute
            break
    
    if lr is None:
        print("ERRORE: LineRoute R17_2 non trovato!")
    else:
        print("OK - LineRoute trovato")
        print("")
        
        # Controlla tutte le fermate
        print("=" * 80)
        print("STATO FERMATE NEL LINEROUTE")
        print("=" * 80)
        print("Seq | StopNo | IsRoutePoint | AccumLength")
        print("-" * 80)
        
        seq = 0
        stop_370_found = False
        for item in lr.LineRouteItems:
            stop_no = item.AttValue("StopPointNo")
            is_route = item.AttValue("IsRoutePoint")
            accum_len = item.AttValue("AccumLength")
            
            # Salta se non e' una fermata (StopPointNo nullo)
            if stop_no is None or stop_no == 0:
                seq += 1
                continue
            
            marker = ""
            if stop_no == 370:
                marker = " <--- FERMATA 370"
                stop_370_found = True
            
            print("%3d | %6d | %12s | %8.3f%s" % (seq, stop_no, is_route, accum_len, marker))
            seq += 1
        
        print("=" * 80)
        
        if not stop_370_found:
            print("\nERRORE: Fermata 370 NON trovata nel LineRoute!")
        else:
            print("\nFermata 370 trovata")
        
        print("")
        
        # Controlla TimeProfile
        print("=" * 80)
        print("FERMATE ABILITATE NEL TIMEPROFILE")
        print("=" * 80)
        
        tp = None
        for time_profile in lr.TimeProfiles:
            tp = time_profile
            break
        
        if tp is None:
            print("ERRORE: Nessun TimeProfile trovato!")
        else:
            tp_name = tp.AttValue("Name")
            print("TimeProfile: %s" % tp_name)
            print("")
            print("Idx | StopNo | Arr    | Dep    | StopTime | PreRun | PostRun")
            print("-" * 80)
            
            # Prima costruisci lista delle fermate abilitate dal LineRoute
            enabled_stops = []
            for item in lr.LineRouteItems:
                stop_no = item.AttValue("StopPointNo")
                is_route = item.AttValue("IsRoutePoint")
                
                if stop_no is not None and stop_no != 0 and is_route == 1.0:
                    enabled_stops.append(stop_no)
            
            print("Fermate abilitate nel LineRoute (IsRoutePoint=1): %d" % len(enabled_stops))
            print("")
            
            idx = 0
            stop_370_in_tp = False
            print("Idx | StopNo | IsProf | Arr    | Dep    | StopTime | PreRun | PostRun")
            print("-" * 90)
            
            for tpi in tp.TimeProfileItems:
                # Usa l'indice per mappare allo StopPointNo
                if idx < len(enabled_stops):
                    stop_no = enabled_stops[idx]
                else:
                    stop_no = -1  # Errore: piu' TimeProfileItems che fermate abilitate
                
                is_profile = tpi.AttValue("IsProfilePoint")
                arr = tpi.AttValue("Arr")
                dep = tpi.AttValue("Dep")
                stop_time = tpi.AttValue("StopTime")
                pre_run = tpi.AttValue("PreRunTime")
                post_run = tpi.AttValue("PostRunTime")
                
                marker = ""
                if stop_no == 370:
                    marker = " <--- FERMATA 370"
                    stop_370_in_tp = True
                
                print("%3d | %6d | %6s | %6d | %6d | %8d | %6d | %7d%s" % (idx, stop_no, is_profile, arr, dep, stop_time, pre_run, post_run, marker))
                idx += 1
            
            print("=" * 80)
            
            if stop_370_in_tp:
                print("\nFermata 370 PRESENTE nel TimeProfile (ABILITATA)")
            else:
                print("\nFermata 370 NON presente nel TimeProfile (DISABILITATA)")

except Exception as e:
    print("ERRORE: %s" % str(e))
    import traceback
    traceback.print_exc()
