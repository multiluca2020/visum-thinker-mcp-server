# Custom Configuration Examples

## Nuove Funzionalità

### 1. **Configurazione Iniziale Custom** (`initial_config`)
Definisce lo stato di partenza PRIMA di testare le configurazioni permutate.

### 2. **Fermate Locked (Fisse)** (`locked_stops`)
Fermate che mantengono sempre lo stesso stato e NON partecipano alle permutazioni.

---

## Use Case 1: Start da "Tutte Disabilitate"

**Scenario:** Vuoi partire con tutte le fermate disabilitate (solo prima e ultima ON) e poi testare aggiungendo fermate progressivamente.

```python
TASKS = [{
    "action": "test_all_configurations",
    "params": {
        "lineroutes": ["R17_2022:R17_2"],
        "layout_file": r"H:\go\trenord_2025\skim_layout.lay",
        "output_dir": r"H:\go\trenord_2025\config_tests",
        
        # START: Solo prima e ultima abilitate
        "initial_config": "all_disabled"
    }
}]
```

**Risultato:**
- Config iniziale: `1000...0001` (solo prima e ultima)
- Poi testa tutte le 2^N permutazioni partendo da questo stato

---

## Use Case 2: Configurazione Iniziale Specifica

**Scenario:** Hai una configurazione base nota (es. fermate principali) e vuoi testare variazioni da lì.

```python
TASKS = [{
    "params": {
        # START: Fermate specifiche abilitate
        "initial_config": {
            "enabled_stops": [328, 372, 327, 500, 600]  # Solo queste ON all'inizio
        }
    }
}]
```

**Risultato:**
- Config iniziale: Solo stop 328, 372, 327, 500, 600 abilitate
- Export iniziale: `R17_2022_R17_2_INIT_101010001.csv`
- Poi testa tutte le permutazioni

---

## Use Case 3: Fermate Sempre ON (Locked ON)

**Scenario:** Alcune fermate sono **critiche** e devono essere SEMPRE abilitate in tutte le configurazioni.

```python
TASKS = [{
    "params": {
        # Fermate 328 e 372 SEMPRE ON in tutte le config
        "locked_stops": {
            328: True,   # Sempre abilitata
            372: True    # Sempre abilitata
        }
    }
}]
```

**Risultato:**
- Fermata 328: SEMPRE ON in tutte le 2^N configurazioni
- Fermata 372: SEMPRE ON in tutte le 2^N configurazioni
- Altre fermate intermedie: variano normalmente
- **Numero config ridotto:** Se hai 10 fermate intermedie ma 2 locked ON, generi 2^8 = 256 config invece di 2^10 = 1024

**Output example:**
```
Config 1: 1110010001  (328 e 372 sempre 1)
Config 2: 1110110001  (328 e 372 sempre 1)
Config 3: 1111010001  (328 e 372 sempre 1)
...
```

---

## Use Case 4: Fermate Sempre OFF (Locked OFF)

**Scenario:** Alcune fermate sono **problematiche** o in manutenzione e devono essere SEMPRE disabilitate.

```python
TASKS = [{
    "params": {
        # Fermate 327 e 329 SEMPRE OFF in tutte le config
        "locked_stops": {
            327: False,  # Sempre disabilitata
            329: False   # Sempre disabilitata
        }
    }
}]
```

**Risultato:**
- Fermata 327: SEMPRE OFF in tutte le configurazioni
- Fermata 329: SEMPRE OFF in tutte le configurazioni
- Altre fermate: variano normalmente
- **Numero config ridotto:** 2^(N-2) invece di 2^N

---

## Use Case 5: Mix Locked ON e OFF

**Scenario:** Alcune fermate fisse ON, altre fisse OFF, resto variabile.

```python
TASKS = [{
    "params": {
        "locked_stops": {
            328: True,   # Sempre ON
            372: True,   # Sempre ON
            327: False,  # Sempre OFF
            329: False   # Sempre OFF
        }
    }
}]
```

**Fermate totali:** 12 (esempio)
- Prima/ultima: SEMPRE ON (fisse)
- 328, 372: SEMPRE ON (locked)
- 327, 329: SEMPRE OFF (locked)
- Restanti 6: VARIABILI

**Numero configurazioni:** 2^6 = 64 (invece di 2^10 = 1024)

---

## Use Case 6: Initial Config + Locked (Combinazione)

**Scenario:** Parti da configurazione specifica E mantieni alcune fermate fisse.

```python
TASKS = [{
    "params": {
        # START: Config custom
        "initial_config": {
            "enabled_stops": [328, 372, 500, 600]
        },
        
        # Durante i test: 328 sempre ON, 327 sempre OFF
        "locked_stops": {
            328: True,   # Sempre ON in tutte le config
            327: False   # Sempre OFF in tutte le config
        }
    }
}]
```

