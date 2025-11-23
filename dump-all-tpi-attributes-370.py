# -*- coding: ascii -*-
"""
Dump COMPLETO di TUTTI gli attributi del TimeProfileItem della fermata 370
"""

try:
    print("=" * 80)
    print("DUMP COMPLETO ATTRIBUTI TimeProfileItem FERMATA 370")
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
            # Trova il TimeProfileItem della fermata 370
            tpi_370 = None
            for tpi in tp.TimeProfileItems:
                stop_no = tpi.AttValue("StopPointNo")
                if int(stop_no) == 370:
                    tpi_370 = tpi
                    break
            
            if not tpi_370:
                print("\nERRORE: TimeProfileItem 370 non trovato!")
            else:
                print("\nTimeProfileItem della fermata 370 trovato!")
                print("\n" + "=" * 80)
                print("TUTTI GLI ATTRIBUTI DISPONIBILI:")
                print("=" * 80)
                
                # Lista di possibili attributi da verificare
                possible_attrs = [
                    # Tempi base
                    "Arr", "Dep", "StopTime", "PreRunTime", "PostRunTime", "AccumRunTime",
                    # Possibili varianti
                    "Stop", "StopDuration", "DwellTime", "Dwell",
                    # Indici
                    "Index", "StopPointNo", "NodeNo", "No",
                    # Altri
                    "IsActive", "Active", "Enabled", "IsEnabled",
                    "ProfilePoint", "IsProfilePoint",
                    # Varianti maiuscole/minuscole
                    "STOPTIME", "stoptime", "StopTime",
                    "DWELLTIME", "dwelltime", "DwellTime",
                    # Possibili attributi nascosti
                    "Time", "Duration", "Wait", "WaitTime",
                    # Attributi di riferimento
                    "StopPoint", "Stop\\No", "Stop\\Time"
                ]
                
                found_attrs = []
                
                for attr in possible_attrs:
                    try:
                        value = tpi_370.AttValue(attr)
                        found_attrs.append((attr, value))
                        print("  %-30s : %s" % (attr, value))
                    except:
                        pass  # Attributo non esiste
                
                print("\n" + "=" * 80)
                print("CONFRONTO CON ALTRI TimeProfileItems:")
                print("=" * 80)
                
                # Confronta con fermate che hanno StopTime diverso
                print("\nFermata 328 (prima fermata):")
                for tpi in tp.TimeProfileItems:
                    if int(tpi.AttValue("StopPointNo")) == 328:
                        for attr, _ in found_attrs[:6]:  # Primi 6 attributi principali
                            try:
                                value = tpi.AttValue(attr)
                                print("  %-30s : %s" % (attr, value))
                            except:
                                pass
                        break
                
                # Trova una fermata random
                print("\nFermata random (seconda nel TimeProfile):")
                idx = 0
                for tpi in tp.TimeProfileItems:
                    if idx == 1:  # Seconda fermata
                        stop_no = tpi.AttValue("StopPointNo")
                        print("  (Stop %d)" % int(stop_no))
                        for attr, _ in found_attrs[:6]:
                            try:
                                value = tpi.AttValue(attr)
                                print("  %-30s : %s" % (attr, value))
                            except:
                                pass
                        break
                    idx += 1
                
                print("\n" + "=" * 80)
                print("ANALISI:")
                print("=" * 80)
                print("\nSe StopTime = 60 nel database ma GUI mostra 0,")
                print("potrebbero esserci queste cause:")
                print("  1. GUI legge un attributo DIVERSO da StopTime")
                print("  2. GUI ha una cache separata non aggiornata")
                print("  3. Esiste un altro TimeProfile attivo")
                print("  4. Il calcolo StopTime e' dinamico e non persistente")
                
                # Verifica se StopTime e' davvero Dep - Arr
                arr = tpi_370.AttValue("Arr")
                dep = tpi_370.AttValue("Dep")
                stoptime = tpi_370.AttValue("StopTime")
                calc = dep - arr
                
                print("\n" + "=" * 80)
                print("VERIFICA CALCOLO:")
                print("=" * 80)
                print("  Arr:                  %s" % arr)
                print("  Dep:                  %s" % dep)
                print("  StopTime (database):  %s" % stoptime)
                print("  Dep - Arr (calcolo):  %s" % calc)
                
                if abs(stoptime - calc) < 0.01:
                    print("\n  OK: StopTime = Dep - Arr (coerente)")
                else:
                    print("\n  PROBLEMA: StopTime != Dep - Arr (incoerente!)")
                
                # Verifica PreRunTime
                print("\n" + "=" * 80)
                print("VERIFICA PRERUNTIME:")
                print("=" * 80)
                
                # Trova fermata precedente
                prev_tpi = None
                found_370 = False
                for tpi in tp.TimeProfileItems:
                    if found_370:
                        break
                    if int(tpi.AttValue("StopPointNo")) == 370:
                        found_370 = True
                    else:
                        prev_tpi = tpi
                
                if prev_tpi:
                    prev_stop = int(prev_tpi.AttValue("StopPointNo"))
                    prev_dep = prev_tpi.AttValue("Dep")
                    curr_arr = tpi_370.AttValue("Arr")
                    pre_run = tpi_370.AttValue("PreRunTime")
                    calc_pre_run = curr_arr - prev_dep
                    
                    print("  Fermata precedente:       %d" % prev_stop)
                    print("  Dep fermata precedente:   %s" % prev_dep)
                    print("  Arr fermata 370:          %s" % curr_arr)
                    print("  PreRunTime (database):    %s" % pre_run)
                    print("  Calcolo (Arr - Dep prev): %s" % calc_pre_run)
                    
                    if abs(pre_run - calc_pre_run) < 0.01:
                        print("\n  OK: PreRunTime calcolato correttamente")
                    else:
                        print("\n  PROBLEMA: PreRunTime = %s ma dovrebbe essere %s" % (pre_run, calc_pre_run))
                        print("  DIFFERENZA: %s secondi" % abs(pre_run - calc_pre_run))

except Exception as e:
    print("\nERRORE: %s" % str(e))
    import traceback
    traceback.print_exc()
