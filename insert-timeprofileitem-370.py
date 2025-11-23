# -*- coding: ascii -*-
"""
Forza l'inserimento del TimeProfileItem per la fermata 370
"""

try:
    print("=" * 80)
    print("INSERIMENTO MANUALE TIMEPROFILEITEM PER FERMATA 370")
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
        print("   OK - LineRoute trovato")
        
        # Prendi il TimeProfile
        print("\n2. Accesso al TimeProfile...")
        tp = None
        for time_profile in lr.TimeProfiles:
            tp = time_profile
            break
        
        if tp is None:
            print("   ERRORE: Nessun TimeProfile trovato!")
        else:
            tp_name = tp.AttValue("Name")
            print("   OK - TimeProfile: %s" % tp_name)
            
            # Trova la fermata 370 nel LineRoute
            print("\n3. Ricerca fermata 370 nel LineRoute...")
            stop_370_lr_item = None
            stop_370_seq = None
            
            seq = 0
            for item in lr.LineRouteItems:
                stop_no = item.AttValue("StopPointNo")
                if stop_no == 370:
                    stop_370_lr_item = item
                    stop_370_seq = seq
                    print("   OK - Fermata 370 trovata alla sequenza: %d" % seq)
                    break
                if stop_no is not None and stop_no > 0:
                    seq += 1
            
            if stop_370_lr_item is None:
                print("   ERRORE: Fermata 370 non trovata!")
            else:
                # Conta quante fermate abilitate ci sono prima
                print("\n4. Calcolo posizione di inserimento...")
                enabled_before = 0
                for item in lr.LineRouteItems:
                    stop_no = item.AttValue("StopPointNo")
                    if stop_no is None or stop_no == 0:
                        continue
                    if stop_no == 370:
                        break
                    is_route = item.AttValue("IsRoutePoint")
                    if is_route == 1.0:
                        enabled_before += 1
                
                insert_pos = enabled_before
                print("   Posizione di inserimento: %d" % insert_pos)
                print("   Fermate abilitate prima: %d" % enabled_before)
                
                # Verifica se esiste gia' nel TimeProfile
                print("\n5. Verifica esistenza nel TimeProfile...")
                already_exists = False
                idx = 0
                for tpi in tp.TimeProfileItems:
                    stop_no = tpi.AttValue("StopPointNo")
                    if stop_no == 370:
                        already_exists = True
                        print("   Fermata 370 GIA' PRESENTE alla posizione: %d" % idx)
                        break
                    idx += 1
                
                if not already_exists:
                    print("   Fermata 370 NON presente - inserimento necessario")
                    
                    # Prova a usare il metodo AddTimeProfileItem
                    print("\n6. Tentativo inserimento TimeProfileItem...")
                    
                    try:
                        # Metodo 1: AddTimeProfileItem con indice
                        print("   Metodo 1: tp.TimeProfileItems.AddTimeProfileItem(index)...")
                        new_tpi = tp.TimeProfileItems.AddTimeProfileItem(insert_pos)
                        print("   OK - TimeProfileItem creato!")
                        
                        # Imposta i tempi
                        print("\n7. Configurazione tempi...")
                        new_tpi.SetAttValue("Arr", 3360)
                        new_tpi.SetAttValue("Dep", 3420)
                        print("   OK - Tempi impostati: Arr=3360, Dep=3420 (StopTime=60)")
                        
                    except Exception as e1:
                        print("   ERRORE Metodo 1: %s" % str(e1))
                        
                        try:
                            # Metodo 2: Usa l'indice del LineRouteItem
                            print("   Metodo 2: tp.TimeProfileItems.AddTimeProfileItem(lr_item_index)...")
                            lr_item_index = stop_370_lr_item.AttValue("Index")
                            new_tpi = tp.TimeProfileItems.AddTimeProfileItem(lr_item_index)
                            print("   OK - TimeProfileItem creato!")
                            
                            # Imposta i tempi
                            print("\n7. Configurazione tempi...")
                            new_tpi.SetAttValue("Arr", 3360)
                            new_tpi.SetAttValue("Dep", 3420)
                            print("   OK - Tempi impostati: Arr=3360, Dep=3420 (StopTime=60)")
                            
                        except Exception as e2:
                            print("   ERRORE Metodo 2: %s" % str(e2))
                            
                            # Metodo 3: Prova senza parametri
                            try:
                                print("   Metodo 3: tp.TimeProfileItems.AddTimeProfileItem()...")
                                new_tpi = tp.TimeProfileItems.AddTimeProfileItem()
                                print("   OK - TimeProfileItem creato!")
                                
                            except Exception as e3:
                                print("   ERRORE Metodo 3: %s" % str(e3))
                                print("\n   TUTTI I METODI FALLITI!")
                else:
                    print("   Nessun inserimento necessario")
    
    print("\n" + "=" * 80)
    print("COMPLETATO")
    print("=" * 80)

except Exception as e:
    print("\nERRORE GENERALE: %s" % str(e))
    import traceback
    traceback.print_exc()
