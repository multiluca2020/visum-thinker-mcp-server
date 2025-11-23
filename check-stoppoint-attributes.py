# -*- coding: ascii -*-
"""
Verifica attributi StopPoint associati ai LineRouteItems
La GUI potrebbe leggere lo StopTime dal StopPoint, non dal TimeProfileItem!
"""

try:
    print("=" * 80)
    print("VERIFICA STOPPOINT ATTRIBUTES (fonte GUI?)")
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
        print("\nAnalisi StopPoints per fermate 328, 301, 370...")
        print("")
        
        # Cerca i LineRouteItems di interesse
        target_stops = [328, 301, 370]
        
        for lri in lr.LineRouteItems:
            try:
                stop_no = lri.AttValue("StopPointNo")
                if stop_no and int(stop_no) in target_stops:
                    is_route_point = lri.AttValue("IsRoutePoint")
                    
                    print("\n" + "=" * 80)
                    print("STOP %d (IsRoutePoint=%s):" % (int(stop_no), is_route_point))
                    print("=" * 80)
                    
                    # Prova ad accedere allo StopPoint
                    try:
                        stop_point = lri.StopPoint
                        if stop_point:
                            print("\nStopPoint object found!")
                            
                            # Lista attributi comuni degli StopPoints
                            stop_attrs = [
                                "No", "Code", "Name", 
                                "StopTime", "DwellTime", "Time", "Duration",
                                "STOPTIME", "stoptime"
                            ]
                            
                            print("\nStopPoint attributes:")
                            for attr in stop_attrs:
                                try:
                                    value = stop_point.AttValue(attr)
                                    print("  %-20s : %s" % (attr, value))
                                except:
                                    pass
                            
                            # Prova anche attributi tramite LineRouteItem
                            print("\nLineRouteItem -> StopPoint attributes:")
                            lri_stop_attrs = [
                                "StopPoint\\StopTime",
                                "StopPoint\\DwellTime",
                                "StopPoint\\Time",
                                "StopPoint\\Duration",
                                "Stop\\StopTime",
                                "Stop\\Time"
                            ]
                            
                            for attr in lri_stop_attrs:
                                try:
                                    value = lri.AttValue(attr)
                                    print("  %-30s : %s" % (attr, value))
                                except:
                                    pass
                        else:
                            print("\nStopPoint object is None")
                    except Exception as e:
                        print("\nNessun StopPoint accessibile: %s" % str(e))
                    
                    # Verifica anche LineRouteItem stesso
                    print("\nLineRouteItem direct attributes:")
                    lri_attrs = [
                        "StopPointNo", "IsRoutePoint", "Index", "DirectionCode",
                        "StopTime", "DwellTime", "Arr", "Dep"
                    ]
                    
                    for attr in lri_attrs:
                        try:
                            value = lri.AttValue(attr)
                            print("  %-20s : %s" % (attr, value))
                        except:
                            pass
            
            except:
                pass  # Skip non-stop items
        
        print("\n" + "=" * 80)
        print("CONCLUSIONE:")
        print("=" * 80)
        print("\nSe troviamo attributi StopTime sugli StopPoints o LineRouteItems")
        print("diversi da quelli sui TimeProfileItems, allora la GUI")
        print("legge da quella fonte invece che dal TimeProfile!")

except Exception as e:
    print("\nERRORE: %s" % str(e))
    import traceback
    traceback.print_exc()
