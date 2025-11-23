# -*- coding: ascii -*-
"""
Verifica stato dopo riavvio Visum
"""

try:
    print("=" * 80)
    print("VERIFICA STATO DOPO RIAVVIO")
    print("=" * 80)
    
    # Trova LineRoute
    print("\n1. Accesso al LineRoute R17_2...")
    lr = None
    for lineroute in Visum.Net.LineRoutes:
        name = lineroute.AttValue("Name")
        if name == "R17_2":
            lr = lineroute
            break
    
    if not lr:
        print("   ERRORE: LineRoute non trovato!")
    else:
        print("   OK")
        
        # Verifica IsRoutePoint per fermate chiave
        print("\n2. Verifica IsRoutePoint nel LineRoute:")
        print("-" * 80)
        
        test_stops = [328, 370]
        for test_stop in test_stops:
            found = False
            for item in lr.LineRouteItems:
                stop_no = item.AttValue("StopPointNo")
                if stop_no == test_stop:
                    is_route = item.AttValue("IsRoutePoint")
                    print("   Stop %d: IsRoutePoint = %s" % (test_stop, is_route))
                    found = True
                    break
            if not found:
                print("   Stop %d: NON TROVATO" % test_stop)
        
        # Verifica TimeProfile
        print("\n3. Verifica TimeProfile:")
        print("-" * 80)
        
        tp = None
        for time_profile in lr.TimeProfiles:
            tp = time_profile
            break
        
        if not tp:
            print("   ERRORE: TimeProfile non trovato!")
        else:
            print("   TimeProfile: %s" % tp.AttValue("Name"))
            
            # Conta TimeProfileItems
            tpi_count = 0
            stops_in_tp = []
            for tpi in tp.TimeProfileItems:
                tpi_count += 1
                stop_no = tpi.AttValue("StopPointNo")
                stops_in_tp.append(int(stop_no))
            
            print("   Totale TimeProfileItems: %d" % tpi_count)
            print("")
            print("   Fermate nel TimeProfile:")
            print("   %s" % stops_in_tp)
            
            # Verifica fermate specifiche
            print("\n4. Verifica fermate specifiche:")
            print("-" * 80)
            
            for test_stop in test_stops:
                if test_stop in stops_in_tp:
                    print("   Stop %d: PRESENTE nel TimeProfile" % test_stop)
                    
                    # Trova i dettagli
                    for tpi in tp.TimeProfileItems:
                        stop_no = tpi.AttValue("StopPointNo")
                        if int(stop_no) == test_stop:
                            arr = tpi.AttValue("Arr")
                            dep = tpi.AttValue("Dep")
                            stop_time = tpi.AttValue("StopTime")
                            print("     Arr=%d, Dep=%d, StopTime=%d" % (arr, dep, stop_time))
                            break
                else:
                    print("   Stop %d: NON PRESENTE nel TimeProfile" % test_stop)
            
            print("\n" + "=" * 80)
            print("CONCLUSIONE:")
            print("=" * 80)
            
            if 328 not in stops_in_tp and 370 not in stops_in_tp:
                print("\nLE MODIFICHE SONO STATE PERSE!")
                print("\nPossibili cause:")
                print("1. Le modifiche non sono state salvate correttamente")
                print("2. Visum ha un bug con AddTimeProfileItem via API")
                print("3. Serve un commit esplicito che non abbiamo chiamato")
                print("\nProva a modificare manualmente dall'interfaccia per vedere")
                print("se il problema e' nell'API o nel file salvato.")
            elif 328 in stops_in_tp or 370 in stops_in_tp:
                print("\nALCUNE MODIFICHE SONO STATE SALVATE!")
                print("Verifica quali fermate sono presenti.")
            else:
                print("\nTUTTE LE MODIFICHE SONO STATE SALVATE CORRETTAMENTE!")

except Exception as e:
    print("\nERRORE: %s" % str(e))
    import traceback
    traceback.print_exc()
