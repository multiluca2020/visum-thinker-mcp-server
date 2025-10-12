# 🤖 Guida Claude: Workflow Interattivo PrT Assignment

Questa guida spiega come **Claude** (o qualsiasi AI assistant) deve usare i tool MCP per creare procedure Visum in modo interattivo con l'utente.

## 📋 Indice

1. [Workflow Completo](#workflow-completo)
2. [Tool Disponibili](#tool-disponibili)
3. [Pattern di Interazione](#pattern-di-interazione)
4. [Esempi di Conversazione](#esempi-di-conversazione)
5. [Gestione Errori](#gestione-errori)
6. [Best Practices](#best-practices)

---

## 🎯 Workflow Completo

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. UTENTE: "Crea una procedura di assegnazione al trasporto    │
│             privato"                                            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 2. CLAUDE: Chiama visum_create_procedure                       │
│    • Tipo: PrT_Assignment                                       │
│    • Nota la POSIZIONE EFFETTIVA restituita (es: 580)          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 3. CLAUDE: "Ho creato la procedura alla posizione 580.         │
│             Vuoi configurare i demand segments?"                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 4. UTENTE: "Sì, mostrami i segments disponibili"               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 5. CLAUDE: Chiama visum_list_demand_segments                   │
│    • Mostra lista numerata (1-36)                               │
│    • Spiega le 4 opzioni di selezione                           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 6. UTENTE: Sceglie una delle 4 opzioni:                        │
│    • "Tutti" → dsegset: "ALL"                                   │
│    • "Solo C" → filterMode: "C"                                 │
│    • "1-10,15" → segmentNumbers: "1-10,15"                      │
│    • "C_CORRETTA_AM,..." → dsegset: "C_CORRETTA_AM,..."         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 7. CLAUDE: Chiama visum_configure_dsegset                      │
│    • procedurePosition: 580 (quella del passo 2!)               │
│    • Parametro appropriato basato su scelta utente              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 8. CLAUDE: "✅ Configurati N segments. La procedura alla       │
│             posizione 580 è pronta per l'esecuzione!"           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tool Disponibili

### 1. `visum_create_procedure`

**Scopo:** Crea una nuova procedura Visum.

**Parametri:**
```typescript
{
  projectId: string,           // ID del progetto Visum aperto
  procedureType: "PrT_Assignment" | "PuT_Assignment" | "Demand_Model" | "Matrix_Calculation",
  position?: number,           // Opzionale, default: 20 (viene ignorato, è solo per backward compatibility)
  parameters?: object          // Opzionale, parametri aggiuntivi
}
```

**Risposta Importante:**
```json
{
  "actual_position": 580,      // ⚠️ QUESTA È LA POSIZIONE REALE!
  "requested_position": 20,
  "message": "...created successfully at position 580..."
}
```

**⚠️ IMPORTANTE:** 
- La procedura NON viene creata alla posizione richiesta!
- Visum aggiunge la procedura alla FINE (ultima posizione disponibile)
- **Devi usare `actual_position` per i passi successivi!**

**Esempio di chiamata:**
```json
{
  "name": "visum_create_procedure",
  "arguments": {
    "projectId": "100625_Versione_base_v0.3_sub_ok_priv_10176442",
    "procedureType": "PrT_Assignment"
  }
}
```

---

### 2. `visum_list_demand_segments`

**Scopo:** Elenca tutti i demand segments PrT disponibili con numerazione.

**Parametri:**
```typescript
{
  projectId: string,
  filterMode?: string          // Opzionale: "C", "H", ecc.
}
```

**Risposta:**
- Lista numerata da 1 a N (es: 36 segments)
- Segments raggruppati per modo (C, H, etc.)
- DSEGSET completo per tutti i segments
- 4 opzioni per la selezione

**Output Tipico:**
```
Mode C (Car → TSys CAR):
  1. C_CORRETTA_AM
  2. C_CORRETTA_IP1
  ...
  24. C_NESTED_S

Mode H (HGV → TSys HGV):
  25. H_CORRETTA_AM
  ...
  36. H_INIZIALE_S

💡 Come procedere:
Opzione 1 - Tutti i segments: "tutti"
Opzione 2 - Solo un modo: "Solo C"
Opzione 3 - Selezione numerica: "1,2,3" o "1-10"
Opzione 4 - Copia manuale: copia i codici
```

**Esempio di chiamata:**
```json
{
  "name": "visum_list_demand_segments",
  "arguments": {
    "projectId": "100625_Versione_base_v0.3_sub_ok_priv_10176442"
  }
}
```

---

### 3. `visum_configure_dsegset`

**Scopo:** Configura i demand segments su una procedura PrT Assignment.

**Parametri (Uno dei seguenti):**
```typescript
{
  projectId: string,
  procedurePosition: number,   // ⚠️ Usa actual_position dal passo 1!
  
  // OPZIONE 1: Keyword "ALL"
  dsegset?: "ALL" | "tutti",
  
  // OPZIONE 2: Filtro per modo
  filterMode?: "C" | "H",
  
  // OPZIONE 3: Selezione numerica
  segmentNumbers?: "1,2,3" | "1-10" | "1-10,15,20",
  
  // OPZIONE 4: DSEGSET esplicito
  dsegset?: "C_CORRETTA_AM,C_CORRETTA_IP1,...",
  
  // Parametri aggiuntivi opzionali
  numIterations?: number,
  precisionDemand?: number
}
```

**Mapping Risposta Utente → Parametro:**

| Risposta Utente | Parametro da usare |
|-----------------|-------------------|
| "tutti", "ALL", "usa tutti" | `dsegset: "ALL"` |
| "solo C", "Solo modo C" | `filterMode: "C"` |
| "1,2,3", "1-10", "1-5,10-15" | `segmentNumbers: "1-10"` |
| "C_CORRETTA_AM,..." | `dsegset: "C_CORRETTA_AM,..."` |

**Esempio di chiamata:**
```json
{
  "name": "visum_configure_dsegset",
  "arguments": {
    "projectId": "100625_Versione_base_v0.3_sub_ok_priv_10176442",
    "procedurePosition": 580,
    "segmentNumbers": "1-10"
  }
}
```

---

## 💬 Pattern di Interazione

### Pattern 1: Creazione Base

```
UTENTE: "Crea una procedura di assegnazione PrT"

CLAUDE FLOW:
1. Chiama visum_create_procedure con tipo PrT_Assignment
2. Estrae actual_position dalla risposta (es: 580)
3. Risponde: "✅ Ho creato una procedura PrT Assignment alla posizione 580.
              Vuoi configurare i demand segments ora?"

UTENTE: "Sì"

CLAUDE FLOW:
4. Chiama visum_list_demand_segments
5. Mostra la lista numerata all'utente
6. Spiega le 4 opzioni di selezione
7. Aspetta la scelta dell'utente

UTENTE: "Usa i primi 10"

CLAUDE FLOW:
8. Interpreta "primi 10" → segmentNumbers: "1-10"
9. Chiama visum_configure_dsegset con:
   - procedurePosition: 580
   - segmentNumbers: "1-10"
10. Conferma: "✅ Configurati 10 demand segments sulla procedura 580!"
```

### Pattern 2: Lista Prima, Poi Crea

```
UTENTE: "Quali demand segments PrT sono disponibili?"

CLAUDE FLOW:
1. Chiama visum_list_demand_segments
2. Mostra la lista completa
3. Risponde: "Ho trovato 36 demand segments. Vuoi creare una procedura 
              di assegnazione con alcuni di questi?"

UTENTE: "Sì, crea una procedura con solo il modo C"

CLAUDE FLOW:
4. Chiama visum_create_procedure
5. Estrae actual_position (es: 581)
6. Chiama subito visum_configure_dsegset con:
   - procedurePosition: 581
   - filterMode: "C"
7. Conferma: "✅ Creata procedura alla posizione 581 con 24 segments modo C!"
```

### Pattern 3: Configurazione Avanzata

```
UTENTE: "Crea una procedura PrT con i segments CORRETTA del modo C"

CLAUDE FLOW:
1. Chiama visum_create_procedure → posizione 582
2. Chiama visum_list_demand_segments
3. Identifica quali sono i "CORRETTA" del modo C:
   - 1. C_CORRETTA_AM
   - 2. C_CORRETTA_IP1
   - 3. C_CORRETTA_IP2
   - 4. C_CORRETTA_IP3
   - 5. C_CORRETTA_PM
   - 6. C_CORRETTA_S
4. Chiama visum_configure_dsegset con:
   - procedurePosition: 582
   - segmentNumbers: "1-6"
5. Conferma i segments configurati
```

---

## 🎭 Esempi di Conversazione

### Esempio 1: Workflow Base

```
👤 UTENTE:
Crea una procedura di assegnazione al trasporto privato

🤖 CLAUDE:
[Chiama: visum_create_procedure con PrT_Assignment]
[Riceve: actual_position = 580]

Perfetto! Ho creato una procedura PrT Assignment alla posizione 580.

Vuoi configurare i demand segments per questa procedura? 
Se sì, posso mostrarti i segments disponibili.

👤 UTENTE:
Sì, mostrami i segments

🤖 CLAUDE:
[Chiama: visum_list_demand_segments]
[Riceve: 36 segments, 24 modo C + 12 modo H]

Ho trovato 36 demand segments disponibili:

**Modo C (Car):** segments 1-24
  1. C_CORRETTA_AM
  2. C_CORRETTA_IP1
  ...
  24. C_NESTED_S

**Modo H (HGV):** segments 25-36
  25. H_CORRETTA_AM
  ...
  36. H_INIZIALE_S

Come vuoi procedere?

**Opzione 1:** "tutti" - Usa tutti e 36 i segments
**Opzione 2:** "solo C" o "solo H" - Filtra per modo
**Opzione 3:** "1-10" o "1,5,10-15" - Seleziona per numeri
**Opzione 4:** Copia e incolla i codici specifici

👤 UTENTE:
Solo modo C

🤖 CLAUDE:
[Chiama: visum_configure_dsegset con filterMode: "C", procedurePosition: 580]
[Riceve: 24 segments configurati]

✅ Perfetto! Ho configurato la procedura alla posizione 580 con tutti 
   e 24 i demand segments del modo C (Car).

La procedura è pronta per l'esecuzione. Puoi trovarla in Visum:
Procedures → Operations → Posizione 580
```

### Esempio 2: Richiesta Specifica

```
👤 UTENTE:
Crea assegnazione PrT solo per i primi 5 time slots del modo car

🤖 CLAUDE:
[Chiama: visum_list_demand_segments per capire quali sono]
[Identifica: 1-5 = C_CORRETTA_AM, IP1, IP2, IP3, PM]

[Chiama: visum_create_procedure]
[Riceve: actual_position = 583]

[Chiama: visum_configure_dsegset con segmentNumbers: "1-5"]

✅ Ho creato una procedura PrT Assignment alla posizione 583 
   configurata con i primi 5 time slots del modo Car:
   
   1. C_CORRETTA_AM
   2. C_CORRETTA_IP1
   3. C_CORRETTA_IP2
   4. C_CORRETTA_IP3
   5. C_CORRETTA_PM

La procedura è pronta!
```

### Esempio 3: Modifica Successiva

```
👤 UTENTE:
Cambia la procedura 580 per usare solo i segments INIZIALE

🤖 CLAUDE:
[Chiama: visum_list_demand_segments]
[Identifica INIZIALE nel modo C: posizioni 7-12]

[Chiama: visum_configure_dsegset con:
  procedurePosition: 580,
  segmentNumbers: "7-12"]

✅ Ho riconfigurato la procedura alla posizione 580.
   Ora usa solo i 6 segments INIZIALE del modo C:
   
   7. C_INIZIALE_AM
   8. C_INIZIALE_IP1
   9. C_INIZIALE_IP2
   10. C_INIZIALE_IP3
   11. C_INIZIALE_PM
   12. C_INIZIALE_S
```

---

## ⚠️ Gestione Errori

### Errore 1: Posizione non trovata

```json
{
  "error": "OPERATION: ItemByKey failed for position 999"
}
```

**Causa:** Stai usando una posizione inesistente.

**Soluzione Claude:**
```
❌ La posizione 999 non esiste. 
   Ricordi la posizione restituita quando hai creato la procedura?
   Dovrebbe essere un numero tipo 576-580.
```

### Errore 2: Progetto non aperto

```json
{
  "error": "Project with ID ... not found"
}
```

**Soluzione Claude:**
```
❌ Il progetto Visum non è aperto.
   Vuoi che lo apra? [Usa visum_project_open tool]
```

### Errore 3: ALL keyword fallisce

```json
{
  "error": "Failed to get all segments"
}
```

**Soluzione Claude:**
```
⚠️ C'è stato un problema con la keyword "ALL".
   Posso usare un metodo alternativo:
   - Filtro per modo C: configura tutti i 24 segments Car
   - Filtro per modo H: configura tutti i 12 segments HGV
   
   Quale preferisci?
```

---

## ✅ Best Practices per Claude

### 1. **Sempre Salvare actual_position**

```javascript
// ❌ SBAGLIATO:
const position = 20; // Posizione richiesta
configureDsegset(position); // Questa fallirà!

// ✅ CORRETTO:
const response = await createProcedure();
const actualPosition = response.result.actual_position; // 580
configureDsegset(actualPosition); // Questa funziona!
```

### 2. **Mostrare sempre la lista prima**

```
// ✅ BUONO:
"Ho trovato 36 segments. Ecco la lista numerata..."
[mostra lista]
"Come vuoi procedere?"

// ❌ CATTIVO:
"Configuro tutti i segments automaticamente"
[chiama configure senza chiedere]
```

### 3. **Interpretare le richieste utente**

| Richiesta Vaga | Interpretazione | Azione |
|----------------|-----------------|---------|
| "tutti" | Tutti i segments | `dsegset: "ALL"` o `filterMode` per entrambi |
| "primi 10" | Segments 1-10 | `segmentNumbers: "1-10"` |
| "solo car" | Modo C | `filterMode: "C"` |
| "CORRETTA" | Segments con nome CORRETTA | Identifica numeri e usa `segmentNumbers` |
| "AM e PM" | Time slots AM e PM | Identifica numeri (1,5,7,11,...) |

### 4. **Confermare sempre**

```
✅ "Ho configurato 10 demand segments sulla procedura 580"
✅ "La procedura è pronta alla posizione 580"
✅ "Puoi trovarla in Visum: Procedures → Operations → 580"
```

### 5. **Gestire richieste ambigue**

```
👤 UTENTE: "Configura alcuni segments"

🤖 CLAUDE: ❌ Non procedere automaticamente!

✅ Invece:
"Quali segments vuoi configurare? Posso mostrarti la lista 
 numerata per aiutarti a scegliere."
```

---

## 🔄 Workflow Completo Codificato

```typescript
// Pseudo-codice per Claude

async function handlePrTAssignmentRequest(userRequest: string) {
  
  // Step 1: Crea la procedura
  const createResponse = await mcp.call("visum_create_procedure", {
    projectId: getCurrentProjectId(),
    procedureType: "PrT_Assignment"
  });
  
  const procedurePosition = createResponse.result.actual_position;
  
  // Step 2: Conferma e chiedi se configurare
  await sendMessage(`✅ Ho creato una procedura PrT Assignment alla posizione ${procedurePosition}.
Vuoi configurare i demand segments?`);
  
  const userWantsConfigure = await waitForUserResponse();
  if (!userWantsConfigure) return;
  
  // Step 3: Mostra lista segments
  const listResponse = await mcp.call("visum_list_demand_segments", {
    projectId: getCurrentProjectId()
  });
  
  await sendMessage(formatSegmentList(listResponse));
  await sendMessage(`Come vuoi procedere?
1. "tutti" - Tutti i segments
2. "solo C" - Solo modo Car
3. "1-10" - Selezione numerica
4. Copia i codici specifici`);
  
  // Step 4: Aspetta scelta utente
  const userChoice = await waitForUserResponse();
  
  // Step 5: Interpreta la scelta
  const configParams = interpretUserChoice(userChoice);
  configParams.projectId = getCurrentProjectId();
  configParams.procedurePosition = procedurePosition; // ⚠️ IMPORTANTE!
  
  // Step 6: Configura DSEGSET
  const configResponse = await mcp.call("visum_configure_dsegset", configParams);
  
  // Step 7: Conferma finale
  const segmentCount = extractSegmentCount(configResponse);
  await sendMessage(`✅ Configurati ${segmentCount} demand segments sulla procedura ${procedurePosition}!
La procedura è pronta per l'esecuzione.`);
}

function interpretUserChoice(choice: string): object {
  const lower = choice.toLowerCase();
  
  if (lower.includes("tutti") || lower.includes("all")) {
    return { filterMode: "C" }; // Usa filterMode invece di ALL che ha bug
  }
  
  if (lower.includes("solo c") || lower.includes("car")) {
    return { filterMode: "C" };
  }
  
  if (lower.includes("solo h") || lower.includes("hgv")) {
    return { filterMode: "H" };
  }
  
  // Check se è notazione numerica
  if (/^\d+(-\d+)?(,\d+(-\d+)?)*$/.test(choice.trim())) {
    return { segmentNumbers: choice.trim() };
  }
  
  // Altrimenti assume sia DSEGSET esplicito
  return { dsegset: choice };
}
```

---

## 📚 Riferimenti

- **VISUM_PROCEDURES_API.md** - Documentazione API completa
- **WORKFLOW_PRT_ASSIGNMENT.md** - Workflow step-by-step
- **MCP_QUICK_CALL.md** - Come testare i tool manualmente
- **test-workflow.py** - Script di test automatico

---

## 🎯 Checklist per Claude

Prima di procedere, verifica:

- [ ] Ho chiamato `visum_create_procedure`?
- [ ] Ho salvato la `actual_position` restituita?
- [ ] Ho mostrato la lista segments all'utente?
- [ ] Ho spiegato le 4 opzioni di selezione?
- [ ] Ho interpretato correttamente la scelta utente?
- [ ] Sto usando `actual_position` (non 20!) per `visum_configure_dsegset`?
- [ ] Ho confermato l'operazione all'utente?
- [ ] Ho indicato dove trovare la procedura in Visum?

---

**Versione:** 1.0  
**Data:** 2025-10-10  
**Autore:** Visum Thinker MCP Server  
**Status:** ✅ Pronto per Produzione
