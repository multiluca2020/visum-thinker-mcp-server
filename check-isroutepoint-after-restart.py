# -*- coding: ascii -*-
"""
Verifica se IsRoutePoint viene salvato correttamente
"""

try:
    print("=" * 80)
    print("VERIFICA ISROUTEPOINT DOPO RIAVVIO")
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
        print("\nLineRoute: R17_2")
        print("")
        
        # Verifica IsRoutePoint per tutte le fermate
        print("IsRoutePoint per tutte le fermate:")
        print("-" * 80)
        
        seq = 0
        for item in lr.LineRouteItems:
            stop_no = item.AttValue("StopPointNo")
            
            if stop_no and stop_no > 0:
                is_route = item.AttValue("IsRoutePoint")
                
                marker = ""
                if int(stop_no) in [328, 370]:
                    marker = " <--- TEST STOP"
                
                print("  %2d. Stop %3d: IsRoutePoint = %s%s" % (seq, int(stop_no), is_route, marker))
                seq += 1
        
        print("\n" + "=" * 80)
        print("RISULTATO:")
        print("=" * 80)
        
        # Cerca specificamente 328 e 370
        stop_328_route = None
        stop_370_route = None
        
        for item in lr.LineRouteItems:
            stop_no = item.AttValue("StopPointNo")
            if stop_no == 328:
                stop_328_route = item.AttValue("IsRoutePoint")
            elif stop_no == 370:
                stop_370_route = item.AttValue("IsRoutePoint")
        
        print("\nStop 328: IsRoutePoint = %s" % stop_328_route)
        print("Stop 370: IsRoutePoint = %s" % stop_370_route)
        
        if stop_328_route == 0.0 and stop_370_route == 0.0:
            print("\nCONCLUSIONE: Le modifiche a IsRoutePoint NON sono state salvate!")
            print("Lo script deve chiamare SaveVersion() DOPO aver impostato IsRoutePoint.")
        elif stop_328_route == 1.0 and stop_370_route == 1.0:
            print("\nCONCLUSIONE: IsRoutePoint e' stato salvato correttamente!")
            print("Ma i TimeProfileItems NON vengono rigenerati automaticamente.")
            print("\nQuesto significa che Visum NON rigenera i TimeProfileItems")
            print("dal LineRoute al caricamento del file.")
            print("\nProbabilmente serve un'azione manuale nell'interfaccia per")
            print("sincronizzare il TimeProfile con il LineRoute.")
        else:
            print("\nCONCLUSIONE: Stato parziale - alcune modifiche salvate, altre no.")

except Exception as e:
    print("\nERRORE: %s" % str(e))
    import traceback
    traceback.print_exc()
