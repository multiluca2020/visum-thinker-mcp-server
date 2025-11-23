# -*- coding: ascii -*-
"""
Script completo per abilitare/disabilitare fermate in un LineRoute
Usa l'approccio StopTime + PreRunTime/PostRunTime (approccio 2)

FUNZIONALITA:
1. Disabilita fermata: IsRoutePoint=False + rimuove TimeProfileItem
2. Abilita fermata: IsRoutePoint=True + inserisce TimeProfileItem con tempi interpolati

IMPORTANTE: Modifica solo le fermate intermedie (non prima/ultima)
"""

# ============================================================================
# CONFIGURAZIONE
# ============================================================================
TARGET_LINEROUTE_NAME = "R17_2"

# Operazioni da eseguire
# Formato: {StopPointNo: {"action": "enable"/"disable", "stop_time": sec, "pre_run_add": sec, "post_run_add": sec}}
OPERATIONS = {
    328: {
        "action": "enable",
        "stop_time": 60,      # 1 minuto di sosta
        "pre_run_add": 30,    # +30 sec al tempo di percorrenza prima
        "post_run_add": 30    # +30 sec al tempo di percorrenza dopo
    }
}

# Tempi di default per fermate abilitate (se non specificati)
DEFAULT_STOP_TIME = 60  # secondi (1 minuto)

# ============================================================================
# FUNZIONI HELPER
# ============================================================================

def get_lr_stop_sequence(lr_items):
    """Ottieni sequenza fermate dal LineRoute"""
    stops = []
    for item in lr_items:
        try:
            stop_point_no = item.AttValue("StopPointNo")
            if stop_point_no and stop_point_no > 0:
                stops.append({
                    'item': item,
                    'stop_point_no': stop_point_no,
                    'is_route': item.AttValue("IsRoutePoint"),
                    'accum_length': item.AttValue("AccumLength"),
                    'index': item.AttValue("Index")
                })
        except:
            pass
    return stops

def interpolate_runtime(prev_stop, next_stop, current_stop):
    """Interpola il tempo di percorrenza basandosi sulle distanze"""
    if prev_stop is None or next_stop is None:
        return DEFAULT_STOP_TIME  # Fallback
    
    # Distanze
    d_prev = prev_stop['accum_length']
    d_curr = current_stop['accum_length']
    d_next = next_stop['accum_length']
    
    # Tempo totale prev->next
    total_time = prev_stop.get('post_run_time', 0)
    
    # Interpola proporzionalmente
    if d_next > d_prev:
        ratio = (d_curr - d_prev) / (d_next - d_prev)
        runtime_to_curr = total_time * ratio
        return max(30, runtime_to_curr)  # Minimo 30 secondi
    
    return DEFAULT_STOP_TIME

# ============================================================================
# SCRIPT PRINCIPALE
# ============================================================================
print("=" * 80)
print("MODIFICA FERMATE LINE ROUTE: %s" % TARGET_LINEROUTE_NAME)
print("=" * 80)

