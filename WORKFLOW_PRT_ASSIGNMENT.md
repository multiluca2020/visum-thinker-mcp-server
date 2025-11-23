# Workflow Completo: Creare e Configurare Procedura PrT Assignment

## 🎯 Obiettivo

Creare una procedura PrT Assignment in Visum e configurarla con i demand segments desiderati, usando i tool MCP.

## 📋 Tools Disponibili

1. **`visum_create_procedure`** - Crea la procedura
2. **`visum_list_demand_segments`** - Lista i segments disponibili
3. **`visum_configure_dsegset`** - Configura i segments sulla procedura

## 🚀 Workflow Passo-Passo

### Step 1: Apri il Progetto Visum

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"project_open","arguments":{"projectPath":"H:\\\\go\\\\italferr2025\\\\Campoleone\\\\100625_Versione_base_v0.3_sub_ok_priv.ver"}}}' | node build/index.js
```

**Output:**
- Project ID: `100625_Versione_base_v0.3_sub_ok_priv_10176442`
- Porta TCP: `7909`

### Step 2: Lista i Demand Segments Disponibili

```bash
echo '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"visum_list_demand_segments","arguments":{"projectId":"100625_Versione_base_v0.3_sub_ok_priv_10176442"}}}' | node build/index.js
```

**Output esempio:**
```
📋 Tutti i Demand Segments PrT

Transport Systems PrT trovati: 3
• CAR: Car
• HGV: HGV  
• MOTO: Moto

Modi PrT disponibili: C, H
Totale segments: 36

Mode C (Car → TSys CAR):
  • C_CORRETTA_AM
  • C_CORRETTA_IP1
  • C_CORRETTA_IP2
  ... (24 segments totali)

Mode H (HGV → TSys HGV):
  • H_CORRETTA_AM
  • H_CORRETTA_IP1
  ... (12 segments totali)

DSEGSET completo:
C_CORRETTA_AM,C_CORRETTA_IP1,...,H_INIZIALE_S
```

### Step 2b (Opzionale): Filtra per Modo Specifico

Per vedere solo i segments del modo "C" (Car):

```bash
echo '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"visum_list_demand_segments","arguments":{"projectId":"100625_Versione_base_v0.3_sub_ok_priv_10176442","filterMode":"C"}}}' | node build/index.js
```

### Step 3: Crea la Procedura PrT Assignment

```bash
echo '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"visum_create_procedure","arguments":{"projectId":"100625_Versione_base_v0.3_sub_ok_priv_10176442","procedureType":"PrT_Assignment","position":20}}}' | node build/index.js
```

**Output:**
```
✅ Procedura Visum Creata

Tipo: PrT_Assignment
Posizione: 20
Codice Operazione: 101
Verificata: ✅ Sì
```

### Step 4: Configura DSEGSET con i Segments Desiderati

#### Opzione A: Tutti i Segments (36)

```bash
echo '{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"visum_configure_dsegset","arguments":{"projectId":"100625_Versione_base_v0.3_sub_ok_priv_10176442","procedurePosition":20,"dsegset":"C_CORRETTA_AM,C_CORRETTA_IP1,C_CORRETTA_IP2,C_CORRETTA_IP3,C_CORRETTA_PM,C_CORRETTA_S,C_INIZIALE_AM,C_INIZIALE_IP1,C_INIZIALE_IP2,C_INIZIALE_IP3,C_INIZIALE_PM,C_INIZIALE_S,C_ITERAZIONE_AM,C_ITERAZIONE_IP1,C_ITERAZIONE_IP2,C_ITERAZIONE_IP3,C_ITERAZIONE_PM,C_ITERAZIONE_S,C_NESTED_AM,C_NESTED_IP1,C_NESTED_IP2,C_NESTED_IP3,C_NESTED_PM,C_NESTED_S,H_CORRETTA_AM,H_CORRETTA_IP1,H_CORRETTA_IP2,H_CORRETTA_IP3,H_CORRETTA_PM,H_CORRETTA_S,H_INIZIALE_AM,H_INIZIALE_IP1,H_INIZIALE_IP2,H_INIZIALE_IP3,H_INIZIALE_PM,H_INIZIALE_S"}}}' | node build/index.js
```

#### Opzione B: Solo Mode C (24 segments)

```bash
echo '{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"visum_configure_dsegset","arguments":{"projectId":"100625_Versione_base_v0.3_sub_ok_priv_10176442","procedurePosition":20,"dsegset":"C_CORRETTA_AM,C_CORRETTA_IP1,C_CORRETTA_IP2,C_CORRETTA_IP3,C_CORRETTA_PM,C_CORRETTA_S,C_INIZIALE_AM,C_INIZIALE_IP1,C_INIZIALE_IP2,C_INIZIALE_IP3,C_INIZIALE_PM,C_INIZIALE_S,C_ITERAZIONE_AM,C_ITERAZIONE_IP1,C_ITERAZIONE_IP2,C_ITERAZIONE_IP3,C_ITERAZIONE_PM,C_ITERAZIONE_S,C_NESTED_AM,C_NESTED_IP1,C_NESTED_IP2,C_NESTED_IP3,C_NESTED_PM,C_NESTED_S"}}}' | node build/index.js
```

#### Opzione C: Con Parametri Addizionali

```bash
echo '{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"visum_configure_dsegset","arguments":{"projectId":"100625_Versione_base_v0.3_sub_ok_priv_10176442","procedurePosition":20,"dsegset":"C_CORRETTA_AM,C_CORRETTA_IP1,...","additionalParams":{"NUMITER":50,"PRECISIONDEMAND":0.01}}}}' | node build/index.js
```

**Output:**
```
✅ DSEGSET Configurato

