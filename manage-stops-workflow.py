# -*- coding: utf-8 -*-
"""
Sistema di gestione workflow per abilitazione/disabilitazione fermate
Esegue task sequenziali su un set di linee con parametri configurabili
"""

import sys
import os
from datetime import datetime

# ============================================================================
# CONFIGURAZIONE LOG
# ============================================================================

# Abilita log su file (utile quando eseguito da Procedure Sequence)
ENABLE_FILE_LOG = True
LOG_DIR = r"H:\go\trenord_2025\logs"
LOG_FILE = None

if ENABLE_FILE_LOG:
    # Crea directory log se non esiste
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    
    # Nome file log con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    LOG_FILE = os.path.join(LOG_DIR, "workflow_%s.log" % timestamp)
    
    # Apri file log
    log_file_handle = open(LOG_FILE, "w", encoding="utf-8")
    
    # Classe per scrivere sia su console che su file
    class TeeOutput:
        def __init__(self, *files):
            self.files = files
        def write(self, text):
            for f in self.files:
                f.write(text)
                f.flush()
        def flush(self):
            for f in self.files:
                f.flush()
    
    # Reindirizza stdout
    original_stdout = sys.stdout
    sys.stdout = TeeOutput(original_stdout, log_file_handle)
    
    print("=" * 80)
    print("LOG ABILITATO: %s" % LOG_FILE)
    print("=" * 80)
    print()

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
    {
        "id": 2,
        "name": "Esegui Procedure Sequence di Visum",
        "action": "execute_procedure_sequence",
        "params": {}
    },
    # ESEMPIO Task 3 - Export tabelle da layout
    # {
    #     "id": 3,
    #     "name": "Esporta tabelle da Global Layout",
    #     "action": "export_layout_tables",
    #     "params": {
    #         "layout_file": r"H:\path\to\your\layout.lay",
    #         "output_dir": r"H:\path\to\output\",
    #         "project_name": "exported_tables"
    #     }
    # },
    
    # ESEMPIO Task 4 - Test tutte le configurazioni fermate
    # {
    #     "id": 4,
    #     "name": "Test tutte le configurazioni fermate",
    #     "action": "test_all_configurations",
    #     "params": {
    #         "lineroutes": TARGET_LINEROUTES,
    #         "layout_file": r"H:\go\trenord_2025\skim_layout.lay",
    #         "output_dir": r"H:\go\trenord_2025\config_tests",
    #         "stop_time": 60,
    #         "pre_run_add": 30,
    #         "post_run_add": 30,
    #         "max_configs": 10,      # Limita a 10 per test rapido (None = tutte)
    #         "random_sample": True   # Sample casuale se > max_configs
    #     }
    # },
]



TASKS = [
     {
         "id": 1,
         "name": "Test tutte le configurazioni fermate",
         "action": "test_all_configurations",
         "params": {
             "lineroutes": ["R17_2022:R17_2", "R17_2022:R17_3",
    "R17_2022:R17_4",
    "R17_2022:R17_5",
    "RE7_2022:RE_7",
    "RE7_2022:RE_7_1",
    "RE7_2022:RE_7_2",
    "RE7_2022:RE_7_3"    # LineRoute R17_2 della linea R17_2022 (ID: 121097.0)
                             ],
             "layout_file": r"H:\go\trenord_2025\skim_layout.lay",
             "output_dir": r"H:\go\trenord_2025\config_tests",
             "max_configs": None,#1,      # Limita per test rapido
             "random_sample": False,
             
             # PARALLEL SLICING - Distribuisci configurazioni tra processi paralleli
             # Esempio: 3 processi -> slice_total=3, slice_index=0/1/2 per ogni processo
             "slice_index": 2,#None,   # Indice slice corrente (0-based): 0, 1, 2, ...
             "slice_total": 3,#None,   # Numero totale slice: 2, 3, 4, ...
             
             # CONFIGURAZIONE DI PARTENZA - Stato iniziale prima di testare configurazioni
             # None = tutte abilitate (default), oppure dict con configurazione specifica
            # "initial_config":  {"enabled_stops": [270,419,91,311,301,369,418,46,149,327,371,372,203,204,328]}, # None,  # Esempio: {"enabled_stops": [328, 372, 327]} o "all_disabled"
            # "initial_config":  {"enabled_stops": [329,328,204,203,372,371,327,149,46,418,369,301,270]}, # None,  # Esempio: {"enabled_stops": [328, 372, 327]} o "all_disabled"
             "initial_config": {
                "enabled_stops": [
                    329,   # COMO LAGO (prima - sempre ON)
                    328,   # COMO BORGHI
                    204,   # COMO CAMERLATA
                    372,   # PORTICHETTO-LUISAGO
                    46,    # LOMAZZO
                    301,   # SARONNO
                    173,   # MILANO BOVISA POLITECNICO
                    419,   # MILANO DOMODOSSOLA
                    270    # MILANO CADORNA (ultima - sempre ON)
                ]
            },
             # FERMATE FISSE (LOCKED) - Non partecipano alle permutazioni
             # Formato: dict con StopNo come chiave, valore True=forzata ON, False=forzata OFF
             # Esempio: {328: True, 372: False} = fermata 328 sempre ON, 372 sempre OFF
            # "locked_stops": {
            #        328: False, 204: False, 203: False, 372: False, 371: False,
            #        327: False, 149: False, 46: False, 418: False, 369: False,
            #        301: False, 370: False, 76: False, 18: False, 311: False,
            #        115: False, 122: False, 91: False, 138: False, 118: False,
            #        173: False, 419: False
            #    }
             "locked_stops": {
                203: False,  # GRANDATE-BRECCIA - fissa OFF
                371: False,  # FINO MORNASCO - fissa OFF
                327: False,  # CADORAGO - fissa OFF
                149: False,  # CASLINO AL PIANO - fissa OFF
                418: False,  # ROVELLASCA-MANERA - fissa OFF
                369: False,  # ROVELLO PORRO - fissa OFF
                370: False,  # SARONNO SUD - fissa OFF
                76: False,   # CARONNO PERTUSELLA - fissa OFF
                18: False,   # CESATE - fissa OFF
                311: False,  # GARBAGNATE MILANESE - fissa OFF
                115: False,  # GARBAGNATE PARCO DELLE GROANE - fissa OFF
                122: False,  # BOLLATE NORD - fissa OFF
                91: False,   # BOLLATE CENTRO - fissa OFF
                138: False,  # NOVATE MILANESE - fissa OFF
                118: False   # MILANO QUARTO OGGIARO - fissa OFF
            }
         }
     }
 ]


# ============================================================================
# FUNZIONI HELPER (da enable-stop-STEP1-WORKING.py)
# ============================================================================

