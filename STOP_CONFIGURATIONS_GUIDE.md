# GENERAZIONE CONFIGURAZIONI FERMATE

## Overview

Questo modulo fornisce funzionalità per:
1. **Verificare consistenza** delle fermate tra multiple LineRoutes
2. **Generare tutte le combinazioni** possibili di fermate abilitate/disabilitate
3. **Testare configurazioni** diverse per analisi scenari

## Use Case

Quando si vogliono testare **tutti i possibili scenari** di fermate abilitate/disabilitate su un set di linee per:
- Analisi tempi di percorrenza
- Ottimizzazione servizio
- Testing assegnazioni
- Validazione modelli

## Funzioni Principali

### 1. `verify_and_get_common_stops(lineroutes)`

Verifica che tutte le linee abbiano le stesse fermate nella stessa sequenza.

**Parametri:**
- `lineroutes`: Lista di stringhe formato `"LineName:LineRouteName"`

**Returns:**
```python
{
    'valid': bool,           # True se tutte hanno stesse fermate
    'stops': list,           # Lista fermate comuni (se valid=True)
    'errors': list           # Lista errori (se valid=False)
}
```

**Struttura `stops`:**
```python
[
    {
        'no': 12345,         # StopPoint number
        'name': 'Milano',    # Nome fermata
        'index': 0           # Posizione nella sequenza
    },
    # ...
]
```

**Output Console:**
```
================================================================================
VERIFICA CONSISTENZA FERMATE
================================================================================

Processando: R17_2022:R17_2
  Fermate: 12
    - 10001: Milano Centrale
    - 10002: Milano Lambrate
    - 10003: Monza
    ... (altre 9)
  -> Usato come riferimento

Processando: R17_2022:R17_3
  Fermate: 12
    - 10001: Milano Centrale
    - 10002: Milano Lambrate
    - 10003: Monza
    ... (altre 9)

Confronto R17_2022:R17_3:
  OK: Sequenza identica

================================================================================
VERIFICA COMPLETATA: TUTTE LE LINEE HANNO STESSE FERMATE
================================================================================

Fermate comuni: 12
  [FISSA] 1. Milano Centrale (StopNo: 10001)
  [VAR]  2. Milano Lambrate (StopNo: 10002)
  [VAR]  3. Monza (StopNo: 10003)
  ...
  [FISSA] 12. Bergamo (StopNo: 10012)
```

### 2. `generate_stop_configurations(stops)`

Genera **tutte** le possibili combinazioni di fermate abilitate/disabilitate.

**Vincoli:**
- Prima fermata: **SEMPRE abilitata**
- Ultima fermata: **SEMPRE abilitata**
- Fermate intermedie: **Variabili** (tutte le combinazioni)

**Parametri:**
- `stops`: Lista fermate da `verify_and_get_common_stops()`

**Returns:**
```python
[
    {
        'id': 1,                              # ID configurazione (1-based)
        'enabled_stops': [10001, 10012],      # Lista StopNo abilitati
        'enabled_count': 2,                   # Numero fermate abilitate
        'pattern': (False, False, ...)        # Pattern bool per debug
    },
    # ...
]
```

**Formula Configurazioni:**
```
Numero configurazioni = 2^n
dove n = numero fermate intermedie (totali - 2)
```

**Esempi:**
- 5 fermate totali → 3 intermedie → 2³ = **8 configurazioni**
- 10 fermate totali → 8 intermedie → 2⁸ = **256 configurazioni**
- 15 fermate totali → 13 intermedie → 2¹³ = **8192 configurazioni**

