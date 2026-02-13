#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Esplora tutti gli attributi e proprietà dell'operazione tipo 103 (Calculate Skim Matrix PrT)
"""

print("\n" + "=" * 70)
print("ESPLORAZIONE OPERAZIONE TIPO 103 (Calculate Skim Matrix PrT)")
print("=" * 70)

try:
    operations = Visum.Procedures.Operations
    
    # Trova posizione disponibile
    last_pos = 0
    for i in range(1, 101):
        try:
            operations.ItemByKey(i)
            last_pos = i
        except:
            break
    
    test_pos = last_pos + 1
    print("\nCreo operazione test alla posizione {}...".format(test_pos))
    
    # Crea operazione tipo 103
    skim_op = operations.AddOperation(test_pos)
    skim_op.SetAttValue("OPERATIONTYPE", 103)
    print("✓ Operazione tipo 103 creata")
    
    # Lista tutte le proprietà disponibili usando dir()
    print("\n" + "=" * 70)
    print("PROPRIETÀ DELL'OPERAZIONE (dir)")
    print("=" * 70)
    
    all_props = dir(skim_op)
    
    # Filtra per nomi che potrebbero essere parametri
    param_names = [p for p in all_props if 'Para' in p or 'Param' in p or 'Skim' in p]
    
    print("\nProprietà che contengono 'Para', 'Param' o 'Skim':")
    for prop in param_names:
        print("  - {}".format(prop))
    
    # Prova nomi comuni per parametri skim
    print("\n" + "=" * 70)
    print("TEST ACCESSO PARAMETRI")
    print("=" * 70)
    
    test_names = [
        "PrTSkimPara",
        "PrTSkimParameters", 
        "PrtSkimPara",
        "PrtSkimParameters",
        "SkimPara",
        "SkimParameters",
        "PrTSkimMatrixPara",
        "SkimMatrixPara",
        "CalcSkimPara",
        "CalculateSkimPara"
    ]
    
    for name in test_names:
        try:
            obj = getattr(skim_op, name)
            print("\n✓ {} FUNZIONA!".format(name))
            print("  Tipo: {}".format(type(obj)))
            
            # Prova a leggere dir() di questo oggetto
            if hasattr(obj, '__dir__'):
                sub_props = dir(obj)
                print("  Proprietà disponibili:")
                
                # Mostra solo proprietà interessanti (non quelle che iniziano con _)
                interesting = [p for p in sub_props if not p.startswith('_') and len(p) > 2]
                for p in interesting[:20]:  # Prime 20
                    print("    - {}".format(p))
                
                if len(interesting) > 20:
                    print("    ... ({} totali)".format(len(interesting)))
            
            # Prova a leggere attributi comuni
            print("\n  Test attributi comuni:")
            common_attrs = [
                "LinkCostAttribute", "ImpedanceAttribute", "Impedance",
                "T0", "TCUR", "TimeAttribute",
                "SkimMatrices", "ResultMatrix", "MatrixNo",
                "SkimItemSet", "SkimItems"
            ]
            
            for attr in common_attrs:
                try:
                    val = obj.AttValue(attr)
                    print("    ✓ {}: {}".format(attr, val))
                except:
                    try:
                        val = getattr(obj, attr)
                        print("    ✓ {} (prop): {}".format(attr, type(val)))
                    except:
                        pass
            
            break  # Trovato, esci dal loop
            
        except AttributeError:
            print("✗ {} non esiste".format(name))
        except Exception as e:
            print("✗ {} errore: {}".format(name, str(e)))
    
    # Prova anche a vedere se ci sono metodi interessanti
    print("\n" + "=" * 70)
    print("METODI DISPONIBILI")
    print("=" * 70)
    
    methods = [m for m in all_props if not m.startswith('_') and callable(getattr(skim_op, m, None))]
    print("\nMetodi pubblici:")
    for method in methods[:30]:
        print("  - {}".format(method))
    
    if len(methods) > 30:
        print("  ... ({} totali)".format(len(methods)))
    
    # Rimuovi operazione test
    print("\n" + "=" * 70)
    print("Rimozione operazione test...")
    operations.RemoveOperation(test_pos)
    print("✓ Operazione rimossa")
    
except Exception as e:
    print("\n✗ ERRORE: {}".format(str(e)))
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
