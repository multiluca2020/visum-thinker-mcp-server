# -*- coding: ascii -*-
"""
Analisi dettagliata TimeProfileItem fermata 370
Confronto con fermate adiacenti per capire il calcolo corretto
"""

try:
    print("=" * 80)
    print("ANALISI TIMEPROFILEITEM FERMATA 370 - CALCOLO TEMPI")
    print("=" * 80)
    
    # Trova LineRoute
    lr = None
    for lineroute in Visum.Net.LineRoutes:
        name = lineroute.AttValue("Name")
        if name == "R17_2":
            lr = lineroute
            break
    
    if not lr:
        print("\nERRORE: LineRoute non trovato!")
    else:
        # TimeProfile
        tp = None
        for time_profile in lr.TimeProfiles:
            tp = time_profile
            break
        
        if not tp:
            print("\nERRORE: TimeProfile non trovato!")
        else:
            print("\nTimeProfile: %s\n" % tp.AttValue("Name"))
            
            # Trova fermata 370 e le adiacenti
            tpi_list = []
            for tpi in tp.TimeProfileItems:
                stop_no = tpi.AttValue("StopPointNo")
                if stop_no:
                    tpi_list.append({
                        'stop': int(stop_no),
                        'index': tpi.AttValue("Index"),
                        'arr': tpi.AttValue("Arr"),
                        'dep': tpi.AttValue("Dep"),
                        'stoptime': tpi.AttValue("StopTime"),
                        'prerun': tpi.AttValue("PreRunTime"),
                        'postrun': tpi.AttValue("PostRunTime")
                    })
            
            # Ordina per index
            tpi_list.sort(key=lambda x: x['index'])
            
            # Trova posizione 370
            pos_370 = None
            for i, item in enumerate(tpi_list):
                if item['stop'] == 370:
                    pos_370 = i
                    break
            
            if pos_370 is None:
                print("ERRORE: Fermata 370 non trovata nel TimeProfile!")
            else:
                prev = tpi_list[pos_370 - 1] if pos_370 > 0 else None
                curr = tpi_list[pos_370]
                next_item = tpi_list[pos_370 + 1] if pos_370 < len(tpi_list) - 1 else None
                
                print("=" * 80)
                print("FERMATE ADIACENTI:")
                print("=" * 80)
                
                if prev:
                    print("\nFERMATA PRECEDENTE: %d" % prev['stop'])
                    print("  Arr:      %8.1f" % prev['arr'])
                    print("  Dep:      %8.1f" % prev['dep'])
                    print("  StopTime: %8.1f" % prev['stoptime'])
                    print("  PreRun:   %8.1f" % prev['prerun'])
                    print("  PostRun:  %8.1f" % prev['postrun'])
                
                print("\nFERMATA 370 (CREATA DA VISUM):")
                print("  Arr:      %8.1f" % curr['arr'])
                print("  Dep:      %8.1f" % curr['dep'])
                print("  StopTime: %8.1f" % curr['stoptime'])
                print("  PreRun:   %8.1f  <--- Questo e' il valore creato da Visum" % curr['prerun'])
                print("  PostRun:  %8.1f" % curr['postrun'])
                
                if next_item:
                    print("\nFERMATA SUCCESSIVA: %d" % next_item['stop'])
                    print("  Arr:      %8.1f" % next_item['arr'])
                    print("  Dep:      %8.1f" % next_item['dep'])
                    print("  StopTime: %8.1f" % next_item['stoptime'])
                    print("  PreRun:   %8.1f" % next_item['prerun'])
                    print("  PostRun:  %8.1f" % next_item['postrun'])
                
                print("\n" + "=" * 80)
                print("CALCOLI:")
                print("=" * 80)
                
                if prev:
                    print("\n[1] PRERUNTIME di 370:")
                    print("    Formula: Arr(370) - Dep(prev)")
                    print("    Calcolo: %.1f - %.1f = %.1f" % (curr['arr'], prev['dep'], curr['arr'] - prev['dep']))
                    print("    Visum:   %.1f" % curr['prerun'])
                    if abs((curr['arr'] - prev['dep']) - curr['prerun']) < 0.1:
                        print("    MATCH: Visum usa Arr(370) - Dep(prev)")
                    else:
                        print("    DIVERSO!")
                
                print("\n[2] STOPTIME di 370:")
                print("    Formula: Dep(370) - Arr(370)")
                print("    Calcolo: %.1f - %.1f = %.1f" % (curr['dep'], curr['arr'], curr['dep'] - curr['arr']))
                print("    Visum:   %.1f" % curr['stoptime'])
                
                if next_item:
                    print("\n[3] POSTRUNTIME di 370:")
                    print("    Formula: Arr(next) - Dep(370)")
                    print("    Calcolo: %.1f - %.1f = %.1f" % (next_item['arr'], curr['dep'], next_item['arr'] - curr['dep']))
                    print("    Visum:   %.1f" % curr['postrun'])
                    if abs((next_item['arr'] - curr['dep']) - curr['postrun']) < 0.1:
                        print("    MATCH: Visum usa Arr(next) - Dep(370)")
                    else:
                        print("    DIVERSO!")
                
                print("\n" + "=" * 80)
                print("CONCLUSIONE:")
                print("=" * 80)
                print("\nVisum ha creato automaticamente la fermata 370 con:")
                print("  PreRunTime:  %.1f secondi" % curr['prerun'])
                print("  StopTime:    %.1f secondi" % curr['stoptime'])
                print("  PostRunTime: %.1f secondi" % curr['postrun'])
                print("\nSe dobbiamo ricrearla manualmente, dobbiamo usare:")
                print("  Arr = Dep(prev) + %.1f" % curr['prerun'])
                print("  Dep = Arr + %.1f" % curr['stoptime'])
                print("\nQuindi: Arr = %.1f + %.1f = %.1f" % (prev['dep'], curr['prerun'], prev['dep'] + curr['prerun']))
                print("        Dep = %.1f + %.1f = %.1f" % (curr['arr'], curr['stoptime'], curr['arr'] + curr['stoptime']))

except Exception as e:
    print("\nERRORE: %s" % str(e))
    import traceback
    traceback.print_exc()
