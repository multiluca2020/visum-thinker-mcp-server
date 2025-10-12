# 🚀 Quick Start: Visum PrT Assignment Workflow

Guida rapida per creare e configurare procedure PrT Assignment in Visum usando i tool MCP.

## 📋 Prerequisiti

1. ✅ Progetto Visum aperto (usa `project_open`)
2. ✅ Server MCP attivo
3. ✅ Conoscenza del Project ID

## 🎯 Workflow in 3 Passi

### Passo 1️⃣: Crea la Procedura

```javascript
// Tool: visum_create_procedure
{
  "projectId": "your_project_id",
  "procedureType": "PrT_Assignment"
}

// Risposta:
{
  "actual_position": 580,  // ⚠️ SALVA QUESTO!
  "requested_position": 20,
  "message": "...created successfully at position 580..."
}
```

**⚠️ IMPORTANTE:** La procedura viene creata alla fine (es: posizione 580), NON alla posizione richiesta (20)!

### Passo 2️⃣: Mostra Segments all'Utente

```javascript
// Tool: visum_list_demand_segments
{
  "projectId": "your_project_id"
}

// Risposta: Lista numerata 1-36
Mode C (Car): 1-24
Mode H (HGV): 25-36

💡 4 Opzioni per l'utente:
1. "tutti" - Tutti i segments
2. "solo C" - Solo modo Car
3. "1-10,15" - Selezione numerica
4. "C_CORRETTA_AM,..." - Codici espliciti
```

### Passo 3️⃣: Configura DSEGSET

```javascript
// Tool: visum_configure_dsegset
{
  "projectId": "your_project_id",
  "procedurePosition": 580,  // ⚠️ Usa actual_position del Passo 1!
  
  // UNA delle seguenti opzioni:
  "segmentNumbers": "1-10",    // Opzione 3: numeri
  "filterMode": "C",           // Opzione 2: filtro modo
  "dsegset": "ALL"             // Opzione 1: tutti (o usa filterMode se fallisce)
}

// Risposta:
{
  "segment_count": 10,
  "message": "DSEGSET configured with 10 demand segments"
}
```

## 🎭 Esempi Pratici

### Esempio 1: Tutti i Segments Modo C

```javascript
// 1. Crea
visum_create_procedure({
  projectId: "100625_...",
  procedureType: "PrT_Assignment"
})
// → actual_position: 580

// 2. Lista (mostra all'utente)
visum_list_demand_segments({ projectId: "100625_..." })
// Utente sceglie: "solo C"

// 3. Configura
visum_configure_dsegset({
  projectId: "100625_...",
  procedurePosition: 580,
  filterMode: "C"
})
// → 24 segments configurati
```

### Esempio 2: Primi 10 Segments

```javascript
// 1. Crea → position 581
// 2. Lista → mostra 1-36
// 3. Utente: "i primi 10"
visum_configure_dsegset({
  projectId: "100625_...",
  procedurePosition: 581,
  segmentNumbers: "1-10"
})
// → 10 segments configurati
```

### Esempio 3: Segments Specifici

```javascript
// 1. Crea → position 582
// 2. Lista → mostra tutti
// 3. Utente: "1,5,10-15,20"
visum_configure_dsegset({
  projectId: "100625_...",
  procedurePosition: 582,
  segmentNumbers: "1,5,10-15,20"
})
// → 9 segments configurati (1,5,10,11,12,13,14,15,20)
```

## 🤖 Per AI Assistants (Claude, etc.)

**Pattern di conversazione:**

```
👤 UTENTE: "Crea una procedura di assegnazione PrT"

🤖 AI:
1. Chiama visum_create_procedure
2. Salva actual_position (es: 580)
3. Rispondi: "✅ Creata alla posizione 580. 
             Vuoi configurare i demand segments?"

👤 UTENTE: "Sì"

🤖 AI:
4. Chiama visum_list_demand_segments
5. Mostra lista numerata all'utente
6. Spiega le 4 opzioni
7. Aspetta scelta utente

👤 UTENTE: "Solo modo C"

🤖 AI:
8. Chiama visum_configure_dsegset con:
   - procedurePosition: 580 (quello salvato!)
   - filterMode: "C"
9. Conferma: "✅ Configurati 24 segments modo C sulla procedura 580!"
```

**Vedi `CLAUDE_WORKFLOW_GUIDE.md` per esempi completi!**

## ⚠️ Errori Comuni

### ❌ Errore 1: Posizione Sbagliata

```javascript
// ❌ SBAGLIATO:
visum_create_procedure() // → actual_position: 580
visum_configure_dsegset({ procedurePosition: 20 }) // ❌ Fallisce!

// ✅ CORRETTO:
const response = visum_create_procedure()
visum_configure_dsegset({ 
  procedurePosition: response.actual_position // 580 ✅
})
```

