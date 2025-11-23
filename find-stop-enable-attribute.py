# -*- coding: ascii -*-
"""
Stampa TUTTI gli attributi disponibili per un LineRouteItem fermata
Per scoprire quale attributo controlla l'abilitazione/disabilitazione
"""

TARGET_LINEROUTE_NAME = "R17_2"

print("=" * 80)
print("ANALISI ATTRIBUTI LINE ROUTE ITEM (FERMATA)")
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
        
        # Prendi il primo LineRouteItem che e' una fermata
        lr_items = target_lr.LineRouteItems
        first_stop = None
        
        for item in lr_items:
            try:
                stop_point_no = item.AttValue("StopPointNo")
                if stop_point_no and stop_point_no > 0:
                    first_stop = item
                    break
            except:
                pass
        
        if first_stop is None:
            print("Nessuna fermata trovata!")
        else:
            print("Prima fermata trovata:")
            print("  Index: %s" % first_stop.AttValue("Index"))
            print("  StopPointNo: %s" % first_stop.AttValue("StopPointNo"))
            print("")
            
            # Ottieni tutti gli attributi disponibili
            print("TUTTI GLI ATTRIBUTI DISPONIBILI:")
            print("-" * 80)
            
            # Accedi alla collezione di attributi
            attrs = Visum.Net.LineRouteItems.Attributes
            
            print("Totale attributi: %d\n" % attrs.Count)
            
            # Lista alcuni attributi interessanti
            interesting = [
                "Index", "NodeNo", "StopPointNo", "IsRoutePoint",
                "IsUsed", "Active", "Enabled", "Disabled", "IsActive",
                "IsEnabled", "IsDisabled", "Status", "State",
                "DirectionCode", "AccumLength", "PostLength"
            ]
            
            print("Attributi interessanti:")
            for attr_name in interesting:
                try:
                    value = first_stop.AttValue(attr_name)
                    print("  %-20s = %s" % (attr_name, value))
                except Exception as e:
                    # Attributo non esiste
                    pass
            
            print("\n" + "=" * 80)
            print("Prova a cercare nella GUI di Visum:")
            print("Line Route Editor > Click destro su fermata > Proprieta'")
            print("Cerca l'attributo che abilita/disabilita la fermata")
            print("=" * 80)

except Exception as e:
    print("ERRORE: %s" % str(e))
    import traceback
    traceback.print_exc()
