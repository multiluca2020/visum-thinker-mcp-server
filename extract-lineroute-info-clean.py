# -*- coding: ascii -*-
"""
Script per estrarre tutte le informazioni di un LineRoute specifico
Da eseguire nella console Python di Visum o tramite win32com

Target: LineRoute R17_2002
Estrae: StopPoints, RoutePoints, profili orari, configurazione fermate
"""

# ============================================================================
# PARTE 1: Setup - Per uso diretto in Visum
# ============================================================================
# Se esegui questo script nella console Python di Visum, 'Visum' e' già disponibile
# Altrimenti decommentare le righe seguenti per win32com:
# import win32com.client
# Visum = win32com.client.Dispatch("Visum.Visum.240")
# Visum.LoadVersion(r"C:\path\to\your\project.ver")

# ============================================================================
# PARTE 2: Configurazione
# ============================================================================
TARGET_LINEROUTE_NAME = "R17_2002"

print("=" * 80)
print("ESTRAZIONE INFORMAZIONI LINE ROUTE: %s" % TARGET_LINEROUTE_NAME)
print("=" * 80)

# ============================================================================
# PARTE 3: Trova il LineRoute target
# ============================================================================
try:
    # Accedi alla collezione LineRoutes
    line_routes = Visum.Net.LineRoutes
    
    # Cerca il LineRoute specifico per nome
    target_lr = None
    for lr in line_routes:
        if lr.AttValue("Name") == TARGET_LINEROUTE_NAME:
            target_lr = lr
            break
    
    if target_lr is None:
        print("ERRORE: LineRoute '%s' non trovato!" % TARGET_LINEROUTE_NAME)
    
    if target_lr is not None:
        print("OK - LineRoute trovato: %s" % TARGET_LINEROUTE_NAME)
        print("")
        
        # ============================================================================
        # PARTE 4: Informazioni base LineRoute
        # ============================================================================
        print("INFORMAZIONI BASE:")
        print("-" * 80)
        
        # Attributi principali
        lr_attrs = [
            "Name",           # Nome del LineRoute
            "LineName",       # Nome della linea parent
            "DirectionCode",  # Codice direzione (> o <)
            "IsRingLine",     # E' una linea circolare?
            "Length",         # Lunghezza totale (km)
            "TravelTime",     # Tempo di percorrenza totale (min)
        ]
        
        for attr in lr_attrs:
            try:
                value = target_lr.AttValue(attr)
                print("  %-20s: %s" % (attr, value))
            except Exception as e:
                print("  %-20s: Non disponibile (%s)" % (attr, e))
        
        print("")
        
        # ============================================================================
        # PARTE 5: Route Points (tutti i punti dell'itinerario)
        # ============================================================================
        print("ROUTE POINTS (Punti Itinerario):")
        print("-" * 80)
        
        route_points = target_lr.RoutePoints
        print("Numero totale di RoutePoints: %d" % route_points.Count)
        print("")
        
        route_points_data = []
        for i, rp in enumerate(route_points, 1):
        try:
            index = rp.AttValue("Index")
            node_no = rp.AttValue("NodeNo")
            direction = rp.AttValue("DirectionCode")
            is_stop = rp.AttValue("IsStopPoint")
            
            rp_info = {
                "Index": index,
                "NodeNo": node_no,
                "DirectionCode": direction,
                "IsStopPoint": is_stop,
            }
            route_points_data.append(rp_info)
            
            # Stampa compatta
            stop_mark = "[STOP]" if is_stop else "      "
            print("  %3d. %s | Node: %6s | Dir: %s" % (i, stop_mark, node_no, direction))
        
        except Exception as e:
            print("  %3d. Errore lettura RoutePoint: %s" % (i, e))
    
    print("")
    
    # ============================================================================
    # PARTE 6: Stop Points (solo le fermate)
    # ============================================================================
    print("STOP POINTS (Fermate):")
    print("-" * 80)
    
    stop_points = target_lr.StopPoints
    print("Numero totale di StopPoints: %d" % stop_points.Count)
    print("")
    
    stop_points_data = []
    for i, sp in enumerate(stop_points, 1):
        try:
            index = sp.AttValue("Index")
            stop_no = sp.AttValue("StopNo")
            stoppoint_no = sp.AttValue("StopPointNo")
            direction = sp.AttValue("DirectionCode")
            
            sp_info = {
                "Index": index,
                "StopNo": stop_no,
                "StopPointNo": stoppoint_no,
                "DirectionCode": direction,
            }
            stop_points_data.append(sp_info)
            
            print("  %3d. Stop: %6s | StopPoint: %6s | Dir: %s" % (i, stop_no, stoppoint_no, direction))
        
        except Exception as e:
            print("  %3d. Errore lettura StopPoint: %s" % (i, e))
    
    print("")
    
    # ============================================================================
    # PARTE 7: Line Route Items (sequenza dettagliata con fermate)
    # ============================================================================
    print("LINE ROUTE ITEMS (Sequenza Dettagliata):")
    print("-" * 80)
    
    lr_items = target_lr.LineRouteItems
    print("Numero totale di LineRouteItems: %d" % lr_items.Count)
    print("")
    
    print("%-5s %-8s %-8s %-8s %-10s %-10s %-8s" % ("Idx", "Node", "Stop", "IsStop", "Dist[km]", "Time[min]", "IsUsed"))
    print("-" * 80)
    
    lr_items_data = []
    for i, item in enumerate(lr_items, 1):
        try:
            index = item.AttValue("Index")
            node_index = item.AttValue("NodeIndex")
            is_stop_point = item.AttValue("IsStopPoint")
            stop_index = item.AttValue("StopIndex") if is_stop_point else "-"
            dist = item.AttValue("DistOnLine")
            time = item.AttValue("TimeOnLine")
            is_used = item.AttValue("IsUsed") if is_stop_point else "-"
            
            item_info = {
                "Index": index,
                "NodeIndex": node_index,
                "StopIndex": stop_index,
                "IsStopPoint": is_stop_point,
                "DistOnLine": dist,
                "TimeOnLine": time,
                "IsUsed": is_used,
            }
            lr_items_data.append(item_info)
            
            # Formattazione output
            is_stop_mark = "YES" if is_stop_point else " "
            is_used_mark = "YES" if is_used == True else ("NO" if is_used == False else "-")
            
            print("%-5s %-8s %-8s %-8s %-10.3f %-10.2f %-8s" % 
                  (index, node_index, str(stop_index), is_stop_mark, dist, time, is_used_mark))
        
        except Exception as e:
            print("%-5s Errore: %s" % (i, e))
    
    print("")
    
    # ============================================================================
    # PARTE 8: Time Profiles (profili orari)
    # ============================================================================
    print("TIME PROFILES (Profili Orari):")
    print("-" * 80)
    
    time_profiles = target_lr.TimeProfiles
    print("Numero totale di TimeProfiles: %d" % time_profiles.Count)
    print("")
    
    if time_profiles.Count > 0:
        for i, tp in enumerate(time_profiles, 1):
            try:
                tp_name = tp.AttValue("Name")
                tp_dep_time = tp.AttValue("Dep")
                tp_arr_time = tp.AttValue("Arr")
                
                print("  %d. TimeProfile: %s" % (i, tp_name))
                print("     Partenza: %s" % tp_dep_time)
                print("     Arrivo:   %s" % tp_arr_time)
                
                # TimeProfileItems (tempi per ogni fermata)
                tp_items = tp.TimeProfileItems
                print("     Items: %d" % tp_items.Count)
                
                if tp_items.Count > 0:
                    print("     %-5s %-10s %-10s" % ("Idx", "Arr[s]", "Dep[s]"))
                    for j, tpi in enumerate(tp_items, 1):
                        arr = tpi.AttValue("Arr")
                        dep = tpi.AttValue("Dep")
                        print("     %-5d %-10s %-10s" % (j, arr, dep))
                
                print("")
            
            except Exception as e:
                print("  %d. Errore TimeProfile: %s" % (i, e))
    else:
        print("  Nessun TimeProfile definito")
    
    print("")
    
    # ============================================================================
    # PARTE 9: Riepilogo
    # ============================================================================
    print("=" * 80)
    print("RIEPILOGO:")
    print("-" * 80)
    print("  LineRoute:        %s" % TARGET_LINEROUTE_NAME)
    print("  RoutePoints:      %d" % route_points.Count)
    print("  StopPoints:       %d" % stop_points.Count)
    print("  LineRouteItems:   %d" % lr_items.Count)
    print("  TimeProfiles:     %d" % time_profiles.Count)
    print("=" * 80)
    
    # ============================================================================
    # PARTE 10: Export opzionale a JSON (decommentare se necessario)
    # ============================================================================
    # import json
    # 
    # output_data = {
    #     "lineroute_name": TARGET_LINEROUTE_NAME,
    #     "route_points": route_points_data,
    #     "stop_points": stop_points_data,
    #     "lineroute_items": lr_items_data,
    # }
    # 
    # with open("lineroute_%s.json" % TARGET_LINEROUTE_NAME, "w") as f:
    #     json.dump(output_data, f, indent=2)
    # 
    # print("\nOK - Dati esportati in: lineroute_%s.json" % TARGET_LINEROUTE_NAME)

except Exception as e:
    print("\nERRORE GENERALE: %s" % e)
    import traceback
    traceback.print_exc()
