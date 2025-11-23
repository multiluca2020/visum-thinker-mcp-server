# -*- coding: ascii -*-
"""
Script semplificato per estrarre informazioni LineRoute
Compatibile con console Python di Visum (no emoji, no exit())
"""

# Puoi cercare per Name (es. "R17_2") o per LineName (es. "R17_2022")
TARGET_LINEROUTE_NAME = "R17_2"  # Cerca per Name
# Oppure decommentare la riga seguente per cercare tutti con stesso LineName:
# SEARCH_BY_LINENAME = "R17_2022"

print("=" * 80)
print("ESTRAZIONE LINE ROUTE: %s" % TARGET_LINEROUTE_NAME)
print("=" * 80)

try:
    # Trova il LineRoute per Name (non LineName!)
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
        print("  Length (km):  %.2f" % target_lr.AttValue("Length"))
        print("")
        
        # LineRouteItems con IsUsed
        print("LINE ROUTE ITEMS:")
        print("-" * 80)
        lr_items = target_lr.LineRouteItems
        print("Totale items: %d\n" % lr_items.Count)
        
        print("%-5s %-8s %-10s %-10s %-10s %-8s" % 
              ("Idx", "Node", "IsStop", "Dist[km]", "Time[min]", "IsUsed"))
        print("-" * 80)
        
        for item in lr_items:
            index = item.AttValue("Index")
            node = item.AttValue("NodeIndex")
            is_stop = item.AttValue("IsStopPoint")
            dist = item.AttValue("DistOnLine")
            time = item.AttValue("TimeOnLine")
            is_used = item.AttValue("IsUsed") if is_stop else "-"
            
            stop_mark = "YES" if is_stop else "NO"
            used_mark = "YES" if is_used == True else ("NO" if is_used == False else "-")
            
            print("%-5d %-8d %-10s %-10.3f %-10.2f %-8s" % 
                  (index, node, stop_mark, dist, time, used_mark))
        
        print("\n" + "=" * 80)
        print("COMPLETATO")
        print("=" * 80)

except Exception as e:
    print("ERRORE: %s" % str(e))
    import traceback
    traceback.print_exc()
