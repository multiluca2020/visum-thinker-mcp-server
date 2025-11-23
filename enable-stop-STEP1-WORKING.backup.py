# -*- coding: ascii -*-
"""
Script per abilitare fermate con calcolo CORRETTO dei tempi
Usa la proporzione delle distanze per interpolare i tempi come fa Visum
"""

# ============================================================================
# CONFIGURAZIONE
# ============================================================================
TARGET_LINEROUTE_NAME = "R17_2"

# Operazioni da eseguire
# Formato: {StopPointNo: {"action": "enable", "stop_time": sec, "pre_run_add": sec, "post_run_add": sec}}
OPERATIONS = {
    370: {
        "action": "enable",
        "stop_time": 60,      # Tempo di sosta desiderato in secondi
        "pre_run_add": 30,    # Secondi da aggiungere al PreRunTime
        "post_run_add": 30    # Secondi da aggiungere al PostRunTime
    }
}

# ============================================================================
# FUNZIONI HELPER
# ============================================================================

def get_lr_stop_sequence(lr_items):
    """Ottieni sequenza fermate dal LineRoute con distanze"""
    stops = []
    for item in lr_items:
        try:
            stop_point_no = item.AttValue("StopPointNo")
            if stop_point_no and stop_point_no > 0:
                stops.append({
                    'item': item,
                    'stop': int(stop_point_no),
                    'is_route': item.AttValue("IsRoutePoint"),
                    'index': item.AttValue("Index"),
                    'accum_length': item.AttValue("AccumLength")  # Distanza cumulativa
                })
        except:
            pass
    
    stops.sort(key=lambda x: x['index'])
    return stops


