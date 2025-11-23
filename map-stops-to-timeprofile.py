# -*- coding: ascii -*-
"""
Mappa la corrispondenza tra LineRouteItems e TimeProfileItems
Mostra quale fermata del LineRoute corrisponde a quale item del TimeProfile
"""

TARGET_LINEROUTE_NAME = "R17_2"

print("=" * 80)
print("MAPPING FERMATE <-> TIME PROFILE ITEMS: %s" % TARGET_LINEROUTE_NAME)
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
        
        # Ottieni LineRouteItems (tutte le fermate)
        lr_items = target_lr.LineRouteItems
        
        # Costruisci lista fermate dal LineRoute
        lr_stops = []
        for item in lr_items:
            try:
                stop_point_no = item.AttValue("StopPointNo")
                if stop_point_no and stop_point_no > 0:
                    is_route = item.AttValue("IsRoutePoint")
                    index = item.AttValue("Index")
                    accum_length = item.AttValue("AccumLength")
                    
                    lr_stops.append({
                        'index': index,
                        'stop_point_no': stop_point_no,
                        'is_route': is_route,
                        'accum_length': accum_length
                    })
            except:
                pass
        
        print("Fermate totali nel LineRoute: %d" % len(lr_stops))
        print("Fermate abilitate (IsRoute=YES): %d" % sum(1 for s in lr_stops if s['is_route']))
        print("Fermate disabilitate (IsRoute=NO): %d\n" % sum(1 for s in lr_stops if not s['is_route']))
        
        # Ottieni TimeProfile
        time_profiles = target_lr.TimeProfiles
        if time_profiles.Count == 0:
            print("Nessun TimeProfile!")
        else:
            tp = time_profiles.Item(0)  # Primo TimeProfile
            tp_items = tp.TimeProfileItems
            
            print("TimeProfileItems nel profilo: %d\n" % tp_items.Count)
            
            # Mappa: seq TimeProfile -> seq LineRoute (solo fermate abilitate)
            print("%-8s %-12s %-12s %-10s %-10s %-10s %-15s" % 
                  ("LR_Seq", "StopPointNo", "IsRoute", "Arr[s]", "Dep[s]", "Stop[s]", "AccumLength[km]"))
            print("-" * 95)
            
            tp_idx = 0  # Indice nel TimeProfile
            
            for lr_seq, lr_stop in enumerate(lr_stops, 1):
                stop_no = lr_stop['stop_point_no']
                is_route = lr_stop['is_route']
                accum = lr_stop['accum_length']
                
                if is_route:
                    # Questa fermata e' abilitata -> ha un TimeProfileItem
                    if tp_idx < tp_items.Count:
                        tpi = tp_items.Item(tp_idx)
                        arr = tpi.AttValue("Arr")
                        dep = tpi.AttValue("Dep")
                        stop_time = dep - arr
                        
                        print("%-8d %-12.0f %-12s %-10.0f %-10.0f %-10.0f %-15.3f" % 
                              (lr_seq, stop_no, "YES", arr, dep, stop_time, accum))
                        
                        tp_idx += 1
                    else:
                        print("%-8d %-12.0f %-12s %-10s %-10s %-10s %-15.3f" % 
                              (lr_seq, stop_no, "YES", "?", "?", "?", accum))
                else:
                    # Fermata disabilitata -> NON ha TimeProfileItem
                    print("%-8d %-12.0f %-12s %-10s %-10s %-10s %-15.3f" % 
                          (lr_seq, stop_no, "NO", "-", "-", "-", accum))
            
            print("\n" + "=" * 95)
            print("NOTA:")
            print("  - Le fermate con IsRoute=YES hanno corrispondenza 1:1 con TimeProfileItems")
            print("  - Le fermate con IsRoute=NO NON appaiono nel TimeProfile")
            print("  - Per abilitare una fermata disabilitata:")
            print("    1. Imposta IsRoutePoint = True")
            print("    2. INSERISCI un nuovo TimeProfileItem nella posizione corretta")
            print("    3. Calcola Arr/Dep basandoti su distanze e fermate vicine")
            print("=" * 95)

except Exception as e:
    print("ERRORE: %s" % str(e))
    import traceback
    traceback.print_exc()