### ❌ Errore 2: Non Mostrare Opzioni

```javascript
// ❌ SBAGLIATO:
visum_create_procedure()
visum_configure_dsegset({ dsegset: "ALL" }) // Decide senza chiedere!

// ✅ CORRETTO:
visum_create_procedure()
visum_list_demand_segments() // Mostra lista
// Chiedi all'utente quale opzione vuole
visum_configure_dsegset({ ... }) // Basato su scelta utente
```

### ❌ Errore 3: ALL Keyword Fallisce

```javascript
// ❌ Se "ALL" fallisce:
visum_configure_dsegset({ dsegset: "ALL" })
// → Error: Failed to get all segments

// ✅ SOLUZIONE: Usa filterMode
visum_configure_dsegset({ filterMode: "C" }) // Solo C
// Poi
visum_configure_dsegset({ filterMode: "H" }) // Aggiungi H
```

## 🧪 Test Manuale

### Opzione 1: Script Wrapper (Raccomandato)

```powershell
# Usa mcp-quick-call.js (termina automaticamente)
node mcp-quick-call.js visum_create_procedure '{\"projectId\":\"...\",\"procedureType\":\"PrT_Assignment\"}'
```

### Opzione 2: Test Automatico

```powershell
# Test completo end-to-end
python test-workflow.py
```

### Opzione 3: Echo Manuale (Ctrl+C per uscire)

```powershell
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"visum_create_procedure","arguments":{...}}}' | node build/index.js
# Premi Ctrl+C dopo la risposta
```

**Vedi `MCP_QUICK_CALL.md` per dettagli completi sul testing!**

## 📚 Documentazione Completa

| File | Descrizione |
|------|-------------|
| **CLAUDE_WORKFLOW_GUIDE.md** | 🤖 Guida completa per AI assistants con esempi di conversazione |
| **VISUM_PROCEDURES_API.md** | 📖 Documentazione API Visum completa |
| **WORKFLOW_PRT_ASSIGNMENT.md** | 📋 Workflow step-by-step con comandi JSON |
| **MCP_QUICK_CALL.md** | 🧪 Guida per test manuali rapidi |
| **test-workflow.py** | ✅ Script di test automatico |

## 🎯 Checklist Rapida

Prima di configurare una procedura, verifica:

- [ ] Ho chiamato `visum_create_procedure`?
- [ ] Ho salvato `actual_position` dalla risposta?
- [ ] Ho mostrato la lista segments all'utente?
- [ ] Ho spiegato le 4 opzioni di selezione?
- [ ] Sto usando `actual_position` per `visum_configure_dsegset`?
- [ ] Ho confermato l'operazione all'utente?

## 💡 Tips & Tricks

### 1. Filtrare per Naming Pattern

```javascript
// Se utente dice: "Solo CORRETTA"
// 1. Lista segments
// 2. Identifica quali hanno "CORRETTA" nel nome:
//    - Modo C: posizioni 1-6 (C_CORRETTA_AM ... C_CORRETTA_S)
// 3. Usa: segmentNumbers: "1-6"
```

### 2. Combinare Time Slots

```javascript
// Se utente dice: "Solo AM e PM"
// 1. Identifica posizioni con "_AM" o "_PM"
//    - C_CORRETTA_AM (1), C_CORRETTA_PM (5)
//    - C_INIZIALE_AM (7), C_INIZIALE_PM (11)
//    - etc.
// 2. Usa: segmentNumbers: "1,5,7,11,13,17,19,23,25,29,31,35"
```

### 3. Test Incrementale

```powershell
# 1. Prima lista per esplorare
node mcp-quick-call.js visum_list_demand_segments '{\"projectId\":\"...\"}'

# 2. Poi crea
node mcp-quick-call.js visum_create_procedure '{\"projectId\":\"...\",\"procedureType\":\"PrT_Assignment\"}'
# Nota la posizione restituita!

# 3. Infine configura
node mcp-quick-call.js visum_configure_dsegset '{\"projectId\":\"...\",\"procedurePosition\":580,\"filterMode\":\"C\"}'
```

## 🆘 Supporto

Per problemi o domande:

1. Consulta `CLAUDE_WORKFLOW_GUIDE.md` per pattern completi
2. Controlla `VISUM_PROCEDURES_API.md` per dettagli API
3. Esegui `python test-workflow.py` per verificare che tutto funzioni
4. Usa `node mcp-quick-call.js` per test rapidi

---

**Versione:** 1.0  
**Data:** 2025-10-10  
**Status:** ✅ Production Ready
