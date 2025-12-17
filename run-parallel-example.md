# Esecuzione Parallela con Slicing

## Concetto

Quando hai molte configurazioni da testare (es. 1024), puoi dividere il lavoro tra N processi Visum paralleli.

Ogni processo gestisce uno **slice** (porzione) delle configurazioni totali.

## Come Funziona

### Parametri Slicing

- `slice_index`: Indice dello slice corrente (0-based)
- `slice_total`: Numero totale di slice (= numero processi paralleli)

### Distribuzione Automatica

Lo script calcola automaticamente quali configurazioni processare:

**Esempio: 1024 configs, 4 processi**

```
Totale: 1024 configurazioni
Slice size: 256 per processo

Processo 0 (slice_index=0): configs 0-255     → 256 configs
Processo 1 (slice_index=1): configs 256-511   → 256 configs  
Processo 2 (slice_index=2): configs 512-767   → 256 configs
Processo 3 (slice_index=3): configs 768-1023  → 256 configs
```

**Esempio: 1000 configs, 3 processi** (remainder distribuito)

```
Totale: 1000 configurazioni
Slice size base: 333
Remainder: 1 (dato al primo processo)

Processo 0 (slice_index=0): configs 0-333     → 334 configs (333+1)
Processo 1 (slice_index=1): configs 334-666   → 333 configs
Processo 2 (slice_index=2): configs 667-999   → 333 configs
```

## Setup per Esecuzione Parallela

### 1. Prepara gli Script

Crea N copie dello script con slice diversi:

**workflow_slice_0.py**
```python
TASKS = [
    {
        "id": 1,
        "action": "test_all_configurations",
        "params": {
            "lineroutes": ["R17_2022:R17_2"],
            "layout_file": r"H:\go\trenord_2025\skim_layout.lay",
            "output_dir": r"H:\go\trenord_2025\config_tests",
            "slice_index": 0,  # ← CAMBIA QUESTO
            "slice_total": 4   # ← Numero processi
        }
    }
]
```

**workflow_slice_1.py**
```python
TASKS = [
    {
        "params": {
            "slice_index": 1,  # ← Secondo processo
            "slice_total": 4
        }
    }
]
```

...e così via per slice_index=2, slice_index=3

### 2. Output Separati (Opzionale)

Puoi anche separare l'output per processo:

```python
"output_dir": r"H:\go\trenord_2025\config_tests\slice_0",
```

### 3. Esegui in Parallelo

Apri **4 istanze di Visum** contemporaneamente e in ognuna esegui:

**Visum 1:**
```python
exec(open(r"h:\visum-thinker-mcp-server\workflow_slice_0.py").read())
```

**Visum 2:**
```python
exec(open(r"h:\visum-thinker-mcp-server\workflow_slice_1.py").read())
```

**Visum 3:**
```python
exec(open(r"h:\visum-thinker-mcp-server\workflow_slice_2.py").read())
```

**Visum 4:**
```python
exec(open(r"h:\visum-thinker-mcp-server\workflow_slice_3.py").read())
```

## Combinazione con max_configs

Puoi combinare slicing con `max_configs`:

```python
{
    "slice_index": 0,
    "slice_total": 4,
    "max_configs": 10,      # ← Testa solo 10 configs del MIO slice
    "random_sample": True   # ← Sample casuale delle 10
}
```

**Esempio:**
- Totale: 1024 configs
- Slice 0 riceve: configs 0-255 (256 configs)
- max_configs=10 + random_sample=True: seleziona 10 casuali tra 0-255

## Vantaggi

✅ **Speedup lineare**: 4 processi = 4x più veloce  
✅ **No coordinazione**: Ogni processo lavora indipendentemente  
✅ **No conflitti**: Ogni slice è distinto  
✅ **Failure isolation**: Se un processo crasha, gli altri continuano

## Limitazioni

⚠️ **Memoria**: Ogni Visum consuma RAM (~2-4 GB)  
⚠️ **CPU**: Utile solo se hai CPU cores sufficienti  
⚠️ **I/O**: Se tutti scrivono su stesso disco, potrebbe rallentare

## Best Practices

1. **Numero processi = CPU cores** (es. 4-8)
2. **Output directories separati** per evitare conflitti
3. **Monitor individuale** con log separati
4. **Test con slice_total=2** prima di scalare

## Esempio Completo

**4 processi, ognuno con output separato:**

```python
# workflow_slice_0.py
TASKS = [{
    "params": {
        "lineroutes": ["R17_2022:R17_2"],
        "layout_file": r"H:\go\trenord_2025\skim_layout.lay",
        "output_dir": r"H:\go\trenord_2025\results\process_0",
        "slice_index": 0,
        "slice_total": 4
    }
}]

# workflow_slice_1.py
TASKS = [{
    "params": {
        "output_dir": r"H:\go\trenord_2025\results\process_1",
        "slice_index": 1,
        "slice_total": 4
    }
}]

# workflow_slice_2.py
TASKS = [{
    "params": {
        "output_dir": r"H:\go\trenord_2025\results\process_2",
        "slice_index": 2,
        "slice_total": 4
    }
}]

# workflow_slice_3.py
TASKS = [{
    "params": {
        "output_dir": r"H:\go\trenord_2025\results\process_3",
        "slice_index": 3,
        "slice_total": 4
    }
}]
```

Ogni processo scriverà in `results/process_0/`, `results/process_1/`, ecc.

## Risultati Finali

Alla fine avrai:
```
H:\go\trenord_2025\results\
  process_0\
    R17_2022_R17_2_1111000.csv
    R17_2022_R17_2_1111001.csv
    ...
  process_1\
    R17_2022_R17_2_1110010.csv
    ...
  process_2\
    ...
  process_3\
    ...
```

Puoi unire i risultati manualmente o con uno script PowerShell.