def abilita_fermata(tp, stops, stop_no, stop_time, pre_run_add=0, post_run_add=0):
    """
    Abilita una fermata disabilitata nel TimeProfile con tempi personalizzati.
    
    Parametri:
        tp: TimeProfile object
        stops: Lista fermate da get_lr_stop_sequence()
        stop_no: Numero fermata da abilitare
        stop_time: Tempo di sosta in secondi
        pre_run_add: Secondi da aggiungere al PreRunTime (default 0)
        post_run_add: Secondi da aggiungere al PostRunTime (default 0)
    
    Returns:
        True se successo, False se errore
    """
    print("\nOperazione: ENABLE fermata %d (StopTime=%d sec, PreRun+%d, PostRun+%d)" % 
          (stop_no, stop_time, pre_run_add, post_run_add))
    print("-" * 80)
    
    # Trova fermata nella sequenza
    stop_idx = None
    for i, s in enumerate(stops):
        if s['stop'] == stop_no:
            stop_idx = i
            break
    
    if stop_idx is None:
        print("  ERRORE: Fermata %d non trovata!" % stop_no)
        return False
    
    if stop_idx == 0 or stop_idx == len(stops) - 1:
        print("  ERRORE: Non puoi modificare prima/ultima fermata!")
        return False
    
    current = stops[stop_idx]
    
    # Trova prev/next ABILITATI
    prev_stop = None
    next_stop = None
    
    for i in range(stop_idx - 1, -1, -1):
        if stops[i]['is_route']:
            prev_stop = stops[i]
            break
    
    for i in range(stop_idx + 1, len(stops)):
        if stops[i]['is_route']:
            next_stop = stops[i]
            break
    
    if not prev_stop or not next_stop:
        print("  ERRORE: Fermate adiacenti non trovate!")
        return False
    
    print("\n  Fermate adiacenti:")
    print("    Prev: %d (dist=%.1f)" % (prev_stop['stop'], prev_stop['accum_length']))
    print("    Curr: %d (dist=%.1f)" % (current['stop'], current['accum_length']))
    print("    Next: %d (dist=%.1f)" % (next_stop['stop'], next_stop['accum_length']))
    
    # Leggi tempi da TimeProfile
    prev_dep = None
    next_arr = None
    
    for tpi in tp.TimeProfileItems:
        s = tpi.AttValue("StopPointNo")
        if s and int(s) == prev_stop['stop']:
            prev_dep = tpi.AttValue("Dep")
        elif s and int(s) == next_stop['stop']:
            next_arr = tpi.AttValue("Arr")
    
    if prev_dep is None or next_arr is None:
        print("  ERRORE: Tempi prev/next non trovati!")
        return False
    
    time_total = next_arr - prev_dep
    print("\n  Tempi TimeProfile:")
    print("    Prev Dep:  %.1f" % prev_dep)
    print("    Next Arr:  %.1f" % next_arr)
    print("    Tempo totale: %.1f sec" % time_total)
    
    # [1] Abilita IsRoutePoint
    print("\n  [1] Impostazione IsRoutePoint...")
    if current['is_route']:
        current['item'].SetAttValue("IsRoutePoint", False)
        print("      Disabilitato temporaneamente")
    
    current['item'].SetAttValue("IsRoutePoint", True)
    print("      IsRoutePoint = True")
    
    # [2] RILEGGI AccumLength (ora aggiornato!)
    print("\n  [2] Rilettura AccumLength dopo abilitazione...")
    prev_accum = prev_stop['item'].AttValue("AccumLength")
    curr_accum = current['item'].AttValue("AccumLength")
    next_accum = next_stop['item'].AttValue("AccumLength")
    
    print("      Prev AccumLength: %.3f" % prev_accum)
    print("      Curr AccumLength: %.3f" % curr_accum)
    print("      Next AccumLength: %.3f" % next_accum)
    
    # [3] Calcola PreRunTime con interpolazione distanze
    dist_prev_curr = curr_accum - prev_accum
    dist_curr_next = next_accum - curr_accum
    dist_total = next_accum - prev_accum
    
    if abs(dist_total) < 0.001:
        print("      ERRORE: Distanza totale = 0, uso proporzione equa")
        pre_run_time = time_total / 2.0
    else:
        pre_run_time = (dist_prev_curr / dist_total) * time_total
    
    print("\n      Calcolo con distanze aggiornate:")
    print("        Dist prev->curr: %.3f" % dist_prev_curr)
    print("        Dist curr->next: %.3f" % dist_curr_next)
    print("        Dist totale:     %.3f" % dist_total)
    print("        Proporzione:     %.6f" % (dist_prev_curr / dist_total if dist_total > 0 else 0.5))
    print("        PreRunTime base: %.1f sec" % pre_run_time)
    
    # [4] Applica offset
    print("\n      Applicazione offset:")
    print("        PreRunTime base:    %.1f sec" % pre_run_time)
    print("        Offset PreRun:      +%d sec" % pre_run_add)
    print("        Offset PostRun:     +%d sec" % post_run_add)
    
    pre_run_time_final = pre_run_time + pre_run_add
    print("        PreRunTime finale:  %.1f sec" % pre_run_time_final)
    
    # [5] Calcola Arr e Dep
    arr = prev_dep + pre_run_time_final
    dep = arr + stop_time
    
    print("\n      Tempi finali fermata %d:" % stop_no)
    print("        Arr: %.1f" % arr)
    print("        Dep: %.1f" % dep)
    
    # [6] Crea TimeProfileItem
    print("\n  [3] Creazione TimeProfileItem...")
    new_tpi = tp.AddTimeProfileItem(current['item'])
    print("      TimeProfileItem creato")
    
    # [7] Imposta tempi
    print("\n  [4] Impostazione tempi...")
    new_tpi.SetAttValue("Arr", arr)
    new_tpi.SetAttValue("Dep", dep)
    print("      Tempi impostati")
    
    # [8] Aggiorna fermata successiva per PostRunTime
    if post_run_add != 0:
        print("\n  [4b] Aggiornamento fermata successiva per PostRun offset...")
        
        # Trova TimeProfileItem della fermata successiva
        next_tpi = None
        for tpi in tp.TimeProfileItems:
            s = tpi.AttValue("StopPointNo")
            if s and int(s) == next_stop['stop']:
                next_tpi = tpi
                break
        
        if next_tpi:
            next_arr_old = next_tpi.AttValue("Arr")
            next_dep_old = next_tpi.AttValue("Dep")
            next_stoptime = next_dep_old - next_arr_old
            
            # Nuovo Arr = vecchio Arr + offset PostRun
            next_arr_new = next_arr_old + post_run_add
            next_dep_new = next_arr_new + next_stoptime  # Mantieni stesso StopTime
            
            print("        Fermata successiva (%d):" % next_stop['stop'])
            print("          Arr: %.1f -> %.1f (+%d)" % (next_arr_old, next_arr_new, post_run_add))
            print("          Dep: %.1f -> %.1f" % (next_dep_old, next_dep_new))
            
            next_tpi.SetAttValue("Arr", next_arr_new)
            next_tpi.SetAttValue("Dep", next_dep_new)
            print("        OK - Fermata successiva aggiornata")
        else:
            print("        WARNING: TimeProfileItem successivo non trovato")
    
    # [9] Verifica
    print("\n  [5] Verifica...")
    arr_read = new_tpi.AttValue("Arr")
    dep_read = new_tpi.AttValue("Dep")
    stoptime_read = new_tpi.AttValue("StopTime")
    prerun_read = new_tpi.AttValue("PreRunTime")
    
    print("      Arr:      %.1f" % arr_read)
    print("      Dep:      %.1f" % dep_read)
    print("      StopTime: %.1f" % stoptime_read)
    print("      PreRun:   %.1f" % prerun_read)
    
    if abs(stoptime_read - stop_time) < 0.1:
        print("\n      OK: StopTime corretto!")
    else:
        print("\n      ATTENZIONE: StopTime = %.1f (atteso %.1f)" % (stoptime_read, stop_time))
    
    print("\n  Completato!")
    return True