**Output Console:**
```
================================================================================
GENERAZIONE CONFIGURAZIONI FERMATE
================================================================================

Fermate fisse (sempre abilitate):
  - Prima: 10001 (Milano Centrale)
  - Ultima: 10012 (Bergamo)

Fermate variabili: 10
  1. Milano Lambrate (StopNo: 10002)
  2. Monza (StopNo: 10003)
  ...
  10. Bergamo Ospedale (StopNo: 10011)

Numero totale configurazioni: 1024 (2^10)

Generazione in corso...
Generazione completata: 1024 configurazioni

Esempi configurazioni:

Config 1 (minimo - solo fermate fisse):
  Fermate abilitate: 2
  StopNos: [10001, 10012]

Config 1024 (massimo - tutte abilitate):
  Fermate abilitate: 12
  StopNos: [10001, 10002, 10003, ..., 10012]

Config 512 (intermedia):
  Fermate abilitate: 7
  StopNos: [10001, 10002, 10005, 10006, 10009, 10010, 10012]

Statistiche:
  Min fermate abilitate: 2
  Max fermate abilitate: 12
  Media: 7.0
```

## Workflow Completo

### Step 1: Verifica Consistenza

```python
# In Visum Python Console

# Definisci linee da verificare
lineroutes = [
    "R17_2022:R17_2",
    "R17_2022:R17_3",
    "R17_2022:R17_4",
    "RE7_2022:RE_7"
]

# Verifica
result = verify_and_get_common_stops(lineroutes)

if not result['valid']:
    print("ERRORE: Fermate non consistenti!")
    for err in result['errors']:
        print("  - %s" % err)
    # STOP - Non continuare
else:
    print("OK: Tutte le linee hanno %d fermate comuni" % len(result['stops']))
```

### Step 2: Genera Configurazioni

```python
# Genera tutte le configurazioni
configs = generate_stop_configurations(result['stops'])

print("Configurazioni generate: %d" % len(configs))

# Mostra prima e ultima
print("\nConfig minima (solo prima+ultima):")
print("  ID: %d" % configs[0]['id'])
print("  Fermate: %s" % configs[0]['enabled_stops'])

print("\nConfig massima (tutte abilitate):")
print("  ID: %d" % configs[-1]['id'])
print("  Fermate: %s" % configs[-1]['enabled_stops'])
```

### Step 3: Applica Configurazione Specifica

```python
# Scegli una configurazione da testare
config = configs[100]  # Esempio: configurazione #100

print("\nApplicando configurazione %d..." % config['id'])
print("Fermate abilitate: %d" % config['enabled_count'])
print("StopNos: %s" % config['enabled_stops'])

# TODO: Applicare la configurazione alle LineRoutes
# (disabilitare tutte le fermate non in config['enabled_stops'])
```

## Esempi Pratici

### Esempio 1: Export Tutte le Configurazioni

```python
import csv

# Verifica e genera
result = verify_and_get_common_stops(TARGET_LINEROUTES)
configs = generate_stop_configurations(result['stops'])

# Export CSV
with open('configurations.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f, delimiter=';')
    
    # Header: ConfigID, EnabledCount, Stop1, Stop2, ...
    stop_names = [s['name'] for s in result['stops']]
    writer.writerow(['ConfigID', 'EnabledCount'] + stop_names)
    
    # Righe: per ogni config, 1/0 per ogni fermata
    for c in configs:
        enabled_set = set(c['enabled_stops'])
        row = [c['id'], c['enabled_count']]
        
        for s in result['stops']:
            row.append(1 if s['no'] in enabled_set else 0)
        
        writer.writerow(row)

print("Export completato: %d configurazioni" % len(configs))
```

**Output CSV:**
```csv
ConfigID;EnabledCount;Milano Centrale;Milano Lambrate;Monza;...;Bergamo
1;2;1;0;0;...;1
2;3;1;1;0;...;1
3;3;1;0;1;...;1
...
1024;12;1;1;1;...;1
```

### Esempio 2: Filtra Configurazioni per Criteri

```python
# Solo configurazioni con almeno 5 fermate
min_stops = 5
filtered = [c for c in configs if c['enabled_count'] >= min_stops]
print("Configurazioni con >= %d fermate: %d" % (min_stops, len(filtered)))

# Solo configurazioni con numero pari di fermate
even_configs = [c for c in configs if c['enabled_count'] % 2 == 0]
print("Configurazioni con numero pari: %d" % len(even_configs))

# Configurazioni con fermate alternate (on-off-on-off...)
alternating = []
for c in configs:
    pattern = c['pattern']
    is_alternating = all(
        pattern[i] != pattern[i+1] 
        for i in range(len(pattern) - 1)
    )
    if is_alternating:
        alternating.append(c)

print("Configurazioni alternate: %d" % len(alternating))
```

