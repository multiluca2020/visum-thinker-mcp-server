# -*- coding: ascii -*-
"""
Estrae TimeProfiles con tempi di arrivo/partenza per ogni fermata
I TimeProfiles contengono i tempi reali delle corse
"""

TARGET_LINEROUTE_NAME = "R17_2"

print("=" * 80)
print("TIME PROFILES: %s" % TARGET_LINEROUTE_NAME)
print("=" * 80)

try:
    # Trova il LineRoute
    line_routes = Visum.Net.LineRoutes
    target_lr = None
    
    for lr in line_routes:
        if lr.AttValue("Name") == TARGET_LINEROUTE_NAME:
            target_lr = lr
            break
    
    if target_lr is None:
        print("ERRORE: LineRoute non trovato!")
    else:
        print("LineRoute: %s\n" % TARGET_LINEROUTE_NAME)
        
        # Ottieni i TimeProfiles
        time_profiles = target_lr.TimeProfiles
        print("Totale TimeProfiles: %d\n" % time_profiles.Count)
        
        if time_profiles.Count == 0:
            print("Nessun TimeProfile definito!")
            print("I tempi vanno configurati nel Time Profile Editor")
        else:
            # Mostra ogni TimeProfile
            for tp_idx, tp in enumerate(time_profiles, 1):
                tp_name = tp.AttValue("Name")
                
                try:
                    tp_dep = tp.AttValue("Dep")
                except:
                    tp_dep = "-"
                
                try:
                    tp_arr = tp.AttValue("Arr")
                except:
                    tp_arr = "-"
                
                print("=" * 80)
                print("TimeProfile %d: %s" % (tp_idx, tp_name))
                print("  Partenza: %s" % tp_dep)
                print("  Arrivo:   %s" % tp_arr)
                print("-" * 80)
                
                # Ottieni i TimeProfileItems (tempi per ogni fermata)
                tp_items = tp.TimeProfileItems
                print("  Fermate nel profilo: %d\n" % tp_items.Count)
                
                if tp_items.Count > 0:
                    print("  %-5s %-10s %-12s %-12s %-12s" % 
                          ("Seq", "Arr[s]", "Dep[s]", "StopTime[s]", "RunTime[s]"))
                    print("  " + "-" * 70)
                    
                    for item_idx, tpi in enumerate(tp_items, 1):
                        try:
                            arr = tpi.AttValue("Arr")
                        except:
                            arr = "-"
                        
                        try:
                            dep = tpi.AttValue("Dep")
                        except:
                            dep = "-"
                        
                        # Calcola StopTime (Dep - Arr)
                        if isinstance(arr, (int, float)) and isinstance(dep, (int, float)):
                            stop_time = dep - arr
                        else:
                            stop_time = "-"
                        
                        # RunTime e' il tempo dalla fermata precedente
                        run_time = "-"  # Lo calcoliamo dopo
                        
                        # Formatta
                        arr_str = "%.0f" % arr if isinstance(arr, (int, float)) else str(arr)
                        dep_str = "%.0f" % dep if isinstance(dep, (int, float)) else str(dep)
                        stop_str = "%.0f" % stop_time if isinstance(stop_time, (int, float)) else str(stop_time)
                        
                        print("  %-5d %-10s %-12s %-12s %-12s" % 
                              (item_idx, arr_str, dep_str, stop_str, run_time))
                    
                    print("")
                else:
                    print("  Nessun TimeProfileItem!\n")
        
        print("=" * 80)
        print("NOTA:")
        print("  - Arr = Tempo di arrivo alla fermata (secondi)")
        print("  - Dep = Tempo di partenza dalla fermata (secondi)")
        print("  - StopTime = Dep - Arr (tempo di sosta)")
        print("  - Per modificare i tempi, usa TimeProfileItem.SetAttValue()")
        print("=" * 80)

except Exception as e:
    print("ERRORE: %s" % str(e))
    import traceback
    traceback.print_exc()
