# TEST CONFIGURAZIONI WORKFLOW

## Overview

Task automatico per testare **tutte le possibili configurazioni** di fermate abilitate/disabilitate su un set di linee.

## Workflow Completo

```
1. Verifica consistenza fermate tra tutte le linee
2. Genera tutte le configurazioni possibili (2^n)
3. BASELINE: Abilita tutte le fermate
4. Esegui Procedure Sequence (baseline)
5. Export layout con nome: {linea}_111111... (tutte a 1)
6. LOOP per ogni configurazione:
   a) Applica configurazione (abilita/disabilita fermate)
   b) Esegui Procedure Sequence
   c) Export layout con nome: {linea}_{pattern} (es. 110101...)
7. Riepilogo finale
```

## Configurazione Task

### Task Definizione

```python
{
    "id": 4,
    "name": "Test tutte le configurazioni fermate",
    "action": "test_all_configurations",
    "params": {
        "lineroutes": TARGET_LINEROUTES,
        "layout_file": r"H:\go\trenord_2025\skim_layout.lay",
        "output_dir": r"H:\go\trenord_2025\config_tests",
        "stop_time": 60,
        "pre_run_add": 30,
        "post_run_add": 30,
        "max_configs": 10,      # Limita numero configurazioni (None = tutte)
        "random_sample": True   # Sample casuale se > max_configs
    }
}
```

### Parametri

| Parametro | Tipo | Obbligatorio | Default | Descrizione |
|-----------|------|--------------|---------|-------------|
| `lineroutes` | list | ❌ No | `TARGET_LINEROUTES` | Lista "LineName:LineRouteName" |
| `layout_file` | str | ✅ Sì | - | Path file .lay da esportare |
| `output_dir` | str | ❌ No | `"./"` | Directory output CSV |
| `stop_time` | int | ❌ No | `60` | Tempo sosta in secondi |
| `pre_run_add` | int | ❌ No | `30` | Offset PreRunTime |
| `post_run_add` | int | ❌ No | `30` | Offset PostRunTime |
| `max_configs` | int | ❌ No | `None` | Limite max configurazioni |
| `random_sample` | bool | ❌ No | `True` | Sample casuale se > max |

## Naming Convention

### Pattern String

Ogni fermata è rappresentata da **1 bit**:
- `1` = Fermata **abilitata**
- `0` = Fermata **disabilitata**

**Nota:** Prima e ultima fermata sono **sempre 1** (sempre abilitate)

### Esempi

**12 fermate totali:**

| Config | Pattern | Descrizione | Fermate Abilitate |
|--------|---------|-------------|-------------------|
| Baseline | `111111111111` | Tutte abilitate | 12 |
| Minimo | `100000000001` | Solo prima+ultima | 2 |
| Esempio 1 | `110101010101` | Alternate (dispari) | 7 |
| Esempio 2 | `101010101011` | Alternate (pari) | 7 |
| Esempio 3 | `111111000001` | Prime 6 + ultima | 7 |

### Nomi File Export

```
{LineName}_{Pattern}_{TableName}.csv
```

**Esempi:**
```
R17_2022_R17_2_111111111111_Links.csv        (baseline)
R17_2022_R17_2_100000000001_Links.csv        (minimo)
R17_2022_R17_2_110101010101_Links.csv        (config specifica)
```

## Funzioni Implementate

### 1. `task_test_all_configurations(params)`

Funzione principale del task. Orchestrazione completo workflow.

**Returns:**
```python
{
    'success': True,
    'total_configs': 10,
    'successful': 9,
    'failed': 1,
    'results': [...]
}
```

### 2. `apply_stop_configuration(lineroutes, enabled_stops, all_stops, ...)`

Applica una specifica configurazione di fermate.

**Features:**
- Processa fermate **una alla volta** per corretto aggiornamento tempi
- Abilita fermate che devono essere abilitate
- Disabilita fermate che devono essere disabilitate
- Aggiorna PreRunTime e PostRunTime

**Returns:**
```python
{
    'enabled': 5,    # Numero fermate abilitate
    'disabled': 3    # Numero fermate disabilitate
}
```

