# Test Scripts - Configurazioni Fermate

## Overview

Questi script testano le funzioni di verifica consistenza e generazione configurazioni fermate.

## ⚠️ IMPORTANTE

**Tutti questi script devono essere eseguiti nella Visum Python Console (Ctrl+P)**

NON eseguirli da terminale PowerShell/Cmd esterno perché richiedono l'oggetto `Visum` che è disponibile solo all'interno di Visum.

## Scripts Disponibili

### 1. `quick-test-configs.py` ⭐ RACCOMANDATO

**Uso:** Test rapido e semplice

```python
# In Visum Python Console (Ctrl+P)
exec(open(r"h:\visum-thinker-mcp-server\quick-test-configs.py").read())
```

**Cosa fa:**
- Carica automaticamente `manage-stops-workflow.py`
- Verifica consistenza fermate su `TARGET_LINEROUTES`
- Genera tutte le configurazioni
- Mostra esempi e statistiche rapide
- Variabile `configs` disponibile per uso successivo

**Output:**
```
================================================================================
TEST RAPIDO GENERAZIONE CONFIGURAZIONI
================================================================================

Caricamento manage-stops-workflow.py...
OK

Linee target configurate:
  - R17_2022:R17_2
  - R17_2022:R17_3
  ...

--------------------------------------------------------------------------------
STEP 1: Verifica consistenza fermate
--------------------------------------------------------------------------------
...
✓ OK: Tutte le linee hanno stesse fermate

Riepilogo:
  Fermate totali:     12
  Fermate variabili:  10
  Configurazioni:     1024 (2^10)

--------------------------------------------------------------------------------
STEP 2: Generazione configurazioni
--------------------------------------------------------------------------------
...
✓ Generazione completata: 1024 configurazioni
...
```

### 2. `test-stop-configurations.py`

**Uso:** Test completo con esempi avanzati

```python
# In Visum Python Console (Ctrl+P)
exec(open(r"h:\visum-thinker-mcp-server\test-stop-configurations.py").read())
```

**Cosa fa:**
- ESEMPIO 1: Workflow completo con analisi distribuzione
- ESEMPIO 2: Export configurazioni su CSV e JSON
- ESEMPIO 3: Filtraggio configurazioni per criteri

**Features:**
- Export CSV con matrice configurazioni (righe=config, colonne=fermate, valori=0/1)
- Export JSON con metadati completi
- Filtri: minimo fermate, pari/dispari, consecutive, sample casuale
- Analisi pattern (alternati, custom)

**File generati:**
- `H:\go\trenord_2025\stop_configurations.csv`
- `H:\go\trenord_2025\stop_configurations.json`

### 3. Uso Diretto nel Workflow

**Uso:** Integrazione diretta nel workflow principale

```python
# In Visum Python Console (Ctrl+P)
exec(open(r"h:\visum-thinker-mcp-server\manage-stops-workflow.py").read())

# Ora le funzioni sono disponibili direttamente
result = verify_and_get_common_stops(TARGET_LINEROUTES)

if result['valid']:
    configs = generate_stop_configurations(result['stops'])
    
    # Usa configs come vuoi
    print("Totale configurazioni: %d" % len(configs))
    
    # Accedi a config specifica
    config_100 = configs[99]  # Config ID=100 (0-based index)
    print("Config 100 ha %d fermate: %s" % (
        config_100['enabled_count'],
        config_100['enabled_stops']
    ))
```

## Errori Comuni

### ❌ Errore: `NameError: name 'Visum' is not defined`

**Causa:** Script eseguito fuori dalla Visum Python Console

**Soluzione:** 
1. Apri Visum
2. Apri progetto
3. Premi `Ctrl+P` per aprire Python Console
4. Esegui: `exec(open(r"path\to\script.py").read())`

### ❌ Errore: `NameError: name 'verify_and_get_common_stops' is not defined`

**Causa:** Funzioni non caricate

**Soluzione:** Gli script caricano automaticamente `manage-stops-workflow.py`. Verifica che il path sia corretto.

### ❌ Errore: `LineRoute non trovato: ...`

**Causa:** Nome LineRoute errato in `TARGET_LINEROUTES`

