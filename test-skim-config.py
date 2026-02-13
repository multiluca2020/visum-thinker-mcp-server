"""
Test configurazione skim matrix con API corretta
Verifica che PrTSkimMatrixParameters e SingleSkimMatrixParameters funzionino
"""

import win32com.client
import sys

def test_skim_config():
    """
    Test rapido della configurazione skim senza eseguire il calcolo
    """
    try:
        print("=" * 70)
        print("TEST CONFIGURAZIONE SKIM MATRIX API")
        print("=" * 70)
        
        # Connetti a Visum
        print("\nConnessione a Visum in corso...")
        visum = win32com.client.Dispatch("Visum.Visum")
        print("✓ Connesso a Visum")
        
        # Verifica progetto aperto
        try:
            num_zones = visum.Net.Zones.Count
            print("✓ Progetto aperto: {} zone".format(num_zones))
        except:
            print("✗ Nessun progetto aperto in Visum")
            return
        
        # Trova demand segments MODE='C'
        print("\n### STEP 1: DEMAND SEGMENTS ###")
        all_segments = visum.Net.DemandSegments.GetAll
        car_segments = []
        for seg in all_segments:
            mode = seg.AttValue("MODE")
            if mode == "C":
                car_segments.append(seg.AttValue("CODE"))
        
        if len(car_segments) == 0:
            print("✗ Nessun demand segment MODE='C' trovato")
            return
        
        # Usa solo il PRIMO segment (API accetta un solo DSeg)
        first_segment = car_segments[0]
        print("✓ Trovati {} segments".format(len(car_segments)))
        print("  Usando il primo: {}".format(first_segment))
        print("  (API accetta un solo DSeg alla volta)")
        
        # Crea operazione test
        print("\n### STEP 2: CREAZIONE OPERAZIONE ###")
        operations = visum.Procedures.Operations
        
        # Trova posizione libera
        last_pos = 0
        for i in range(1, 101):
            try:
                operations.ItemByKey(i)
                last_pos = i
            except:
                break
        
        test_pos = last_pos + 1
        print("Posizione test: {}".format(test_pos))
        
        # Crea operazione tipo 103
        skim_op = operations.AddOperation(test_pos)
        skim_op.SetAttValue("OPERATIONTYPE", 103)
        print("✓ Operazione tipo 103 creata")
        
        # Test accesso parametri
        print("\n### STEP 3: TEST ACCESSO PARAMETRI ###")
        
        try:
            skim_params = skim_op.PrTSkimMatrixParameters
            print("✓ PrTSkimMatrixParameters accessibile")
        except Exception as e:
            print("✗ Errore accesso PrTSkimMatrixParameters: {}".format(e))
            print("  Provo con nomi alternativi...")
            
            # Prova nomi alternativi
            for name in ["PrTSkimPara", "SkimMatrixParameters", "SkimParameters"]:
                try:
                    skim_params = getattr(skim_op, name)
                    print("✓ {} funziona!".format(name))
                    break
                except:
                    print("  ✗ {} non funziona".format(name))
            else:
                print("\n✗ Nessun nome property funziona")
                print("Attributi disponibili su operation:")
                for attr in dir(skim_op):
                    if "skim" in attr.lower() or "matrix" in attr.lower():
                        print("  - {}".format(attr))
                return
        
        # Test configurazione DSeg
        print("\n### STEP 4: TEST CONFIGURAZIONE DSeg ###")
        try:
            skim_params.SetAttValue("DSeg", first_segment)
            print("✓ DSeg configurato: {}".format(first_segment))
        except Exception as e:
            print("✗ Errore DSeg: {}".format(e))
        
        # Test configurazione SearchCriterion
        print("\n### STEP 5: TEST CONFIGURAZIONE SearchCriterion ###")
        
        # Prova diversi formati
        for criterion_value in ["criteria_t0", 0, "t0", "T0"]:
            try:
                skim_params.SetAttValue("SearchCriterion", criterion_value)
                print("✓ SearchCriterion={} funziona".format(repr(criterion_value)))
                break
            except Exception as e:
                print("✗ SearchCriterion={} fallito: {}".format(repr(criterion_value), e))
        
        # Test accesso SingleSkimMatrixParameters
        print("\n### STEP 6: TEST SingleSkimMatrixParameters ###")
        
        skim_names = ["T0", "TCur", "TripDist"]
        for skim_name in skim_names:
            try:
                single_skim = skim_params.SingleSkimMatrixParameters(skim_name)
                print("✓ SingleSkimMatrixParameters('{}') accessibile".format(skim_name))
                
                # Test configurazione Calculate
                try:
                    single_skim.SetAttValue("Calculate", True)
                    print("  ✓ Calculate=True impostato")
                except Exception as e:
                    print("  ✗ Errore Calculate: {}".format(e))
                
            except Exception as e:
                print("✗ SingleSkimMatrixParameters('{}') fallito: {}".format(skim_name, e))
        
        # Rimuovi operazione test
        print("\n### STEP 7: CLEANUP ###")
        try:
            skim_op.Delete()
            print("✓ Operazione test rimossa")
        except Exception as e:
            print("⚠ Impossibile rimuovere operazione: {}".format(e))
            print("  Rimuovila manualmente dalla posizione {}".format(test_pos))
        
        print("\n" + "=" * 70)
        print("TEST COMPLETATO")
        print("=" * 70)
        print("\nSe tutti i test sono ✓, la configurazione API è corretta!")
        print("Puoi procedere con create_skim_matrices()")
        
    except Exception as e:
        print("\n✗ Errore durante il test: {}".format(e))
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_skim_config()
