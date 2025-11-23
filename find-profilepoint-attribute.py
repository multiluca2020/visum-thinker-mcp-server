# -*- coding: ascii -*-
"""
Trova l'attributo che controlla il checkbox Profile Point nel TimeProfileItem
"""

try:
    print("=" * 80)
    print("RICERCA ATTRIBUTO PROFILE POINT")
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
            print("\nPrima fermata nel TimeProfile:")
            print("-" * 80)
            
            tpi = None
            for item in tp.TimeProfileItems:
                tpi = item
                break
            
            if tpi:
                stop_no = tpi.AttValue("StopPointNo")
                print("StopPointNo: %s" % stop_no)
                print("")
                print("TUTTI GLI ATTRIBUTI DISPONIBILI:")
                print("")
                
                # Lista di attributi da provare
                test_attrs = [
                    "IsProfilePoint", "ProfilePoint", "IsProfile", "Profile",
                    "IsActive", "Active", "IsEnabled", "Enabled",
                    "IsUsed", "Used", "IsSelected", "Selected",
                    "IsVisible", "Visible", "IsValid", "Valid",
                    "IsRoutePoint", "RoutePoint", "IsStop", "Stop",
                    "IsTimed", "Timed", "IsTimePoint", "TimePoint"
                ]
                
                found_attrs = []
                for attr in test_attrs:
                    try:
                        value = tpi.AttValue(attr)
                        found_attrs.append((attr, value, type(value).__name__))
                        print("  %-25s : %-15s [%s]" % (attr, value, type(value).__name__))
                    except:
                        pass
                
                print("\n" + "=" * 80)
                print("ATTRIBUTI TROVATI: %d" % len(found_attrs))
                print("=" * 80)
                
                if found_attrs:
                    print("\nAttributi booleani/numerici che potrebbero essere il 'Profile Point':")
                    for attr, value, vtype in found_attrs:
                        if vtype in ['bool', 'float', 'int'] or value in [0, 1, 0.0, 1.0, True, False]:
                            print("  %-25s = %s" % (attr, value))
                else:
                    print("\nNESSUN ATTRIBUTO TROVATO!")
                    print("Possibilita':")
                    print("1. L'attributo ha un nome diverso")
                    print("2. Il 'Profile Point' e' controllato automaticamente da Visum")
                    print("3. Il checkbox e' solo visuale e non corrisponde a un attributo")
                
                # Prova a listare TUTTI gli attributi usando GetMultiAttValues
                print("\n" + "=" * 80)
                print("TENTATIVO GetAllAttributes:")
                print("=" * 80)
                
                try:
                    # Non esiste GetAllAttributes, proviamo con gli attributi comuni
                    common_attrs = ["Arr", "Dep", "StopTime", "PreRunTime", "PostRunTime", 
                                   "Index", "No", "NodeNo", "StopPointNo"]
                    
                    print("\nAttributi standard del TimeProfileItem:")
                    for attr in common_attrs:
                        try:
                            value = tpi.AttValue(attr)
                            print("  %-25s : %s" % (attr, value))
                        except:
                            pass
                    
                except Exception as e:
                    print("ERRORE: %s" % str(e))

except Exception as e:
    print("\nERRORE GENERALE: %s" % str(e))
    import traceback
    traceback.print_exc()
