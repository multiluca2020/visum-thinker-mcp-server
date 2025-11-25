# -*- coding: utf-8 -*-
"""
Script semplificato per test rapido generazione configurazioni

NOTA: Eseguire nella Visum Python Console (Ctrl+P)
Uso: exec(open(r"h:\visum-thinker-mcp-server\quick-test-configs.py").read())
"""

print("=" * 80)
print("TEST RAPIDO GENERAZIONE CONFIGURAZIONI")
print("=" * 80)
print()

# Carica workflow (include tutte le funzioni necessarie)
print("Caricamento manage-stops-workflow.py...")
exec(open(r"h:\visum-thinker-mcp-server\manage-stops-workflow.py").read())
print("OK")
print()

# ============================================================================
# TEST RAPIDO
# ============================================================================

print("Linee target configurate:")
for lr in TARGET_LINEROUTES:
    print("  - %s" % lr)
print()

# Verifica consistenza
print("-" * 80)
print("STEP 1: Verifica consistenza fermate")
print("-" * 80)

result = verify_and_get_common_stops(TARGET_LINEROUTES)

if not result['valid']:
    print("\n✗ ERRORE: Fermate non consistenti!")
    for err in result['errors']:
        print("  - %s" % err)
    print("\nTest terminato.")
else:
    print("\n✓ OK: Tutte le linee hanno stesse fermate")
    
    num_stops = len(result['stops'])
    num_variable = num_stops - 2
    num_configs = 2 ** num_variable
    
    print("\nRiepilogo:")
    print("  Fermate totali:     %d" % num_stops)
    print("  Fermate variabili:  %d" % num_variable)
    print("  Configurazioni:     %d (2^%d)" % (num_configs, num_variable))
    print()
    
    # Genera configurazioni
    print("-" * 80)
    print("STEP 2: Generazione configurazioni")
    print("-" * 80)
    
    configs = generate_stop_configurations(result['stops'])
    
    print("\n✓ Generazione completata: %d configurazioni" % len(configs))
    print()
    
    # Mostra esempi
    print("-" * 80)
    print("ESEMPI CONFIGURAZIONI")
    print("-" * 80)
    
    print("\n1. Config MINIMA (ID=%d) - Solo fermate fisse:" % configs[0]['id'])
    print("   Fermate abilitate: %d" % configs[0]['enabled_count'])
    print("   StopNos: %s" % configs[0]['enabled_stops'])
    
    print("\n2. Config MASSIMA (ID=%d) - Tutte abilitate:" % configs[-1]['id'])
    print("   Fermate abilitate: %d" % configs[-1]['enabled_count'])
    print("   StopNos: %s" % configs[-1]['enabled_stops'])
    
    if len(configs) > 10:
        mid = len(configs) // 2
        print("\n3. Config INTERMEDIA (ID=%d):" % configs[mid]['id'])
        print("   Fermate abilitate: %d" % configs[mid]['enabled_count'])
        print("   StopNos: %s" % configs[mid]['enabled_stops'])
        
        quarter = len(configs) // 4
        print("\n4. Config ESEMPIO (ID=%d):" % configs[quarter]['id'])
        print("   Fermate abilitate: %d" % configs[quarter]['enabled_count'])
        print("   StopNos: %s" % configs[quarter]['enabled_count'])
    
    # Statistiche rapide
    print("\n" + "-" * 80)
    print("STATISTICHE")
    print("-" * 80)
    
    enabled_counts = [c['enabled_count'] for c in configs]
    
    print("\nFermate abilitate:")
    print("  Minimo:  %d" % min(enabled_counts))
    print("  Massimo: %d" % max(enabled_counts))
    print("  Media:   %.1f" % (sum(enabled_counts) / len(enabled_counts)))
    
    # Distribuzione semplificata
    from collections import Counter
    counts = Counter(enabled_counts)
    
    print("\nDistribuzione (top 5):")
    for count, freq in counts.most_common(5):
        pct = (freq / len(configs)) * 100
        print("  %2d fermate: %5d config (%.1f%%)" % (count, freq, pct))
    
    print("\n" + "=" * 80)
    print("TEST COMPLETATO")
    print("=" * 80)
    print("\nVariabile 'configs' contiene tutte le %d configurazioni" % len(configs))
    print("\nEsempi accesso:")
    print("  configs[0]          # Prima configurazione")
    print("  configs[-1]         # Ultima configurazione")
    print("  configs[99]         # Config #100")
    print("  len(configs)        # Numero totale")
    print()
    print("Struttura:")
    print("  config['id']            # ID configurazione (1-based)")
    print("  config['enabled_stops'] # Lista StopNo abilitati")
    print("  config['enabled_count'] # Numero fermate abilitate")
    print()
