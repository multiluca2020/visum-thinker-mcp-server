# -*- coding: ascii -*-
"""
Analisi dettagliata dei TimeProfileItems esistenti
"""

try:
    print("=" * 80)
    print("ANALISI TIMEPROFILEITEMS ESISTENTI")
    print("=" * 80)
    
    # Trova LineRoute
    lr = None
    for lineroute in Visum.Net.LineRoutes:
        name = lineroute.AttValue("Name")
        if name == "R17_2":
            lr = lineroute
            break
    
    if not lr:
        print("ERRORE: LineRoute non trovato!")
    else:
        # Accedi al TimeProfile
        tp = None
        for time_profile in lr.TimeProfiles:
            tp = time_profile
            break
        
        if not tp:
            print("ERRORE: TimeProfile non trovato!")
        else:
            print("\nTimeProfile: %s" % tp.AttValue("Name"))
            print("")
            
            # Lista tutti i TimeProfileItems
            print("TUTTI I TIMEPROFILEITEMS:")
            print("-" * 80)
            
            idx = 0
            for tpi in tp.TimeProfileItems:
                print("\nTimeProfileItem #%d:" % idx)
                
                # Attributi standard
                attrs_to_check = [
                    "StopPointNo", "NodeNo", "Index", 
                    "Arr", "Dep", "StopTime", "PreRunTime", "PostRunTime",
                    "AccumRunTime"
                ]
                
                for attr in attrs_to_check:
                    try:
                        value = tpi.AttValue(attr)
                        print("  %-20s : %s" % (attr, value))
                    except Exception as e:
                        print("  %-20s : [ERRORE: %s]" % (attr, str(e)))
                
                # Prova a vedere se c'e' un riferimento al LineRouteItem
                print("\n  Riferimenti:")
                ref_attrs = ["LineRouteItem", "RouteItem", "Stop", "StopPoint", "Node"]
                for attr in ref_attrs:
                    try:
                        value = tpi.AttValue(attr)
                        print("    %-20s : %s (type: %s)" % (attr, value, type(value).__name__))
                    except:
                        pass
                
                idx += 1
            
            print("\n" + "=" * 80)
            print("CONFRONTO CON LINEROUTE")
            print("=" * 80)
            
            # Costruisci mappa fermate abilitate
            print("\nFermate con IsRoutePoint=True nel LineRoute:")
            print("-" * 80)
            
            enabled_stops = []
            for item in lr.LineRouteItems:
                stop_no = item.AttValue("StopPointNo")
                if stop_no and stop_no > 0:
                    is_route = item.AttValue("IsRoutePoint")
                    if is_route == 1.0:
                        enabled_stops.append(stop_no)
                        print("  Stop %s" % int(stop_no))
            
            print("\nTotale fermate abilitate (IsRoutePoint=True): %d" % len(enabled_stops))
            
            # Confronta con TimeProfileItems
            tpi_stops = []
            for tpi in tp.TimeProfileItems:
                stop_no = tpi.AttValue("StopPointNo")
                tpi_stops.append(stop_no)
            
            print("Totale TimeProfileItems:                     %d" % len(tpi_stops))
            
            # Trova differenze
            print("\n" + "=" * 80)
            print("DIFFERENZE:")
            print("=" * 80)
            
            enabled_set = set([int(x) for x in enabled_stops])
            tpi_set = set([int(x) for x in tpi_stops if x])
            
            missing_in_tp = enabled_set - tpi_set
            extra_in_tp = tpi_set - enabled_set
            
            if missing_in_tp:
                print("\nFermate con IsRoutePoint=True MA NON nel TimeProfile:")
                for stop in sorted(missing_in_tp):
                    print("  - Stop %d" % stop)
            
            if extra_in_tp:
                print("\nFermate nel TimeProfile MA con IsRoutePoint=False:")
                for stop in sorted(extra_in_tp):
                    print("  - Stop %d" % stop)
            
            if not missing_in_tp and not extra_in_tp:
                print("\nTUTTO SINCRONIZZATO!")
            
            print("\n" + "=" * 80)
            print("CONCLUSIONE:")
            print("=" * 80)
            
            if missing_in_tp:
                print("\nLe seguenti fermate hanno IsRoutePoint=True ma NON sono nel TimeProfile:")
                for stop in sorted(missing_in_tp):
                    print("  - Stop %d" % stop)
                print("\nQueste fermate NON appariranno nell'interfaccia Time Profile Editor.")
                print("Non esiste un metodo API per crearle manualmente.")
                print("\nSOLUZIONE: Modificare manualmente dall'interfaccia di Visum:")
                print("1. Apri Line Route Editor")
                print("2. Clicca sul checkbox IsRoutePoint per le fermate")
                print("3. Visum dovrebbe creare automaticamente i TimeProfileItems")

except Exception as e:
    print("\nERRORE: %s" % str(e))
    import traceback
    traceback.print_exc()
