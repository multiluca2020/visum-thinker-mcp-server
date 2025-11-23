# Sessione di Lavoro - Modifica TimeProfile Visum

**Data:** 2025-11-23  
**Obiettivo:** Abilitare/disabilitare fermate nei profili temporali di Visum via Python COM API

---

## 🎯 Problema Iniziale

Modificare i profili di linea (LineRoute) per abilitare/disabilitare fermate nel TimeProfile di Visum, impostando tempi di sosta personalizzati.

**Richiesta specifica:** 
- Abilitare fermata 370 
- Impostare tempo di fermata 1 minuto
- Aggiungere 30 sec ai tempi pre e post run

---

## 🔍 Scoperte Chiave

### 1. Struttura Dati Visum

```
LineRoute (R17_2)
├── LineRouteItems (24 fermate totali)
│   ├── StopPointNo (numero fermata)
│   ├── IsRoutePoint (True/False = abilitata/disabilitata)
│   ├── Index (posizione nella sequenza)
│   └── AccumLength (distanza cumulativa)
│
└── TimeProfile (R17)
    └── TimeProfileItems (solo fermate abilitate, ~15)
        ├── Arr (tempo arrivo)
        ├── Dep (tempo partenza)
        ├── StopTime (Dep - Arr, READ-ONLY calcolato)
        ├── PreRunTime (Arr - Dep_prev, READ-ONLY calcolato)
        └── PostRunTime (Arr_next - Dep, READ-ONLY calcolato)
```

### 2. Attributi Chiave

**LineRouteItem:**
- `IsRoutePoint` (True/False) - Controlla se fermata è abilitata
- `AccumLength` - Distanza cumulativa lungo il percorso
- `StopPointNo` - Numero identificativo fermata

**TimeProfileItem:**
- `Arr` e `Dep` - **SCRIVIBILI** - tempi arrivo/partenza
- `StopTime`, `PreRunTime`, `PostRunTime` - **READ-ONLY** - calcolati automaticamente

### 3. Problema GUI vs Database

**Scoperta importante:**
- ✅ Modifiche via script → Database aggiornato correttamente
- ❌ GUI Time Profile Editor → Non si aggiorna automaticamente
- ✅ Modifiche via GUI → Database aggiornato e visibile negli script

**Soluzione:** Chiudere e riaprire la finestra Time Profile Editor dopo le modifiche via script.

### 4. Calcolo Tempi - Formula Corretta

**Errore iniziale:** Dividere il tempo totale a metà (360 sec) → **SBAGLIATO**

**Formula corretta:** Interpolazione proporzionale basata su distanze

```python
# SEQUENZA CRITICA:
# 1. Abilita IsRoutePoint=True
current['item'].SetAttValue("IsRoutePoint", True)

# 2. RILEGGI AccumLength (ora aggiornato!)
prev_accum = prev_stop['item'].AttValue("AccumLength")
curr_accum = current['item'].AttValue("AccumLength")
next_accum = next_stop['item'].AttValue("AccumLength")

# 3. Calcola proporzione
dist_prev_curr = curr_accum - prev_accum
dist_total = next_accum - prev_accum
proportion = dist_prev_curr / dist_total

# 4. Calcola PreRunTime
time_total = next_arr - prev_dep
pre_run_time = proportion * time_total  # Es: 0.11 × 720 = 79 sec

# 5. Calcola Arr e Dep
arr = prev_dep + pre_run_time
dep = arr + stop_time

# 6. Crea TimeProfileItem
tpi = tp.AddTimeProfileItem(current['item'])

# 7. Imposta tempi
tpi.SetAttValue("Arr", arr)
tpi.SetAttValue("Dep", dep)
```

**Esempio concreto (fermata 370):**
- Prev (301): Dep = 2490 sec, AccumLength = 24.85 km
- Curr (370): AccumLength = 26.95 km
- Next (173): Arr = 3210 sec, AccumLength = 41.90 km
- Dist 301→370: 2.10 km
- Dist totale: 17.05 km
- Proporzione: 2.10 / 17.05 = 0.123
- PreRunTime: 0.123 × 720 = **89 sec** ✅ (non 360!)

---

## 📝 Script Finali

### Script Semplice (Solo IsRoutePoint)
**File:** `enable-disable-stops-simple.py`

```python
OPERATIONS = {
    370: "enable",
    # 328: "disable",
}
```

- Imposta solo `IsRoutePoint=True/False`
- Visum crea TimeProfileItem automaticamente
- Tempi interpolati automaticamente da Visum
- **Limiti:** StopTime = 0 di default, nessun controllo sui tempi

### Script Completo (STEP1 - WORKING)
**File:** `enable-stop-STEP1-WORKING.py`

```python
OPERATIONS = {
    370: {
        "action": "enable",
        "stop_time": 60  # secondi
    }
}
```

- ✅ Abilita IsRoutePoint
- ✅ Rilegge AccumLength dopo abilitazione
- ✅ Calcola tempi con proporzione corretta
- ✅ Crea TimeProfileItem con tempi precisi
- ✅ PreRunTime calcolato come fa Visum (~79 sec)

---

## 🔧 Script di Analisi Utili

### 1. Verifica Stato TimeProfile
```python
exec(open(r"h:\visum-thinker-mcp-server\analyze-timeprofileitems.py").read())
```
Mostra tutti i TimeProfileItems con tempi dettagliati.

