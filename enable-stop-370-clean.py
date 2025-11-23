# -*- coding: ascii -*-
"""
Script per abilitare fermata 370 da progetto PULITO
Con logging dettagliato di ogni passo
"""

try:
    print("=" * 80)
    print("ABILITAZIONE FERMATA 370 DA PROGETTO PULITO")
    print("=" * 80)
    
    # Step 1: Trova LineRoute
    print("\n[STEP 1] Ricerca LineRoute R17_2...")
    lr = None
    for lineroute in Visum.Net.LineRoutes:
        name = lineroute.AttValue("Name")
        if name == "R17_2":
            lr = lineroute
            break
    
    if not lr:
        print("ERRORE: LineRoute non trovato!")
        raise Exception("LineRoute R17_2 non trovato")
    
    print("  OK: LineRoute trovato")
    print("      Name: %s" % lr.AttValue("Name"))
    print("      LineName: %s" % lr.AttValue("LineName"))
    
    # Step 2: Trova TimeProfile
    print("\n[STEP 2] Ricerca TimeProfile...")
    tp = None
    for time_profile in lr.TimeProfiles:
        tp = time_profile
        break
    
    if not tp:
        print("ERRORE: TimeProfile non trovato!")
        raise Exception("TimeProfile non trovato")
    
    tp_name = tp.AttValue("Name")
    print("  OK: TimeProfile trovato")
    print("      Name: %s" % tp_name)
    
    # Step 3: Conta TimeProfileItems PRIMA
    print("\n[STEP 3] Stato INIZIALE TimeProfile...")
    initial_count = 0
    has_370_before = False
    
    for tpi in tp.TimeProfileItems:
        initial_count += 1
        stop_no = tpi.AttValue("StopPointNo")
        if stop_no and int(stop_no) == 370:
            has_370_before = True
    
    print("  TimeProfileItems iniziali: %d" % initial_count)
    print("  Fermata 370 presente: %s" % has_370_before)
    
    # Step 4: Trova LineRouteItem della fermata 370
    print("\n[STEP 4] Ricerca LineRouteItem fermata 370...")
    lri_370 = None
    lri_370_index = None
    
    for lri in lr.LineRouteItems:
        stop_no = lri.AttValue("StopPointNo")
        if stop_no and int(stop_no) == 370:
            lri_370 = lri
            lri_370_index = lri.AttValue("Index")
            break
    
    if not lri_370:
        print("ERRORE: LineRouteItem 370 non trovato!")
        raise Exception("LineRouteItem 370 non trovato")
    
    print("  OK: LineRouteItem 370 trovato")
    print("      Index: %s" % lri_370_index)
    
    is_route_point_before = lri_370.AttValue("IsRoutePoint")
    print("      IsRoutePoint PRIMA: %s" % is_route_point_before)
    
    # Step 5: Trova fermata precedente e successiva
    print("\n[STEP 5] Ricerca fermate adiacenti...")
    
    stops_sequence = []
    for lri in lr.LineRouteItems:
        stop_no = lri.AttValue("StopPointNo")
        if stop_no:
            is_rp = lri.AttValue("IsRoutePoint")
            idx = lri.AttValue("Index")
            stops_sequence.append({
                'stop': int(stop_no),
                'index': idx,
                'is_route_point': is_rp,
                'item': lri
            })
    
    # Ordina per index
    stops_sequence.sort(key=lambda x: x['index'])
    
    # Trova posizione 370
    pos_370 = None
    for i, stop in enumerate(stops_sequence):
        if stop['stop'] == 370:
            pos_370 = i
            break
    
    if pos_370 is None:
        print("ERRORE: Fermata 370 non trovata nella sequenza!")
        raise Exception("Fermata 370 non in sequenza")
    
    # Trova prev/next abilitati
    prev_enabled = None
    next_enabled = None
    
    for i in range(pos_370 - 1, -1, -1):
        if stops_sequence[i]['is_route_point']:
            prev_enabled = stops_sequence[i]
            break
    
    for i in range(pos_370 + 1, len(stops_sequence)):
        if stops_sequence[i]['is_route_point']:
            next_enabled = stops_sequence[i]
            break
    
    if not prev_enabled or not next_enabled:
        print("ERRORE: Fermate adiacenti non trovate!")
        raise Exception("Prev/Next non trovati")
    
    print("  Fermata precedente: %d" % prev_enabled['stop'])
    print("  Fermata 370:        %d" % stops_sequence[pos_370]['stop'])
    print("  Fermata successiva: %d" % next_enabled['stop'])
    
    # Step 6: Leggi tempi dalle fermate adiacenti nel TimeProfile
    print("\n[STEP 6] Lettura tempi da TimeProfile...")
    
    prev_dep = None
    next_arr = None
    
    for tpi in tp.TimeProfileItems:
        stop_no = tpi.AttValue("StopPointNo")
        if stop_no:
            if int(stop_no) == prev_enabled['stop']:
                prev_dep = tpi.AttValue("Dep")
                print("  Fermata %d Dep: %s" % (prev_enabled['stop'], prev_dep))
            elif int(stop_no) == next_enabled['stop']:
                next_arr = tpi.AttValue("Arr")
                print("  Fermata %d Arr: %s" % (next_enabled['stop'], next_arr))
    
    if prev_dep is None or next_arr is None:
        print("ERRORE: Tempi non trovati!")
        raise Exception("Tempi prev/next non trovati")
    
    # Step 7: Calcola tempi per fermata 370
    print("\n[STEP 7] Calcolo tempi per fermata 370...")
    
    # Tempo totale disponibile tra prev e next
    total_time = next_arr - prev_dep
    print("  Tempo totale prev->next: %s sec" % total_time)
    
    # Dividi: metà per PreRun, 60 per Stop, resto per PostRun
    stop_time = 60.0
    pre_run_time = (total_time - stop_time) / 2.0
    
    arr_370 = prev_dep + pre_run_time
    dep_370 = arr_370 + stop_time
    
    print("  Arr calcolato: %s" % arr_370)
    print("  Dep calcolato: %s" % dep_370)
    print("  StopTime: %s" % stop_time)
    print("  PreRunTime: %s" % pre_run_time)
    
    # Step 8: Abilita IsRoutePoint
    print("\n[STEP 8] Abilitazione IsRoutePoint...")
    
    # Prima disabilita (per forzare ricreazione)
    lri_370.SetAttValue("IsRoutePoint", False)
    print("  IsRoutePoint impostato a False")
    
    # Poi riabilita
    lri_370.SetAttValue("IsRoutePoint", True)
    print("  IsRoutePoint impostato a True")
    
    is_route_point_after = lri_370.AttValue("IsRoutePoint")
    print("  IsRoutePoint DOPO: %s" % is_route_point_after)
    
    # Step 9: Crea TimeProfileItem
    print("\n[STEP 9] Creazione TimeProfileItem...")
    
    new_tpi = tp.AddTimeProfileItem(lri_370)
    print("  TimeProfileItem creato")
    
    # Step 10: Imposta tempi
    print("\n[STEP 10] Impostazione tempi...")
    
    new_tpi.SetAttValue("Arr", arr_370)
    print("  Arr impostato: %s" % arr_370)
    
    new_tpi.SetAttValue("Dep", dep_370)
    print("  Dep impostato: %s" % dep_370)
    
    # Step 11: Verifica lettura immediata
    print("\n[STEP 11] Verifica IMMEDIATA dopo impostazione...")
    
    arr_read = new_tpi.AttValue("Arr")
    dep_read = new_tpi.AttValue("Dep")
    stoptime_read = new_tpi.AttValue("StopTime")
    
    print("  Arr letto:      %s" % arr_read)
    print("  Dep letto:      %s" % dep_read)
    print("  StopTime letto: %s" % stoptime_read)
    
    if abs(stoptime_read - stop_time) < 0.01:
        print("  OK: StopTime corretto!")
    else:
        print("  PROBLEMA: StopTime = %s (atteso %s)" % (stoptime_read, stop_time))
    
    # Step 12: Conta TimeProfileItems DOPO
    print("\n[STEP 12] Stato FINALE TimeProfile...")
    
    final_count = 0
    has_370_after = False
    
    for tpi in tp.TimeProfileItems:
        final_count += 1
        stop_no = tpi.AttValue("StopPointNo")
        if stop_no and int(stop_no) == 370:
            has_370_after = True
    
    print("  TimeProfileItems finali: %d" % final_count)
    print("  Fermata 370 presente: %s" % has_370_after)
    
    # Step 13: Riepilogo
    print("\n" + "=" * 80)
    print("OPERAZIONE COMPLETATA")
    print("=" * 80)
    print("\nRisultato:")
    print("  TimeProfileItems: %d -> %d" % (initial_count, final_count))
    print("  Fermata 370 aggiunta: %s" % has_370_after)
    print("  StopTime database: %s secondi" % stoptime_read)
    
    print("\n" + "=" * 80)
    print("ADESSO VERIFICA NELLA GUI:")
    print("=" * 80)
    print("1. Apri Edit > Time Profiles")
    print("2. Seleziona LineRoute R17_2")
    print("3. Seleziona TimeProfile '%s'" % tp_name)
    print("4. Trova la fermata 370 nella lista")
    print("5. Verifica il valore di StopTime nella colonna")
    print("")
    print("DIMMI: Quale valore vedi nella colonna StopTime per la fermata 370?")

except Exception as e:
    print("\nERRORE: %s" % str(e))
    import traceback
    traceback.print_exc()
