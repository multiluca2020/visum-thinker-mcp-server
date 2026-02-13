#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verifica quali Transport Systems sono disponibili nel progetto
"""

print("\n" + "=" * 70)
print("TRANSPORT SYSTEMS NEL PROGETTO")
print("=" * 70)

try:
    # Lista tutti i TSystems
    all_tsys = Visum.Net.TSystems.GetAll
    
    print("\nTotale Transport Systems: {}".format(len(all_tsys)))
    print("\n{:<10} {:<20} {:<10}".format("CODE", "NAME", "TYPE"))
    print("-" * 70)
    
    prt_systems = []
    
    for tsys in all_tsys:
        code = tsys.AttValue("CODE")
        name = tsys.AttValue("NAME")
        tsys_type = tsys.AttValue("TYPE")
        
        print("{:<10} {:<20} {:<10}".format(code, name, tsys_type))
        
        if tsys_type == "PRT":
            prt_systems.append(code)
    
    print("\n" + "=" * 70)
    print("TRANSPORT SYSTEMS PRT: {}".format(", ".join(prt_systems)))
    print("=" * 70)
    
    # Verifica anche gli attributi disponibili sull'operazione tipo 103
    print("\n" + "=" * 70)
    print("VERIFICA ATTRIBUTI OPERAZIONE SKIM (tipo 103)")
    print("=" * 70)
    
    # Crea temporaneamente un'operazione per vedere gli attributi
    operations = Visum.Procedures.Operations
    
    # Trova posizione
    last_pos = 0
    for i in range(1, 101):
        try:
            operations.ItemByKey(i)
            last_pos = i
        except:
            break
    
    test_pos = last_pos + 1
    print("\nCreo operazione test alla posizione {}...".format(test_pos))
    
    test_op = operations.AddOperation(test_pos)
    test_op.SetAttValue("OPERATIONTYPE", 103)
    
    print("Operazione creata: {}".format(test_op))
    
    # Prova a leggere attributi
    print("\nAttributi disponibili:")
    
    test_attrs = [
        "DSEGSET", "DSegSet", "DEMANDSEGS", "DemandSegments",
        "TSYSCODE", "TSysCode", "TSYSSET", "TSysSet",
        "LINKIMPEDANCE", "LinkImpedance", "IMPEDANCE",
        "RESULTMATRIX", "ResultMatrix", "MATRIXNO"
    ]
    
    for attr in test_attrs:
        try:
            val = test_op.AttValue(attr)
            print("  ✓ {}: {}".format(attr, val))
        except Exception as e:
            print("  ✗ {}: non esiste".format(attr))
    
    # Rimuovi operazione test
    print("\nRimozione operazione test...")
    operations.RemoveOperation(test_pos)
    print("✓ Operazione rimossa")
    
except Exception as e:
    print("\n✗ ERRORE: {}".format(str(e)))
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
