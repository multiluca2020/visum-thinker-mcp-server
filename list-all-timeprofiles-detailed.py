# -*- coding: ascii -*-
"""
Lista TUTTI i TimeProfiles del LineRoute e identifica quale viene usato dalla GUI
"""

try:
    print("=" * 80)
    print("TUTTI I TIMEPROFILES DEL LINEROUTE R17_2")
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
        print("LineName: %s" % lr.AttValue("LineName"))
        print("")
        
        # Conta i TimeProfiles
        tp_count = 0
        for tp in lr.TimeProfiles:
            tp_count += 1
        
        print("NUMERO TOTALE DI TIMEPROFILES: %d" % tp_count)
        print("=" * 80)
        
        if tp_count == 0:
            print("\nNESSUN TIMEPROFILE TROVATO!")
        else:
            # Analizza ogni TimeProfile
            tp_idx = 0
            for tp in lr.TimeProfiles:
                tp_idx += 1
                
                print("\n" + "=" * 80)
                print("TIMEPROFILE #%d" % tp_idx)
                print("=" * 80)
                
                # Attributi del TimeProfile
                print("\nAttributi:")
                attrs_to_check = ["Name", "No", "Index", "IsActive", "Code"]
                for attr in attrs_to_check:
                    try:
                        value = tp.AttValue(attr)
                        print("  %-20s : %s" % (attr, value))
                    except:
                        pass
                
                # Conta TimeProfileItems
                tpi_count = 0
                stops_in_tp = []
                for tpi in tp.TimeProfileItems:
                    tpi_count += 1
                    stop_no = tpi.AttValue("StopPointNo")
                    if stop_no:
                        stops_in_tp.append(int(stop_no))
                
                print("\nTimeProfileItems: %d" % tpi_count)
                print("Fermate: %s" % stops_in_tp)
                
                # Verifica se contiene 370
                has_370 = 370 in stops_in_tp
                has_328 = 328 in stops_in_tp
                
                print("\nFermata 328 presente: %s" % ("SI" if has_328 else "NO"))
                print("Fermata 370 presente: %s" % ("SI" if has_370 else "NO"))
                
                if has_370:
                    print("\n*** QUESTO TIMEPROFILE CONTIENE LA FERMATA 370! ***")
                    
                    # Mostra dettagli fermata 370
                    for tpi in tp.TimeProfileItems:
                        stop_no = tpi.AttValue("StopPointNo")
                        if int(stop_no) == 370:
                            print("\nDettagli fermata 370:")
                            print("  Arr:      %s" % tpi.AttValue("Arr"))
                            print("  Dep:      %s" % tpi.AttValue("Dep"))
                            print("  StopTime: %s" % tpi.AttValue("StopTime"))
                            break
            
            print("\n" + "=" * 80)
            print("CONCLUSIONE:")
            print("=" * 80)
            
            if tp_count > 1:
                print("\nCI SONO %d TIMEPROFILES!" % tp_count)
                print("\nProbabilmente la GUI mostra un TimeProfile diverso da quello")
                print("che stiamo modificando con lo script.")
                print("\nDobbiamo identificare quale TimeProfile viene visualizzato")
                print("nella GUI e modificare quello specifico.")
            else:
                print("\nC'e' un solo TimeProfile.")
                print("Le modifiche dovrebbero essere visibili nella GUI.")
                print("\nSe non lo sono, potrebbe essere un problema di refresh")
                print("o un bug di Visum.")

except Exception as e:
    print("\nERRORE: %s" % str(e))
    import traceback
    traceback.print_exc()
