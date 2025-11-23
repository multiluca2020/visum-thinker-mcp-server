# -*- coding: ascii -*-
"""
Verifica COMPLETA di tutti i TimeProfiles e versioni
Forse la GUI legge da un TimeProfile diverso o da una versione precedente
"""

try:
    print("=" * 80)
    print("RICERCA COMPLETA DI TUTTI I TIMEPROFILES NELLA RETE")
    print("=" * 80)
    
    # Trova LineRoute R17_2
    lr = None
    for lineroute in Visum.Net.LineRoutes:
        name = lineroute.AttValue("Name")
        if name == "R17_2":
            lr = lineroute
            break
    
    if not lr:
        print("\nERRORE: LineRoute R17_2 non trovato!")
    else:
        print("\nLineRoute: %s" % lr.AttValue("Name"))
        print("LineName: %s" % lr.AttValue("LineName"))
        
        print("\n" + "=" * 80)
        print("TUTTI I TIMEPROFILES DI QUESTO LINEROUTE:")
        print("=" * 80)
        
        tp_count = 0
        for tp in lr.TimeProfiles:
            tp_count += 1
            tp_name = tp.AttValue("Name")
            
            print("\n--- TimeProfile #%d: %s ---" % (tp_count, tp_name))
            
            # Conta items
            item_count = 0
            has_370 = False
            stop_370_data = None
            
            for tpi in tp.TimeProfileItems:
                item_count += 1
                stop_no = tpi.AttValue("StopPointNo")
                if int(stop_no) == 370:
                    has_370 = True
                    stop_370_data = {
                        'arr': tpi.AttValue("Arr"),
                        'dep': tpi.AttValue("Dep"),
                        'stoptime': tpi.AttValue("StopTime")
                    }
            
            print("  Total items: %d" % item_count)
            print("  Ha fermata 370: %s" % has_370)
            
            if has_370:
                print("  >>> FERMATA 370 IN QUESTO TIMEPROFILE:")
                print("      Arr:      %s" % stop_370_data['arr'])
                print("      Dep:      %s" % stop_370_data['dep'])
                print("      StopTime: %s" % stop_370_data['stoptime'])
        
        print("\n" + "=" * 80)
        print("TOTALE TimeProfiles trovati: %d" % tp_count)
        print("=" * 80)
        
        # Verifica anche a livello di rete globale
        print("\n" + "=" * 80)
        print("VERIFICA TUTTI I TIMEPROFILES NELLA RETE (tutte le linee):")
        print("=" * 80)
        
        all_tp_count = 0
        tp_with_370 = []
        
        for lineroute in Visum.Net.LineRoutes:
            lr_name = lineroute.AttValue("Name")
            
            for tp in lineroute.TimeProfiles:
                all_tp_count += 1
                tp_name = tp.AttValue("Name")
                
                # Verifica se ha fermata 370
                for tpi in tp.TimeProfileItems:
                    stop_no = tpi.AttValue("StopPointNo")
                    if stop_no and int(stop_no) == 370:
                        tp_with_370.append({
                            'lineroute': lr_name,
                            'timeprofile': tp_name,
                            'arr': tpi.AttValue("Arr"),
                            'dep': tpi.AttValue("Dep"),
                            'stoptime': tpi.AttValue("StopTime")
                        })
                        break
        
        print("\nTotale TimeProfiles in tutta la rete: %d" % all_tp_count)
        print("TimeProfiles con fermata 370: %d" % len(tp_with_370))
        
        if tp_with_370:
            print("\nDettagli:")
            for item in tp_with_370:
                print("\n  LineRoute: %s" % item['lineroute'])
                print("  TimeProfile: %s" % item['timeprofile'])
                print("  Arr: %s, Dep: %s, StopTime: %s" % 
                      (item['arr'], item['dep'], item['stoptime']))
        
        print("\n" + "=" * 80)
        print("PROVA DIRETTA: Accedi al TimeProfile dall'interfaccia")
        print("=" * 80)
        print("\nAdesso:")
        print("1. Apri Edit > Time Profiles")
        print("2. Seleziona LineRoute R17_2")
        print("3. Guarda quale TimeProfile e' selezionato nella dropdown")
        print("4. Dimmi il nome esatto del TimeProfile attivo nella GUI")
        print("")
        print("Se la GUI mostra un TimeProfile diverso da 'R17', allora")
        print("stiamo modificando il TimeProfile sbagliato!")

except Exception as e:
    print("\nERRORE: %s" % str(e))
    import traceback
    traceback.print_exc()