try:
    # Trova il LineRoute
    line_routes = Visum.Net.LineRoutes
    target_lr = None
    
    for lr in line_routes:
        if lr.AttValue("Name") == TARGET_LINEROUTE_NAME:
            target_lr = lr
            break
    
    if target_lr is None:
        print("ERRORE: LineRoute non trovato!")
    else:
        print("LineRoute: %s" % TARGET_LINEROUTE_NAME)
        print("Operazioni da eseguire: %d\n" % len(OPERATIONS))
        
        # Ottieni sequenza fermate
        lr_items = target_lr.LineRouteItems
        stops = get_lr_stop_sequence(lr_items)
        
        print("Fermate totali: %d" % len(stops))
        print("Fermate abilitate: %d" % sum(1 for s in stops if s['is_route']))
        print("")
        
        # Ottieni TimeProfile
        time_profiles = target_lr.TimeProfiles
        if time_profiles.Count == 0:
            print("ERRORE: Nessun TimeProfile! Creane uno prima.")
        else:
            tp = None
            for t in time_profiles:
                tp = t
                break
            
            print("TimeProfile: %s" % tp.AttValue("Name"))
            print("=" * 80)
            
            # Elabora ogni operazione
            for stop_no, op_config in OPERATIONS.items():
                # Supporta sia il vecchio formato che il nuovo
                if isinstance(op_config, str):
                    operation = op_config
                    stop_time = DEFAULT_STOP_TIME
                    pre_run_add = 0
                    post_run_add = 0
                else:
                    operation = op_config.get("action", "enable")
                    stop_time = op_config.get("stop_time", DEFAULT_STOP_TIME)
                    pre_run_add = op_config.get("pre_run_add", 0)
                    post_run_add = op_config.get("post_run_add", 0)
                
                print("\nOperazione: %s fermata %d" % (operation.upper(), stop_no))
                print("-" * 80)
                
                # Trova la fermata nella sequenza
                stop_idx = None
                for i, s in enumerate(stops):
                    if s['stop_point_no'] == stop_no:
                        stop_idx = i
                        break
                
                if stop_idx is None:
                    print("  ERRORE: Fermata %d non trovata!" % stop_no)
                    continue
                
                # Verifica che non sia prima/ultima
                if stop_idx == 0:
                    print("  ERRORE: Non puoi modificare la prima fermata!")
                    continue
                if stop_idx == len(stops) - 1:
                    print("  ERRORE: Non puoi modificare l'ultima fermata!")
                    continue
                
                current = stops[stop_idx]
                
                if operation == "disable":
                    # DISABILITA FERMATA
                    if not current['is_route']:
                        print("  Fermata gia' disabilitata, skip.")
                        continue
                    
                    print("  Disabilitazione fermata %d..." % stop_no)
                    
                    # 1. Imposta IsRoutePoint = False
                    try:
                        current['item'].SetAttValue("IsRoutePoint", False)
                        print("  OK - IsRoutePoint impostato a False")
                    except Exception as e:
                        print("  ERRORE: %s" % str(e))
                        continue
                    
                    # 2. Rimuovi il TimeProfileItem corrispondente
                    # (Visum lo fa automaticamente quando IsRoutePoint=False)
                    print("  TimeProfileItem rimosso automaticamente")
                    
                elif operation == "enable":
                    # ABILITA FERMATA
                    # NON saltare se gia' abilitata - potrebbe non essere nel TimeProfile!
                    # if current['is_route']:
                    #     print("  Fermata gia' abilitata, skip.")
                    #     continue
                    
                    print("  Abilitazione fermata %d..." % stop_no)
                    
                    # 1. Forza ricreazione: prima disabilita, poi riabilita
                    try:
                        if current['is_route']:
                            print("  IsRoutePoint gia' True - forzando disabilitazione...")
                            current['item'].SetAttValue("IsRoutePoint", False)
                            print("  OK - IsRoutePoint disabilitato")
                        
                        print("  Impostazione IsRoutePoint a True...")
                        current['item'].SetAttValue("IsRoutePoint", True)
                        print("  OK - IsRoutePoint impostato a True")
                    except Exception as e:
                        print("  ERRORE impostazione IsRoutePoint: %s" % str(e))
                        continue
                    
                    # 2. Inserisci manualmente il TimeProfileItem
                    print("  Inserimento TimeProfileItem...")
                    
                    try:
                        # Accedi al TimeProfile (usa il primo disponibile)
                        tp = None
                        for time_profile in lr.TimeProfiles:
                            tp = time_profile
                            break
                        
                        if tp is None:
                            print("  ERRORE: Nessun TimeProfile trovato!")
                            continue
                        
                        # Usa il metodo AddTimeProfileItem con il LineRouteItem
                        tpi = tp.AddTimeProfileItem(current['item'])
                        print("  OK - TimeProfileItem creato")
                        
                        # Configura i tempi
                        print("  Configurazione tempi TimeProfileItem...")
                        
                        # Leggi i valori attuali (Visum ha gia' interpolato)
                        current_arr = tpi.AttValue("Arr")
                        current_dep = tpi.AttValue("Dep")
                        print("  Tempi iniziali: Arr=%d, Dep=%d" % (current_arr, current_dep))
                        
                        # Trova fermata precedente e successiva nel TimeProfile
                        prev_tpi = None
                        next_tpi = None
                        found_current = False
                        
                        for item in tp.TimeProfileItems:
                            item_stop = item.AttValue("StopPointNo")
                            if item_stop == stop_no:
                                found_current = True
                            elif not found_current:
                                prev_tpi = item  # Ultima fermata prima della corrente
                            elif found_current and next_tpi is None:
                                next_tpi = item  # Prima fermata dopo la corrente
                                break
                        
                        # Calcola i nuovi tempi
                        if prev_tpi and next_tpi:
                            prev_dep = prev_tpi.AttValue("Dep")
                            next_arr = next_tpi.AttValue("Arr")
                            
                            # Nuovo Arr = Dep precedente + PreRunTime originale + pre_run_add
                            original_pre_run = current_arr - prev_dep
                            new_arr = prev_dep + original_pre_run + pre_run_add
                            
                            # Nuovo Dep = Arr + stop_time
                            new_dep = new_arr + stop_time
                            
                            # Imposta i nuovi tempi
                            tpi.SetAttValue("Arr", new_arr)
                            tpi.SetAttValue("Dep", new_dep)
                            print("  OK - Arr=%d, Dep=%d (StopTime=%d, PreRun+%d)" % (new_arr, new_dep, stop_time, pre_run_add))
                            
                            # Aggiorna fermata successiva per il PostRunTime
                            next_dep = next_tpi.AttValue("Dep")
                            original_post_run = next_arr - current_dep
                            new_next_arr = new_dep + original_post_run + post_run_add
                            new_next_dep = new_next_arr + (next_dep - next_arr)  # Mantieni lo stesso StopTime
                            
                            next_tpi.SetAttValue("Arr", new_next_arr)
                            next_tpi.SetAttValue("Dep", new_next_dep)
                            print("  OK - Fermata successiva aggiornata (PostRun+%d)" % post_run_add)
                        else:
                            # Fallback: usa solo lo StopTime
                            new_dep = current_arr + stop_time
                            tpi.SetAttValue("Dep", new_dep)
                            print("  OK - Dep=%d (Arr + StopTime=%d)" % (new_dep, stop_time))
                    
                    except Exception as e:
                        print("  ERRORE configurazione tempi: %s" % str(e))
                        import traceback
                        traceback.print_exc()
                    
                    print("  TimeProfileItem configurato")
                
                print("  Completato!")
            
            print("\n" + "=" * 80)
            print("OPERAZIONI COMPLETATE CON SUCCESSO!")
            print("=" * 80)
            print("\nLe modifiche sono state applicate al database di Visum.")
            print("\nPer vedere le modifiche nell'interfaccia:")
            print("  1. CHIUDI la finestra Time Profile Editor (se aperta)")
            print("  2. RIAPRI: Edit > Time Profiles > Seleziona linea")
            print("  3. Le fermate modificate appariranno nella lista")
            print("\nOppure:")
            print("  - Salva il progetto (Ctrl+S)")
            print("  - Chiudi e riapri Visum")
            print("\nNOTA: Le modifiche sono GIA' nel database, solo l'interfaccia")
            print("      non si aggiorna automaticamente.")
            print("=" * 80)

except Exception as e:
    print("ERRORE GENERALE: %s" % str(e))
    import traceback
    traceback.print_exc()
