# -*- coding: utf-8 -*-
"""
Script di test per la funzionalità di export layout
Dimostra come configurare il task di export nel workflow
"""

# ESEMPIO 1: Task singolo - Solo export
TASKS_EXPORT_ONLY = [
    {
        "id": 1,
        "name": "Esporta tabelle da Global Layout",
        "action": "export_layout_tables",
        "params": {
            # Path al file .lay (MODIFICA QUESTO PATH!)
            "layout_file": r"H:\go\trenord_2025\skim_layout.lay",
            
            # Directory output per i CSV
            "output_dir": r"H:\go\trenord_2025\exported_tables",
            
            # Prefisso per i nomi file (opzionale, default="export")
            "project_name": "trenord_skim"
        }
    }
]

# ESEMPIO 2: Workflow completo - Abilita, Esegui, Esporta
TASKS_COMPLETE = [
    {
        "id": 1,
        "name": "Abilita tutte le fermate disabilitate",
        "action": "enable_all_disabled",
        "lineroutes": [
            "R17_2022:R17_2",
            "R17_2022:R17_3",
        ],
        "params": {
            "stop_time": 60,
            "pre_run_add": 30,
            "post_run_add": 30
        }
    },
    {
        "id": 2,
        "name": "Esegui Procedure Sequence di Visum",
        "action": "execute_procedure_sequence",
        "params": {}
    },
    {
        "id": 3,
        "name": "Esporta risultati da layout",
        "action": "export_layout_tables",
        "params": {
            "layout_file": r"H:\go\trenord_2025\results_layout.lay",
            "output_dir": r"H:\go\trenord_2025\final_results",
            "project_name": "trenord_final"
        }
    }
]

# ESEMPIO 3: Export multipli - Diversi layout
TASKS_MULTI_EXPORT = [
    {
        "id": 1,
        "name": "Esporta tabelle base",
        "action": "export_layout_tables",
        "params": {
            "layout_file": r"H:\layouts\base_tables.lay",
            "output_dir": r"H:\exports\base",
            "project_name": "base"
        }
    },
    {
        "id": 2,
        "name": "Esporta tabelle avanzate",
        "action": "export_layout_tables",
        "params": {
            "layout_file": r"H:\layouts\advanced_tables.lay",
            "output_dir": r"H:\exports\advanced",
            "project_name": "advanced"
        }
    }
]

"""
COME USARE:

1. Apri Visum Python Console (Ctrl+P)

2. Modifica manage-stops-workflow.py:
   - Trova la sezione TASKS
   - Decomment il task 3 (export_layout_tables)
   - Modifica i path nel task:
     * layout_file: Path al tuo file .lay
     * output_dir: Directory dove salvare i CSV
     * project_name: Prefisso per i file

3. Esegui lo script:
   exec(open(r"h:\visum-thinker-mcp-server\manage-stops-workflow.py").read())

4. Controlla i risultati:
   - CSV salvati in output_dir
   - Log in H:\go\trenord_2025\logs\workflow_YYYYMMDD_HHMMSS.log

STRUTTURA CSV:
- Delimiter: punto e virgola (;)
- Encoding: UTF-8
- Filename: {project_name}_{table_name}.csv
- Headers: Nome colonna (attributi con sub-attributes: ATTR_SUB1_SUB2)

TABELLE SUPPORTATE:
- LINK, NODE, ZONE, ODPAIR
- LINE, LINEROUTE, TIMEPROFILE, TIMEPROFILEITEM
- VEHJOURNEYSECTION, STOP, STOPPOINTAREA
- CONNECTOR

PERFORMANCE:
- 227K righe × 29 colonne: ~6.7 secondi
- Dipende da numero tabelle e dimensioni dati
"""

print(__doc__)