### Esempio 3: Sample Casuale per Testing

```python
import random

# Seleziona N configurazioni casuali
sample_size = 10
sample = random.sample(configs, sample_size)

print("Testing %d configurazioni casuali:" % sample_size)
for c in sample:
    print("\nConfig %d: %d fermate" % (c['id'], c['enabled_count']))
    print("  StopNos: %s" % c['enabled_stops'])
    
    # TODO: Applica configurazione e esegui test
    # apply_configuration(c['enabled_stops'])
    # run_assignment()
    # collect_results()
```

### Esempio 4: Analisi Distribuzione

```python
from collections import Counter

# Conta quante configurazioni per ogni numero di fermate
counts = Counter(c['enabled_count'] for c in configs)

print("\nDistribuzione configurazioni per numero fermate:")
print("\nFermate | Configs | Percentuale")
print("--------|---------|------------")

for num_stops in sorted(counts.keys()):
    num_configs = counts[num_stops]
    pct = (num_configs / len(configs)) * 100
    bar = "#" * int(pct / 2)
    print("%7d | %7d | %5.1f%% %s" % (num_stops, num_configs, pct, bar))
```

**Output:**
```
Fermate | Configs | Percentuale
--------|---------|------------
      2 |       1 |   0.1% 
      3 |      10 |   1.0% #
      4 |      45 |   4.4% ##
      5 |     120 |  11.7% ######
      6 |     210 |  20.5% ##########
      7 |     252 |  24.6% ############
      8 |     210 |  20.5% ##########
      9 |     120 |  11.7% ######
     10 |      45 |   4.4% ##
     11 |      10 |   1.0% #
     12 |       1 |   0.1% 
```

## Performance

### Complessità

| Fermate Totali | Fermate Variabili | Configurazioni | Tempo Generazione | Memoria |
|----------------|-------------------|----------------|-------------------|---------|
| 5 | 3 | 8 | < 0.1 sec | < 1 KB |
| 10 | 8 | 256 | < 0.1 sec | 50 KB |
| 15 | 13 | 8,192 | ~0.5 sec | 1.5 MB |
| 20 | 18 | 262,144 | ~15 sec | 50 MB |
| 25 | 23 | 8,388,608 | ~10 min | 1.5 GB |

**Raccomandazioni:**
- ✅ **< 15 fermate:** Genera tutte le configurazioni
- ⚠️ **15-20 fermate:** Usa sample o filtri
- ❌ **> 20 fermate:** Troppo grande, usa approccio diverso

### Ottimizzazioni

Per progetti con molte fermate:

```python
# Opzione 1: Sample casuale
import random
max_configs = 1000
if len(configs) > max_configs:
    configs = random.sample(configs, max_configs)
    print("Sample ridotto a %d configurazioni" % max_configs)

# Opzione 2: Filtra a priori
# Solo configurazioni con 40-60% fermate abilitate
total_stops = len(result['stops'])
min_enabled = int(total_stops * 0.4)
max_enabled = int(total_stops * 0.6)

configs_filtered = [
    c for c in configs 
    if min_enabled <= c['enabled_count'] <= max_enabled
]

# Opzione 3: Generazione lazy (itertools)
from itertools import islice, product

def generate_configs_lazy(stops, limit=None):
    """Generator per configurazioni (non carica tutto in memoria)"""
    first_stop = stops[0]['no']
    last_stop = stops[-1]['no']
    variable_stops = [s['no'] for s in stops[1:-1]]
    
    combos = product([False, True], repeat=len(variable_stops))
    if limit:
        combos = islice(combos, limit)
    
    for i, combo in enumerate(combos):
        enabled = [first_stop]
        for var_stop, is_enabled in zip(variable_stops, combo):
            if is_enabled:
                enabled.append(var_stop)
        enabled.append(last_stop)
        
        yield {
            'id': i + 1,
            'enabled_stops': enabled,
            'enabled_count': len(enabled)
        }

# Usa solo prime 1000 configurazioni
for config in generate_configs_lazy(result['stops'], limit=1000):
    # Process config...
    pass
```

