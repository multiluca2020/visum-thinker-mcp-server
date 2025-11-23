# -*- coding: ascii -*-
"""
Trova tutti gli attributi disponibili su TimeProfileItem
"""

try:
    # Trova il LineRoute
    print("Ricerca LineRoute R17_2...")
    lr = None
    for lineroute in Visum.Net.LineRoutes:
        name = lineroute.AttValue("Name")
        if name == "R17_2":
            lr = lineroute
            break
    
    if lr is None:
        print("ERRORE: LineRoute R17_2 non trovato!")
    else:
        print("OK - LineRoute trovato")
        
        # Prendi il primo TimeProfile
        tp = None
        for time_profile in lr.TimeProfiles:
            tp = time_profile
            break
        
        if tp is None:
            print("ERRORE: Nessun TimeProfile trovato!")
        else:
            print("OK - TimeProfile trovato: %s" % tp.AttValue("Name"))
            
            # Prendi il primo TimeProfileItem
            tpi = None
            for item in tp.TimeProfileItems:
                tpi = item
                break
            
            if tpi is None:
                print("ERRORE: Nessun TimeProfileItem trovato!")
            else:
                print("\n" + "=" * 80)
                print("ATTRIBUTI DISPONIBILI SU TIMEPROFILEITEM")
                print("=" * 80)
                
                # Lista di attributi comuni da provare
                test_attrs = [
                    "Arr", "Dep", "StopTime", "PreRunTime", "PostRunTime",
                    "IsProfilePoint", "IsRoutePoint", "IsActive", "IsUsed",
                    "Active", "Used", "Enabled", "ProfilePoint", "RoutePoint",
                    "Index", "No", "NodeNo", "StopPointNo"
                ]
                
                for attr in test_attrs:
                    try:
                        value = tpi.AttValue(attr)
                        print("  %-20s : %s" % (attr, value))
                    except Exception as e:
                        pass  # Attributo non esiste
                
                print("=" * 80)

except Exception as e:
    print("ERRORE: %s" % str(e))
    import traceback
    traceback.print_exc()