Procedura: Posizione 20
Segments configurati: 36
Lunghezza DSEGSET: 500+ caratteri
Verificato: ✅ Sì

Parametri configurati:
• DSEGSET
• NUMITER=50
• PRECISIONDEMAND=0.01

🎉 La procedura è ora pronta per l'esecuzione!
```

## 💡 Workflow Interattivo (Claude Simulation)

Quando l'utente chiede di creare una procedura, il workflow è:

### 1. Claude chiede all'utente:

```
Ho creato la procedura PrT Assignment alla posizione 20.

Vuoi configurare i demand segments? Ho trovato:
- Mode C (Car): 24 segments
- Mode H (HGV): 12 segments
- Totale: 36 segments

Opzioni:
1. Usa tutti i 36 segments
2. Usa solo Mode C (Car)
3. Usa solo Mode H (HGV)
4. Selezione personalizzata

Quale preferisci?
```

### 2. Utente risponde (esempio):

```
Usa tutti i segments
```

### 3. Claude esegue:

```bash
# Automaticamente esegue visum_configure_dsegset con tutti i segments
```

### 4. Claude conferma:

```
✅ Ho configurato la procedura con tutti i 36 demand segments!

La procedura è pronta. Vuoi che aggiunga anche parametri di convergenza?
- Numero iterazioni (default: 20)
- Precisione (default: 0.01)
```

## 📚 Riferimenti Rapidi

### Comandi di Base

```bash
# 1. Apri progetto
project_open → projectId

# 2. Lista segments
visum_list_demand_segments(projectId) → dsegset string

# 3. Crea procedura
visum_create_procedure(projectId, "PrT_Assignment", 20)