## Integrazione con Workflow

### Task Type: `test_all_configurations`

Possibile estensione del workflow per testare automaticamente tutte le configurazioni:

```python
{
    "id": 4,
    "name": "Test tutte configurazioni fermate",
    "action": "test_all_configurations",
    "params": {
        "max_configs": 100,        # Limite massimo da testare
        "random_sample": True,     # Se True, sample casuale
        "run_assignment": True,    # Esegui assegnazione per ogni config
        "export_results": True,    # Export risultati in CSV
        "output_dir": r"H:\results\configs"
    }
}
```

**Pseudocodice implementazione:**
```python
def task_test_all_configurations(params):
    # 1. Verifica consistenza
    result = verify_and_get_common_stops(TARGET_LINEROUTES)
    
    # 2. Genera configurazioni
    configs = generate_stop_configurations(result['stops'])
    
    # 3. Sample se necessario
    max_configs = params.get('max_configs', len(configs))
    if len(configs) > max_configs:
        if params.get('random_sample'):
            configs = random.sample(configs, max_configs)
        else:
            configs = configs[:max_configs]
    
    # 4. Test ogni configurazione
    results = []
    for config in configs:
        # Applica configurazione
        apply_configuration_to_lineroutes(
            TARGET_LINEROUTES, 
            config['enabled_stops']
        )
        
        # Esegui assegnazione
        if params.get('run_assignment'):
            execute_procedure_sequence()
        
        # Raccogli metriche
        metrics = collect_network_metrics()
        
        results.append({
            'config_id': config['id'],
            'enabled_count': config['enabled_count'],
            'metrics': metrics
        })
    
    # 5. Export risultati
    if params.get('export_results'):
        export_config_results(results, params.get('output_dir'))
    
    return results
```

## Validazione

### Verifiche Automatiche

La funzione `verify_and_get_common_stops()` verifica:

1. **Esistenza LineRoutes:** Tutti gli elementi in `TARGET_LINEROUTES` esistono
2. **Stesso numero fermate:** Tutte le LineRoutes hanno stesso numero di fermate
3. **Stessa sequenza StopNo:** StopNo identici nella stessa posizione
4. **Stessi nomi:** Nomi fermate identici (opzionale, solo warning)

### Errori Comuni

| Errore | Causa | Soluzione |
|--------|-------|-----------|
| "LineRoute non trovato" | Nome errato in TARGET_LINEROUTES | Verifica nome esatto in Visum |
| "ha N fermate, riferimento ha M" | Numero fermate diverso | Usare solo LineRoutes con stessa struttura |
| "Pos X: StopNo Y vs Z" | Sequenza fermate diversa | Controllare percorsi in Visum |
| "Troppo elevato configurazioni" | > 20 fermate variabili | Usa sample o filtri |

## Testing

### Test Script

Esegui `test-stop-configurations.py` per test completo:

```bash
# In Visum Python Console
exec(open(r"h:\visum-thinker-mcp-server\test-stop-configurations.py").read())
```

**Output atteso:**
- Verifica consistenza fermate
- Generazione configurazioni
- Statistiche distribuzione
- Export CSV e JSON
- Filtering esempi

## References

### Related Functions
- `get_lr_stop_sequence()` - Ottiene sequenza fermate da LineRoute
- `abilita_fermata()` - Abilita singola fermata con timing
- `disabilita_fermata()` - Disabilita singola fermata

### Related Files
- `manage-stops-workflow.py` - Main workflow script (linee 119-300)
- `test-stop-configurations.py` - Test examples
- `enable-stop-STEP1-WORKING.py` - Original enable/disable functions

### Documentation
- `CLAUDE_WORKFLOW_GUIDE.md` - Complete workflow guide
- `EXPORT_TABLES_GUIDE.md` - Export functionality guide

---

**Status:** ✅ IMPLEMENTATO  
**Ultimo aggiornamento:** 2025-11-25  
**Versione:** 1.0
