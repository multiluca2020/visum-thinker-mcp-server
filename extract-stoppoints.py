# -*- coding: ascii -*-
"""
Estrae STOP POINTS di un LineRoute con attributo IsUsed
Gli StopPoints hanno l'attributo IsUsed per abilitare/disabilitare fermate
"""

TARGET_LINEROUTE_NAME = "R17_2"

print("=" * 80)
print("ESTRAZIONE STOP POINTS: %s" % TARGET_LINEROUTE_NAME)
print("=" * 80)

try:
    # Trova il LineRoute per Name
    line_routes = Visum.Net.LineRoutes
    target_lr = None
    
    for lr in line_routes:
        if lr.AttValue("Name") == TARGET_LINEROUTE_NAME:
            target_lr = lr
            break
    
    if target_lr is None:
        print("ERRORE: LineRoute non trovato!")
    else:
        print("OK - LineRoute trovato\n")
        
        # Informazioni base
        print("INFORMAZIONI BASE:")
        print("-" * 80)
        print("  Name:         %s" % target_lr.AttValue("Name"))
        print("  LineName:     %s" % target_lr.AttValue("LineName"))
        print("  Direction:    %s" % target_lr.AttValue("DirectionCode"))
        print("")
        
        # LINE ROUTE ITEMS (tutti i punti, filtriamo le fermate)
        print("LINE ROUTE ITEMS (Fermate):")
        print("-" * 80)
        lr_items = target_lr.LineRouteItems
        print("Totale items: %d\n" % lr_items.Count)
        
        print("%-5s %-10s %-12s %-15s" % 
              ("Idx", "NodeNo", "IsRoutePoint", "StopPointNo"))
        print("-" * 80)
        
        stop_count = 0
        for item in lr_items:
            index = item.AttValue("Index")
            node_no = item.AttValue("NodeNo")
            is_route_point = item.AttValue("IsRoutePoint")
            
            try:
                stop_point_no = item.AttValue("StopPointNo")
            except:
                stop_point_no = 0
            
            # Solo se e' una fermata (ha StopPointNo valido)
            if stop_point_no and stop_point_no > 0:
                stop_count += 1
                route_mark = "YES" if is_route_point else "NO"
                
                print("%-5d %-10s %-12s %-15s" % 
                      (index, node_no, route_mark, stop_point_no))
        
        print("\n" + "=" * 80)
        print("COMPLETATO - Totale fermate: %d / %d items" % (stop_count, lr_items.Count))
        print("=" * 80)

except Exception as e:
    print("ERRORE: %s" % str(e))
    import traceback
    traceback.print_exc()
