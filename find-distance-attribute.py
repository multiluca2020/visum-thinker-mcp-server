# -*- coding: ascii -*-
"""
Analizza attributi di distanza sui LineRouteItems
per capire quale usare per l'interpolazione
"""

try:
    print("=" * 80)
    print("ANALISI ATTRIBUTI DISTANZA LINEROUTE")
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
        print("\nLineRoute: %s\n" % lr.AttValue("Name"))
        
        # Lista attributi da testare
        distance_attrs = [
            "AccumLength", "Length", "DirectDist", "DirectDistOnNet",
            "Dist", "Distance", "AccumDist", "CumLength"
        ]
        
        print("Attributi disponibili sui LineRouteItems:\n")
        
        # Prendi primi 3 stops per test
        stops_to_check = [301, 370, 173]
        items_data = []
        
        for lri in lr.LineRouteItems:
            stop_no = lri.AttValue("StopPointNo")
            if stop_no and int(stop_no) in stops_to_check:
                data = {
                    'stop': int(stop_no),
                    'index': lri.AttValue("Index")
                }
                
                # Testa ogni attributo
                for attr in distance_attrs:
                    try:
                        value = lri.AttValue(attr)
                        data[attr] = value
                    except:
                        data[attr] = None
                
                items_data.append(data)
        
        # Ordina per index
        items_data.sort(key=lambda x: x['index'])
        
        # Stampa tabella
        print("%-10s | %-6s | %-12s | %-12s | %-12s" % ("Stop", "Index", "AccumLength", "Length", "Altri..."))
        print("-" * 80)
        
        for item in items_data:
            print("%-10d | %-6.0f | " % (item['stop'], item['index']), end="")
            
            for attr in distance_attrs[:2]:
                val = item.get(attr)
                if val is not None:
                    print("%-12.3f | " % val, end="")
                else:
                    print("%-12s | " % "N/A", end="")
            
            # Mostra altri attributi disponibili
            others = []
            for attr in distance_attrs[2:]:
                if item.get(attr) is not None:
                    others.append("%s=%.3f" % (attr, item[attr]))
            print(", ".join(others) if others else "Nessuno")
        
        # Calcola differenze
        print("\n" + "=" * 80)
        print("CALCOLO DIFFERENZE:")
        print("=" * 80)
        
        if len(items_data) >= 3:
            prev = items_data[0]  # 301
            curr = items_data[1]  # 370
            next_item = items_data[2]  # 173
            
            for attr in distance_attrs:
                if prev.get(attr) is not None and curr.get(attr) is not None and next_item.get(attr) is not None:
                    diff_prev_curr = curr[attr] - prev[attr]
                    diff_curr_next = next_item[attr] - curr[attr]
                    diff_total = next_item[attr] - prev[attr]
                    
                    if abs(diff_total) > 0.001:  # Evita divisione per zero
                        proportion = diff_prev_curr / diff_total
                        
                        print("\n%s:" % attr)
                        print("  301: %.6f" % prev[attr])
                        print("  370: %.6f" % curr[attr])
                        print("  173: %.6f" % next_item[attr])
                        print("  Diff 301->370: %.6f" % diff_prev_curr)
                        print("  Diff 370->173: %.6f" % diff_curr_next)
                        print("  Diff totale:   %.6f" % diff_total)
                        print("  Proporzione:   %.6f (= %.1f%%)" % (proportion, proportion * 100))
                        
                        # Calcola tempo con questa proporzione
                        # Tempo totale 301->173 = 720 sec (da output precedente)
                        time_total = 720.0
                        pre_run = proportion * time_total
                        print("  PreRunTime se usiamo questo: %.1f sec" % pre_run)
                        
                        if abs(pre_run - 79.0) < 1.0:
                            print("  >>> QUESTO E' CORRETTO! (Visum usa 79 sec)")
        
        print("\n" + "=" * 80)
        print("CONCLUSIONE:")
        print("=" * 80)
        print("\nL'attributo che da proporzione corretta")
        print("(PreRunTime ~79 sec) e' quello giusto da usare!")

except Exception as e:
    print("\nERRORE: %s" % str(e))
    import traceback
    traceback.print_exc()
