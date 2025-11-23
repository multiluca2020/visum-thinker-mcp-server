# -*- coding: utf-8 -*-
"""
Script per estrarre tutte le informazioni di un LineRoute specifico
Da eseguire nella console Python di Visum o tramite win32com

Target: LineRoute R17_2002
Estrae: StopPoints, RoutePoints, profili orari, configurazione fermate
"""

# ============================================================================
# PARTE 1: Setup - Per uso diretto in Visum
# ============================================================================
# Se esegui questo script nella console Python di Visum, 'Visum' è già disponibile
# Altrimenti decommentare le righe seguenti per win32com:
# import win32com.client
# Visum = win32com.client.Dispatch("Visum.Visum.240")
# Visum.LoadVersion(r"C:\path\to\your\project.ver")

# ============================================================================
# PARTE 2: Configurazione
# ============================================================================
TARGET_LINEROUTE_NAME = "R17_2002"

print("=" * 80)
print(f"ESTRAZIONE INFORMAZIONI LINE ROUTE: {TARGET_LINEROUTE_NAME}")
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
        print(f"❌ ERRORE: LineRoute '{TARGET_LINEROUTE_NAME}' non trovato!")
        print("\nLineRoutes disponibili:")
        for lr in line_routes:
            print(f"  - {lr.AttValue('Name')}")
        exit(1)
    
    print(f"✅ LineRoute trovato: {TARGET_LINEROUTE_NAME}")
    print()
    
    # ============================================================================
    # PARTE 4: Informazioni base LineRoute
    # ============================================================================
    print("📋 INFORMAZIONI BASE:")
    print("-" * 80)
    
    # Attributi principali
    lr_attrs = [
        "Name",           # Nome del LineRoute
        "LineName",       # Nome della linea parent
        "DirectionCode",  # Codice direzione (> o <)
        "IsRingLine",     # È una linea circolare?
        "Length",         # Lunghezza totale (km)
        "TravelTime",     # Tempo di percorrenza totale (min)
    ]
    
    for attr in lr_attrs:
        try:
            value = target_lr.AttValue(attr)
            print(f"  {attr:20s}: {value}")
        except Exception as e:
            print(f"  {attr:20s}: ⚠️ Non disponibile ({e})")
    
    print()
    
    # ============================================================================
    # PARTE 5: Route Points (tutti i punti dell'itinerario)
    # ============================================================================
    print("🗺️  ROUTE POINTS (Punti Itinerario):")
    print("-" * 80)
    
    route_points = target_lr.RoutePoints
    print(f"Numero totale di RoutePoints: {route_points.Count}")
    print()
    
    route_points_data = []
    for i, rp in enumerate(route_points, 1):
        try:
            rp_info = {
                "Index": rp.AttValue("Index"),
                "NodeNo": rp.AttValue("NodeNo"),
                "NodeName": rp.AttValue("NodeName") if hasattr(rp, "NodeName") else "N/A",
                "DirectionCode": rp.AttValue("DirectionCode"),
                "IsStopPoint": rp.AttValue("IsStopPoint"),
            }
            route_points_data.append(rp_info)
            
            # Stampa compatta
            is_stop = "🚏 STOP" if rp_info["IsStopPoint"] else "     "
            print(f"  {i:3d}. {is_stop} | Node: {rp_info['NodeNo']:6} | Dir: {rp_info['DirectionCode']} | Name: {rp_info.get('NodeName', 'N/A')}")
        
        except Exception as e:
            print(f"  {i:3d}. ⚠️ Errore lettura RoutePoint: {e}")
    
    print()
    
    # ============================================================================
    # PARTE 6: Stop Points (solo le fermate)
    # ============================================================================
    print("🚏 STOP POINTS (Fermate):")
    print("-" * 80)
    
    stop_points = target_lr.StopPoints
    print(f"Numero totale di StopPoints: {stop_points.Count}")
    print()
    
    stop_points_data = []
    for i, sp in enumerate(stop_points, 1):
        try:
            sp_info = {
                "Index": sp.AttValue("Index"),
                "StopNo": sp.AttValue("StopNo"),
                "StopName": sp.AttValue("StopName") if hasattr(sp, "StopName") else "N/A",
                "StopPointNo": sp.AttValue("StopPointNo"),
                "DirectionCode": sp.AttValue("DirectionCode"),
            }
            stop_points_data.append(sp_info)
            
            print(f"  {i:3d}. Stop: {sp_info['StopNo']:6} | StopPoint: {sp_info['StopPointNo']:6} | Dir: {sp_info['DirectionCode']} | Name: {sp_info.get('StopName', 'N/A')}")
        
        except Exception as e:
            print(f"  {i:3d}. ⚠️ Errore lettura StopPoint: {e}")
    
    print()
    
    # ============================================================================
    # PARTE 7: Line Route Items (sequenza dettagliata con fermate)
    # ============================================================================
    print("📍 LINE ROUTE ITEMS (Sequenza Dettagliata):")
    print("-" * 80)
    
    lr_items = target_lr.LineRouteItems
    print(f"Numero totale di LineRouteItems: {lr_items.Count}")
    print()
    
    print(f"{'Idx':<5} {'Node':<8} {'Stop':<8} {'IsStop':<8} {'Dist[km]':<10} {'Time[min]':<10} {'IsUsed':<8}")
    print("-" * 80)
    
    lr_items_data = []
    for i, item in enumerate(lr_items, 1):
        try:
            item_info = {
                "Index": item.AttValue("Index"),
                "NodeIndex": item.AttValue("NodeIndex"),
                "StopIndex": item.AttValue("StopIndex") if item.AttValue("IsStopPoint") else "-",
                "IsStopPoint": item.AttValue("IsStopPoint"),
                "DistOnLine": item.AttValue("DistOnLine"),
                "TimeOnLine": item.AttValue("TimeOnLine"),
                "IsUsed": item.AttValue("IsUsed") if item.AttValue("IsStopPoint") else "-",
            }
            lr_items_data.append(item_info)
            
            # Formattazione output
            is_stop_mark = "✓" if item_info["IsStopPoint"] else " "
            is_used_mark = "✓" if item_info["IsUsed"] == True else ("✗" if item_info["IsUsed"] == False else "-")
            
            print(f"{item_info['Index']:<5} {item_info['NodeIndex']:<8} {str(item_info['StopIndex']):<8} {is_stop_mark:<8} "
                  f"{item_info['DistOnLine']:<10.3f} {item_info['TimeOnLine']:<10.2f} {is_used_mark:<8}")
        
        except Exception as e:
            print(f"{i:<5} ⚠️ Errore: {e}")
    
    print()
    
    # ============================================================================
    # PARTE 8: Time Profiles (profili orari)
    # ============================================================================
    print("⏰ TIME PROFILES (Profili Orari):")
    print("-" * 80)
    
    time_profiles = target_lr.TimeProfiles
    print(f"Numero totale di TimeProfiles: {time_profiles.Count}")
    print()
    
    if time_profiles.Count > 0:
        for i, tp in enumerate(time_profiles, 1):
            try:
                tp_name = tp.AttValue("Name")
                tp_dep_time = tp.AttValue("Dep")
                tp_arr_time = tp.AttValue("Arr")
                
                print(f"  {i}. TimeProfile: {tp_name}")
                print(f"     Partenza: {tp_dep_time}")
                print(f"     Arrivo:   {tp_arr_time}")
                
                # TimeProfileItems (tempi per ogni fermata)
                tp_items = tp.TimeProfileItems
                print(f"     Items: {tp_items.Count}")
                
                if tp_items.Count > 0:
                    print(f"     {'Idx':<5} {'Arr[s]':<10} {'Dep[s]':<10}")
                    for j, tpi in enumerate(tp_items, 1):
                        arr = tpi.AttValue("Arr")
                        dep = tpi.AttValue("Dep")
                        print(f"     {j:<5} {arr:<10} {dep:<10}")
                
                print()
            
            except Exception as e:
                print(f"  {i}. ⚠️ Errore TimeProfile: {e}")
    else:
        print("  Nessun TimeProfile definito")
    
    print()
    
    # ============================================================================
    # PARTE 9: Riepilogo
    # ============================================================================
    print("=" * 80)
    print("📊 RIEPILOGO:")
    print("-" * 80)
    print(f"  LineRoute:        {TARGET_LINEROUTE_NAME}")
    print(f"  RoutePoints:      {route_points.Count}")
    print(f"  StopPoints:       {stop_points.Count}")
    print(f"  LineRouteItems:   {lr_items.Count}")
    print(f"  TimeProfiles:     {time_profiles.Count}")
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
    # with open(f"lineroute_{TARGET_LINEROUTE_NAME}.json", "w", encoding="utf-8") as f:
    #     json.dump(output_data, f, indent=2, ensure_ascii=False)
    # 
    # print(f"\n✅ Dati esportati in: lineroute_{TARGET_LINEROUTE_NAME}.json")

except Exception as e:
    print(f"\n❌ ERRORE GENERALE: {e}")
    import traceback
    traceback.print_exc()
