# -*- coding: ascii -*-
"""
Cerca metodi per confermare/commit modifiche al TimeProfile
"""

try:
    print("=" * 80)
    print("RICERCA METODI COMMIT/LOCK/CONFIRM")
    print("=" * 80)
    
    # Trova LineRoute
    lr = None
    for lineroute in Visum.Net.LineRoutes:
        name = lineroute.AttValue("Name")
        if name == "R17_2":
            lr = lineroute
            break
    
    if lr:
        tp = None
        for time_profile in lr.TimeProfiles:
            tp = time_profile
            break
        
        if tp:
            print("\nMETODI DISPONIBILI SU TIMEPROFILE:")
            print("-" * 80)
            
            # Lista TUTTI i metodi (non solo quelli filtrati)
            all_methods = []
            for attr in dir(tp):
                if not attr.startswith('_'):
                    try:
                        obj = getattr(tp, attr)
                        if callable(obj):
                            all_methods.append(attr)
                    except:
                        pass
            
            print("\nTutti i metodi callable:")
            for method in sorted(all_methods):
                print("  - %s" % method)
            
            print("\n" + "=" * 80)
            print("SUGGERIMENTO:")
            print("=" * 80)
            print("\nL'API COM di Visum non supporta la modifica permanente dei")
            print("TimeProfileItems via AddTimeProfileItem().")
            print("\nLe modifiche vengono perse al riavvio perche' Visum rigenera")
            print("i TimeProfileItems dal LineRoute quando carica il file.")
            print("\nSOLUZIONE:")
            print("1. Modifica manualmente dall'interfaccia (Line Route Editor)")
            print("2. Usa uno script VBScript/Python esterno che simula click GUI")
            print("3. Modifica il file .ver direttamente (richiede reverse engineering)")
            print("\nPer ora, le modifiche funzionano durante la sessione corrente")
            print("di Visum, ma non vengono salvate nel file.")

except Exception as e:
    print("\nERRORE: %s" % str(e))
    import traceback
    traceback.print_exc()
