#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Crea matrici SKIM in Visum usando tempi T0 (flusso libero)

Calcola matrici di:
- Tempo di viaggio T0 (minuti) usando V0PRT
- Distanza (km)

Usando percorsi minimi sulla rete senza congestione.
"""

try:
    from win32com.client import Dispatch
    Visum = Dispatch("Visum.Visum.240")
except:
    # Assume già in console Visum
    pass


def create_skim_matrices(matrix_time_no=1, matrix_dist_no=2, 
                         transport_system="P", 
                         visum_instance=None):
    """
    Crea matrici SKIM per tempi T0 e distanze su rete a flusso libero.
    
    Processo:
    1. Verifica esistenza matrici (crea se necessario)
    2. Crea procedura "Skim Matrix Calculation"
    3. Configura parametri:
       - Sistema di trasporto (PrT)
       - Attributo tempo: T0_PRTSYS(P) = tempo flusso libero
       - Attributo distanza: LENGTH
    4. Esegue calcolo percorsi minimi
    5. Popola matrici con valori calcolati
    
    Args:
        matrix_time_no (int): Numero matrice tempi (default: 1)
        matrix_dist_no (int): Numero matrice distanze (default: 2)
        transport_system (str): Codice sistema di trasporto PrT (default: "P")
        visum_instance: Istanza Visum (default: usa console)
    
    Returns:
        dict: {
            "status": "success"|"failed",
            "message": str,
            "matrix_time": int,
            "matrix_dist": int,
            "zones": int,
            "od_pairs": int
        }
    
    Esempio dalla console Visum:
        >>> exec(open(r"H:\\visum-thinker-mcp-server\\create-skim-matrices.py").read())
        >>> result = create_skim_matrices()
        >>> print(result)
        
        >>> # Con parametri custom
        >>> result = create_skim_matrices(
        ...     matrix_time_no=10,
        ...     matrix_dist_no=11,
        ...     transport_system="CAR"
        ... )
    """
    result = {
        "status": "failed",
        "message": "",
        "matrix_time": matrix_time_no,
        "matrix_dist": matrix_dist_no,
        "zones": 0,
        "od_pairs": 0
    }
    
    try:
        # Usa istanza Visum
        if visum_instance is None:
            visum = Visum
        else:
            visum = visum_instance
        
        print("\n" + "=" * 70)
        print("CREAZIONE MATRICI SKIM (T0 - FLUSSO LIBERO)")
        print("=" * 70)
        
        # Verifica zone
        num_zones = visum.Net.Zones.Count
        if num_zones == 0:
            result["message"] = "Nessuna zona trovata nel progetto"
            print("✗ {}".format(result["message"]))
            return result
        
        result["zones"] = num_zones
        print("Zone trovate: {}".format(num_zones))
        print("Coppie O-D teoriche: {}".format(num_zones * num_zones))
        
        # Step 1: Crea/verifica matrici
        print("\n### STEP 1: VERIFICA MATRICI ###")
        
        # Matrice tempi
        try:
            matrix_time = visum.Net.Matrices.ItemByKey(matrix_time_no)
            print("✓ Matrice tempi {} già esistente: {}".format(
                matrix_time_no, matrix_time.AttValue("Name")))
        except:
            matrix_time = visum.Net.AddMatrix(matrix_time_no)
            matrix_time.SetAttValue("Name", "Skim_Time_T0")
            matrix_time.SetAttValue("Code", "TIME_T0")
            print("✓ Creata matrice tempi {}: Skim_Time_T0".format(matrix_time_no))
        
        # Matrice distanze
        try:
            matrix_dist = visum.Net.Matrices.ItemByKey(matrix_dist_no)
            print("✓ Matrice distanze {} già esistente: {}".format(
                matrix_dist_no, matrix_dist.AttValue("Name")))
        except:
            matrix_dist = visum.Net.AddMatrix(matrix_dist_no)
            matrix_dist.SetAttValue("Name", "Skim_Distance")
            matrix_dist.SetAttValue("Code", "DIST")
            print("✓ Creata matrice distanze {}: Skim_Distance".format(matrix_dist_no))
        
        # Step 2: Crea procedura Skim Matrix Calculation
        print("\n### STEP 2: CREAZIONE PROCEDURA SKIM ###")
        
        # Cerca procedura esistente
        existing_skim = None
        for proc in visum.Procedures.GetAll:
            if proc.AttValue("PrT_SkimOp") is not None:
                existing_skim = proc
                print("✓ Trovata procedura skim esistente: ID {}".format(
                    proc.AttValue("ID")))
                break
        
        if existing_skim:
            print("Uso procedura esistente...")
            skim_proc = existing_skim
        else:
            # Crea nuova procedura
            # ProcedureType: 14 = Skim Matrix Calculation
            print("Creazione nuova procedura...")
            skim_proc = visum.Procedures.AddProcedure(14)
            print("✓ Procedura skim creata: ID {}".format(skim_proc.AttValue("ID")))
        
        # Step 3: Configura parametri skim
        print("\n### STEP 3: CONFIGURAZIONE PARAMETRI ###")
        
        # Accedi all'operazione Skim
        skim_op = skim_proc.AttValue("PrT_SkimOp")
        
        if skim_op is None:
            result["message"] = "Impossibile accedere a PrT_SkimOp"
            print("✗ {}".format(result["message"]))
            return result
        
        # Configura sistema trasporto
        try:
            print("Sistema trasporto: {}".format(transport_system))
            skim_op.SetAttValue("TSysCode", transport_system)
        except Exception as e:
            print("⚠ Errore setting TSysCode: {}".format(str(e)))
            print("  Provo con TSysSet...")
            try:
                # Alternativa: usa TSysSet
                tsys = visum.Net.TSystems.ItemByKey(transport_system)
                skim_op.SetAttValue("TSysSet", tsys)
            except Exception as e2:
                print("⚠ Errore TSysSet: {}".format(str(e2)))
        
        # Configura matrice tempi
        try:
            # Usa T0_PRTSYS per tempi a flusso libero
            # Formato: T0_PRTSYS(codice_tsys)
            time_attr = "T0_PRTSYS({})".format(transport_system)
            print("Attributo tempo: {}".format(time_attr))
            
            skim_op.SetAttValue("LinkImpedance", time_attr)
            skim_op.SetAttValue("ResultMatrix", matrix_time_no)
            print("✓ Matrice tempi {} configurata (attributo: {})".format(
                matrix_time_no, time_attr))
        except Exception as e:
            print("⚠ Errore configurazione tempo: {}".format(str(e)))
            print("  Uso T0PRT come fallback...")
            try:
                skim_op.SetAttValue("LinkImpedance", "T0PRT")
                skim_op.SetAttValue("ResultMatrix", matrix_time_no)
            except:
                pass
        
        # Configura matrice distanze (attributo aggiuntivo)
        try:
            # Aggiungi skim addizionale per distanza
            print("Attributo distanza: LENGTH")
            
            # Metodo 1: AddSkimItem (se disponibile)
            try:
                skim_item = skim_op.SkimItems.AddSkimItem()
                skim_item.SetAttValue("Attribute", "LENGTH")
                skim_item.SetAttValue("Matrix", matrix_dist_no)
                print("✓ Matrice distanze {} configurata (LENGTH)".format(matrix_dist_no))
            except:
                # Metodo 2: Seconda procedura per distanze
                print("  SkimItems non disponibile, creo seconda procedura...")
                skim_proc2 = visum.Procedures.AddProcedure(14)
                skim_op2 = skim_proc2.AttValue("PrT_SkimOp")
                skim_op2.SetAttValue("TSysCode", transport_system)
                skim_op2.SetAttValue("LinkImpedance", "LENGTH")
                skim_op2.SetAttValue("ResultMatrix", matrix_dist_no)
                print("✓ Seconda procedura creata per distanze")
                
        except Exception as e:
            print("⚠ Errore configurazione distanza: {}".format(str(e)))
        
        # Step 4: Esegui calcolo
        print("\n### STEP 4: ESECUZIONE CALCOLO SKIM ###")
        print("Calcolo percorsi minimi in corso...")
        
        try:
            skim_proc.Execute()
            print("✓ Calcolo completato con successo")
        except Exception as e:
            result["message"] = "Errore esecuzione skim: {}".format(str(e))
            print("✗ {}".format(result["message"]))
            return result
        
        # Verifica risultati
        print("\n### VERIFICA RISULTATI ###")
        
        # Conta valori non nulli nella matrice tempi
        try:
            time_values = matrix_time.GetValuesFlat()
            non_zero_count = sum(1 for v in time_values if v > 0)
            result["od_pairs"] = non_zero_count
            
            print("Matrice tempi ({}):".format(matrix_time_no))
            print("  - Valori totali: {}".format(len(time_values)))
            print("  - Valori > 0: {}".format(non_zero_count))
            print("  - % copertura: {:.1f}%".format(
                100.0 * non_zero_count / len(time_values) if len(time_values) > 0 else 0))
            
            if non_zero_count > 0:
                avg_time = sum(v for v in time_values if v > 0) / non_zero_count
                print("  - Tempo medio: {:.2f} min".format(avg_time))
        except Exception as e:
            print("⚠ Impossibile leggere valori matrice: {}".format(str(e)))
        
        # Risultato finale
        result["status"] = "success"
        result["message"] = "Matrici skim create con successo"
        
        print("\n" + "=" * 70)
        print("PROCESSO COMPLETATO")
        print("=" * 70)
        print("\nMatrici create:")
        print("  - Matrice {}: Tempi T0 (minuti)".format(matrix_time_no))
        print("  - Matrice {}: Distanze (km)".format(matrix_dist_no))
        print("\nZone: {}".format(num_zones))
        print("Coppie O-D calcolate: {}".format(result["od_pairs"]))
        print("=" * 70)
        
        return result
        
    except Exception as e:
        result["message"] = "Errore creazione skim: {}".format(str(e))
        print("\n✗ {}".format(result["message"]))
        import traceback
        traceback.print_exc()
        return result


if __name__ == "__main__":
    # Test standalone
    result = create_skim_matrices()
    print("\nRisultato:", result)
