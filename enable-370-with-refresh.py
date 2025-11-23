# -*- coding: ascii -*-
"""
Script per abilitare fermata 370 con tentativo di refresh GUI
"""

OPERATIONS = {
    370: {
        "action": "enable",
        "stop_time": 60,
        "pre_run_add": 0,
        "post_run_add": 0
    }
}

def get_lr_stop_sequence(lr):
    """Estrae la sequenza di fermate dal LineRoute"""
    stops = []
    for item in lr.LineRouteItems:
        try:
            stop_no = item.AttValue("StopPointNo")
            if stop_no:
                stops.append({
                    'stop': int(stop_no),
                    'index': item.AttValue("Index"),
                    'is_route_point': item.AttValue("IsRoutePoint"),
                    'item': item
                })
        except:
            pass
    
    stops.sort(key=lambda x: x['index'])
    return stops

try:
    print("=" * 80)
    print("ABILITAZIONE FERMATA 370 CON TENTATIVO REFRESH GUI")
    print("=" * 80)
    
    # Trova LineRoute
    lr = None
    for lineroute in Visum.Net.LineRoutes:
        name = lineroute.AttValue("Name")
        if name == "R17_2":
            lr = lineroute
            break
    
    if not lr:
        raise Exception("LineRoute R17_2 non trovato")
    
    print("\n[1] LineRoute trovato: %s" % lr.AttValue("Name"))
    
    # Trova TimeProfile
    tp = None
    for time_profile in lr.TimeProfiles:
        tp = time_profile
        break
    
    if not tp:
        raise Exception("TimeProfile non trovato")
    
    print("[2] TimeProfile trovato: %s" % tp.AttValue("Name"))
    
    # Sequenza fermate
    stops_sequence = get_lr_stop_sequence(lr)
    print("[3] Sequenza fermate: %d totali" % len(stops_sequence))
    
    # Elabora operazione per fermata 370
    for stop_no, config in OPERATIONS.items():
        print("\n" + "=" * 80)
        print("OPERAZIONE: %s fermata %d" % (config['action'].upper(), stop_no))
        print("=" * 80)
        
        # Trova stop nella sequenza
        stop_info = None
        stop_pos = None
        for i, s in enumerate(stops_sequence):
            if s['stop'] == stop_no:
                stop_info = s
                stop_pos = i
                break
        
        if not stop_info:
            print("ERRORE: Fermata %d non trovata!" % stop_no)
            continue
        
        if config['action'] == 'enable':
            # Trova prev/next abilitati
            prev_stop = None
            next_stop = None
            
            for i in range(stop_pos - 1, -1, -1):
                if stops_sequence[i]['is_route_point']:
                    prev_stop = stops_sequence[i]
                    break
            
            for i in range(stop_pos + 1, len(stops_sequence)):
                if stops_sequence[i]['is_route_point']:
                    next_stop = stops_sequence[i]
                    break
            
            if not prev_stop or not next_stop:
                print("ERRORE: Fermate adiacenti non trovate!")
                continue
            
            print("\n[A] Fermate adiacenti:")
            print("    Prev: %d" % prev_stop['stop'])
            print("    Curr: %d" % stop_info['stop'])
            print("    Next: %d" % next_stop['stop'])
            
            # Leggi tempi da TimeProfile
            prev_dep = None
            next_arr = None
            
            for tpi in tp.TimeProfileItems:
                s = tpi.AttValue("StopPointNo")
                if s and int(s) == prev_stop['stop']:
                    prev_dep = tpi.AttValue("Dep")
                elif s and int(s) == next_stop['stop']:
                    next_arr = tpi.AttValue("Arr")
            
            if prev_dep is None or next_arr is None:
                print("ERRORE: Tempi prev/next non trovati!")
                continue
            
            print("\n[B] Tempi adiacenti:")
            print("    Prev Dep: %s" % prev_dep)
            print("    Next Arr: %s" % next_arr)
            
            # Calcola tempi
            total_time = next_arr - prev_dep
            stop_time = config['stop_time']
            pre_run = (total_time - stop_time) / 2.0 + config['pre_run_add']
            
            arr = prev_dep + pre_run
            dep = arr + stop_time
            
            print("\n[C] Tempi calcolati:")
            print("    Arr: %s" % arr)
            print("    Dep: %s" % dep)
            print("    StopTime: %s" % stop_time)
            
            # Abilita
            print("\n[D] Abilitazione...")
            current_item = stop_info['item']
            
            # Force recreation
            current_item.SetAttValue("IsRoutePoint", False)
            current_item.SetAttValue("IsRoutePoint", True)
            print("    IsRoutePoint: True")
            
            # Crea TimeProfileItem
            new_tpi = tp.AddTimeProfileItem(current_item)
            print("    TimeProfileItem creato")
            
            # Imposta tempi
            new_tpi.SetAttValue("Arr", arr)
            new_tpi.SetAttValue("Dep", dep)
            print("    Tempi impostati")
            
            # Verifica
            stoptime_read = new_tpi.AttValue("StopTime")
            print("\n[E] Verifica database:")
            print("    StopTime letto: %s" % stoptime_read)
            
            if abs(stoptime_read - stop_time) < 0.01:
                print("    OK: Database aggiornato correttamente!")
            else:
                print("    PROBLEMA: StopTime = %s (atteso %s)" % (stoptime_read, stop_time))
    
    print("\n" + "=" * 80)
    print("TENTATIVO REFRESH GUI")
    print("=" * 80)
    
    # Tenta vari metodi di refresh
    try:
        print("\n[1] Tentativo UpdateDisplay()...")
        Visum.Graphics.UpdateDisplay()
        print("    OK")
    except Exception as e:
        print("    Non disponibile: %s" % str(e))
    
    try:
        print("\n[2] Tentativo Redraw()...")
        Visum.Graphics.Redraw()
        print("    OK")
    except Exception as e:
        print("    Non disponibile: %s" % str(e))
    
    try:
        print("\n[3] Tentativo Refresh su LineRoute...")
        lr.Refresh()
        print("    OK")
    except Exception as e:
        print("    Non disponibile: %s" % str(e))
    
    try:
        print("\n[4] Tentativo Refresh su TimeProfile...")
        tp.Refresh()
        print("    OK")
    except Exception as e:
        print("    Non disponibile: %s" % str(e))
    
    print("\n" + "=" * 80)
    print("OPERAZIONE COMPLETATA")
    print("=" * 80)
    print("\n>>> CHIUDI la finestra Time Profile Editor (se aperta)")
    print(">>> RIAPRI: Edit > Time Profiles")
    print(">>> Seleziona R17_2, TimeProfile 'R17'")
    print(">>> Verifica fermata 370")
    print("\nSe anche dopo chiusura/riapertura non vedi la fermata 370,")
    print("allora e' necessario salvare e riaprire il progetto completo.")

except Exception as e:
    print("\nERRORE: %s" % str(e))
    import traceback
    traceback.print_exc()
