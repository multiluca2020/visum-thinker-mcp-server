# -*- coding: ascii -*-
"""
Test del metodo SetActive su TimeProfileItems
"""

try:
    print("=" * 80)
    print("TEST METODO SetActive SU TIMEPROFILEITEMS")
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
        # Accedi al TimeProfile
        tp = None
        for time_profile in lr.TimeProfiles:
            tp = time_profile
            break
        
        if not tp:
            print("\nERRORE: TimeProfile non trovato!")
        else:
            print("\nTimeProfile: %s" % tp.AttValue("Name"))
            
            # Trova TimeProfileItem della fermata 370
            print("\n1. Ricerca TimeProfileItem fermata 370...")
            tpi_370 = None
            for tpi in tp.TimeProfileItems:
                stop_no = tpi.AttValue("StopPointNo")
                if int(stop_no) == 370:
                    tpi_370 = tpi
                    print("   OK - Trovato!")
                    break
            
            if not tpi_370:
                print("   ERRORE: TimeProfileItem 370 non trovato!")
            else:
                # Verifica metodo SetActive
                print("\n2. Verifica metodo SetActive...")
                
                if hasattr(tpi_370, 'SetActive'):
                    print("   Metodo SetActive disponibile!")
                    print("")
                    
                    # Prova a chiamarlo
                    print("3. Tentativo chiamata SetActive(True)...")
                    try:
                        result = tpi_370.SetActive(True)
                        print("   OK - SetActive(True) completato")
                        print("   Risultato: %s" % result)
                    except Exception as e:
                        print("   ERRORE: %s" % str(e))
                    
                    # Verifica se esiste un attributo Active o IsActive
                    print("\n4. Verifica attributo Active/IsActive...")
                    for attr in ["Active", "IsActive", "Enabled", "IsEnabled", "Visible", "IsVisible"]:
                        try:
                            value = tpi_370.AttValue(attr)
                            print("   %s = %s" % (attr, value))
                        except:
                            pass
                    
                else:
                    print("   Metodo SetActive NON disponibile su TimeProfileItem!")
                    
                    # Verifica su TimeProfileItems collection
                    print("\n3. Verifica SetActive sulla collection TimeProfileItems...")
                    tpi_collection = tp.TimeProfileItems
                    
                    if hasattr(tpi_collection, 'SetActive'):
                        print("   Metodo SetActive disponibile sulla collection!")
                        print("\n   Questo metodo probabilmente serve per filtrare/selezionare")
                        print("   quali TimeProfileItems considerare, non per attivarli nella GUI.")
                    else:
                        print("   SetActive non disponibile neanche sulla collection")
            
            # Salva dopo il tentativo
            print("\n5. Salvataggio progetto...")
            try:
                Visum.SaveVersion()
                print("   OK - Progetto salvato")
            except Exception as e:
                print("   ERRORE: %s" % str(e))
            
            print("\n" + "=" * 80)
            print("CONCLUSIONE:")
            print("=" * 80)
            print("\nSetActive sulla collection serve per filtrare/selezionare items")
            print("in query e operazioni, NON per attivarli nella GUI.")
            print("\nLa GUI probabilmente non si aggiorna perche':")
            print("1. Mantiene una cache interna separata dal database")
            print("2. Non esiste un metodo API per forzare il refresh")
            print("\nDevi chiudere e riaprire la finestra Time Profile Editor.")

except Exception as e:
    print("\nERRORE GENERALE: %s" % str(e))
    import traceback
    traceback.print_exc()
