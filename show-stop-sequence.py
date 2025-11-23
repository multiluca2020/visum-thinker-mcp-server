# -*- coding: ascii -*-
"""
Estrae la sequenza completa delle fermate con tempi
Mostra: Index, StopPointNo, IsRoutePoint, StopTime, RunTime
"""

TARGET_LINEROUTE_NAME = "R17_2"

print("=" * 80)
print("SEQUENZA FERMATE CON TEMPI: %s" % TARGET_LINEROUTE_NAME)
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
        print("LineRoute: %s" % TARGET_LINEROUTE_NAME)
        print("LineName: %s" % target_lr.AttValue("LineName"))
        print("")
        
        # Ottieni tutti i LineRouteItems
        lr_items = target_lr.LineRouteItems
        
        print("%-5s %-12s %-12s %-12s %-12s %-12s" % 
              ("Seq", "StopPointNo", "IsRoute", "StopTime", "RunTime", "AccumLength"))
        print("-" * 80)
        
        stops = []
        seq = 0
        
        for item in lr_items:
            try:
                stop_point_no = item.AttValue("StopPointNo")
                
                # Solo fermate valide
                if stop_point_no and stop_point_no > 0:
                    seq += 1
                    index = item.AttValue("Index")
                    is_route = item.AttValue("IsRoutePoint")
                    
                    # Prova a ottenere StopTime e RunTime
                    try:
                        stop_time = item.AttValue("StopTime")
                    except:
                        stop_time = "-"
                    
                    try:
                        run_time = item.AttValue("RunTime")
                    except:
                        run_time = "-"
                    
                    try:
                        accum_length = item.AttValue("AccumLength")
                    except:
                        accum_length = "-"
                    
                    route_str = "YES" if is_route else "NO"
                    
                    stop_info = {
                        'seq': seq,
                        'index': index,
                        'stop_point_no': stop_point_no,
                        'is_route': is_route,
                        'stop_time': stop_time,
                        'run_time': run_time,
                        'accum_length': accum_length
                    }
                    stops.append(stop_info)
                    
                    # Formatta output
                    stop_time_str = "%.2f" % stop_time if isinstance(stop_time, (int, float)) else str(stop_time)
                    run_time_str = "%.2f" % run_time if isinstance(run_time, (int, float)) else str(run_time)
                    accum_str = "%.3f" % accum_length if isinstance(accum_length, (int, float)) else str(accum_length)
                    
                    # Evidenzia prima e ultima fermata
                    marker = ""
                    if seq == 1:
                        marker = " <- PRIMA (non modificabile)"
                    
                    print("%-5d %-12.0f %-12s %-12s %-12s %-12s%s" % 
                          (seq, stop_point_no, route_str, stop_time_str, run_time_str, accum_str, marker))
            
            except Exception as e:
                pass
        
        # Marca ultima fermata
        if stops:
            print("\nNota: Fermata %d (seq %d) e' l'ULTIMA (non modificabile)" % 
                  (stops[-1]['stop_point_no'], stops[-1]['seq']))
        
        print("\n" + "=" * 80)
        print("Totale fermate: %d" % len(stops))
        print("Fermate modificabili: %d (escluse prima e ultima)" % max(0, len(stops) - 2))
        print("=" * 80)
        
        # Salva la lista per uso successivo
        print("\nAttributi disponibili per ogni fermata:")
        if stops:
            first = stops[0]
            for key in first.keys():
                print("  - %s" % key)

except Exception as e:
    print("ERRORE: %s" % str(e))
    import traceback
    traceback.print_exc()