**Workflow:**
1. **Step iniziale:** Applica initial_config (328, 372, 500, 600 ON)
2. **Export iniziale:** `R17_2022_R17_2_INIT_1010100.csv`
3. **Test configurazioni:** Tutte le config hanno 328 sempre ON, 327 sempre OFF

---

## Use Case 7: Parallel Slicing + Locked + Custom Initial

**Scenario:** Esecuzione parallela completa con tutte le feature.

**Processo 0:**
```python
TASKS = [{
    "params": {
        "lineroutes": ["R17_2022:R17_2"],
        "layout_file": r"H:\go\trenord_2025\skim_layout.lay",
        "output_dir": r"H:\go\trenord_2025\results\process_0",
        
        # Custom initial config
        "initial_config": "all_disabled",
        
        # Locked stops
        "locked_stops": {
            328: True,   # Sempre ON
            327: False   # Sempre OFF
        },
        
        # Parallel slicing
        "slice_index": 0,
        "slice_total": 4
    }
}]
```

**Processo 1, 2, 3:** Stessi parametri, solo `slice_index` cambia (1, 2, 3)

**Risultato:**
- Ogni processo testa 1/4 delle configurazioni
- Tutte partono da "all_disabled"
- In tutte: 328 sempre ON, 327 sempre OFF
- Speedup 4x

---

## Use Case 8: Riduzione Drastica Configurazioni

**Scenario:** Hai 20 fermate intermedie (2^20 = 1M configurazioni!) ma vuoi testare solo variazioni su 5 fermate specifiche.

```python
# Fermate intermedie: 10 totali (esempio semplificato)
# StopNos: 300, 301, 302, 303, 304, 305, 306, 307, 308, 309

TASKS = [{
    "params": {
        # Lock 5 fermate come sempre ON
        "locked_stops": {
            300: True,
            301: True,
            302: True,
            303: True,
            304: True
        }
        # Restanti 5 (305-309) variano -> 2^5 = 32 config invece di 2^10 = 1024
    }
}]
```

**Before:** 1024 configurazioni (2^10)  
**After:** 32 configurazioni (2^5)  
**Speedup:** 32x più veloce!

---

## Statistiche Generazione Configurazioni

### Output Console con Locked Stops

```
GENERAZIONE CONFIGURAZIONI FERMATE
================================================================================

Fermate fisse SEMPRE ON (prima/ultima + locked ON):
  - Prima: 100 (Stazione A)
  - Locked ON: 328 (Fermata Importante)
  - Locked ON: 372 (Hub Principale)
  - Ultima: 999 (Stazione Z)

Fermate fisse SEMPRE OFF (locked OFF):
  - Locked OFF: 327 (Fermata Chiusa)
  - Locked OFF: 329 (In Manutenzione)

Fermate VARIABILI (partecipano alle permutazioni): 6
  1. Fermata X (StopNo: 350)
  2. Fermata Y (StopNo: 351)
  3. Fermata Z (StopNo: 352)
  ...

Numero totale configurazioni: 64 (2^6)
```

---

## Best Practices

### 1. **Usa `locked_stops` per Ridurre Spazio di Ricerca**
   - Se sai che alcune fermate DEVONO essere ON/OFF, lockale
   - Riduce drasticamente il numero di configurazioni

### 2. **Usa `initial_config` per Baseline Realistiche**
   - Parti da configurazione operativa nota
   - Testa variazioni incrementali

### 3. **Combina con `max_configs` per Test Rapidi**
   ```python
   "locked_stops": {328: True, 327: False},  # Riduci spazio
   "max_configs": 50,                         # Sample limitato
   "random_sample": True                      # Casuale
   ```

### 4. **Parallel Slicing su Spazio Ridotto**
   - Prima riduci con `locked_stops` (es. 2^10 → 2^6)
   - Poi dividi con `slice_total` (es. 64 config / 4 proc = 16 config/proc)

---

## Pattern File Output

Con locked stops, il pattern riflette lo stato effettivo:

```
Esempio: 10 fermate intermedie, locked {328: True, 327: False}

Pattern bits:
Position 0: Prima (sempre 1)
Position 1: Stop 300 (variabile)
Position 2: Stop 328 (locked ON = sempre 1)  ← LOCKED
Position 3: Stop 327 (locked OFF = sempre 0) ← LOCKED
Position 4: Stop 350 (variabile)
...
Position 11: Ultima (sempre 1)

Filename example: R17_2022_R17_2_111010110101.csv
                                    ↑↑
                                    ||
                                    |└─ 327 sempre 0
                                    └── 328 sempre 1
```

---

## Validazione Parametri

Lo script valida automaticamente:

✅ `locked_stops` contiene solo StopNo validi  
✅ `initial_config.enabled_stops` contiene stop esistenti  
✅ Prima e ultima fermata non possono essere locked  
✅ `slice_index < slice_total`  

Se errori, lo script stampa messaggio e termina.
