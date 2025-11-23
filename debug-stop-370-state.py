# -*- coding: ascii -*-
"""
Verifica dettagliata dello stato della fermata 370
"""

try:
    # Trova il LineRoute
    print("Ricerca LineRoute R17_2...")
    lr = None
    for lineroute in Visum.Net.LineRoutes:
        name = lineroute.AttValue("Name")
        if name == "R17_2":
            lr = lineroute
            break
    
    if lr is None:
        print("ERRORE: LineRoute R17_2 non trovato!")
    else:
        print("OK - LineRoute trovato\n")
        
        # Cerca la fermata 370
        print("=" * 80)
        print("FERMATA 370 - DETTAGLIO COMPLETO")
        print("=" * 80)
        
        stop_370_item = None
        stop_370_index = None
        seq = 0
        
        for item in lr.LineRouteItems:
            stop_no = item.AttValue("StopPointNo")
            
            if stop_no == 370:
                stop_370_item = item
                stop_370_index = seq
                
                print("TROVATA alla sequenza: %d" % seq)
                print("")
                print("Attributi LineRouteItem:")
                print("  StopPointNo    : %s (type: %s)" % (stop_no, type(stop_no)))
                
                is_route = item.AttValue("IsRoutePoint")
                print("  IsRoutePoint   : %s (type: %s)" % (is_route, type(is_route)))
                
                accum_len = item.AttValue("AccumLength")
                print("  AccumLength    : %s" % accum_len)
                
                index = item.AttValue("Index")
                print("  Index          : %s" % index)
                
                print("")
                print("Valutazione booleana:")
                print("  is_route == True       : %s" % (is_route == True))
                print("  is_route == 1.0        : %s" % (is_route == 1.0))
                print("  is_route == 1          : %s" % (is_route == 1))
                print("  bool(is_route)         : %s" % bool(is_route))
                print("  is_route != 0          : %s" % (is_route != 0))
                
                break
            
            if stop_no is not None and stop_no > 0:
                seq += 1
        
        if stop_370_item is None:
            print("ERRORE: Fermata 370 NON trovata!")
        else:
            print("")
            print("=" * 80)
            print("VERIFICA NEL TIMEPROFILE")
            print("=" * 80)
            
            # Prendi il TimeProfile
            tp = None
            for time_profile in lr.TimeProfiles:
                tp = time_profile
                break
            
            if tp is None:
                print("ERRORE: Nessun TimeProfile trovato!")
            else:
                print("TimeProfile: %s" % tp.AttValue("Name"))
                print("")
                
                # Conta le fermate abilitate prima della 370
                enabled_before_370 = 0
                for item in lr.LineRouteItems:
                    stop_no = item.AttValue("StopPointNo")
                    if stop_no is None or stop_no == 0:
                        continue
                    if stop_no == 370:
                        break
                    is_route = item.AttValue("IsRoutePoint")
                    if is_route == 1.0:
                        enabled_before_370 += 1
                
                print("Fermate abilitate prima della 370: %d" % enabled_before_370)
                print("")
                
                # Cerca la fermata 370 nel TimeProfile
                found_in_tp = False
                idx = 0
                for tpi in tp.TimeProfileItems:
                    stop_no = tpi.AttValue("StopPointNo")
                    if stop_no == 370:
                        found_in_tp = True
                        print("TROVATA nel TimeProfile alla posizione: %d" % idx)
                        print("")
                        print("Attributi TimeProfileItem:")
                        print("  StopPointNo : %s" % stop_no)
                        print("  Arr         : %s" % tpi.AttValue("Arr"))
                        print("  Dep         : %s" % tpi.AttValue("Dep"))
                        print("  StopTime    : %s" % tpi.AttValue("StopTime"))
                        print("  PreRunTime  : %s" % tpi.AttValue("PreRunTime"))
                        print("  PostRunTime : %s" % tpi.AttValue("PostRunTime"))
                        break
                    idx += 1
                
                if not found_in_tp:
                    print("NON TROVATA nel TimeProfile")
                    print("Posizione attesa: %d" % enabled_before_370)

except Exception as e:
    print("ERRORE: %s" % str(e))
    import traceback
    traceback.print_exc()
