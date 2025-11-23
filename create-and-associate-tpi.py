# -*- coding: ascii -*-
"""
Crea TimeProfileItem e associalo allo StopPoint
"""

try:
    print("=" * 80)
    print("CREAZIONE E ASSOCIAZIONE TIMEPROFILEITEM")
    print("=" * 80)
    
    # Trova LineRoute
    print("\n1. Accesso al LineRoute R17_2...")
    lr = None
    for lineroute in Visum.Net.LineRoutes:
        name = lineroute.AttValue("Name")
        if name == "R17_2":
            lr = lineroute
            break
    
    if not lr:
        print("   ERRORE: LineRoute non trovato!")
    else:
        print("   OK")
        
        # Accedi al TimeProfile
        print("\n2. Accesso al TimeProfile...")
        tp = None
        for time_profile in lr.TimeProfiles:
            tp = time_profile
            break
        
        if not tp:
            print("   ERRORE: TimeProfile non trovato!")
        else:
            print("   OK - TimeProfile: %s" % tp.AttValue("Name"))
            
            # Esplora metodi disponibili su TimeProfileItems collection
            print("\n3. Metodi disponibili su TimeProfileItems:")
            print("-" * 80)
            
            tpi_collection = tp.TimeProfileItems
            
            methods = []
            for attr in dir(tpi_collection):
                if not attr.startswith('_'):
                    try:
                        obj = getattr(tpi_collection, attr)
                        if callable(obj):
                            methods.append(attr)
                    except:
                        pass
            
            for method in sorted(methods):
                print("  - %s" % method)
            
            # Prova metodi di creazione
            print("\n4. Tentativo creazione TimeProfileItem:")
            print("-" * 80)
            
            # Metodo 1: AddTimeProfileItem() senza parametri
            print("\n  Metodo 1: AddTimeProfileItem()...")
            try:
                new_tpi = tpi_collection.AddTimeProfileItem()
                print("    OK - TimeProfileItem creato!")
                print("    Type: %s" % type(new_tpi).__name__)
                
                # Cerca attributi per l'associazione
                print("\n  Attributi disponibili sul nuovo TimeProfileItem:")
                for attr in ["StopPointNo", "StopPoint", "Stop", "NodeNo", "Node", 
                            "LineRouteItem", "RouteItem", "Index", "No"]:
                    try:
                        value = new_tpi.AttValue(attr)
                        print("    %-20s : %s" % (attr, value))
                    except:
                        pass
                
                # Prova a impostare StopPointNo
                print("\n  Tentativo impostazione StopPointNo = 328...")
                try:
                    new_tpi.SetAttValue("StopPointNo", 328)
                    print("    OK - StopPointNo impostato")
                except Exception as e:
                    print("    ERRORE: %s" % str(e))
                
                # Verifica se e' stato aggiunto
                print("\n5. Verifica aggiunta al TimeProfile:")
                count = 0
                has_328 = False
                for tpi in tp.TimeProfileItems:
                    count += 1
                    stop_no = tpi.AttValue("StopPointNo")
                    if stop_no == 328:
                        has_328 = True
                
                print("   TimeProfileItems totali: %d" % count)
                print("   Fermata 328 presente: %s" % has_328)
                
            except Exception as e1:
                print("    ERRORE Metodo 1: %s" % str(e1))
                
                # Metodo 2: CreateTimeProfileItem()
                print("\n  Metodo 2: CreateTimeProfileItem()...")
                try:
                    new_tpi = tpi_collection.CreateTimeProfileItem()
                    print("    OK - TimeProfileItem creato!")
                except Exception as e2:
                    print("    ERRORE Metodo 2: %s" % str(e2))
                    
                    # Metodo 3: Add()
                    print("\n  Metodo 3: Add()...")
                    try:
                        new_tpi = tpi_collection.Add()
                        print("    OK - TimeProfileItem creato!")
                    except Exception as e3:
                        print("    ERRORE Metodo 3: %s" % str(e3))
                        print("\n    TUTTI I METODI FALLITI!")

except Exception as e:
    print("\nERRORE GENERALE: %s" % str(e))
    import traceback
    traceback.print_exc()