# 4. Configura segments
visum_configure_dsegset(projectId, 20, dsegset)
```

### Project ID Corrente

**Progetto:** Campoleone 100625_Versione_base_v0.3_sub_ok_priv.ver  
**Project ID:** `100625_Versione_base_v0.3_sub_ok_priv_10176442`  
**Porta TCP:** 7909

### Modi e Segments (Progetto Campoleone)

- **Mode C (Car):** 24 segments  
  - Pattern: `C_<TYPE>_<TIMEPERIOD>`
  - Types: CORRETTA, INIZIALE, ITERAZIONE, NESTED
  - Time periods: AM, IP1, IP2, IP3, PM, S

- **Mode H (HGV):** 12 segments
  - Pattern: `H_<TYPE>_<TIMEPERIOD>`
  - Types: CORRETTA, INIZIALE
  - Time periods: AM, IP1, IP2, IP3, PM, S

### DSEGSET Strings

**Tutti (36):**
```
C_CORRETTA_AM,C_CORRETTA_IP1,C_CORRETTA_IP2,C_CORRETTA_IP3,C_CORRETTA_PM,C_CORRETTA_S,C_INIZIALE_AM,C_INIZIALE_IP1,C_INIZIALE_IP2,C_INIZIALE_IP3,C_INIZIALE_PM,C_INIZIALE_S,C_ITERAZIONE_AM,C_ITERAZIONE_IP1,C_ITERAZIONE_IP2,C_ITERAZIONE_IP3,C_ITERAZIONE_PM,C_ITERAZIONE_S,C_NESTED_AM,C_NESTED_IP1,C_NESTED_IP2,C_NESTED_IP3,C_NESTED_PM,C_NESTED_S,H_CORRETTA_AM,H_CORRETTA_IP1,H_CORRETTA_IP2,H_CORRETTA_IP3,H_CORRETTA_PM,H_CORRETTA_S,H_INIZIALE_AM,H_INIZIALE_IP1,H_INIZIALE_IP2,H_INIZIALE_IP3,H_INIZIALE_PM,H_INIZIALE_S
```

**Solo C (24):**
```
C_CORRETTA_AM,C_CORRETTA_IP1,C_CORRETTA_IP2,C_CORRETTA_IP3,C_CORRETTA_PM,C_CORRETTA_S,C_INIZIALE_AM,C_INIZIALE_IP1,C_INIZIALE_IP2,C_INIZIALE_IP3,C_INIZIALE_PM,C_INIZIALE_S,C_ITERAZIONE_AM,C_ITERAZIONE_IP1,C_ITERAZIONE_IP2,C_ITERAZIONE_IP3,C_ITERAZIONE_PM,C_ITERAZIONE_S,C_NESTED_AM,C_NESTED_IP1,C_NESTED_IP2,C_NESTED_IP3,C_NESTED_PM,C_NESTED_S
```

### Step 5: Verifica Esecuzione Assegnazione (Nuovo!)

**Dopo aver eseguito la procedura in Visum**, verifica che l'assegnazione sia stata completata con successo:

```bash
echo '{"jsonrpc":"2.0","id":5,"method":"tools/call","params":{"name":"visum_check_assignment","arguments":{"projectId":"100625_Versione_base_v0.3_sub_ok_priv_10176442"}}}' | node build/index.js
```

**Output se assegnazione completata:**
```
✅ Assegnazione PrT Trovata

Periodo di analisi: AP
Archi totali: 227,508
Archi con traffico: 186,234 (81.8%)

Statistiche Volume:
• Volume totale: 1,234,567 veicoli
• Volume massimo: 5,432
• Volume medio: 853.94
Archi congestionati (V/C > 0.9): 3,421

⏱️ Tempo verifica: 2,340ms
```

**Output se assegnazione NON eseguita:**
```
⚠️ Assegnazione PrT Non Trovata

Motivo: Attribute VolVehPrT(AP) not found - assignment not executed
Archi nella rete: 227,508

💡 L'assegnazione non è stata ancora eseguita.
```

**Verifica per periodo specifico (AM, PM, etc.):**
```bash
echo '{"jsonrpc":"2.0","id":5,"method":"tools/call","params":{"name":"visum_check_assignment","arguments":{"projectId":"100625_Versione_base_v0.3_sub_ok_priv_10176442","analysisPeriod":"AM"}}}' | node build/index.js
```

## ✅ Checklist Completa

- [ ] Progetto aperto (`project_open`)
- [ ] Segments listati (`visum_list_demand_segments`)
- [ ] Utente ha scelto quali segments usare
- [ ] Procedura creata (`visum_create_procedure`)
- [ ] DSEGSET configurato (`visum_configure_dsegset`)
- [ ] Parametri opzionali configurati (NUMITER, PRECISIONDEMAND)
- [ ] Procedura eseguita in Visum GUI
- [ ] **Assegnazione verificata (`visum_check_assignment`)** ⭐ NEW!

## 🎓 Best Practices

1. **Sempre lista i segments prima** - L'utente deve vedere cosa è disponibile
2. **Chiedi conferma** - "Vuoi usare tutti i segments o solo alcuni?"
3. **Offri opzioni chiare** - Tutti, solo C, solo H, personalizzato
4. **Verifica la configurazione** - Il tool verifica automaticamente
5. **Documenta la scelta** - Salva quale DSEGSET è stato usato

---

**Ultima modifica:** 2025-10-10  
**Tools implementati:** ✅ TUTTI  
**Status:** 🎉 PRONTO PER L'USO