def verify_and_get_common_stops(lineroutes):
    """
    Trova la LineRoute con più fermate (MASTER) e verifica che le altre
    siano sottoinsieme del master. Gestisce il caso in cui alcune fermate
    del master non sono presenti in tutte le linee.
    
    Strategia:
    1. Trova LineRoute con maggior numero di fermate → MASTER
    2. Verifica che fermate di altre linee siano sottoinsieme del MASTER
    3. Ritorna lista fermate del MASTER + info su quali linee hanno quali fermate
    
    Parametri:
        lineroutes: Lista di "LineName:LineRouteName" strings
    
    Returns:
        dict con:
            'valid': bool - True se verifica OK
            'stops': list - Lista fermate del MASTER
            'master_lr': str - Nome della LineRoute master
            'stop_coverage': dict - {stop_no: [lista lineroutes che hanno quella fermata]}
            'errors': list - Lista errori (se valid=False)
    """
    print("\n" + "=" * 80)
    print("VERIFICA CONSISTENZA FERMATE - STRATEGIA MASTER")
    print("=" * 80)
    print()
    
    all_stops_data = []
    errors = []
    
    # Raccogli fermate da ogni LineRoute
    for lr_spec in lineroutes:
        if ":" in lr_spec:
            line_name, lr_name = lr_spec.split(":", 1)
        else:
            line_name = None
            lr_name = lr_spec
        
        print("Processando: %s" % lr_spec)
        
        # Trova LineRoute
        target_lr = None
        
        if line_name:
            for line in Visum.Net.Lines:
                if line.AttValue("Name") == line_name:
                    for lr in line.LineRoutes:
                        if lr.AttValue("Name") == lr_name:
                            target_lr = lr
                            break
                    break
        else:
            for lr in Visum.Net.LineRoutes:
                if lr.AttValue("Name") == lr_name:
                    target_lr = lr
                    break
        
        if not target_lr:
            msg = "LineRoute non trovato: %s" % lr_spec
            print("  ERRORE: %s" % msg)
            errors.append(msg)
            continue
        
        # Ottieni sequenza fermate
        stops = get_lr_stop_sequence(target_lr.LineRouteItems)
        
        if not stops:
            msg = "Nessuna fermata trovata in %s" % lr_spec
            print("  ERRORE: %s" % msg)
            errors.append(msg)
            continue
        
        # Estrai info fermate: numero fermata e nome
        stop_info = []
        for s in stops:
            stop_no = s['stop']
            
            # Ottieni nome fermata da StopPoint
            try:
                stop_point = Visum.Net.StopPoints.ItemByKey(stop_no)
                stop_name = stop_point.AttValue("Name")
            except:
                stop_name = "Stop_%d" % stop_no
            
            stop_info.append({
                'no': stop_no,
                'name': stop_name,
                'index': s['index']
            })
        
        print("  Fermate: %d" % len(stop_info))
        for si in stop_info[:3]:
            print("    - %d: %s" % (si['no'], si['name']))
        if len(stop_info) > 3:
            print("    ... (altre %d)" % (len(stop_info) - 3))
        
        all_stops_data.append({
            'lr_spec': lr_spec,
            'stops': stop_info,
            'stop_count': len(stop_info)
        })
    
    if errors:
        print("\n" + "=" * 80)
        print("VERIFICA FALLITA - ERRORI RACCOLTA DATI")
        print("=" * 80)
        for err in errors:
            print("  - %s" % err)
        return {
            'valid': False,
            'stops': [],
            'errors': errors
        }
    
    # STEP 1: Trova LineRoute MASTER (con più fermate)
    print("\n" + "-" * 80)
    print("STEP 1: RICERCA LINEROUTE MASTER (con più fermate)")
    print("-" * 80)
    print()
    
    master_data = max(all_stops_data, key=lambda x: x['stop_count'])
    master_lr_name = master_data['lr_spec']
    master_stops = master_data['stops']
    master_stop_set = set(s['no'] for s in master_stops)
    
    print("✓ MASTER: %s" % master_lr_name)
    print("  Fermate: %d" % len(master_stops))
    print()
    
    # STEP 2: Verifica che altre LineRoutes siano sottoinsieme del master
    print("\n" + "-" * 80)
    print("STEP 2: VERIFICA SOTTOINSIEME")
    print("-" * 80)
    
    all_valid = True
    stop_coverage = {}  # {stop_no: [lista lr_spec che hanno quella fermata]}
    
    # Inizializza coverage con tutte le fermate del master
    for s in master_stops:
        stop_coverage[s['no']] = [master_lr_name]
    
    for data in all_stops_data:
        if data['lr_spec'] == master_lr_name:
            continue  # Skip master
        
        print("\nConfronto %s:" % data['lr_spec'])
        print("  Fermate: %d" % len(data['stops']))
        
        current_stop_set = set(s['no'] for s in data['stops'])
        
        # Verifica che sia sottoinsieme del master
        extra_stops = current_stop_set - master_stop_set
        
        if extra_stops:
            # Ha fermate NON presenti nel master → ERRORE
            msg = "%s: ha fermate NON presenti nel master" % data['lr_spec']
            print("  ERRORE: %s" % msg)
            print("    Fermate extra (non nel master):")
            for stop_no in sorted(extra_stops)[:5]:
                curr_name = next((s['name'] for s in data['stops'] if s['no'] == stop_no), "?")
                print("      - StopNo %d (%s)" % (stop_no, curr_name))
            if len(extra_stops) > 5:
                print("      ... (altre %d)" % (len(extra_stops) - 5))
            errors.append(msg)
            all_valid = False
        else:
            # OK: è sottoinsieme
            missing_from_current = master_stop_set - current_stop_set
            
            if missing_from_current:
                print("  OK: Sottoinsieme del master (%d fermate in meno)" % len(missing_from_current))
                print("    Fermate master NON presenti in questa linea:")
                for stop_no in sorted(missing_from_current)[:3]:
                    master_name = next((s['name'] for s in master_stops if s['no'] == stop_no), "?")
                    print("      - StopNo %d (%s)" % (stop_no, master_name))
                if len(missing_from_current) > 3:
                    print("      ... (altre %d)" % (len(missing_from_current) - 3))
            else:
                print("  OK: Stesse fermate del master")
            
            # Aggiorna coverage
            for s in data['stops']:
                stop_coverage[s['no']].append(data['lr_spec'])
    
    # STEP 3: Riepilogo finale
    print("\n" + "=" * 80)
    if all_valid:
        print("VERIFICA COMPLETATA: STRATEGIA MASTER OK")
        print("=" * 80)
        print()
        print("✓ MASTER: %s" % master_lr_name)
        print("  Fermate master: %d" % len(master_stops))
        print()
        print("Fermate master (sequenza):")
        for i, s in enumerate(master_stops):
            marker = "[FISSA]" if i == 0 or i == len(master_stops) - 1 else "[VAR] "
            
            # Mostra coverage (in quante linee è presente)
            coverage_count = len(stop_coverage[s['no']])
            total_lines = len(all_stops_data)
            
            if coverage_count == total_lines:
                coverage_str = "presente in TUTTE le linee"
            else:
                coverage_str = "presente in %d/%d linee" % (coverage_count, total_lines)
            
            print("  %s %d. %s (StopNo: %d) - %s" % (marker, i + 1, s['name'], s['no'], coverage_str))
        
        print()
        print("NOTA: Le configurazioni useranno la sequenza del MASTER.")
        print("      Fermate non presenti in alcune linee saranno skippate per quelle linee.")
        print()
        
        return {
            'valid': True,
            'stops': master_stops,
            'master_lr': master_lr_name,
            'stop_coverage': stop_coverage,
            'errors': []
        }
    else:
        print("VERIFICA FALLITA: ALCUNE LINEE NON SONO SOTTOINSIEME DEL MASTER")
        print("=" * 80)
        for err in errors:
            print("  - %s" % err)
        return {
            'valid': False,
            'stops': [],
            'stop_coverage': {},
            'errors': errors
        }


