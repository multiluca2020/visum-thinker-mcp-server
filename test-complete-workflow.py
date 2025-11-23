# -*- coding: ascii -*-
"""
Test completo: modifica + salva + verifica
"""

try:
    print("=" * 80)
    print("TEST COMPLETO: MODIFICA + SALVA + VERIFICA")
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
        
        # Trova fermata 328
        print("\n2. Ricerca fermata 328...")
        stop_328_item = None
        for item in lr.LineRouteItems:
            stop_no = item.AttValue("StopPointNo")
            if stop_no == 328:
                stop_328_item = item
                print("   OK - Fermata 328 trovata")
                break
        
        if not stop_328_item:
            print("   ERRORE: Fermata 328 non trovata!")
        else:
            # Verifica stato attuale
            print("\n3. Stato attuale fermata 328:")
            is_route = stop_328_item.AttValue("IsRoutePoint")
            print("   IsRoutePoint: %s" % is_route)
            
            # Imposta IsRoutePoint = True
            print("\n4. Impostazione IsRoutePoint = True...")
            stop_328_item.SetAttValue("IsRoutePoint", True)
            print("   OK")
            
            # Verifica che sia stato impostato
            is_route_new = stop_328_item.AttValue("IsRoutePoint")
            print("   Nuovo valore IsRoutePoint: %s" % is_route_new)
            
            # Accedi al TimeProfile
            print("\n5. Accesso al TimeProfile...")
            tp = None
            for time_profile in lr.TimeProfiles:
                tp = time_profile
                break
            
            if not tp:
                print("   ERRORE: TimeProfile non trovato!")
            else:
                print("   OK - TimeProfile: %s" % tp.AttValue("Name"))
                
                # Conta TimeProfileItems PRIMA
                print("\n6. TimeProfileItems PRIMA di AddTimeProfileItem:")
                tpi_before = []
                for tpi in tp.TimeProfileItems:
                    stop_no = tpi.AttValue("StopPointNo")
                    tpi_before.append(stop_no)
                
                print("   Count: %d" % len(tpi_before))
                print("   Fermate: %s" % [int(x) for x in tpi_before])
                has_328_before = 328.0 in tpi_before
                print("   Fermata 328 presente: %s" % has_328_before)
                
                # AddTimeProfileItem
                if not has_328_before:
                    print("\n7. Chiamata AddTimeProfileItem...")
                    try:
                        new_tpi = tp.AddTimeProfileItem(stop_328_item)
                        print("   OK - AddTimeProfileItem completato")
                        print("   Ritorno: %s" % type(new_tpi).__name__)
                        
                        # Imposta tempi
                        print("\n8. Impostazione tempi...")
                        new_tpi.SetAttValue("Arr", 100)
                        new_tpi.SetAttValue("Dep", 160)
                        print("   OK - Arr=100, Dep=160")
                        
                    except Exception as e:
                        print("   ERRORE: %s" % str(e))
                else:
                    print("\n7. Fermata 328 gia' presente, skip AddTimeProfileItem")
                
                # Conta TimeProfileItems DOPO
                print("\n9. TimeProfileItems DOPO AddTimeProfileItem:")
                tpi_after = []
                for tpi in tp.TimeProfileItems:
                    stop_no = tpi.AttValue("StopPointNo")
                    tpi_after.append(stop_no)
                
                print("   Count: %d" % len(tpi_after))
                print("   Fermate: %s" % [int(x) for x in tpi_after])
                has_328_after = 328.0 in tpi_after
                print("   Fermata 328 presente: %s" % has_328_after)
                
                # Salva
                print("\n10. Salvataggio progetto...")
                try:
                    Visum.SaveVersion()
                    print("   OK - Progetto salvato")
                except Exception as e:
                    print("   ERRORE: %s" % str(e))
                
                # Verifica finale
                print("\n11. Verifica finale (dopo salvataggio):")
                tpi_final = []
                for tpi in tp.TimeProfileItems:
                    stop_no = tpi.AttValue("StopPointNo")
                    tpi_final.append(stop_no)
                
                print("   Count: %d" % len(tpi_final))
                has_328_final = 328.0 in tpi_final
                print("   Fermata 328 presente: %s" % has_328_final)
                
                # Risultato
                print("\n" + "=" * 80)
                print("RISULTATO:")
                print("=" * 80)
                print("Prima:   %d items, 328 presente: %s" % (len(tpi_before), has_328_before))
                print("Dopo:    %d items, 328 presente: %s" % (len(tpi_after), has_328_after))
                print("Finale:  %d items, 328 presente: %s" % (len(tpi_final), has_328_final))
                
                if not has_328_after:
                    print("\nCONCLUSIONE: AddTimeProfileItem() NON ha aggiunto la fermata!")
                    print("L'API Visum COM potrebbe non supportare questa operazione.")
                elif not has_328_final:
                    print("\nCONCLUSIONE: La fermata e' stata aggiunta ma persa dopo SaveVersion!")
                else:
                    print("\nCONCLUSIONE: SUCCESS! La fermata e' stata aggiunta correttamente.")
                    print("Chiudi e riapri il Time Profile Editor per vederla.")

except Exception as e:
    print("\nERRORE GENERALE: %s" % str(e))
    import traceback
    traceback.print_exc()
