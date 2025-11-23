# -*- coding: ascii -*-
"""
Sistema di gestione workflow per abilitazione/disabilitazione fermate
Esegue task sequenziali su un set di linee con parametri configurabili
"""

# ============================================================================
# CONFIGURAZIONE GLOBALE
# ============================================================================

# Parametri di default per abilitazione fermate
DEFAULT_STOP_TIME = 60        # Tempo di sosta in secondi (1 minuto)
DEFAULT_PRE_RUN_ADD = 30      # Offset PreRunTime in secondi
DEFAULT_POST_RUN_ADD = 30     # Offset PostRunTime in secondi

# Set di linee da processare
# Formato: "LineName:LineRouteName" per specificare linea e percorso
# ATTENZIONE: Case-sensitive! Usare esattamente come in Visum
# Nota: Possono esistere LineRoute con stesso nome in linee diverse!
TARGET_LINEROUTES = [
    "R17_2022:R17_2",      # LineRoute R17_2 della linea R17_2022 (ID: 121097.0)
    "R17_2022:R17_3",
    "R17_2022:R17_4",
    "R17_2022:R17_5",
    "RE7_2022:RE_7",
    "RE7_2022:RE_7_1",
    "RE7_2022:RE_7_2",
    "RE7_2022:RE_7_3",

    # Aggiungi altre linee qui
]

# ============================================================================
# DEFINIZIONE TASK
# ============================================================================

# Task da eseguire in sequenza
TASKS = [
    {
        "id": 1,
        "name": "Abilita tutte le fermate disabilitate",
        "action": "enable_all_disabled",
        "lineroutes": TARGET_LINEROUTES,
        "params": {
            "stop_time": DEFAULT_STOP_TIME,
            "pre_run_add": DEFAULT_PRE_RUN_ADD,
            "post_run_add": DEFAULT_POST_RUN_ADD
        }
    },
    # Aggiungi altri task qui
]

# ============================================================================
# FUNZIONI HELPER (da enable-stop-STEP1-WORKING.py)
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
                    'accum_length': item.AttValue("AccumLength")
                })
        except:
            pass
    
    stops.sort(key=lambda x: x['index'])
    return stops


def abilita_fermata(tp, stops, stop_no, stop_time, pre_run_add=0, post_run_add=0):
    """
    Abilita una fermata disabilitata nel TimeProfile con tempi personalizzati.
    Returns: True se successo, False se errore
    """
    print("    Abilitazione fermata %d (StopTime=%d, PreRun+%d, PostRun+%d)..." % 
          (stop_no, stop_time, pre_run_add, post_run_add))
    
    # Trova fermata nella sequenza
    stop_idx = None
    for i, s in enumerate(stops):
        if s['stop'] == stop_no:
            stop_idx = i
            break
    
    if stop_idx is None:
        print("      ERRORE: Fermata non trovata!")
        return False
    
    if stop_idx == 0 or stop_idx == len(stops) - 1:
        print("      SKIP: Prima/ultima fermata")
        return False
    
    current = stops[stop_idx]
    
    # Verifica che NON sia già abilitata controllando IsRoutePoint
    if current['is_route']:
        print("      SKIP - IsRoutePoint gia' True")
        return True  # Non è un errore, semplicemente già abilitata
    
    # Verifica anche che non esista già nel TimeProfile
    for tpi in tp.TimeProfileItems:
        s = tpi.AttValue("StopPointNo")
        if s and int(s) == stop_no:
            print("      SKIP - TimeProfileItem gia' esistente")
            return True
    
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
        print("      ERRORE: Fermate adiacenti non trovate!")
        return False
    
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
        print("      ERRORE: Tempi prev/next non trovati!")
        return False
    
    time_total = next_arr - prev_dep
    
    # Abilita IsRoutePoint
    if current['is_route']:
        current['item'].SetAttValue("IsRoutePoint", False)
    current['item'].SetAttValue("IsRoutePoint", True)
    
    # RILEGGI AccumLength (ora aggiornato!)
    prev_accum = prev_stop['item'].AttValue("AccumLength")
    curr_accum = current['item'].AttValue("AccumLength")
    next_accum = next_stop['item'].AttValue("AccumLength")
    
    # Calcola PreRunTime con interpolazione distanze
    dist_prev_curr = curr_accum - prev_accum
    dist_total = next_accum - prev_accum
    
    if abs(dist_total) < 0.001:
        pre_run_time = time_total / 2.0
    else:
        pre_run_time = (dist_prev_curr / dist_total) * time_total
    
    # Applica offset
    pre_run_time_final = pre_run_time + pre_run_add
    
    # Calcola Arr e Dep
    arr = prev_dep + pre_run_time_final
    dep = arr + stop_time
    
    # Crea TimeProfileItem
    try:
        new_tpi = tp.AddTimeProfileItem(current['item'])
    except Exception as e:
        error_msg = str(e)
        if "already in TimeProfile" in error_msg:
            print("      ERRORE: TimeProfileItem gia' esistente (nonostante i controlli)")
            print("      Tento di recuperare il TimeProfileItem esistente...")
            
            # Cerca il TimeProfileItem esistente
            existing_tpi = None
            for tpi in tp.TimeProfileItems:
                s = tpi.AttValue("StopPointNo")
                if s and int(s) == stop_no:
                    existing_tpi = tpi
                    break
            
            if existing_tpi:
                print("      TimeProfileItem trovato, aggiorno i tempi...")
                new_tpi = existing_tpi
            else:
                print("      ERRORE: Non riesco a trovare il TimeProfileItem!")
                return False
        else:
            print("      ERRORE: %s" % error_msg)
            return False
    
    new_tpi.SetAttValue("Arr", arr)
    new_tpi.SetAttValue("Dep", dep)
    
    # Aggiorna fermata successiva per PostRunTime
    if post_run_add != 0:
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
            
            next_arr_new = next_arr_old + post_run_add
            next_dep_new = next_arr_new + next_stoptime
            
            next_tpi.SetAttValue("Arr", next_arr_new)
            next_tpi.SetAttValue("Dep", next_dep_new)
    
    # Verifica
    stoptime_read = new_tpi.AttValue("StopTime")
    if abs(stoptime_read - stop_time) < 0.1:
        print("      OK - StopTime: %.1f sec" % stoptime_read)
    else:
        print("      ATTENZIONE: StopTime = %.1f (atteso %.1f)" % (stoptime_read, stop_time))
    
    return True