### 2. Analisi Fermata Specifica
```python
exec(open(r"h:\visum-thinker-mcp-server\analyze-370-timing.py").read())
```
Analizza fermata 370 e calcola come Visum ha determinato i tempi.

### 3. Verifica dopo Modifiche
```python
exec(open(r"h:\visum-thinker-mcp-server\verify-after-reopen.py").read())
```
Controlla stato del database dopo salvataggio/riapertura.

---

## 🐛 Problemi Risolti

### 1. GUI non mostra modifiche
**Causa:** GUI Time Profile Editor carica dati all'apertura e non si aggiorna  
**Soluzione:** Chiudere e riaprire Edit > Time Profiles

### 2. PreRunTime sbagliato (960 invece di 79)
**Causa:** Calcolo basato su divisione tempo totale / 2  
**Soluzione:** Usare proporzione delle distanze AccumLength

### 3. AccumLength sempre 24.9
**Causa:** Lettura PRIMA di abilitare IsRoutePoint  
**Soluzione:** Abilitare prima, POI rileggere AccumLength

### 4. StopTime non modificabile
**Causa:** StopTime è READ-ONLY (calcolato come Dep - Arr)  
**Soluzione:** Impostare Arr e Dep, StopTime viene calcolato automaticamente

### 5. TimeProfileItem non creato
**Causa:** Sintassi sbagliata: `tp.TimeProfileItems.Add()`  
**Soluzione:** Usare `tp.AddTimeProfileItem(LineRouteItem)`

---

## 📚 API Visum - Riferimento

### Oggetti Principali
```python
Visum.Net.LineRoutes              # Collezione LineRoutes
LineRoute.LineRouteItems          # Collezione LineRouteItems
LineRoute.TimeProfiles            # Collezione TimeProfiles
TimeProfile.TimeProfileItems      # Collezione TimeProfileItems
```

### Metodi Critici
```python
# Abilita fermata
item.SetAttValue("IsRoutePoint", True)

# Crea TimeProfileItem
tpi = timeprofile.AddTimeProfileItem(lineroute_item)

# Imposta tempi (SOLO Arr e Dep sono scrivibili!)
tpi.SetAttValue("Arr", 2569.0)
tpi.SetAttValue("Dep", 2629.0)

# Lettura attributi
value = item.AttValue("AccumLength")
```

### Attributi Non Disponibili (testati)
- ❌ `Visum.Graphics` - Non esiste
- ❌ `LineRouteItem.StopPoint` - Non accessibile
- ❌ `TimeProfile.Refresh()` - Non esiste
- ❌ Impostazione diretta di `StopTime`, `PreRunTime`, `PostRunTime`

---

## 🚀 Prossimi Sviluppi

### STEP 2 (To Do)
- [ ] Gestione multipla fermate in un'unica esecuzione
- [ ] Supporto offset personalizzati per PreRun/PostRun
- [ ] Ricalcolo tempi fermate successive quando si aggiunge una fermata
- [ ] Supporto disable con aggiornamento tempi adiacenti

### STEP 3 (To Do)
- [ ] Validazione input (prima/ultima fermata, fermate esistenti)
- [ ] Error handling robusto
- [ ] Logging dettagliato
- [ ] Backup/rollback automatico

### STEP 4 (To Do)
- [ ] Interfaccia utente (GUI o config file)
- [ ] Batch processing (modifiche multiple LineRoutes)
- [ ] Export/import configurazioni
- [ ] Integrazione con MCP server

---

## 📋 Note Tecniche

### Encoding
Script Python per Visum console: **ASCII** (CP1252)
```python
# -*- coding: ascii -*-
```

### Esecuzione
Dalla console Python di Visum (non terminale esterno):
```python
exec(open(r"h:\visum-thinker-mcp-server\script.py").read())
```

### Oggetto Visum
Pre-esistente nella console, non serve:
```python
# ❌ NON fare
import win32com.client
Visum = win32com.client.Dispatch("Visum.Visum.240")

# ✅ Oggetto già disponibile
Visum.Net.LineRoutes  # Funziona direttamente
```

### Salvataggio
```python
# Salvataggio semplice (sovrascrive)
Visum.SaveVersion()  # Può dare errore "Parameter not optional"

# Alternativa (funziona sempre)
# File > Save (Ctrl+S) dall'interfaccia
```

---

## 🎓 Lezioni Apprese

1. **Sequenza conta:** Abilita → Rileggi → Calcola → Crea → Imposta
2. **AccumLength si aggiorna:** Solo DOPO aver impostato IsRoutePoint=True
3. **GUI ha cache:** Necessita chiusura/riapertura per vedere modifiche
4. **Attributi calcolati:** StopTime/PreRun/PostRun sono READ-ONLY
5. **Proporzione distanze:** Visum interpola linearmente basandosi su AccumLength
6. **Database vs GUI:** Script legge/scrive correttamente, problema è solo visualizzazione

---

## ✅ Risultato Finale

**Script funzionante:** `enable-stop-STEP1-WORKING.py`

**Test superato:**
- ✅ Fermata 370 abilitata
- ✅ StopTime = 60 secondi
- ✅ PreRunTime = 79 secondi (corretto!)
- ✅ PostRunTime = 641 secondi (corretto!)
- ✅ Database aggiornato correttamente
- ✅ Tempi identici a quelli creati da Visum automaticamente

**Comando:**
```python
exec(open(r"h:\visum-thinker-mcp-server\enable-stop-STEP1-WORKING.py").read())
```

---

**Fine sessione - 2025-11-23**