# ============================================================================
# MAIN
# ============================================================================

try:
    print("=" * 80)
    print("ABILITAZIONE FERMATE CON CALCOLO TEMPI CORRETTO")
    print("=" * 80)
    print("\nUsa interpolazione proporzionale basata su distanze")
    print("come fa Visum automaticamente\n")
    
    # Trova LineRoute
    print("Ricerca LineRoute '%s'..." % TARGET_LINEROUTE_NAME)
    
    target_lr = None
    for lr in Visum.Net.LineRoutes:
        if lr.AttValue("Name") == TARGET_LINEROUTE_NAME:
            target_lr = lr
            break
    
    if target_lr is None:
        print("ERRORE: LineRoute '%s' non trovato!" % TARGET_LINEROUTE_NAME)
    else:
        print("OK - LineRoute trovato\n")
        
        # Ottieni TimeProfile
        tp = None
        for time_profile in target_lr.TimeProfiles:
            tp = time_profile
            break
        
        if not tp:
            print("ERRORE: Nessun TimeProfile trovato!")
        else:
            print("TimeProfile: %s\n" % tp.AttValue("Name"))
            print("=" * 80)
            
            # Ottieni sequenza fermate con distanze
            stops = get_lr_stop_sequence(target_lr.LineRouteItems)
            
            # Elabora operazioni
            for stop_no, config in OPERATIONS.items():
                operation = config.get("action", "enable")
                
                if operation == "enable":
                    stop_time = config.get("stop_time", 0)
                    pre_run_add = config.get("pre_run_add", 0)
                    post_run_add = config.get("post_run_add", 0)
                    
                    # Usa la funzione abilita_fermata
                    success = abilita_fermata(tp, stops, stop_no, stop_time, pre_run_add, post_run_add)
                    
                    if not success:
                        print("  ERRORE nell'abilitazione fermata %d" % stop_no)
                
                elif operation == "disable":
                    print("\nOperazione: DISABLE fermata %d" % stop_no)
                    print("-" * 80)
                    print("  TODO: Funzione disabilita_fermata() non ancora implementata")
                
                else:
                    print("\nOperazione: %s fermata %d - SCONOSCIUTA" % (operation, stop_no))
                    print("  ERRORE: Operazione '%s' non valida" % operation) 
                     
                print("-" * 80)
                
                # Trova fermata
                stop_idx = None
                for i, s in enumerate(stops):
                    if s['stop'] == stop_no:
                        stop_idx = i
                        break
                
                if stop_idx is None:
                    print("  ERRORE: Fermata %d non trovata!" % stop_no)
                    continue
                
                if stop_idx == 0 or stop_idx == len(stops) - 1:
                    print("  ERRORE: Non puoi modificare prima/ultima fermata!")
                    continue
                
                current = stops[stop_idx]
                
                if operation == "enable":
                    # Trova prev/next ABILITATI
                    prev_stop = None
                    next_stop = None
                    
                    for i in range(stop_idx - 1, -1, -1):
                        if stops[i]['is_route']:
                            prev_stop = stops[i]
                            break
                    
                    for i in range(stop_idx + 1, len(stops)):
                        if stops[i]['is_route']:
                            next_stop = stops[i]
                            break
                    
                    if not prev_stop or not next_stop:
                        print("  ERRORE: Fermate adiacenti non trovate!")
                        continue
                    
                    print("\n  Fermate adiacenti:")
                    print("    Prev: %d (dist=%.1f)" % (prev_stop['stop'], prev_stop['accum_length']))
                    print("    Curr: %d (dist=%.1f)" % (current['stop'], current['accum_length']))
                    print("    Next: %d (dist=%.1f)" % (next_stop['stop'], next_stop['accum_length']))
                    
                    # Leggi tempi da TimeProfile
                    prev_dep = None
                    next_arr = None
                    
                    for tpi in tp.TimeProfileItems:
                        s = tpi.AttValue("StopPointNo")
                        if s and int(s) == prev_stop['stop']:
                            prev_dep = tpi.AttValue("Dep")
                        elif s and int(s) == next_stop['stop']:
                            next_arr = tpi.AttValue("Arr")
                    
                    if prev_dep is None or next_arr is None:
                        print("  ERRORE: Tempi prev/next non trovati!")
                        continue
                    
                    print("\n  Tempi TimeProfile:")
                    print("    Prev Dep:  %.1f" % prev_dep)
                    print("    Next Arr:  %.1f" % next_arr)
                    
                    # CALCOLO CORRETTO: Interpolazione proporzionale basata su POSIZIONE
                    # Conta quante fermate ci sono tra prev e next
                    stops_between_prev_curr = 0
                    stops_between_curr_next = 0
                    
                    for i in range(stop_idx):
                        if stops[i]['stop'] == prev_stop['stop']:
                            stops_between_prev_curr = stop_idx - i - 1
                            break
                    
                    for i in range(stop_idx + 1, len(stops)):
                        if stops[i]['stop'] == next_stop['stop']:
                            stops_between_curr_next = i - stop_idx - 1
                            break
                    
                    total_stops_between = stops_between_prev_curr + 1 + stops_between_curr_next
                    time_total = next_arr - prev_dep
                    
                    # Proporzione basata sul numero di "segmenti" tra le fermate
                    # Se prev->curr ha 3 segmenti e curr->next ha 5, totale = 8
                    # PreRun = (3+1) / (8+1) * tempo_totale
                    segments_to_curr = stops_between_prev_curr + 1
                    total_segments = total_stops_between + 1
                    
                    pre_run_time = (segments_to_curr / total_segments) * time_total
                    
                    print("\n  Calcolo interpolazione (basato su posizione):")
                    print("    Fermate tra prev e curr: %d" % stops_between_prev_curr)
                    print("    Fermate tra curr e next: %d" % stops_between_curr_next)
                    print("    Segmenti a curr:         %d" % segments_to_curr)
                    print("    Segmenti totali:         %d" % total_segments)
                    print("    Tempo totale:            %.1f sec" % time_total)
                    print("    Proporzione:             %.3f" % (segments_to_curr / total_segments))
                    print("    PreRunTime calcolato:    %.1f sec" % pre_run_time)
                    
                    # Calcola Arr e Dep
                    arr_370 = prev_dep + pre_run_time
                    dep_370 = arr_370 + stop_time
                    
                    print("\n  Tempi finali:")
                    print("    Arr:      %.1f" % arr_370)
                    print("    Dep:      %.1f" % dep_370)
                    print("    StopTime: %.1f" % stop_time)
                    
                    # Abilita IsRoutePoint
                    print("\n  [1] Impostazione IsRoutePoint...")
                    if current['is_route']:
                        current['item'].SetAttValue("IsRoutePoint", False)
                        print("      Disabilitato temporaneamente")
                    
                    current['item'].SetAttValue("IsRoutePoint", True)
                    print("      IsRoutePoint = True")
                    
                    # RILEGGI LE DISTANZE AGGIORNATE
                    print("\n  [2] Rilettura AccumLength dopo abilitazione...")
                    prev_accum = prev_stop['item'].AttValue("AccumLength")
                    curr_accum = current['item'].AttValue("AccumLength")
                    next_accum = next_stop['item'].AttValue("AccumLength")
                    
                    print("      Prev AccumLength: %.3f" % prev_accum)
                    print("      Curr AccumLength: %.3f" % curr_accum)
                    print("      Next AccumLength: %.3f" % next_accum)
                    
                    # RICALCOLA con distanze aggiornate
                    dist_prev_curr = curr_accum - prev_accum
                    dist_curr_next = next_accum - curr_accum
                    dist_total = next_accum - prev_accum
                    
                    if abs(dist_total) < 0.001:
                        print("      ERRORE: Distanza totale = 0, uso proporzione equa")
                        pre_run_time = time_total / 2.0
                    else:
                        pre_run_time = (dist_prev_curr / dist_total) * time_total
                    
                    print("\n      Calcolo con distanze aggiornate:")
                    print("        Dist prev->curr: %.3f" % dist_prev_curr)
                    print("        Dist curr->next: %.3f" % dist_curr_next)
                    print("        Dist totale:     %.3f" % dist_total)
                    print("        Proporzione:     %.6f" % (dist_prev_curr / dist_total if dist_total > 0 else 0.5))
                    print("        PreRunTime:      %.1f sec" % pre_run_time)
                    
                    # AGGIUNGI OFFSET a PreRunTime e PostRunTime
                    print("\n      Applicazione offset:")
                    print("        PreRunTime base:    %.1f sec" % pre_run_time)
                    print("        Offset PreRun:      +%d sec" % pre_run_add)
                    print("        Offset PostRun:     +%d sec" % post_run_add)
                    
                    pre_run_time_final = pre_run_time + pre_run_add
                    print("        PreRunTime finale:  %.1f sec" % pre_run_time_final)
                    
                    # RICALCOLA Arr e Dep con PreRunTime finale
                    arr_370 = prev_dep + pre_run_time_final
                    dep_370 = arr_370 + stop_time
                    
                    # PostRun si ottiene modificando la fermata SUCCESSIVA
                    # PostRun di curr = Arr(next) - Dep(curr)
                    # Vogliamo PostRun + post_run_add, quindi:
                    # nuovo Arr(next) = Dep(curr) + PostRun_originale + post_run_add
                    
                    print("\n      Tempi finali fermata %d:" % stop_no)
                    print("        Arr: %.1f" % arr_370)
                    print("        Dep: %.1f" % dep_370)
                    
                    # Crea TimeProfileItem
                    print("\n  [3] Creazione TimeProfileItem...")
                    new_tpi = tp.AddTimeProfileItem(current['item'])
                    print("      TimeProfileItem creato")
                    
                    # Imposta tempi
                    print("\n  [4] Impostazione tempi...")
                    new_tpi.SetAttValue("Arr", arr_370)
                    new_tpi.SetAttValue("Dep", dep_370)
                    print("      Tempi impostati")
                    
                    # AGGIORNA FERMATA SUCCESSIVA per PostRunTime
                    if post_run_add != 0:
                        print("\n  [4b] Aggiornamento fermata successiva per PostRun offset...")
                        
                        # Trova TimeProfileItem della fermata successiva
                        next_tpi = None
                        for tpi in tp.TimeProfileItems:
                            s = tpi.AttValue("StopPointNo")
                            if s and int(s) == next_stop['stop']:
                                next_tpi = tpi
                                break
                        
                        if next_tpi:
                            next_arr_old = next_tpi.AttValue("Arr")
                            next_dep_old = next_tpi.AttValue("Dep")
                            next_stoptime = next_dep_old - next_arr_old
                            
                            # Nuovo Arr = vecchio Arr + offset PostRun
                            next_arr_new = next_arr_old + post_run_add
                            next_dep_new = next_arr_new + next_stoptime  # Mantieni stesso StopTime
                            
                            print("        Fermata successiva (%d):" % next_stop['stop'])
                            print("          Arr: %.1f -> %.1f (+%d)" % (next_arr_old, next_arr_new, post_run_add))
                            print("          Dep: %.1f -> %.1f" % (next_dep_old, next_dep_new))
                            
                            next_tpi.SetAttValue("Arr", next_arr_new)
                            next_tpi.SetAttValue("Dep", next_dep_new)
                            print("        OK - Fermata successiva aggiornata")
                        else:
                            print("        WARNING: TimeProfileItem successivo non trovato")
                    
                    print("      Tempi impostati con offset")
                    
                    # Verifica
                    print("\n  [5] Verifica...")
                    arr_read = new_tpi.AttValue("Arr")
                    dep_read = new_tpi.AttValue("Dep")
                    stoptime_read = new_tpi.AttValue("StopTime")
                    prerun_read = new_tpi.AttValue("PreRunTime")
                    
                    print("      Arr:      %.1f" % arr_read)
                    print("      Dep:      %.1f" % dep_read)
                    print("      StopTime: %.1f" % stoptime_read)
                    print("      PreRun:   %.1f" % prerun_read)
                    
                    if abs(stoptime_read - stop_time) < 0.1:
                        print("\n      OK: StopTime corretto!")
                    else:
                        print("\n      ATTENZIONE: StopTime = %.1f (atteso %.1f)" % (stoptime_read, stop_time))
                    
                    print("\n  Completato!")
            
            print("\n" + "=" * 80)
            print("OPERAZIONI COMPLETATE!")
            print("=" * 80)
            print("\nPer vedere le modifiche:")
            print("  - Chiudi e riapri Edit > Time Profiles")
            print("  - Oppure salva e riapri il progetto")
            print("=" * 80)

except Exception as e:
    print("\nERRORE: %s" % str(e))
    import traceback
    traceback.print_exc()
