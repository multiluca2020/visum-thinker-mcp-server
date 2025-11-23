# -*- coding: ascii -*-
"""
Inserisci TimeProfileItem per fermata 370 usando il metodo corretto
"""

try:
    print("=" * 80)
    print("INSERIMENTO TIMEPROFILEITEM PER FERMATA 370")
    print("=" * 80)
    
    # Trova il LineRoute
    print("\n1. Ricerca LineRoute R17_2...")
    lr = None
    for lineroute in Visum.Net.LineRoutes:
        name = lineroute.AttValue("Name")
        if name == "R17_2":
            lr = lineroute
            break
    
    if lr is None:
        print("   ERRORE: LineRoute R17_2 non trovato!")
    else:
        print("   OK")
        
        # Prendi il TimeProfile
        print("\n2. Accesso al TimeProfile...")
        tp = None
        for time_profile in lr.TimeProfiles:
            tp = time_profile
            break
        
        if tp is None:
            print("   ERRORE: Nessun TimeProfile trovato!")
        else:
            print("   OK - TimeProfile: %s" % tp.AttValue("Name"))
            
            # Trova il LineRouteItem della fermata 370
            print("\n3. Ricerca LineRouteItem per fermata 370...")
            stop_370_lr_item = None
            
            for item in lr.LineRouteItems:
                stop_no = item.AttValue("StopPointNo")
                if stop_no == 370:
                    stop_370_lr_item = item
                    lr_item_index = item.AttValue("Index")
                    print("   OK - Trovato LineRouteItem con Index: %s" % lr_item_index)
                    break
            
            if stop_370_lr_item is None:
                print("   ERRORE: Fermata 370 non trovata!")
            else:
                # Conta la posizione di inserimento
                print("\n4. Calcolo posizione di inserimento...")
                
                # La fermata 370 va inserita tra 173 (pos 11) e 419 (pos 12)
                # Quindi alla posizione 12
                insert_pos = 12
                print("   Posizione di inserimento: %d (dopo fermata 173)" % insert_pos)
                
                # Usa il metodo AddTimeProfileItem sul TimeProfile
                print("\n5. Inserimento TimeProfileItem...")
                print("   Chiamata: tp.AddTimeProfileItem(LineRouteItem)...")
                
                try:
                    # Il metodo potrebbe richiedere il LineRouteItem come parametro
                    new_tpi = tp.AddTimeProfileItem(stop_370_lr_item)
                    print("   OK - TimeProfileItem creato!")
                    
                    # Verifica se e' stato creato
                    print("\n6. Verifica creazione...")
                    found = False
                    for tpi in tp.TimeProfileItems:
                        stop_no = tpi.AttValue("StopPointNo")
                        if stop_no == 370:
                            found = True
                            print("   OK - Fermata 370 trovata nel TimeProfile!")
                            print("   Arr: %s" % tpi.AttValue("Arr"))
                            print("   Dep: %s" % tpi.AttValue("Dep"))
                            break
                    
                    if not found:
                        print("   ERRORE: Fermata 370 NON trovata dopo inserimento!")
                    
                    # Configura i tempi
                    if found:
                        print("\n7. Configurazione tempi...")
                        # Arr dovrebbe essere tra 3180 (fermata 173) e 3390 (fermata 419)
                        # Interpoliamo: circa 3360
                        new_tpi.SetAttValue("Arr", 3360)
                        new_tpi.SetAttValue("Dep", 3420)  # +60 sec di sosta
                        print("   OK - Arr=3360, Dep=3420 (StopTime=60)")
                        
                except Exception as e:
                    print("   ERRORE: %s" % str(e))
                    
                    # Prova altri parametri
                    print("\n   Tentativo con Index del LineRouteItem...")
                    try:
                        new_tpi = tp.AddTimeProfileItem(lr_item_index)
                        print("   OK - TimeProfileItem creato!")
                    except Exception as e2:
                        print("   ERRORE: %s" % str(e2))
                        
                        # Prova con posizione nel TimeProfile
                        print("\n   Tentativo con posizione TimeProfile (12)...")
                        try:
                            new_tpi = tp.AddTimeProfileItem(12)
                            print("   OK - TimeProfileItem creato!")
                        except Exception as e3:
                            print("   ERRORE: %s" % str(e3))
    
    print("\n" + "=" * 80)
    print("COMPLETATO")
    print("=" * 80)

except Exception as e:
    print("\nERRORE GENERALE: %s" % str(e))
    import traceback
    traceback.print_exc()
