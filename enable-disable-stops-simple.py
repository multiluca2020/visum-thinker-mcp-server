# -*- coding: ascii -*-
"""
Script per abilitare/disabilitare fermate in un LineRoute
Versione SEMPLICE: modifica solo IsRoutePoint, senza toccare i TimeProfileItems

FUNZIONALITA:
1. Disabilita fermata: IsRoutePoint=False (TimeProfileItem rimosso automaticamente)
2. Abilita fermata: IsRoutePoint=True (TimeProfileItem creato automaticamente da Visum)

IMPORTANTE: Modifica solo le fermate intermedie (non prima/ultima)
"""

# ============================================================================
# CONFIGURAZIONE
# ============================================================================
TARGET_LINEROUTE_NAME = "R17_2"

# Operazioni da eseguire
# Formato: {StopPointNo: "enable" o "disable"}
OPERATIONS = {
    370: "enable",
    # 328: "disable",
}

# ============================================================================
# FUNZIONI HELPER
# ============================================================================

def get_lr_stop_sequence(lr_items):
    """Ottieni sequenza fermate dal LineRoute"""
    stops = []
    for item in lr_items:
        try:
            stop_point_no = item.AttValue("StopPointNo")
            if stop_point_no and stop_point_no > 0:
                stops.append({
                    'item': item,
                    'stop_point_no': stop_point_no,
                    'is_route': item.AttValue("IsRoutePoint"),
                    'index': item.AttValue("Index")
                })
        except:
            pass
    
    # Ordina per index
    stops.sort(key=lambda x: x['index'])
    return stops


def configure_timeprofile_items(tp, stops, operations):
    """
    FUNZIONE DISABILITATA - Non usata per ora
    
    Configura manualmente i TimeProfileItems con tempi personalizzati.
    Per il futuro, se serve modificare anche i tempi oltre a IsRoutePoint.
    """
    pass
    # Codice commentato per uso futuro:
    # for stop_no, config in operations.items():
    #     # Trova TimeProfileItem
    #     # Configura Arr/Dep/StopTime
    #     pass


# ============================================================================
# MAIN
# ============================================================================

try:
    print("=" * 80)
    print("SCRIPT ABILITAZIONE/DISABILITAZIONE FERMATE - VERSIONE SEMPLICE")
    print("=" * 80)
    print("\nModifica solo IsRoutePoint su LineRouteItems")
    print("TimeProfileItems gestiti automaticamente da Visum\n")
    
    # Trova il LineRoute
    print("Ricerca LineRoute '%s'..." % TARGET_LINEROUTE_NAME)
    
    target_lr = None
    for lr in Visum.Net.LineRoutes:
        if lr.AttValue("Name") == TARGET_LINEROUTE_NAME:
            target_lr = lr
            break
    
    if target_lr is None:
        print("ERRORE: LineRoute '%s' non trovato!" % TARGET_LINEROUTE_NAME)
    else:
        print("OK - LineRoute trovato")
        print("  Name: %s" % target_lr.AttValue("Name"))
        print("  LineName: %s" % target_lr.AttValue("LineName"))
        print("")
        
        # Ottieni sequenza fermate
        lr_items = target_lr.LineRouteItems
        stops = get_lr_stop_sequence(lr_items)
        
        print("Fermate totali: %d" % len(stops))
        print("Fermate abilitate (IsRoutePoint=True): %d" % sum(1 for s in stops if s['is_route']))
        print("")
        print("=" * 80)
        
        # Elabora ogni operazione
        for stop_no, operation in OPERATIONS.items():
            print("\nOperazione: %s fermata %d" % (operation.upper(), stop_no))
            print("-" * 80)
            
            # Trova la fermata nella sequenza
            stop_idx = None
            for i, s in enumerate(stops):
                if s['stop_point_no'] == stop_no:
                    stop_idx = i
                    break
            
            if stop_idx is None:
                print("  ERRORE: Fermata %d non trovata!" % stop_no)
                continue
            
            # Verifica che non sia prima/ultima
            if stop_idx == 0:
                print("  ERRORE: Non puoi modificare la prima fermata!")
                continue
            if stop_idx == len(stops) - 1:
                print("  ERRORE: Non puoi modificare l'ultima fermata!")
                continue
            
            current = stops[stop_idx]
            current_is_route = current['is_route']
            
            print("  Fermata %d - IsRoutePoint attuale: %s" % (stop_no, current_is_route))
            
            if operation == "disable":
                # DISABILITA FERMATA
                if not current_is_route:
                    print("  Fermata gia' disabilitata, skip.")
                    continue
                
                print("  Disabilitazione...")
                
                try:
                    current['item'].SetAttValue("IsRoutePoint", False)
                    print("  OK - IsRoutePoint = False")
                    print("  TimeProfileItem sara' rimosso automaticamente da Visum")
                except Exception as e:
                    print("  ERRORE: %s" % str(e))
                    continue
                
            elif operation == "enable":
                # ABILITA FERMATA
                if current_is_route:
                    print("  Fermata gia' abilitata")
                    print("  Forzo ricreazione (False -> True)...")
                    try:
                        current['item'].SetAttValue("IsRoutePoint", False)
                        print("  Step 1: IsRoutePoint = False")
                    except Exception as e:
                        print("  ERRORE step 1: %s" % str(e))
                        continue
                
                print("  Abilitazione...")
                
                try:
                    current['item'].SetAttValue("IsRoutePoint", True)
                    print("  OK - IsRoutePoint = True")
                    print("  TimeProfileItem sara' creato automaticamente da Visum")
                    print("  con tempi interpolati tra le fermate adiacenti")
                except Exception as e:
                    print("  ERRORE: %s" % str(e))
                    continue
            
            else:
                print("  ERRORE: Operazione '%s' non valida (usa 'enable' o 'disable')" % operation)
                continue
            
            print("  Completato!")
        
        print("\n" + "=" * 80)
        print("OPERAZIONI COMPLETATE!")
        print("=" * 80)
        print("\nModifiche applicate:")
        print("  - IsRoutePoint aggiornato sui LineRouteItems")
        print("  - TimeProfileItems gestiti automaticamente da Visum")
        print("\nPer vedere le modifiche:")
        print("  1. Apri Edit > Time Profiles")
        print("  2. Seleziona LineRoute '%s'" % TARGET_LINEROUTE_NAME)
        print("  3. Le fermate modificate appariranno/scompariranno")
        print("\nNOTA: Se la finestra Time Profile era gia' aperta,")
        print("      chiudila e riaprila per vedere le modifiche.")
        print("=" * 80)

except Exception as e:
    print("\nERRORE GENERALE: %s" % str(e))
    import traceback
    traceback.print_exc()