def generate_stop_configurations(stops, locked_stops=None):
    """
    Genera tutte le possibili combinazioni di fermate abilitate/disabilitate.
    Prima e ultima fermata sono sempre abilitate.
    
    Parametri:
        stops: Lista di dict con 'no', 'name', 'index'
        locked_stops: Dict {stop_no: bool} - True=forzata ON, False=forzata OFF, None=variabile
    
    Returns:
        list di configurazioni, ogni configurazione e' una lista di stop_no abilitati
    """
    from itertools import product
    
    print("\n" + "=" * 80)
    print("GENERAZIONE CONFIGURAZIONI FERMATE")
    print("=" * 80)
    print()
    
    if len(stops) < 2:
        print("ERRORE: Servono almeno 2 fermate (prima e ultima)")
        return []
    
    # Fermate fisse (prima e ultima + locked)
    first_stop = stops[0]['no']
    last_stop = stops[-1]['no']
    
    locked_stops = locked_stops or {}
    
    # Separa fermate in: fisse ON, fisse OFF, variabili
    locked_on = []   # Fermate forzate ON (oltre prima e ultima)
    locked_off = []  # Fermate forzate OFF
    variable_stops = []  # Fermate che partecipano alle permutazioni
    
    for s in stops[1:-1]:  # Escludi prima e ultima
        stop_no = s['no']
        if stop_no in locked_stops:
            if locked_stops[stop_no]:
                locked_on.append(s)
            else:
                locked_off.append(s)
        else:
            variable_stops.append(s)
    
    print("Fermate fisse SEMPRE ON (prima/ultima + locked ON):")
    print("  - Prima: %d (%s)" % (first_stop, stops[0]['name']))
    for s in locked_on:
        print("  - Locked ON: %d (%s)" % (s['no'], s['name']))
    print("  - Ultima: %d (%s)" % (last_stop, stops[-1]['name']))
    print()
    
    if locked_off:
        print("Fermate fisse SEMPRE OFF (locked OFF):")
        for s in locked_off:
            print("  - Locked OFF: %d (%s)" % (s['no'], s['name']))
        print()
    
    print("Fermate VARIABILI (partecipano alle permutazioni): %d" % len(variable_stops))
    for i, s in enumerate(variable_stops):
        print("  %d. %s (StopNo: %d)" % (i + 1, s['name'], s['no']))
    print()
    
    # Calcola numero totale configurazioni: 2^n dove n = fermate variabili
    num_configs = 2 ** len(variable_stops)
    
    print("Numero totale configurazioni: %d (2^%d)" % (num_configs, len(variable_stops)))
    print()
    
    if num_configs > 10000:
        print("ATTENZIONE: Numero molto elevato di configurazioni!")
        print("Considerare limitare il numero di fermate variabili.")
        print()
    
    # Genera tutte le combinazioni (True/False per ogni fermata variabile)
    configurations = []
    
    print("Generazione in corso...")
    
    for i, combo in enumerate(product([False, True], repeat=len(variable_stops))):
        # combo e' una tupla di bool (False=disabilitata, True=abilitata)
        
        # Costruisci lista fermate abilitate per questa configurazione
        enabled_stops = [first_stop]  # Prima sempre abilitata
        
        # Aggiungi locked ON
        for s in locked_on:
            enabled_stops.append(s['no'])
        
        # Aggiungi variabili in base a combo
        for var_stop, is_enabled in zip(variable_stops, combo):
            if is_enabled:
                enabled_stops.append(var_stop['no'])
        
        enabled_stops.append(last_stop)  # Ultima sempre abilitata
        
        # Ordina per mantenere ordine sequenziale (opzionale ma più pulito)
        enabled_stops.sort()
        
        configurations.append({
            'id': i + 1,
            'enabled_stops': enabled_stops,
            'enabled_count': len(enabled_stops),
            'pattern': combo  # Tupla di bool per debug
        })
    
    print("Generazione completata: %d configurazioni" % len(configurations))
    print()
    
    # Mostra esempi
    print("Esempi configurazioni:")
    print()
    
    # Config 1: Tutte disabilitate (solo prima e ultima)
    config_min = configurations[0]
    print("Config %d (minimo - solo fermate fisse):" % config_min['id'])
    print("  Fermate abilitate: %d" % config_min['enabled_count'])
    print("  StopNos: %s" % config_min['enabled_stops'])
    print()
    
    # Config ultima: Tutte abilitate
    config_max = configurations[-1]
    print("Config %d (massimo - tutte abilitate):" % config_max['id'])
    print("  Fermate abilitate: %d" % config_max['enabled_count'])
    print("  StopNos: %s" % config_max['enabled_stops'])
    print()
    
    # Config intermedia
    if len(configurations) > 2:
        config_mid = configurations[len(configurations) // 2]
        print("Config %d (intermedia):" % config_mid['id'])
        print("  Fermate abilitate: %d" % config_mid['enabled_count'])
        print("  StopNos: %s" % config_mid['enabled_stops'])
        print()
    
    # Statistiche
    print("Statistiche:")
    enabled_counts = [c['enabled_count'] for c in configurations]
    print("  Min fermate abilitate: %d" % min(enabled_counts))
    print("  Max fermate abilitate: %d" % max(enabled_counts))
    print("  Media: %.1f" % (sum(enabled_counts) / len(enabled_counts)))
    print()
    
    return configurations


def apply_stop_configuration(lineroutes, enabled_stops, all_stops, stop_time=60, pre_run_add=30, post_run_add=30, stop_coverage=None):
    """
    Applica una configurazione specifica di fermate abilitate/disabilitate.
    Processa fermate una per volta per garantire corretto aggiornamento tempi.
    GESTISCE ECCEZIONE: Se una fermata non è presente in una LineRoute, viene skippata.
    
    Parametri:
        lineroutes: Lista "LineName:LineRouteName" 
        enabled_stops: Lista di StopNo che devono essere abilitati
        all_stops: Lista completa di tutti gli stop (da verify_and_get_common_stops - master)
        stop_time: Tempo sosta in secondi
        pre_run_add: Offset PreRunTime
        post_run_add: Offset PostRunTime
        stop_coverage: Dict {stop_no: [lista lr_spec]} - quali linee hanno quali fermate (opzionale)
    
    Returns:
        dict con risultato applicazione
    """
    print("\n" + "=" * 80)
    print("APPLICAZIONE CONFIGURAZIONE FERMATE")
    print("=" * 80)
    
    enabled_set = set(enabled_stops)
    total_enabled = 0
    total_disabled = 0
    total_skipped = 0  # Fermate non presenti in questa linea
    
    # Per ogni LineRoute
    for lr_spec in lineroutes:
        if ":" in lr_spec:
            line_name, lr_name = lr_spec.split(":", 1)
        else:
            line_name = None
            lr_name = lr_spec
        
        print("\nProcessando LineRoute: %s" % lr_spec)
        
        # Trova LineRoute
        target_lr = None
        if line_name:
            for line in Visum.Net.Lines:
                if line.AttValue("Name") == line_name:
                    for lr in line.LineRoutes:
                        if lr.AttValue("Name") == lr_name:
                            target_lr = lr
                            break
                    break
        else:
            for lr in Visum.Net.LineRoutes:
                if lr.AttValue("Name") == lr_name:
                    target_lr = lr
                    break
        
        if not target_lr:
            print("  ERRORE: LineRoute non trovato!")
            continue
        
        # Ottieni tutti i TimeProfiles
        tp_list = [tp for tp in target_lr.TimeProfiles]
        print("  TimeProfiles: %d" % len(tp_list))
        
        # Per ogni TimeProfile
        for tp in tp_list:
            tp_name = tp.AttValue("Name")
            print("\n  TimeProfile: %s" % tp_name)
            
            # Ottieni sequenza fermate
            stops = get_lr_stop_sequence(target_lr.LineRouteItems)
            
            # Processa ogni fermata (escluse prima e ultima)
            for i, stop_info in enumerate(all_stops):
                if i == 0 or i == len(all_stops) - 1:
                    continue  # Skip prima e ultima (sempre abilitate)
                
                stop_no = stop_info['no']
                
                # ECCEZIONE: Verifica se questa fermata è presente in questa LineRoute
                if stop_coverage and stop_no in stop_coverage:
                    if lr_spec not in stop_coverage[stop_no]:
                        # Fermata NON presente in questa LineRoute → SKIP
                        print("    ⊘ Fermata %d: non presente in questa linea (SKIP)" % stop_no)
                        total_skipped += 1
                        continue
                
                should_be_enabled = stop_no in enabled_set
                
                # Rileggi stato corrente
                stops = get_lr_stop_sequence(target_lr.LineRouteItems)
                current_state = None
                for s in stops:
                    if s['stop'] == stop_no:
                        current_state = s['is_route']
                        break
                
                # Se current_state è None, la fermata non esiste in questa linea
                if current_state is None:
                    print("    ⊘ Fermata %d: non trovata in questa linea (SKIP)" % stop_no)
                    total_skipped += 1
                    continue
                
                if should_be_enabled and not current_state:
                    # Deve essere abilitata ma non lo è
                    success = abilita_fermata(tp, stops, stop_no, stop_time, pre_run_add, post_run_add)
                    if success:
                        total_enabled += 1
                        print("    ✓ Fermata %d abilitata" % stop_no)
                
                elif not should_be_enabled and current_state:
                    # Deve essere disabilitata ma è abilitata
                    success = disabilita_fermata(tp, stops, stop_no, pre_run_add, post_run_add)
                    if success:
                        total_disabled += 1
                        print("    ✓ Fermata %d disabilitata" % stop_no)
    
    print("\n" + "=" * 80)
    print("Configurazione applicata:")
    print("  Fermate abilitate:   %d" % total_enabled)
    print("  Fermate disabilitate: %d" % total_disabled)
    print("  Fermate skippate:    %d" % total_skipped)
    print("=" * 80)
    
    return {
        'enabled': total_enabled,
        'disabled': total_disabled,
        'skipped': total_skipped
    }


def disabilita_fermata(tp, stops, stop_no, pre_run_remove=30, post_run_remove=30):
    """
    Disabilita una fermata rimuovendo il TimeProfileItem.
    Prima rimuove gli offset temporali dalle fermate adiacenti, poi elimina la fermata.
    
    Parametri:
        tp: TimeProfile object
        stops: Lista fermate da get_lr_stop_sequence()
        stop_no: Numero fermata da disabilitare
        pre_run_remove: Offset da rimuovere dal PreRunTime della fermata (default 30)
        post_run_remove: Offset da rimuovere dal PostRunTime della fermata successiva (default 30)
    
    Returns:
        True se successo, False se errore
    """
    print("    Disabilitazione fermata %d (PreRun-%d, PostRun-%d)..." % 
          (stop_no, pre_run_remove, post_run_remove))
    
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
        print("      SKIP: Prima/ultima fermata non può essere disabilitata")
        return False
    
    current = stops[stop_idx]
    
    # Verifica che sia abilitata
    if not current['is_route']:
        print("      SKIP: Già disabilitata")
        return True
    
    # STEP 1: Trova fermata precedente e successiva ABILITATE
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
    
    # STEP 2: Trova TimeProfileItem della fermata corrente
    current_tpi = None
    for tpi in tp.TimeProfileItems:
        s = tpi.AttValue("StopPointNo")
        if s and int(s) == stop_no:
            current_tpi = tpi
            break
    
    if not current_tpi:
        print("      ERRORE: TimeProfileItem non trovato!")
        return False
    
    # STEP 3: Disabilita IsRoutePoint di B
    # Visum eliminerà automaticamente il TimeProfileItem e ricalcolerà i tempi
    try:
        current['item'].SetAttValue("IsRoutePoint", False)
        print("      IsRoutePoint disabilitato")
    except Exception as e:
        print("      ERRORE disabilitazione IsRoutePoint: %s" % str(e))
        return False
    
    # STEP 4: Sottrai 60 sec dal nuovo PostRunTime di A (che ora va direttamente a C)
    # Dopo che Visum ha ricalcolato, sottraiamo i 60 sec di offset
    total_remove = pre_run_remove + post_run_remove
    
    if total_remove != 0:
        # Trova la fermata successiva (C)
        next_tpi = None
        for tpi in tp.TimeProfileItems:
            s = tpi.AttValue("StopPointNo")
            if s and int(s) == next_stop['stop']:
                next_tpi = tpi
                break
        
        if next_tpi:
            try:
                # Leggi il tempo attuale (dopo che Visum ha ricalcolato)
                arr_old = next_tpi.AttValue("Arr")
                dep_next_old = next_tpi.AttValue("Dep")
                stoptime_next = dep_next_old - arr_old
                
                # Sottrai 60 sec dal PostRunTime di A
                arr_new = arr_old - total_remove
                dep_new = arr_new + stoptime_next  # Mantiene stesso StopTime
                
                next_tpi.SetAttValue("Arr", arr_new)
                next_tpi.SetAttValue("Dep", dep_new)
                
                print("      Offset rimosso dal PostRunTime di A: Arr(C=%d) %.1f -> %.1f (-%d sec)" % 
                      (next_stop['stop'], arr_old, arr_new, total_remove))
            except Exception as e:
                print("      WARNING: Impossibile rimuovere offset: %s" % str(e))
        else:
            print("      WARNING: Fermata successiva non trovata")
    
    print("      OK - Fermata disabilitata")
    return True


def export_layout_tables(layout_file, output_dir, project_name="export"):
    """
    Esporta tutte le tabelle visibili da un Global Layout (.lay) in file CSV
    
    Parametri:
        layout_file: Path al file .lay
        output_dir: Directory output per i CSV
        project_name: Prefisso per i nomi file
    
    Returns: dict con risultato export
    """
    import xml.etree.ElementTree as ET
    
    print("\n" + "=" * 80)
    print("EXPORT TABELLE DA GLOBAL LAYOUT")
    print("=" * 80)
    print("\nLayout file: %s" % layout_file)
    print("Output dir:  %s" % output_dir)
    print("Project:     %s" % project_name)
    print()
    
    try:
        # Parse layout XML
        print("Parsing layout XML...")
        tree = ET.parse(layout_file)
        root = tree.getroot()
        
        # Find all visible tables
        tables_info = []
        for list_item in root.iter('listLayoutItem'):
            graphic = list_item.find('.//listGraphicParameterLayoutItems')
            if graphic is not None:
                net_obj_type = graphic.get('netObjectType')
                if net_obj_type:
                    table_name_elem = list_item.find('.//caption')
                    table_name = table_name_elem.get('text', net_obj_type) if table_name_elem is not None else net_obj_type
                    
                    col_defs = []
                    for attr_def in list_item.iter('attributeDefinition'):
                        col_defs.append(attr_def.attrib)
                    
                    tables_info.append({
                        'name': table_name,
                        'type': net_obj_type,
                        'columns': col_defs
                    })
        
        print("Tabelle trovate: %d" % len(tables_info))
        for t in tables_info:
            print("  - %s (%s): %d colonne" % (t['name'], t['type'], len(t['columns'])))
        print()
        
        # Map net object types to Visum collections
        type_to_collection = {
            'LINK': 'Visum.Net.Links',
            'NODE': 'Visum.Net.Nodes',
            'ZONE': 'Visum.Net.Zones',
            'ODPAIR': 'Visum.Net.ODPairs',
            'LINE': 'Visum.Net.Lines',
            'LINEROUTE': 'Visum.Net.LineRoutes',
            'TIMEPROFILE': 'Visum.Net.TimeProfiles',
            'TIMEPROFILEITEM': 'Visum.Net.TimeProfileItems',
            'VEHJOURNEYSECTION': 'Visum.Net.VehicleJourneySections',
            'STOP': 'Visum.Net.Stops',
            'STOPPOINTAREA': 'Visum.Net.StopPointAreas',
            'CONNECTOR': 'Visum.Net.Connectors'
        }
        
        # Export each table
        results = []
        for table in tables_info:
            table_type = table['type']
            table_name = table['name']
            
            print("\nProcessando: %s (%s)" % (table_name, table_type))
            
            collection_path = type_to_collection.get(table_type)
            if not collection_path:
                print("  SKIP: Tipo sconosciuto")
                results.append({'table': table_name, 'status': 'SKIPPED', 'reason': 'Unknown type'})
                continue
            
            try:
                collection = eval(collection_path)
                count = collection.Count
                print("  Oggetti: %d" % count)
            except Exception as e:
                print("  ERRORE: %s" % str(e))
                results.append({'table': table_name, 'status': 'ERROR', 'reason': str(e)})
                continue
            
            # Build attribute list
            full_attrs = []
            headers = []
            
            for col in table['columns']:
                attr_id = col['attributeID']
                sub1 = col.get('subAttributeID1', '')
                sub2 = col.get('subAttributeID2', '')
                sub3 = col.get('subAttributeID3', '')
                
                if sub1 or sub2 or sub3:
                    subs = [s for s in [sub1, sub2, sub3] if s]
                    full_attr = attr_id + '(' + ','.join(subs) + ')'
                    header = attr_id + '_' + '_'.join(subs)
                else:
                    full_attr = attr_id
                    header = attr_id
                
                full_attrs.append(full_attr)
                headers.append(header)
            
            print("  Colonne: %d" % len(full_attrs))
            
            # Get data
            try:
                print("  Recupero dati...")
                data = collection.GetMultipleAttributes(full_attrs)
                
                # Build CSV
                print("  Generazione CSV...")
                lines = [';'.join(headers)]
                
                # FILTRO SPECIALE per ODPAIR: usa odpair_list__r7.csv
                if table_type == 'ODPAIR':
                    print("  Applicando filtro ODPAIR da odpair_list__r7.csv...")
                    
                    # Carica coppie OD valide
                    odpair_filter_file = r"h:\go\trenord_2025\odpair_list__r7.csv"
                    valid_pairs = set()
                    
                    try:
                        import csv
                        with open(odpair_filter_file, 'r', encoding='utf-8') as f:
                            reader = csv.DictReader(f)
                            for row in reader:
                                zona_o = int(row['Zona_o'])
                                zona_d = int(row['Zona_d'])
                                valid_pairs.add((zona_o, zona_d))
                        
                        print("  Coppie OD valide caricate: %d" % len(valid_pairs))
                    except Exception as e:
                        print("  WARNING: Impossibile caricare filtro ODPAIR: %s" % str(e))
                        print("  Procedo SENZA filtro")
                        valid_pairs = None
                    
                    # Trova indici colonne FROMZONENO e TOZONENO
                    from_idx = None
                    to_idx = None
                    for i, h in enumerate(headers):
                        if h.upper() == 'FROMZONENO':
                            from_idx = i
                        elif h.upper() == 'TOZONENO':
                            to_idx = i
                    
                    if valid_pairs and from_idx is not None and to_idx is not None:
                        # Applica filtro
                        filtered_count = 0
                        for row_tuple in data:
                            # FROMZONENO e TOZONENO sono float, convertiamo in int
                            from_zone = int(float(row_tuple[from_idx]))
                            to_zone = int(float(row_tuple[to_idx]))
                            
                            if (from_zone, to_zone) in valid_pairs:
                                lines.append(';'.join(str(v) for v in row_tuple))
                                filtered_count += 1
                        
                        print("  Righe filtrate: %d/%d (%.1f%%)" % (filtered_count, len(data), 100.0 * filtered_count / len(data) if len(data) > 0 else 0))
                    else:
                        # Filtro non applicabile, scrivi tutto
                        print("  WARNING: Colonne FROMZONENO/TOZONENO non trovate, scrivo tutti i dati")
                        for row_tuple in data:
                            lines.append(';'.join(str(v) for v in row_tuple))
                else:
                    # Altre tabelle: nessun filtro
                    for row_tuple in data:
                        lines.append(';'.join(str(v) for v in row_tuple))
                
                # Write file
                safe_name = table_name.replace('/', '_').replace('\\', '_').replace(' ', '_')
                output_file = os.path.join(output_dir, '%s_%s.csv' % (project_name, safe_name))
                
                text = '\n'.join(lines)
                with open(output_file, 'w', encoding='utf-8', newline='') as f:
                    f.write(text)
                
                size_mb = os.path.getsize(output_file) / (1024 * 1024)
                
                # Calcola righe effettive (esclude header)
                actual_rows = len(lines) - 1
                
                print("  OK: %s (%.2f MB, %d righe)" % (output_file, size_mb, actual_rows))
                
                results.append({
                    'table': table_name,
                    'type': table_type,
                    'status': 'SUCCESS',
                    'file': output_file,
                    'rows': actual_rows,
                    'cols': len(full_attrs),
                    'size_mb': round(size_mb, 2)
                })
                
            except Exception as e:
                print("  ERRORE export: %s" % str(e))
                results.append({
                    'table': table_name,
                    'status': 'ERROR',
                    'reason': str(e)[:100]
                })
        
        # Summary
        print("\n" + "=" * 80)
        print("RIEPILOGO EXPORT")
        print("=" * 80)
        
        success = [r for r in results if r['status'] == 'SUCCESS']
        errors = [r for r in results if r['status'] == 'ERROR']
        skipped = [r for r in results if r['status'] == 'SKIPPED']
        
        print("\nSuccesso: %d" % len(success))
        for r in success:
            print("  - %s: %d righe x %d col = %.2f MB" % (r['table'], r['rows'], r['cols'], r['size_mb']))
        
        if errors:
            print("\nErrori: %d" % len(errors))
            for r in errors:
                print("  - %s: %s" % (r['table'], r['reason']))
        
        if skipped:
            print("\nSaltati: %d" % len(skipped))
            for r in skipped:
                print("  - %s: %s" % (r['table'], r['reason']))
        
        print("\nDirectory output: %s" % output_dir)
        print()
        
        return {
            'success': True,
            'total_tables': len(tables_info),
            'successful': len(success),
            'errors': len(errors),
            'skipped': len(skipped),
            'details': results
        }
        
    except Exception as e:
        print("\nERRORE: %s" % str(e))
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e)
        }