# ============================================================================
# TASK HANDLERS
# ============================================================================

def task_enable_all_disabled(lineroutes, params):
    """
    Task: Abilita tutte le fermate disabilitate su un set di linee
    Processa le fermate in sequenza temporale per aggiornare i tempi in modo congruente
    """
    print("\n" + "=" * 80)
    print("TASK: ABILITA TUTTE LE FERMATE DISABILITATE")
    print("=" * 80)
    
    stop_time = params.get("stop_time", DEFAULT_STOP_TIME)
    pre_run_add = params.get("pre_run_add", DEFAULT_PRE_RUN_ADD)
    post_run_add = params.get("post_run_add", DEFAULT_POST_RUN_ADD)
    
    print("\nParametri:")
    print("  StopTime:     %d sec" % stop_time)
    print("  PreRun add:   +%d sec" % pre_run_add)
    print("  PostRun add:  +%d sec" % post_run_add)
    print("  Linee target: %s" % ", ".join(lineroutes))
    print()
    
    total_enabled = 0
    total_errors = 0
    
    # Processa ogni linea
    for lr_spec in lineroutes:
        # lr_spec puo' essere:
        # - "LineName:LineRouteName" (es. "R17:R17_2")
        # - "LineRouteName" (es. "R17_2") - cerca in tutte le linee
        
        if ":" in lr_spec:
            line_name, lr_name = lr_spec.split(":", 1)
        else:
            line_name = None
            lr_name = lr_spec
        
        print("\n" + "-" * 80)
        if line_name:
            print("Linea: %s, LineRoute: %s" % (line_name, lr_name))
        else:
            print("LineRoute: %s" % lr_name)
        print("-" * 80)
        
        # Trova LineRoute
        target_lr = None
        
        if line_name:
            # Cerca in una linea specifica
            line_found = False
            for line in Visum.Net.Lines:
                current_line_name = line.AttValue("Name")
                if current_line_name == line_name:
                    line_found = True
                    print("  Linea '%s' trovata, cerco LineRoute '%s'..." % (line_name, lr_name))
                    
                    # Debug: mostra tutti i LineRoute disponibili
                    available_lrs = []
                    for lr in line.LineRoutes:
                        lr_name_found = lr.AttValue("Name")
                        available_lrs.append(lr_name_found)
                        if lr_name_found == lr_name:
                            target_lr = lr
                            break
                    
                    if not target_lr:
                        print("  LineRoute disponibili in linea '%s': %s" % (line_name, ", ".join(available_lrs)))
                    break
            
            if not line_found:
                print("  DEBUG: Linea '%s' non trovata. Cerco linee simili..." % line_name)
                similar = []
                for line in Visum.Net.Lines:
                    ln = line.AttValue("Name")
                    if line_name in ln or ln in line_name:
                        similar.append(ln)
                if similar:
                    print("  Linee simili trovate: %s" % ", ".join(similar[:5]))
        else:
            # Cerca in tutte le linee
            for lr in Visum.Net.LineRoutes:
                if lr.AttValue("Name") == lr_name:
                    target_lr = lr
                    break
        
        if target_lr is None:
            if line_name:
                print("  ERRORE: LineRoute '%s' nella linea '%s' non trovato!" % (lr_name, line_name))
            else:
                print("  ERRORE: LineRoute '%s' non trovato!" % lr_name)
            total_errors += 1
            continue
        
        # Ottieni TimeProfile
        # Conta quanti TimeProfiles ci sono
        tp_list = []
        for time_profile in target_lr.TimeProfiles:
            tp_list.append(time_profile)
        
        if not tp_list:
            print("  ERRORE: Nessun TimeProfile trovato!")
            total_errors += 1
            continue
        
        print("  TimeProfiles trovati: %d" % len(tp_list))
        
        # Usa il primo TimeProfile (o modifica qui per scegliere)
        tp = tp_list[0]
        tp_name = tp.AttValue("Name")
        print("  Uso TimeProfile: %s" % tp_name)
        
        if len(tp_list) > 1:
            print("  NOTA: Ci sono %d TimeProfiles, uso solo il primo!" % len(tp_list))
            for i, t in enumerate(tp_list):
                print("    [%d] %s" % (i, t.AttValue("Name")))
        
        # Ottieni sequenza fermate
        stops = get_lr_stop_sequence(target_lr.LineRouteItems)
        
        # Trova fermate disabilitate (escludendo prima e ultima)
        disabled_stops = []
        for i, s in enumerate(stops):
            if i > 0 and i < len(stops) - 1:  # Non prima/ultima
                if not s['is_route']:
                    disabled_stops.append(s)
        
        if not disabled_stops:
            print("  Nessuna fermata disabilitata trovata (escluse prima/ultima)")
            continue
        
        print("\n  Fermate disabilitate da abilitare: %d" % len(disabled_stops))
        for s in disabled_stops:
            print("    - Fermata %d (Index %d)" % (s['stop'], s['index']))
        
        print("\n  Abilitazione in sequenza temporale...")
        
        # Abilita in sequenza (le fermate sono gia' ordinate per index)
        enabled_count = 0
        error_count = 0
        
        for disabled in disabled_stops:
            print("\n  Processando fermata %d..." % disabled['stop'])
            
            # Rileggi sequenza aggiornata dopo ogni abilitazione
            stops = get_lr_stop_sequence(target_lr.LineRouteItems)
            
            # Debug: verifica stato attuale
            current_state = None
            for s in stops:
                if s['stop'] == disabled['stop']:
                    current_state = s['is_route']
                    break
            print("    Stato IsRoutePoint attuale: %s" % current_state)
            
            success = abilita_fermata(tp, stops, disabled['stop'], 
                                     stop_time, pre_run_add, post_run_add)
            
            if success:
                enabled_count += 1
            else:
                error_count += 1
        
        print("\n  Risultato LineRoute %s:" % lr_name)
        print("    Abilitate: %d" % enabled_count)
        print("    Errori:    %d" % error_count)
        
        total_enabled += enabled_count
        total_errors += error_count
    
    # Riepilogo finale
    print("\n" + "=" * 80)
    print("TASK COMPLETATO")
    print("=" * 80)
    print("Totale fermate abilitate: %d" % total_enabled)
    print("Totale errori:            %d" % total_errors)
    print("=" * 80)
    
    return {
        "enabled": total_enabled,
        "errors": total_errors
    }


