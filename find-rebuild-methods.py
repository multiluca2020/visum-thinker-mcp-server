# -*- coding: ascii -*-
"""
Cerca metodi per rigenerare/rebuild TimeProfile
"""

try:
    print("=" * 80)
    print("RICERCA METODI REBUILD/GENERATE TIMEPROFILE")
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
            
            # Lista TUTTI i metodi
            all_methods = [attr for attr in dir(tp) if not attr.startswith('_')]
            
            for method in sorted(all_methods):
                # Filtra solo i metodi interessanti
                method_lower = method.lower()
                if any(keyword in method_lower for keyword in [
                    'add', 'create', 'generate', 'build', 'rebuild', 
                    'init', 'update', 'calc', 'set', 'remove', 'delete',
                    'insert', 'item', 'profile'
                ]):
                    try:
                        obj = getattr(tp, method)
                        obj_type = type(obj).__name__
                        print("  %-40s [%s]" % (method, obj_type))
                    except:
                        print("  %-40s [ERROR]" % method)
            
            # Prova metodi specifici
            print("\n" + "=" * 80)
            print("TENTATIVI DI RIGENERAZIONE:")
            print("=" * 80)
            
            # Tentativo 1: Chiamare AddTimeProfileItem con ogni LineRouteItem
            print("\n1. Tentativo rigenerazione completa TimeProfile...")
            try:
                # Prima conta quanti sono abilitati
                enabled_count = 0
                for item in lr.LineRouteItems:
                    stop_no = item.AttValue("StopPointNo")
                    if stop_no and stop_no > 0:
                        is_route = item.AttValue("IsRoutePoint")
                        if is_route == 1.0:
                            enabled_count += 1
                
                print("   Fermate con IsRoutePoint=True: %d" % enabled_count)
                
                # Conta quanti TimeProfileItems ci sono
                tpi_count = 0
                for tpi in tp.TimeProfileItems:
                    tpi_count += 1
                
                print("   TimeProfileItems esistenti: %d" % tpi_count)
                
                if enabled_count != tpi_count:
                    print("   MISMATCH! Il TimeProfile non e' sincronizzato con LineRoute!")
                    print("   Questo suggerisce che le modifiche via API non sono permanenti.")
                else:
                    print("   OK - Sincronizzati")
                    
            except Exception as e:
                print("   ERRORE: %s" % str(e))
            
            # Tentativo 2: Verifica se c'è un metodo per forzare il sync
            print("\n2. Ricerca metodi 'Synchronize' o 'Sync'...")
            sync_methods = [attr for attr in dir(tp) if 'sync' in attr.lower()]
            if sync_methods:
                for method in sync_methods:
                    print("   Trovato: %s" % method)
                    try:
                        func = getattr(tp, method)
                        if callable(func):
                            print("   Tentativo chiamata...")
                            func()
                            print("   OK")
                    except Exception as e:
                        print("   ERRORE: %s" % str(e))
            else:
                print("   Nessun metodo Sync trovato")
    
    print("\n" + "=" * 80)
    print("CONCLUSIONE:")
    print("=" * 80)
    print("Se i TimeProfileItems rimangono sempre 14, significa che:")
    print("1. AddTimeProfileItem() non funziona correttamente via API")
    print("2. Le modifiche vengono scartate quando l'interfaccia fa refresh")
    print("3. Potrebbe essere necessario modificare manualmente dall'interfaccia")
    print("=" * 80)

except Exception as e:
    print("\nERRORE: %s" % str(e))
    import traceback
    traceback.print_exc()