def execute_procedure_sequence():
    """
    Esegue la Procedure Sequence corrente di Visum
    Returns: dict con risultato esecuzione
    """
    print("\n" + "=" * 80)
    print("ESECUZIONE PROCEDURE SEQUENCE")
    print("=" * 80)
    print("\nData/Ora inizio: %s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print()
    
    try:
        # Recupero informazioni sulla Procedure Sequence corrente
        print("Recupero informazioni Procedure Sequence...")
        
        # Conta operazioni nella sequenza corrente
        try:
            operations = Visum.Procedures.Operations
            op_count = operations.Count
            
            print("Procedure Sequence corrente")
            print("Operazioni totali: %d" % op_count)
            print()
            
            # Mostra operazioni
            if op_count > 0:
                print("Operazioni da eseguire:")
                for i in range(1, op_count + 1):
                    try:
                        op = operations.ItemByKey(i)
                        op_name = op.AttValue("Name")
                        try:
                            op_type = op.AttValue("OperationType")
                            print("  [%d] %s (Type: %s)" % (i, op_name, op_type))
                        except:
                            print("  [%d] %s" % (i, op_name))
                    except:
                        print("  [%d] (impossibile leggere operazione)" % i)
                print()
            else:
                print("ATTENZIONE: Nessuna operazione nella Procedure Sequence!")
                print()
        except Exception as e:
            print("ATTENZIONE: Impossibile leggere dettagli operazioni: %s" % str(e))
            print("Procedo comunque con l'esecuzione...")
            print()
        
        # Esegui la Procedure Sequence
        print("=" * 80)
        print("INIZIO ESECUZIONE")
        print("=" * 80)
        print()
        
        start_time = datetime.now()
        
        # Esegui tutta la sequenza
        Visum.Procedures.Execute()
        
        print("\n" + "=" * 80)
        print("ESECUZIONE COMPLETATA CON SUCCESSO")
        print("=" * 80)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("\nData/Ora fine: %s" % end_time.strftime("%Y-%m-%d %H:%M:%S"))
        print("Durata totale: %.2f secondi (%.2f minuti)" % (duration, duration / 60.0))
        print()
        
        return {
            "success": True,
            "duration_seconds": duration,
            "operations_count": op_count if 'op_count' in locals() else 0
        }
        
    except Exception as e:
        print("\n" + "=" * 80)
        print("ERRORE DURANTE ESECUZIONE PROCEDURE SEQUENCE")
        print("=" * 80)
        print("Errore: %s" % str(e))
        import traceback
        traceback.print_exc()
        
        return {
            "success": False,
            "error": str(e)
        }


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
                print("      ERRORE: Non trovo il TimeProfileItem!")
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

def task_test_all_configurations(params):
    """
    Task: Testa tutte le configurazioni possibili di fermate abilitate/disabilitate.
    
    Workflow:
    1. Verifica consistenza fermate tra tutte le linee
    2. Genera tutte le configurazioni possibili
    3. Per ogni configurazione:
       - Applica configurazione (abilita/disabilita fermate)
       - Esegui Procedure Sequence
       - Esporta risultati con nome che identifica configurazione
    
    Parametri:
        lineroutes: Lista "LineName:LineRouteName"
        layout_file: Path al file .lay da esportare
        output_dir: Directory dove salvare export
        stop_time: Tempo sosta (default 60)
        pre_run_add: Offset PreRunTime (default 30)
        post_run_add: Offset PostRunTime (default 30)
        max_configs: Limite massimo configurazioni da testare (default: tutte)
        random_sample: Se True, sample casuale se > max_configs
        slice_index: Indice slice corrente per esecuzione parallela (0-based, default: None)
        slice_total: Numero totale slice per esecuzione parallela (default: None)
        initial_config: Configurazione di partenza (default: None = tutte abilitate)
                       - None: tutte fermate abilitate
                       - "all_disabled": solo prima e ultima
                       - {"enabled_stops": [328, 372, ...]}: lista custom
        locked_stops: Fermate fisse che NON partecipano alle permutazioni (default: None)
                     - None: tutte fermate intermedie sono variabili
                     - {stop_no: True/False}: True=sempre ON, False=sempre OFF
                     - Esempio: {328: True, 372: False} = 328 sempre ON, 372 sempre OFF
        
    Configurazione Iniziale:
        Lo stato di partenza PRIMA di testare le configurazioni:
        - None (default): Tutte fermate abilitate
        - "all_disabled": Solo prima e ultima abilitate
        - {"enabled_stops": [stop_no1, stop_no2, ...]}: Lista custom di fermate ON
        
    Fermate Locked (Fisse):
        Fermate che mantengono sempre lo stesso stato durante TUTTE le configurazioni:
        - {328: True}: Fermata 328 sempre ON in tutte le config
        - {372: False}: Fermata 372 sempre OFF in tutte le config
        - {328: True, 372: False, 327: True}: Multiple locks
        - Fermate locked NON partecipano alle permutazioni (2^n ridotto)
        
    Esecuzione Parallela:
        Per distribuire il lavoro tra N processi paralleli:
        - Processo 1: slice_index=0, slice_total=N
        - Processo 2: slice_index=1, slice_total=N
        - ...
        - Processo N: slice_index=N-1, slice_total=N
        
        Esempio con 1024 config e 4 processi:
        - Processo 0: configs 0-255   (256 configs)
        - Processo 1: configs 256-511 (256 configs)
        - Processo 2: configs 512-767 (256 configs)
        - Processo 3: configs 768-1023 (256 configs)
    """
    print("\n" + "=" * 80)
    print("TASK: TEST TUTTE LE CONFIGURAZIONI FERMATE")
    print("=" * 80)
    
    lineroutes = params.get('lineroutes', TARGET_LINEROUTES)
    layout_file = params.get('layout_file')
    output_dir = params.get('output_dir', './')
    stop_time = params.get('stop_time', 60)
    pre_run_add = params.get('pre_run_add', 30)
    post_run_add = params.get('post_run_add', 30)
    max_configs = params.get('max_configs', None)
    random_sample = params.get('random_sample', True)
    slice_index = params.get('slice_index', None)
    slice_total = params.get('slice_total', None)
    initial_config = params.get('initial_config', None)
    locked_stops = params.get('locked_stops', None)
    
    if not layout_file:
        print("\nERRORE: Parametro 'layout_file' mancante!")
        return {'success': False, 'error': 'Missing layout_file'}
    
    print("\nParametri:")
    print("  Linee:       %s" % ", ".join(lineroutes))
    print("  Layout file: %s" % layout_file)
    print("  Output dir:  %s" % output_dir)
    print("  Stop time:   %d sec" % stop_time)
    print("  Max configs: %s" % (max_configs if max_configs else "tutte"))
    
    if initial_config:
        print("  INITIAL CONFIG:")
        if isinstance(initial_config, dict) and 'enabled_stops' in initial_config:
            print("    Custom: %s" % initial_config['enabled_stops'])
        elif initial_config == "all_disabled":
            print("    All disabled (solo prima e ultima)")
        else:
            print("    %s" % initial_config)
    
    if locked_stops:
        print("  LOCKED STOPS:")
        for stop_no, state in locked_stops.items():
            print("    Stop %d: %s" % (stop_no, "ALWAYS ON" if state else "ALWAYS OFF"))
    
    if slice_index is not None and slice_total is not None:
        print("  PARALLEL SLICING:")
        print("    Slice index: %d" % slice_index)
        print("    Slice total: %d" % slice_total)
        print("    (Questo processo gestirà slice %d di %d)" % (slice_index + 1, slice_total))
    
    print()
    
    # STEP 1: Verifica consistenza fermate
    print("\n" + "-" * 80)
    print("STEP 1: VERIFICA CONSISTENZA FERMATE")
    print("-" * 80)
    
    result = verify_and_get_common_stops(lineroutes)
    
    if not result['valid']:
        print("\nERRORE: Fermate non consistenti tra le linee!")
        for err in result['errors']:
            print("  - %s" % err)
        return {'success': False, 'error': 'Inconsistent stops', 'details': result['errors']}
    
    print("\n✓ OK: Tutte le linee hanno %d fermate comuni" % len(result['stops']))
    
    # Estrai stop_coverage per gestire fermate non presenti in tutte le linee
    stop_coverage = result.get('stop_coverage', {})
    
    # STEP 2: Genera configurazioni
    print("\n" + "-" * 80)
    print("STEP 2: GENERAZIONE CONFIGURAZIONI")
    print("-" * 80)
    
    all_configs = generate_stop_configurations(result['stops'], locked_stops=locked_stops)
    
    # SLICING per esecuzione parallela
    if slice_index is not None and slice_total is not None:
        print("\n" + "=" * 80)
        print("APPLICAZIONE PARALLEL SLICING")
        print("=" * 80)
        
        if slice_index < 0 or slice_index >= slice_total:
            print("\nERRORE: slice_index=%d fuori range (0-%d)" % (slice_index, slice_total - 1))
            return {'success': False, 'error': 'Invalid slice_index'}
        
        total_configs = len(all_configs)
        slice_size = total_configs // slice_total
        remainder = total_configs % slice_total
        
        # Calcola start/end per questo slice
        # Distribuisci il remainder tra i primi slice
        if slice_index < remainder:
            start = slice_index * (slice_size + 1)
            end = start + slice_size + 1
        else:
            start = slice_index * slice_size + remainder
            end = start + slice_size
        
        print("\nConfigurazione totali: %d" % total_configs)
        print("Slice size base:       %d" % slice_size)
        print("Remainder:             %d (distribuito nei primi %d slice)" % (remainder, remainder))
        print()
        print("Slice %d/%d:" % (slice_index + 1, slice_total))
        print("  Start index: %d" % start)
        print("  End index:   %d (escluso)" % end)
        print("  Configs:     %d" % (end - start))
        
        # Applica slicing
        all_configs_sliced = all_configs[start:end]
        
        print("\n✓ Slice selezionato: %d configurazioni (da %d a %d)" % (len(all_configs_sliced), start, end - 1))
        
        # Usa le configs sliced come base
        configs_to_process = all_configs_sliced
        
    else:
        # Nessuno slicing
        configs_to_process = all_configs
    
    # Applica max_configs se specificato
    if max_configs and len(configs_to_process) > max_configs:
        print("\nConfigurazioni dopo slicing: %d" % len(configs_to_process))
        print("Limite richiesto: %d" % max_configs)
        
        if random_sample:
            import random
            configs = random.sample(configs_to_process, max_configs)
            print("✓ Sample casuale di %d configurazioni selezionato" % max_configs)
        else:
            configs = configs_to_process[:max_configs]
            print("✓ Prime %d configurazioni selezionate" % max_configs)
    else:
        configs = configs_to_process
        print("\n✓ Configurazioni da testare: %d" % len(configs))
    
    # Nome base per export (prima linea)
    base_name = lineroutes[0].replace(":", "_").replace(" ", "_")
    
    # STEP 3: Imposta configurazione iniziale
    print("\n" + "-" * 80)
    print("STEP 3: CONFIGURAZIONE INIZIALE")
    print("-" * 80)
    
    # Determina configurazione iniziale
    if initial_config == "all_disabled":
        # Solo prima e ultima abilitate
        print("Config iniziale: TUTTE DISABILITATE (solo prima e ultima)")
        init_enabled = [result['stops'][0]['no'], result['stops'][-1]['no']]
    elif isinstance(initial_config, dict) and 'enabled_stops' in initial_config:
        # Custom lista fermate
        print("Config iniziale: CUSTOM")
        init_enabled = initial_config['enabled_stops']
    else:
        # Default: tutte abilitate
        print("Config iniziale: TUTTE ABILITATE (default)")
        init_enabled = [s['no'] for s in result['stops']]
    
    print("\nFermate abilitate inizialmente: %d" % len(init_enabled))
    print("StopNos: %s" % init_enabled)
    print()
    
    print("Applicando configurazione iniziale...")
    apply_stop_configuration(
        lineroutes, 
        init_enabled,
        result['stops'],
        stop_time, pre_run_add, post_run_add,
        stop_coverage=stop_coverage
    )
    
    # STEP 4 e 5: Esecuzione e export configurazione iniziale
    # SOLO per slice 0 (o se non c'è slicing)
    if slice_index is None or slice_index == 0:
        # Esegui Procedure Sequence per configurazione iniziale
        print("\n" + "-" * 80)
        print("STEP 4: ESECUZIONE PROCEDURE SEQUENCE (CONFIG INIZIALE)")
        print("-" * 80)
        
        init_result = execute_procedure_sequence()
        
        if not init_result.get('success'):
            print("\nERRORE: Procedure Sequence iniziale fallita!")
            return {'success': False, 'error': 'Initial config procedure failed'}
        
        # Export configurazione iniziale
        print("\n" + "-" * 80)
        print("STEP 5: EXPORT CONFIGURAZIONE INIZIALE")
        print("-" * 80)
        
        # Costruisci pattern string per config iniziale
        init_enabled_set = set(init_enabled)
        pattern_bits = []
        for s in result['stops']:
            pattern_bits.append('1' if s['no'] in init_enabled_set else '0')
        pattern_str = ''.join(pattern_bits)
        
        init_name = "%s_INIT_%s" % (base_name, pattern_str)
        
        init_export = export_layout_tables(
            layout_file,
            output_dir,
            init_name
        )
        
        print("\n✓ Configurazione iniziale completata: %s" % init_name)
    else:
        # Slice > 0: salta esecuzione e export iniziale
        print("\n" + "-" * 80)
        print("STEP 4-5: SKIP (Slice %d > 0)" % slice_index)
        print("-" * 80)
        print("\n⊘ Configurazione iniziale applicata ma NON eseguita/esportata")
        print("  (Solo slice 0 esegue ed esporta la config iniziale)")
        print("\n✓ Pronto per testare configurazioni assegnate a questo slice")
    
    # STEP 6: Loop configurazioni
    print("\n\n" + "=" * 80)
    print("STEP 6: TEST CONFIGURAZIONI (%d totali)" % len(configs))
    print("=" * 80)
    
    results = []
    
    for idx, config in enumerate(configs):
        print("\n\n" + "#" * 80)
        print("# CONFIGURAZIONE %d/%d (ID=%d)" % (idx + 1, len(configs), config['id']))
        print("#" * 80)
        
        # Costruisci pattern string (1=abilitata, 0=disabilitata)
        enabled_set = set(config['enabled_stops'])
        pattern_bits = []
        for stop_info in result['stops']:
            pattern_bits.append('1' if stop_info['no'] in enabled_set else '0')
        pattern_str = ''.join(pattern_bits)
        
        print("\nPattern: %s (%d fermate abilitate)" % (pattern_str, config['enabled_count']))
        
        # A) Applica configurazione
        print("\n" + "-" * 80)
        print("A) APPLICAZIONE CONFIGURAZIONE")
        print("-" * 80)
        
        apply_result = apply_stop_configuration(
            lineroutes,
            config['enabled_stops'],
            result['stops'],
            stop_time, pre_run_add, post_run_add,
            stop_coverage=stop_coverage
        )
        
        # B) Esegui Procedure Sequence
        print("\n" + "-" * 80)
        print("B) ESECUZIONE PROCEDURE SEQUENCE")
        print("-" * 80)
        
        proc_result = execute_procedure_sequence()
        
        if not proc_result.get('success'):
            print("\nWARNING: Procedure Sequence fallita per config %d" % config['id'])
            results.append({
                'config_id': config['id'],
                'pattern': pattern_str,
                'success': False,
                'error': proc_result.get('error')
            })
            continue
        
        # C) Export risultati
        print("\n" + "-" * 80)
        print("C) EXPORT RISULTATI")
        print("-" * 80)
        
        config_name = "%s_%s" % (base_name, pattern_str)
        
        export_result = export_layout_tables(
            layout_file,
            output_dir,
            config_name
        )
        
        results.append({
            'config_id': config['id'],
            'pattern': pattern_str,
            'enabled_count': config['enabled_count'],
            'apply_result': apply_result,
            'proc_result': proc_result,
            'export_result': export_result,
            'success': True
        })
        
        print("\n✓ Config %d completata: %s" % (config['id'], config_name))
    
    # RIEPILOGO FINALE
    print("\n\n" + "=" * 80)
    print("TASK COMPLETATO - RIEPILOGO")
    print("=" * 80)
    
    success_count = sum(1 for r in results if r['success'])
    fail_count = len(results) - success_count
    
    print("\nConfigurazioni testate: %d" % len(results))
    print("  Successo: %d" % success_count)
    print("  Fallite:  %d" % fail_count)
    print("\nDirectory output: %s" % output_dir)
    print()
    
    return {
        'success': True,
        'total_configs': len(results),
        'successful': success_count,
        'failed': fail_count,
        'results': results
    }


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
        
        # Ottieni sequenza fermate (comune a tutti i TimeProfiles)
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
        
        # PROCESSA TUTTI I TimeProfiles
        for tp_idx, tp in enumerate(tp_list):
            tp_name = tp.AttValue("Name")
            print("\n  " + "~" * 70)
            print("  TimeProfile [%d/%d]: %s" % (tp_idx + 1, len(tp_list), tp_name))
            print("  " + "~" * 70)
            
            print("\n  Abilitazione in sequenza temporale...")
            
            # Abilita in sequenza (le fermate sono gia' ordinate per index)
            enabled_count = 0
            error_count = 0
            
            for disabled in disabled_stops:
                print("\n    Processando fermata %d..." % disabled['stop'])
                
                # Rileggi sequenza aggiornata dopo ogni abilitazione
                stops = get_lr_stop_sequence(target_lr.LineRouteItems)
                
                # Debug: verifica stato attuale
                current_state = None
                for s in stops:
                    if s['stop'] == disabled['stop']:
                        current_state = s['is_route']
                        break
                print("      Stato IsRoutePoint attuale: %s" % current_state)
                
                success = abilita_fermata(tp, stops, disabled['stop'], 
                                         stop_time, pre_run_add, post_run_add)
                
                if success:
                    enabled_count += 1
                else:
                    error_count += 1
            
            print("\n  Risultato TimeProfile %s:" % tp_name)
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
        elif task_action == "execute_procedure_sequence":
            result = execute_procedure_sequence()
            results.append({
                "task_id": task_id,
                "task_name": task_name,
                "result": result
            })
        elif task_action == "export_layout_tables":
            task_params = task.get("params", {})
            layout_file = task_params.get('layout_file')
            output_dir = task_params.get('output_dir', './')
            project_name = task_params.get('project_name', 'export')
            
            if not layout_file:
                print("\nERRORE: Parametro 'layout_file' mancante!")
                results.append({
                    "task_id": task_id,
                    "task_name": task_name,
                    "result": {"error": "Missing layout_file parameter"}
                })
            else:
                result = export_layout_tables(layout_file, output_dir, project_name)
                results.append({
                    "task_id": task_id,
                    "task_name": task_name,
                    "result": result
                })
        elif task_action == "test_all_configurations":
            result = task_test_all_configurations(task.get("params", {}))
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

finally:
    # Chiudi file log se aperto
    if ENABLE_FILE_LOG and LOG_FILE:
        print("\n" + "=" * 80)
        print("LOG SALVATO: %s" % LOG_FILE)
        print("=" * 80)
        sys.stdout = original_stdout  # Ripristina stdout originale
        log_file_handle.close()
