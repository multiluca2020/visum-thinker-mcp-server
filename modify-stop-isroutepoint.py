# -*- coding: ascii -*-
"""
Script per modificare IsRoutePoint delle fermate in un LineRoute
IsRoutePoint = True  -> Fermata ABILITATA
IsRoutePoint = False -> Fermata DISABILITATA
"""

# ============================================================================
# CONFIGURAZIONE
# ============================================================================
TARGET_LINEROUTE_NAME = "R17_2"

# Specifica quali fermate modificare (per StopPointNo)
# Esempio: {329: True, 328: False, 204: True}
# True = abilita, False = disabilita
STOPS_TO_MODIFY = {
    329: True,   # Abilita fermata 329
    328: False,  # Disabilita fermata 328
    204: True,   # Abilita fermata 204
}

# ============================================================================
# SCRIPT
# ============================================================================
print("=" * 80)
print("MODIFICA FERMATE LINE ROUTE: %s" % TARGET_LINEROUTE_NAME)
print("=" * 80)

try:
    # Trova il LineRoute
    line_routes = Visum.Net.LineRoutes
    target_lr = None
    
    for lr in line_routes:
        if lr.AttValue("Name") == TARGET_LINEROUTE_NAME:
            target_lr = lr
            break
    
    if target_lr is None:
        print("ERRORE: LineRoute non trovato!")
    else:
        print("LineRoute trovato: %s" % TARGET_LINEROUTE_NAME)
        print("Fermate da modificare: %d\n" % len(STOPS_TO_MODIFY))
        
        # Itera sui LineRouteItems
        lr_items = target_lr.LineRouteItems
        modifications = 0
        
        print("%-5s %-15s %-15s %-20s %-20s" % 
              ("Idx", "StopPointNo", "Azione", "IsRoutePoint Prima", "IsRoutePoint Dopo"))
        print("-" * 80)
        
        for item in lr_items:
            try:
                # Verifica se e' una fermata
                stop_point_no = item.AttValue("StopPointNo")
                if not stop_point_no or stop_point_no <= 0:
                    continue
                
                # Verifica se questa fermata deve essere modificata
                if stop_point_no in STOPS_TO_MODIFY:
                    index = item.AttValue("Index")
                    old_value = item.AttValue("IsRoutePoint")
                    new_value = STOPS_TO_MODIFY[stop_point_no]
                    
                    # Modifica IsRoutePoint
                    item.SetAttValue("IsRoutePoint", new_value)
                    
                    # Verifica la modifica
                    current_value = item.AttValue("IsRoutePoint")
                    
                    action = "ABILITA" if new_value else "DISABILITA"
                    old_str = "YES" if old_value else "NO"
                    new_str = "YES" if current_value else "NO"
                    
                    print("%-5d %-15.0f %-15s %-20s %-20s" % 
                          (index, stop_point_no, action, old_str, new_str))
                    
                    modifications += 1
            
            except Exception as e:
                print("Errore su item: %s" % str(e))
        
        print("\n" + "=" * 80)
        print("COMPLETATO:")
        print("  Fermate modificate: %d" % modifications)
        print("  IMPORTANTE: Salva il progetto per rendere permanenti le modifiche!")
        print("=" * 80)

except Exception as e:
    print("ERRORE: %s" % str(e))
    import traceback
    traceback.print_exc()
