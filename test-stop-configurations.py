# -*- coding: utf-8 -*-
"""
Test script per generazione configurazioni fermate
Dimostra l'uso delle funzioni verify_and_get_common_stops() e generate_stop_configurations()

IMPORTANTE: Questo script deve essere eseguito nella Visum Python Console (Ctrl+P)
dove l'oggetto 'Visum' è già disponibile.

Uso:
    exec(open(r"h:\visum-thinker-mcp-server\test-stop-configurations.py").read())
"""

print("""
================================================================================
TEST CONFIGURAZIONI FERMATE
================================================================================

NOTA: Questo script carica automaticamente le funzioni da manage-stops-workflow.py
""")

# Carica le funzioni necessarie da manage-stops-workflow.py
print("Caricamento funzioni...")
exec(open(r"h:\visum-thinker-mcp-server\manage-stops-workflow.py").read())

print("Funzioni caricate: verify_and_get_common_stops, generate_stop_configurations")
print()

# ============================================================================
# ESEMPIO 1: Verifica consistenza e genera configurazioni
# ============================================================================

print("""
ESEMPIO 1: WORKFLOW COMPLETO
============================

Questo esempio:
1. Verifica che tutte le linee in TARGET_LINEROUTES abbiano stesse fermate
2. Se verificato, genera tutte le possibili configurazioni
3. Mostra statistiche sulle configurazioni generate
""")

# Esegui verifica
result = verify_and_get_common_stops(TARGET_LINEROUTES)

if result['valid']:
    print("\n✓ VERIFICA OK - Tutte le linee hanno stesse fermate")
    
    # Genera configurazioni
    configs = generate_stop_configurations(result['stops'])
    
    print("\n" + "=" * 80)
    print("CONFIGURAZIONI GENERATE: %d" % len(configs))
    print("=" * 80)
    
    # Mostra alcune configurazioni specifiche
    print("\nPrime 5 configurazioni:")
    for i in range(min(5, len(configs))):
        c = configs[i]
        print("\nConfig %d:" % c['id'])
        print("  Fermate abilitate: %d" % c['enabled_count'])
        print("  StopNos: %s" % c['enabled_stops'])
    
    print("\n\nUltime 5 configurazioni:")
    for i in range(max(0, len(configs) - 5), len(configs)):
        c = configs[i]
        print("\nConfig %d:" % c['id'])
        print("  Fermate abilitate: %d" % c['enabled_count'])
        print("  StopNos: %s" % c['enabled_stops'])
    
    # Analisi distribuzione
    print("\n" + "=" * 80)
    print("ANALISI DISTRIBUZIONE")
    print("=" * 80)
    
    from collections import Counter
    counts = Counter(c['enabled_count'] for c in configs)
    
    print("\nDistribuzione per numero fermate abilitate:")
    for count in sorted(counts.keys()):
        num_configs = counts[count]
        pct = (num_configs / len(configs)) * 100
        bar = "#" * int(pct / 2)
        print("  %2d fermate: %4d config (%.1f%%) %s" % (count, num_configs, pct, bar))
    
    # Trova configurazioni interessanti
    print("\n" + "=" * 80)
    print("CONFIGURAZIONI INTERESSANTI")
    print("=" * 80)
    
    # Config con esattamente metà fermate abilitate
    total_stops = len(result['stops'])
    half = total_stops // 2
    
    half_configs = [c for c in configs if c['enabled_count'] == half]
    print("\nConfigurazioni con esattamente %d fermate abilitate: %d" % (half, len(half_configs)))
    
    if half_configs:
        print("\nEsempio:")
        c = half_configs[0]
        print("  Config ID: %d" % c['id'])
        print("  StopNos: %s" % c['enabled_stops'])
    
    # Config con solo fermate pari/dispari
    print("\n\nPattern alternati:")
    
    # Alterna on-off-on-off...
    if len(configs) > 1:
        # Pattern: 1,3,5,7... (indici dispari)
        odd_pattern = tuple(i % 2 == 1 for i in range(len(result['stops']) - 2))
        odd_configs = [c for c in configs if c['pattern'] == odd_pattern]
        if odd_configs:
            c = odd_configs[0]
            print("  Pattern dispari (on-off-on...): Config %d, %d fermate" % (c['id'], c['enabled_count']))
        
        # Pattern: 0,2,4,6... (indici pari)
        even_pattern = tuple(i % 2 == 0 for i in range(len(result['stops']) - 2))
        even_configs = [c for c in configs if c['pattern'] == even_pattern]
        if even_configs:
            c = even_configs[0]
            print("  Pattern pari (off-on-off...): Config %d, %d fermate" % (c['id'], c['enabled_count']))
    