### 3. `disabilita_fermata(tp, stops, stop_no, ...)`

Disabilita una singola fermata.

**Operazioni:**
1. Trova fermata nel TimeProfile
2. Rimuove TimeProfileItem
3. Imposta IsRoutePoint = False

**Returns:** `True` se successo, `False` se errore

## Esempi Pratici

### Esempio 1: Test Completo (Tutte le Configurazioni)

```python
# In manage-stops-workflow.py, aggiungi task:

TASKS = [
    {
        "id": 1,
        "name": "Test tutte le configurazioni",
        "action": "test_all_configurations",
        "params": {
            "lineroutes": ["R17_2022:R17_2"],
            "layout_file": r"H:\go\trenord_2025\skim_layout.lay",
            "output_dir": r"H:\go\trenord_2025\all_configs",
            "stop_time": 60,
            "max_configs": None  # TUTTE le configurazioni
        }
    }
]

# Esegui in Visum Python Console
exec(open(r"h:\visum-thinker-mcp-server\manage-stops-workflow.py").read())
```

**Output:**
- Se 12 fermate → 10 variabili → **1024 configurazioni**
- Tempo stimato: ~1024 × (apply + procedure + export)
- Se procedure = 2 min → **~34 ore totali**

### Esempio 2: Test Rapido (Sample Limitato)

```python
TASKS = [
    {
        "id": 1,
        "name": "Test sample configurazioni",
        "action": "test_all_configurations",
        "params": {
            "lineroutes": ["R17_2022:R17_2"],
            "layout_file": r"H:\go\trenord_2025\skim_layout.lay",
            "output_dir": r"H:\go\trenord_2025\sample_configs",
            "max_configs": 10,        # Solo 10 configurazioni
            "random_sample": True     # Sample casuale
        }
    }
]
```

**Output:**
- 10 configurazioni casuali testate
- Tempo stimato: ~20 minuti (se procedure = 2 min)

### Esempio 3: Test Incrementale (Step by Step)

```python
TASKS = [
    {
        "id": 1,
        "name": "Test prime 5 configurazioni",
        "action": "test_all_configurations",
        "params": {
            "lineroutes": ["R17_2022:R17_2"],
            "layout_file": r"H:\go\trenord_2025\skim_layout.lay",
            "output_dir": r"H:\go\trenord_2025\test_step1",
            "max_configs": 5,
            "random_sample": False  # Prime 5 in ordine
        }
    }
]
```

## Performance

### Stima Tempi

**Formula:**
```
Tempo totale = N_configs × (T_apply + T_procedure + T_export)
```

**Valori tipici:**
- `T_apply` = 10-30 sec (dipende da numero TimeProfiles)
- `T_procedure` = 1-5 min (dipende da complessità assegnazioni)
- `T_export` = 5-10 sec (dipende da numero tabelle/righe)

**Esempi:**

| Fermate | Configs | T_proc | Tempo Totale |
|---------|---------|--------|--------------|
| 5 | 8 | 2 min | ~20 min |
| 10 | 256 | 2 min | ~9 ore |
| 12 | 1,024 | 2 min | ~34 ore |
| 15 | 8,192 | 2 min | ~273 ore (11 giorni!) |

**Raccomandazioni:**
- ✅ **< 256 configs:** Esegui tutte
- ⚠️ **256-1024:** Usa sample o esegui overnight
- ❌ **> 1024:** Troppo lungo, usa sample significativo

### Ottimizzazioni

#### 1. Sample Casuale

```python
"max_configs": 100,
"random_sample": True
```

Pro: Rappresentativo di tutte le configurazioni  
Contro: Potrebbe mancare configurazioni critiche

#### 2. Sample Strutturato

```python
# Pre-filtra configurazioni interessanti
# Esempio: Solo config con 40-60% fermate abilitate

# In uno script custom:
result = verify_and_get_common_stops(TARGET_LINEROUTES)
all_configs = generate_stop_configurations(result['stops'])

total_stops = len(result['stops'])
min_enabled = int(total_stops * 0.4)
max_enabled = int(total_stops * 0.6)

filtered = [c for c in all_configs if min_enabled <= c['enabled_count'] <= max_enabled]

# Usa filtered come base
```