**Soluzione:** 
1. Verifica nomi esatti in Visum GUI
2. Controlla case-sensitive
3. Usa formato `"LineName:LineRouteName"`

### ❌ Warning: Troppo elevato configurazioni

**Causa:** Troppe fermate variabili (> 20)

**Soluzione:**
```python
# Usa sample invece di tutte
import random
max_configs = 1000
if len(configs) > max_configs:
    configs = random.sample(configs, max_configs)
```

## Performance Reference

| Fermate | Variabili | Configurazioni | Tempo | Memoria |
|---------|-----------|----------------|-------|---------|
| 5 | 3 | 8 | < 0.1s | < 1 KB |
| 10 | 8 | 256 | < 0.1s | 50 KB |
| 12 | 10 | 1,024 | < 0.2s | 200 KB |
| 15 | 13 | 8,192 | ~0.5s | 1.5 MB |
| 20 | 18 | 262,144 | ~15s | 50 MB |

## Workflow Tipico

```python
# 1. Carica e testa
exec(open(r"h:\visum-thinker-mcp-server\quick-test-configs.py").read())

# 2. Se tutto OK, configs è ora disponibile
print("Configurazioni disponibili: %d" % len(configs))

# 3. Seleziona configurazioni da testare
test_configs = configs[:10]  # Prime 10

# 4. Loop su configurazioni
for config in test_configs:
    print("\nTestando config %d..." % config['id'])
    
    # TODO: Applica configurazione
    # apply_configuration(config['enabled_stops'])
    
    # TODO: Esegui procedure sequence
    # execute_procedure_sequence()
    
    # TODO: Raccogli risultati
    # results = collect_metrics()
```

## Variabili Disponibili Dopo Esecuzione

Dopo aver eseguito `quick-test-configs.py` o `test-stop-configurations.py`:

```python
# Disponibili:
result         # Dict con validazione e lista stops
configs        # Lista di tutte le configurazioni
TARGET_LINEROUTES  # Lista linee configurate

# Accesso configurazioni
configs[0]     # Prima (minima)
configs[-1]    # Ultima (massima)
configs[n]     # Config specifica

# Struttura config
config = {
    'id': 1,                          # ID univoco (1-based)
    'enabled_stops': [10001, 10012],  # Lista StopNo abilitati
    'enabled_count': 2,               # Quante fermate abilitate
    'pattern': (False, False, ...)    # Pattern bool (debug)
}

# Struttura result
result = {
    'valid': True,                    # Validazione OK?
    'stops': [...],                   # Lista fermate comuni
    'errors': []                      # Lista errori
}

# Struttura stops
stop = {
    'no': 10001,                      # StopPoint number
    'name': 'Milano Centrale',        # Nome fermata
    'index': 0                        # Posizione sequenza
}
```

## Export Dati

### Export CSV

```python
import csv

with open('my_configs.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f, delimiter=';')
    
    # Header
    writer.writerow(['ConfigID', 'EnabledCount', 'StopNos'])
    
    # Dati
    for c in configs:
        writer.writerow([
            c['id'],
            c['enabled_count'],
            ','.join(str(s) for s in c['enabled_stops'])
        ])
```

### Export JSON

```python
import json

data = {
    'total_configs': len(configs),
    'configurations': configs
}

with open('my_configs.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)
```

## Troubleshooting

### Script non trova file

Usa **path assoluto** con `r` prefix:
```python
exec(open(r"h:\visum-thinker-mcp-server\quick-test-configs.py").read())
```

### Import errors nel linter

Gli errori del linter (codice rosso nell'editor) sono **normali** perché:
- `Visum` è definito solo in runtime
- Funzioni caricate dinamicamente con `exec()`

Gli script funzioneranno correttamente in Visum Console.

### Script molto lento

Per molte fermate (>15), usa **sample**:
```python
import random
configs_sample = random.sample(configs, 100)  # Solo 100 casuali
```

## See Also

- `STOP_CONFIGURATIONS_GUIDE.md` - Documentazione completa
- `manage-stops-workflow.py` - Script principale con funzioni
- `CLAUDE_WORKFLOW_GUIDE.md` - Workflow generale

---

**Nota:** Tutti gli script sono pensati per **esecuzione interattiva** nella Visum Python Console, non per esecuzione batch da terminale esterno.
