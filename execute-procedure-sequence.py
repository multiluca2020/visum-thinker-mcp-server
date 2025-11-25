# -*- coding: utf-8 -*-
"""
Script per eseguire una Procedure Sequence di Visum
"""

import sys
import os
from datetime import datetime

# ============================================================================
# CONFIGURAZIONE
# ============================================================================

# Nome della Procedure Sequence da eseguire (lascia vuoto per usare quella attiva)
PROCEDURE_SEQUENCE_NAME = ""  # Es: "MyProcedure" o "" per quella corrente

# Abilita log su file
ENABLE_FILE_LOG = True
LOG_DIR = r"h:\visum-thinker-mcp-server\logs"
LOG_FILE = None

# ============================================================================
# SETUP LOG
# ============================================================================

if ENABLE_FILE_LOG:
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    LOG_FILE = os.path.join(LOG_DIR, "procedure_execution_%s.log" % timestamp)
    
    log_file_handle = open(LOG_FILE, "w", encoding="utf-8")
    
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
    
    original_stdout = sys.stdout
    sys.stdout = TeeOutput(original_stdout, log_file_handle)
    
    print("=" * 80)
    print("LOG ABILITATO: %s" % LOG_FILE)
    print("=" * 80)
    print()

# ============================================================================
# ESECUZIONE PROCEDURE SEQUENCE
# ============================================================================

try:
    print("=" * 80)
    print("ESECUZIONE PROCEDURE SEQUENCE")
    print("=" * 80)
    print("\nData/Ora inizio: %s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print()
    
    # Ottieni informazioni sulla Procedure Sequence corrente
    print("Recupero informazioni Procedure Sequence...")
    
    # Conta operazioni nella sequenza corrente
    try:
        # Visum.Procedures è la collezione di operazioni della sequenza corrente
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
    
    # Metodo 1: Esegui tutta la sequenza
    try:
        Visum.Procedures.Execute()
        print("\n" + "=" * 80)
        print("ESECUZIONE COMPLETATA CON SUCCESSO")
        print("=" * 80)
    except Exception as e:
        print("\n" + "=" * 80)
        print("ERRORE DURANTE ESECUZIONE")
        print("=" * 80)
        print("Errore: %s" % str(e))
        import traceback
        traceback.print_exc()
        raise
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("\nData/Ora fine: %s" % end_time.strftime("%Y-%m-%d %H:%M:%S"))
    print("Durata totale: %.2f secondi (%.2f minuti)" % (duration, duration / 60.0))
    print()

except Exception as e:
    print("\nERRORE FATALE: %s" % str(e))
    import traceback
    traceback.print_exc()

finally:
    # Chiudi file log
    if ENABLE_FILE_LOG and LOG_FILE:
        print("\n" + "=" * 80)
        print("LOG SALVATO: %s" % LOG_FILE)
        print("=" * 80)
        sys.stdout = original_stdout
        log_file_handle.close()