#### 3. Parallel Processing

**Attualmente:** Sequenziale (una config alla volta)  
**Possibile:** Parallelizzare con multiple istanze Visum

**Nota:** Richiede licenze Visum multiple e orchestrazione complessa

## Output Struttura

### Directory Layout

```
output_dir/
├── R17_2022_R17_2_111111111111_Links.csv     (baseline)
├── R17_2022_R17_2_111111111111_Nodes.csv
├── R17_2022_R17_2_111111111111_ODPairs.csv
├── R17_2022_R17_2_100000000001_Links.csv     (config 1)
├── R17_2022_R17_2_100000000001_Nodes.csv
├── R17_2022_R17_2_100000000001_ODPairs.csv
├── R17_2022_R17_2_110000000001_Links.csv     (config 2)
├── ...
└── workflow_20251125_153045.log              (log file)
```

### Result Object

```python
result = {
    'success': True,
    'total_configs': 10,
    'successful': 9,
    'failed': 1,
    'results': [
        {
            'config_id': 1,
            'pattern': '100000000001',
            'enabled_count': 2,
            'apply_result': {...},
            'proc_result': {...},
            'export_result': {...},
            'success': True
        },
        # ...
    ]
}
```

## Analisi Risultati

### Post-Processing

Dopo l'esecuzione, puoi analizzare i risultati:

```python
import pandas as pd
import glob

# Carica tutti i Links.csv
output_dir = r"H:\go\trenord_2025\config_tests"
files = glob.glob(os.path.join(output_dir, "*_Links.csv"))

results = []
for f in files:
    # Estrai pattern dal nome
    basename = os.path.basename(f)
    pattern = basename.split('_')[2]  # Assumi formato: Line_LR_PATTERN_Table.csv
    
    # Carica dati
    df = pd.read_csv(f, delimiter=';')
    
    # Calcola metriche
    metrics = {
        'pattern': pattern,
        'enabled_stops': pattern.count('1'),
        'total_volume': df['VolVehPrT(AP)'].sum() if 'VolVehPrT(AP)' in df else 0,
        'avg_speed': df['V0PRT'].mean() if 'V0PRT' in df else 0,
        # ... altre metriche
    }
    
    results.append(metrics)

# Crea dataframe risultati
results_df = pd.DataFrame(results)

# Analisi
print(results_df.sort_values('total_volume', ascending=False).head(10))
```

### Visualizzazione

```python
import matplotlib.pyplot as plt

# Scatter: Fermate abilitate vs Volume totale
plt.scatter(results_df['enabled_stops'], results_df['total_volume'])
plt.xlabel('Fermate Abilitate')
plt.ylabel('Volume Totale')
plt.title('Impatto Fermate su Volume')
plt.show()

# Heatmap configurazioni
# ...
```

## Troubleshooting

### Errore: "Fermate non consistenti"

**Causa:** Le LineRoutes in `lineroutes` hanno fermate diverse

**Soluzione:**
1. Verifica con `verify_and_get_common_stops()`
2. Usa solo LineRoutes con stessa struttura fermate

### Errore: "Procedure Sequence fallita"

**Causa:** Assegnazione fallisce per configurazione specifica

**Soluzione:**
- Task continua con prossima configurazione
- Controlla log per dettagli errore
- Config fallita marcata con `success: False`

### Warning: "Troppo lungo"

**Causa:** Troppe configurazioni da testare

**Soluzione:**
- Usa `max_configs` per limitare
- Esegui sample rappresentativo
- Considera esecuzione batch overnight

### Timeout Visum

**Causa:** Procedure Sequence molto lunga

**Soluzione:**
- Aumenta timeout Visum (se possibile)
- Semplifica Procedure Sequence
- Riduci dimensione rete

## See Also

- `STOP_CONFIGURATIONS_GUIDE.md` - Generazione configurazioni
- `EXPORT_TABLES_GUIDE.md` - Export layout tables
- `CLAUDE_WORKFLOW_GUIDE.md` - Workflow generale

---

**Status:** ✅ IMPLEMENTATO  
**Ultimo aggiornamento:** 2025-11-25  
**Versione:** 1.0