# ============================================================================
# WORKFLOW EXECUTOR
# ============================================================================

def execute_workflow(tasks):
    """Esegue tutti i task in sequenza"""
    print("\n" + "=" * 80)
    print("INIZIO WORKFLOW - %d TASK" % len(tasks))
    print("=" * 80)
    
    results = []
    
    for task in tasks:
        task_id = task.get("id", "?")
        task_name = task.get("name", "Unnamed")
        task_action = task.get("action")
        
        print("\n\n")
        print("#" * 80)
        print("# TASK %s: %s" % (task_id, task_name))
        print("#" * 80)
        
        # Esegui task appropriato
        if task_action == "enable_all_disabled":
            result = task_enable_all_disabled(
                task.get("lineroutes", []),
                task.get("params", {})
            )
            results.append({
                "task_id": task_id,
                "task_name": task_name,
                "result": result
            })
        else:
            print("\nERRORE: Action '%s' non riconosciuta!" % task_action)
            results.append({
                "task_id": task_id,
                "task_name": task_name,
                "result": {"error": "Unknown action"}
            })
    
    # Riepilogo finale workflow
    print("\n\n")
    print("=" * 80)
    print("WORKFLOW COMPLETATO")
    print("=" * 80)
    for r in results:
        print("\nTask %s: %s" % (r["task_id"], r["task_name"]))
        print("  Risultato: %s" % r["result"])
    print("=" * 80)
    
    return results


# ============================================================================
# MAIN
# ============================================================================

try:
    results = execute_workflow(TASKS)
    
    print("\n\nPer vedere le modifiche nella GUI:")
    print("  - Chiudi e riapri Edit > Time Profiles")
    print("  - Oppure salva e riapri il progetto")

except Exception as e:
    print("\nERRORE WORKFLOW: %s" % str(e))
    import traceback
    traceback.print_exc()