else:
    print("\n✗ VERIFICA FALLITA - Fermate non consistenti tra le linee")
    print("\nErrori:")
    for err in result['errors']:
        print("  - %s" % err)
    print("\nImpossibile generare configurazioni.")


# ============================================================================
# ESEMPIO 2: Export configurazioni su file
# ============================================================================

print("\n\n" + "=" * 80)
print("ESEMPIO 2: EXPORT CONFIGURAZIONI")
print("=" * 80)

result = verify_and_get_common_stops(TARGET_LINEROUTES)

if result['valid']:
    configs = generate_stop_configurations(result['stops'])
    
    # Export su CSV
    import csv
    output_file = r"H:\go\trenord_2025\stop_configurations.csv"
    
    print("\nExport configurazioni su: %s" % output_file)
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        
        # Header
        stop_names = [s['name'] for s in result['stops']]
        header = ['ConfigID', 'EnabledCount'] + stop_names
        writer.writerow(header)
        
        # Dati
        for c in configs:
            enabled_set = set(c['enabled_stops'])
            row = [c['id'], c['enabled_count']]
            
            for s in result['stops']:
                row.append(1 if s['no'] in enabled_set else 0)
            
            writer.writerow(row)
    
    print("Export completato: %d righe" % (len(configs) + 1))
    
    # Export su JSON
    import json
    json_file = r"H:\go\trenord_2025\stop_configurations.json"
    
    print("\nExport JSON su: %s" % json_file)
    
    export_data = {
        'reference_line': TARGET_LINEROUTES[0] if TARGET_LINEROUTES else "unknown",
        'total_stops': len(result['stops']),
        'variable_stops': len(result['stops']) - 2,
        'total_configurations': len(configs),
        'stops': result['stops'],
        'configurations': configs
    }
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    print("Export completato")


# ============================================================================
# ESEMPIO 3: Filtra configurazioni per criteri specifici
# ============================================================================

print("\n\n" + "=" * 80)
print("ESEMPIO 3: FILTRAGGIO CONFIGURAZIONI")
print("=" * 80)

result = verify_and_get_common_stops(TARGET_LINEROUTES)

if result['valid']:
    configs = generate_stop_configurations(result['stops'])
    
    # Criterio 1: Solo configurazioni con almeno N fermate abilitate
    min_stops = 5
    filtered = [c for c in configs if c['enabled_count'] >= min_stops]
    print("\nConfigurations con almeno %d fermate: %d" % (min_stops, len(filtered)))
    
    # Criterio 2: Solo configurazioni con numero pari/dispari di fermate
    even_configs = [c for c in configs if c['enabled_count'] % 2 == 0]
    odd_configs = [c for c in configs if c['enabled_count'] % 2 == 1]
    print("Configurazioni con numero pari di fermate: %d" % len(even_configs))
    print("Configurazioni con numero dispari di fermate: %d" % len(odd_configs))
    
    # Criterio 3: Configurazioni con fermate consecutive
    print("\nConfigurazioni con tutte fermate consecutive:")
    consecutive_count = 0
    
    for c in configs:
        # Verifica se gli indici sono consecutivi
        stop_indices = []
        for s in result['stops']:
            if s['no'] in c['enabled_stops']:
                stop_indices.append(s['index'])
        
        stop_indices.sort()
        is_consecutive = all(
            stop_indices[i+1] - stop_indices[i] == 1 
            for i in range(len(stop_indices) - 1)
        )
        
        if is_consecutive and len(stop_indices) > 2:  # Più di solo prima+ultima
            consecutive_count += 1
    
    print("  Totale: %d" % consecutive_count)
    
    # Criterio 4: Sample casuale
    import random
    sample_size = min(10, len(configs))
    sample = random.sample(configs, sample_size)
    
    print("\nSample casuale di %d configurazioni:" % sample_size)
    for c in sample:
        print("  Config %d: %d fermate" % (c['id'], c['enabled_count']))


print("\n\n" + "=" * 80)
print("TEST COMPLETATO")
print("=" * 80)
