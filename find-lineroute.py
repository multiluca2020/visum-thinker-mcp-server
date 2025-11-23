# -*- coding: ascii -*-
"""
Script diagnostico per trovare tutte le linee che contengono un LineRoute specifico
"""

SEARCH_LINEROUTE_NAME = "R17_2"

print("=" * 80)
print("RICERCA LINEROUTE: '%s'" % SEARCH_LINEROUTE_NAME)
print("=" * 80)
print()

found_count = 0

for line in Visum.Net.Lines:
    line_name = line.AttValue("Name")
    
    for lr in line.LineRoutes:
        lr_name = lr.AttValue("Name")
        
        if lr_name == SEARCH_LINEROUTE_NAME:
            found_count += 1
            print("Trovato #%d:" % found_count)
            print("  Line Name:       %s" % line_name)
            print("  LineRoute Name:  %s" % lr_name)
            
            # Mostra anche altri attributi utili
            try:
                line_num = line.AttValue("No")
                print("  Line No:         %s" % line_num)
            except:
                pass
            
            try:
                lr_id = lr.AttValue("ID")
                print("  LineRoute ID:    %s" % lr_id)
            except:
                pass
            
            # Conta TimeProfiles
            tp_count = 0
            for tp in lr.TimeProfiles:
                tp_count += 1
            print("  TimeProfiles:    %d" % tp_count)
            
            # Conta fermate
            stop_count = 0
            for item in lr.LineRouteItems:
                try:
                    if item.AttValue("StopPointNo") > 0:
                        stop_count += 1
                except:
                    pass
            print("  Fermate totali:  %d" % stop_count)
            print()

print("=" * 80)
if found_count == 0:
    print("NESSUN RISULTATO TROVATO")
    print()
    print("Suggerimento: Prova a cercare con nome diverso (case-sensitive)")
    print("Oppure cerca parte del nome:")
    print()
    
    # Mostra tutti i LineRoute che contengono la stringa
    print("LineRoute che contengono '%s' nel nome:" % SEARCH_LINEROUTE_NAME)
    similar_count = 0
    for line in Visum.Net.Lines:
        line_name = line.AttValue("Name")
        for lr in line.LineRoutes:
            lr_name = lr.AttValue("Name")
            if SEARCH_LINEROUTE_NAME.lower() in lr_name.lower():
                similar_count += 1
                print("  - Line: %s, LineRoute: %s" % (line_name, lr_name))
                if similar_count >= 10:
                    print("  ... (primi 10 risultati)")
                    break
        if similar_count >= 10:
            break
else:
    print("TOTALE TROVATI: %d" % found_count)
print("=" * 80)
