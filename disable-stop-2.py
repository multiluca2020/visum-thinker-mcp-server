# -*- coding: utf-8 -*-
"""
Script per disabilitare la fermata numero 2 sulla linea R17_2022:R17_2
Esegui questo script nella console Python di Visum DOPO aver eseguito manage-stops-workflow.py
"""

# Importa funzioni dal workflow
import sys
import os
sys.path.insert(0, r"h:\visum-thinker-mcp-server")

# Carica le funzioni helper
exec(open(r"h:\visum-thinker-mcp-server\manage-stops-workflow.py").read())

print("=" * 80)
print("DISABILITAZIONE FERMATA 2 SU R17_2022:R17_2")
print("=" * 80)
print()

# Trova la LineRoute R17_2
line_name = "R17_2022"
lr_name = "R17_2"

print("Ricerca LineRoute: %s:%s" % (line_name, lr_name))

target_lr = None
for line in Visum.Net.Lines:
    if line.AttValue("Name") == line_name:
        for lr in line.LineRoutes:
            if lr.AttValue("Name") == lr_name:
                target_lr = lr
                break
        break

if not target_lr:
    print("ERRORE: LineRoute non trovato!")
    sys.exit(1)

print("LineRoute trovato!")
print()

# Ottieni TimeProfiles
tp_list = [tp for tp in target_lr.TimeProfiles]
print("TimeProfiles trovati: %d" % len(tp_list))
print()

# Ottieni sequenza fermate
stops = get_lr_stop_sequence(target_lr.LineRouteItems)
print("Fermate totali: %d" % len(stops))
print()

# Mostra tutte le fermate
print("Sequenza fermate:")
for i, s in enumerate(stops):
    stop_no = s['stop']
    
    try:
        stop_point = Visum.Net.StopPoints.ItemByKey(stop_no)
        stop_name = stop_point.AttValue("Name")
    except:
        stop_name = "Stop_%d" % stop_no
    
    status = "ABILITATA" if s['is_route'] else "disabilitata"
    marker = "[%d]" % i
    print("  %s StopNo %d: %s - %s" % (marker, stop_no, stop_name, status))

print()
print("-" * 80)

# Determina quale StopNo corrisponde alla posizione 2 (terza fermata, index 2)
if len(stops) < 3:
    print("ERRORE: Non ci sono abbastanza fermate (servono almeno 3)")
    sys.exit(1)

stop_to_disable = stops[2]  # Index 2 = terza fermata (0, 1, 2)
stop_no = stop_to_disable['stop']

print("Fermata da disabilitare: posizione [2] = StopNo %d" % stop_no)

try:
    stop_point = Visum.Net.StopPoints.ItemByKey(stop_no)
    stop_name = stop_point.AttValue("Name")
    print("Nome: %s" % stop_name)
except:
    print("Nome: Stop_%d" % stop_no)

print()

# Chiedi conferma
risposta = input("Vuoi procedere con la disabilitazione? (s/n): ")
if risposta.lower() != 's':
    print("Operazione annullata")
    sys.exit(0)

print()
print("=" * 80)
print("INIZIO DISABILITAZIONE")
print("=" * 80)
print()

# Disabilita su tutti i TimeProfiles
success_count = 0
error_count = 0

for tp_idx, tp in enumerate(tp_list):
    tp_name = tp.AttValue("Name")
    print("TimeProfile [%d/%d]: %s" % (tp_idx + 1, len(tp_list), tp_name))
    
    # Rileggi sequenza fermate per questo TimeProfile
    stops_fresh = get_lr_stop_sequence(target_lr.LineRouteItems)
    
    # Disabilita la fermata
    success = disabilita_fermata(tp, stops_fresh, stop_no, pre_run_remove=30, post_run_remove=30)
    
    if success:
        success_count += 1
        print("  ✓ Fermata %d disabilitata" % stop_no)
    else:
        error_count += 1
        print("  ✗ Errore disabilitazione fermata %d" % stop_no)
    print()

print("=" * 80)
print("DISABILITAZIONE COMPLETATA")
print("=" * 80)
print("Successi: %d" % success_count)
print("Errori:   %d" % error_count)
print("=" * 80)
