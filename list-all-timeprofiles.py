# -*- coding: ascii -*-
"""
Lista tutti i TimeProfiles del LineRoute R17_2
"""

try:
    print("=" * 80)
    print("TIMEPROFILES DEL LINEROUTE R17_2")
    print("=" * 80)
    
    # Trova il LineRoute
    lr = None
    for lineroute in Visum.Net.LineRoutes:
        name = lineroute.AttValue("Name")
        if name == "R17_2":
            lr = lineroute
            break
    
    if lr is None:
        print("ERRORE: LineRoute R17_2 non trovato!")
    else:
        print("\nLineRoute trovato: R17_2")
        print("LineName: %s" % lr.AttValue("LineName"))
        print("")
        
        # Lista tutti i TimeProfiles
        print("TimeProfiles disponibili:")
        print("-" * 80)
        
        tp_count = 0
        for tp in lr.TimeProfiles:
            tp_count += 1
            tp_name = tp.AttValue("Name")
            
            print("\nTimeProfile #%d: %s" % (tp_count, tp_name))
            
            # Conta i TimeProfileItems
            tpi_count = 0
            has_370 = False
            for tpi in tp.TimeProfileItems:
                tpi_count += 1
                stop_no = tpi.AttValue("StopPointNo")
                if stop_no == 370:
                    has_370 = True
            
            print("  TimeProfileItems: %d" % tpi_count)
            print("  Fermata 370 presente: %s" % ("SI" if has_370 else "NO"))
            
            # Mostra primi e ultimi stop
            if tpi_count > 0:
                print("  Primo stop: %s" % None)
                print("  Ultimo stop: %s" % None)
                
                # Lista tutti gli stop
                print("\n  Tutti gli stop:")
                idx = 0
                for tpi in tp.TimeProfileItems:
                    stop_no = tpi.AttValue("StopPointNo")
                    arr = tpi.AttValue("Arr")
                    dep = tpi.AttValue("Dep")
                    marker = " <--- 370" if stop_no == 370 else ""
                    print("    %2d. Stop %s - Arr:%s Dep:%s%s" % (idx, stop_no, arr, dep, marker))
                    idx += 1
        
        if tp_count == 0:
            print("\nNESSUN TimeProfile trovato!")
        
        print("\n" + "=" * 80)
        print("METODI DISPONIBILI SU TimeProfile")
        print("=" * 80)
        
        if tp_count > 0:
            tp = None
            for time_profile in lr.TimeProfiles:
                tp = time_profile
                break
            
            print("\nMetodi che contengono 'add' o 'insert' o 'create':")
            for attr in dir(tp):
                attr_lower = attr.lower()
                if 'add' in attr_lower or 'insert' in attr_lower or 'create' in attr_lower:
                    print("  - %s" % attr)
            
            print("\nMetodi che contengono 'update' o 'refresh' o 'calc':")
            for attr in dir(tp):
                attr_lower = attr.lower()
                if 'update' in attr_lower or 'refresh' in attr_lower or 'calc' in attr_lower:
                    print("  - %s" % attr)

except Exception as e:
    print("\nERRORE: %s" % str(e))
    import traceback
    traceback.print_exc()
