# -*- coding: ascii -*-
"""
Mostra TimeProfile con StopTime e RunTime (approccio 2)
Verifica quali attributi sono effettivamente editabili
"""

TARGET_LINEROUTE_NAME = "R17_2"

print("=" * 80)
print("TIME PROFILE CON STOPTIME E RUNTIME: %s" % TARGET_LINEROUTE_NAME)
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
        
        # Ottieni TimeProfile
        time_profiles = target_lr.TimeProfiles
        if time_profiles.Count == 0:
            print("Nessun TimeProfile!")
        else:
            # Prendi il primo TimeProfile
            tp = None
            for t in time_profiles:
                tp = t
                break
            
            if tp is None:
                print("Errore: TimeProfile non accessibile!")
            else:
                tp_items = tp.TimeProfileItems
                
                print("TimeProfile: %s" % tp.AttValue("Name"))
                print("Fermate: %d\n" % tp_items.Count)
                
                print("%-5s %-10s %-10s %-10s %-12s %-12s" % 
                      ("Seq", "Arr[s]", "Dep[s]", "Stop[s]", "PreRun[s]", "PostRun[s]"))
                print("-" * 80)
                
                for idx, tpi in enumerate(tp_items, 1):
                    arr = tpi.AttValue("Arr")
                    dep = tpi.AttValue("Dep")
                    
                    try:
                        stop_time = tpi.AttValue("StopTime")
                    except:
                        stop_time = "-"
                    
                    try:
                        pre_run = tpi.AttValue("PreRunTime")
                    except:
                        pre_run = "-"
                    
                    try:
                        post_run = tpi.AttValue("PostRunTime")
                    except:
                        post_run = "-"
                    
                    # Formatta
                    arr_str = "%.0f" % arr if isinstance(arr, (int, float)) else str(arr)
                    dep_str = "%.0f" % dep if isinstance(dep, (int, float)) else str(dep)
                    stop_str = "%.0f" % stop_time if isinstance(stop_time, (int, float)) else str(stop_time)
                    pre_str = "%.0f" % pre_run if isinstance(pre_run, (int, float)) else str(pre_run)
                    post_str = "%.0f" % post_run if isinstance(post_run, (int, float)) else str(post_run)
                    
                    print("%-5d %-10s %-10s %-10s %-12s %-12s" % 
                          (idx, arr_str, dep_str, stop_str, pre_str, post_str))
                
                print("\n" + "=" * 80)
                print("VERIFICA EDITABILITA:")
                print("-" * 80)
                
                # Prova a leggere il secondo item per vedere attributi disponibili
                if tp_items.Count > 1:
                    tpi_idx = 0
                    tpi_second = None
                    for tpi in tp_items:
                        if tpi_idx == 1:
                            tpi_second = tpi
                            break
                        tpi_idx += 1
                    
                    if tpi_second:
                        attrs_to_check = [
                            "StopTime", "PreRunTime", "PostRunTime", 
                            "Arr", "Dep", "AccumRunTime"
                        ]
                        
                        print("Attributi disponibili sul TimeProfileItem #2:")
                        for attr in attrs_to_check:
                            try:
                                value = tpi_second.AttValue(attr)
                                print("  %-15s = %s" % (attr, value))
                            except Exception as e:
                                print("  %-15s = ERRORE: %s" % (attr, str(e)[:50]))
                
                print("=" * 80)

except Exception as e:
    print("ERRORE: %s" % str(e))
    import traceback
    traceback.print_exc()
