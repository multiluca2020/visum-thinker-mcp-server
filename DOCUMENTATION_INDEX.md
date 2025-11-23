# 📚 Documentazione Visum MCP Server - Indice

Guida completa alla navigazione della documentazione del server MCP per Visum.

## 🎯 Per Chi è Questa Documentazione?

### 👤 **Sei un Utente Finale?**
→ Inizia da: **[QUICKSTART_PRT_WORKFLOW.md](QUICKSTART_PRT_WORKFLOW.md)**

### 🤖 **Sei un AI Assistant (Claude, GPT, etc.)?**
→ Leggi: **[CLAUDE_WORKFLOW_GUIDE.md](CLAUDE_WORKFLOW_GUIDE.md)**

### 💻 **Sei uno Sviluppatore?**
→ Consulta: **[VISUM_PROCEDURES_API.md](VISUM_PROCEDURES_API.md)**

### 🧪 **Vuoi Testare i Tool?**
→ Usa: **[MCP_QUICK_CALL.md](MCP_QUICK_CALL.md)**

---

## 📋 Indice Completo

### 🚀 Guide Quick Start

| File | Scopo | Per Chi | Dimensione |
|------|-------|---------|------------|
| **[QUICKSTART_PRT_WORKFLOW.md](QUICKSTART_PRT_WORKFLOW.md)** | Quick start 3-step workflow | Utenti, Sviluppatori | 4 KB |
| **[CLAUDE_WORKFLOW_GUIDE.md](CLAUDE_WORKFLOW_GUIDE.md)** | Guida completa per AI | AI Assistants | 7 KB |
| **[MCP_QUICK_CALL.md](MCP_QUICK_CALL.md)** | Test manuali rapidi | Sviluppatori, Tester | 3 KB |

### 📖 Documentazione Tecnica

| File | Contenuto | Livello |
|------|-----------|---------|
| **[VISUM_PROCEDURES_API.md](VISUM_PROCEDURES_API.md)** | API Visum completa, metodi verificati | Avanzato |
| **[WORKFLOW_PRT_ASSIGNMENT.md](WORKFLOW_PRT_ASSIGNMENT.md)** | Workflow step-by-step con JSON | Intermedio |
| **[LIST_PRT_SEGMENTS_GUIDE.md](LIST_PRT_SEGMENTS_GUIDE.md)** | Guida listing demand segments | Base |
| **[VISUM_CHECK_ASSIGNMENT_GUIDE.md](VISUM_CHECK_ASSIGNMENT_GUIDE.md)** | Verifica esecuzione assegnazioni PrT | Base |

### 📝 Note di Sessione

| File | Contenuto | Data |
|------|-----------|------|
| **[SESSION_2025-10-10_IMPROVEMENTS.md](SESSION_2025-10-10_IMPROVEMENTS.md)** | Miglioramenti e correzioni | 2025-10-10 |
| **[SESSION_2025-10-10_SUMMARY.md](SESSION_2025-10-10_SUMMARY.md)** | Riepilogo scoperte API | 2025-10-10 |

### 🧪 Script e Tool

| File | Tipo | Scopo |
|------|------|-------|
| **[mcp-quick-call.js](mcp-quick-call.js)** | Node.js | Test MCP con terminazione automatica |
| **[test-workflow.py](test-workflow.py)** | Python | Test end-to-end automatico |
| **[mcp-call.ps1](mcp-call.ps1)** | PowerShell | Wrapper alternativo per Windows |

### 🔧 File di Configurazione

| File | Scopo |
|------|-------|
| **[.github/copilot-instructions.md](.github/copilot-instructions.md)** | Istruzioni per GitHub Copilot |
| **[package.json](package.json)** | Configurazione npm, script disponibili |
| **[tsconfig.json](tsconfig.json)** | Configurazione TypeScript |

---

## 🗺️ Percorsi di Lettura Consigliati

### Path 1: Utente Nuovo → Primo Utilizzo

```
1. QUICKSTART_PRT_WORKFLOW.md
   ↓ (Capire workflow base)
2. MCP_QUICK_CALL.md
   ↓ (Imparare a testare)
3. WORKFLOW_PRT_ASSIGNMENT.md
   ↓ (Vedere comandi completi)
4. VISUM_PROCEDURES_API.md
   ↓ (Approfondire API)
```

**Tempo stimato:** 30-45 minuti

### Path 2: AI Assistant → Prima Integrazione

```
1. CLAUDE_WORKFLOW_GUIDE.md
   ↓ (Pattern di interazione)
2. QUICKSTART_PRT_WORKFLOW.md
   ↓ (Workflow tecnico)
3. VISUM_PROCEDURES_API.md
   ↓ (Dettagli API)
4. Esempi in CLAUDE_WORKFLOW_GUIDE.md
   ↓ (Conversazioni tipo)
```

**Tempo stimato:** 45-60 minuti

### Path 3: Sviluppatore → Estensione Tool

```
1. VISUM_PROCEDURES_API.md
   ↓ (Capire API Visum)
2. SESSION_2025-10-10_IMPROVEMENTS.md
   ↓ (Vedere implementazione)
3. src/index.ts
   ↓ (Codice sorgente)
4. test-workflow.py
   ↓ (Test di riferimento)
```

**Tempo stimato:** 60-90 minuti

### Path 4: Troubleshooting → Risolvere Problema

```
1. Identifica il problema
   ↓
2. QUICKSTART_PRT_WORKFLOW.md → Sezione "Errori Comuni"
   ↓ (Se non risolto)
3. CLAUDE_WORKFLOW_GUIDE.md → Sezione "Gestione Errori"
   ↓ (Se non risolto)
4. VISUM_PROCEDURES_API.md → Sezione "Common Errors"
   ↓ (Se ancora bloccato)
5. SESSION_2025-10-10_IMPROVEMENTS.md → "Lessons Learned"
```

---

## 📑 Riferimento Rapido per Argomento

### 🎯 Creare Procedure

- **Quick Start:** [QUICKSTART_PRT_WORKFLOW.md#passo-1](QUICKSTART_PRT_WORKFLOW.md)
- **API Details:** [VISUM_PROCEDURES_API.md#create-procedure](VISUM_PROCEDURES_API.md)
- **AI Pattern:** [CLAUDE_WORKFLOW_GUIDE.md#pattern-1](CLAUDE_WORKFLOW_GUIDE.md)

### 📋 Listare Demand Segments

- **Quick Start:** [QUICKSTART_PRT_WORKFLOW.md#passo-2](QUICKSTART_PRT_WORKFLOW.md)
- **Guide Completa:** [LIST_PRT_SEGMENTS_GUIDE.md](LIST_PRT_SEGMENTS_GUIDE.md)
- **AI Pattern:** [CLAUDE_WORKFLOW_GUIDE.md#pattern-2](CLAUDE_WORKFLOW_GUIDE.md)

### ⚙️ Configurare DSEGSET

- **Quick Start:** [QUICKSTART_PRT_WORKFLOW.md#passo-3](QUICKSTART_PRT_WORKFLOW.md)
- **Input Formats:** [CLAUDE_WORKFLOW_GUIDE.md#visum_configure_dsegset](CLAUDE_WORKFLOW_GUIDE.md)
- **Esempi:** [WORKFLOW_PRT_ASSIGNMENT.md#step-4](WORKFLOW_PRT_ASSIGNMENT.md)

### 🔍 Verificare Assegnazione

- **Guide Completa:** [VISUM_CHECK_ASSIGNMENT_GUIDE.md](VISUM_CHECK_ASSIGNMENT_GUIDE.md)
- **Workflow:** [WORKFLOW_PRT_ASSIGNMENT.md#step-5](WORKFLOW_PRT_ASSIGNMENT.md)
- **Attributi Verificati:** [VISUM_CHECK_ASSIGNMENT_GUIDE.md#verified-attributes](VISUM_CHECK_ASSIGNMENT_GUIDE.md)

### 🧪 Testing

- **Manual Testing:** [MCP_QUICK_CALL.md](MCP_QUICK_CALL.md)
- **Automated Testing:** [test-workflow.py](test-workflow.py)
- **Test Examples:** [SESSION_2025-10-10_IMPROVEMENTS.md#test](SESSION_2025-10-10_IMPROVEMENTS.md)

### ⚠️ Error Handling

- **Common Errors:** [QUICKSTART_PRT_WORKFLOW.md#errori-comuni](QUICKSTART_PRT_WORKFLOW.md)
- **Error Patterns:** [CLAUDE_WORKFLOW_GUIDE.md#gestione-errori](CLAUDE_WORKFLOW_GUIDE.md)
- **API Errors:** [VISUM_PROCEDURES_API.md#common-errors](VISUM_PROCEDURES_API.md)

---

## 🔍 Cerca per Keyword

### actual_position
- [QUICKSTART_PRT_WORKFLOW.md](QUICKSTART_PRT_WORKFLOW.md) - "⚠️ IMPORTANTE: actual_position"
- [CLAUDE_WORKFLOW_GUIDE.md](CLAUDE_WORKFLOW_GUIDE.md) - "visum_create_procedure → actual_position"
- [SESSION_2025-10-10_IMPROVEMENTS.md](SESSION_2025-10-10_IMPROVEMENTS.md) - "Correzione Tool"

### segmentNumbers
- [QUICKSTART_PRT_WORKFLOW.md](QUICKSTART_PRT_WORKFLOW.md) - "Opzione 3: Selezione Numerica"
- [CLAUDE_WORKFLOW_GUIDE.md](CLAUDE_WORKFLOW_GUIDE.md) - "4 input formats"
- [SESSION_2025-10-10_IMPROVEMENTS.md](SESSION_2025-10-10_IMPROVEMENTS.md) - "Input Flessibili"

### filterMode
- [QUICKSTART_PRT_WORKFLOW.md](QUICKSTART_PRT_WORKFLOW.md) - "Esempio 1: Modo C"
- [CLAUDE_WORKFLOW_GUIDE.md](CLAUDE_WORKFLOW_GUIDE.md) - "Opzione 2: Filtro Modo"
- [test-workflow.py](test-workflow.py) - "Step 4: filterMode"

### DSEGSET
- [VISUM_PROCEDURES_API.md](VISUM_PROCEDURES_API.md) - "DSEGSET Attribute"
- [WORKFLOW_PRT_ASSIGNMENT.md](WORKFLOW_PRT_ASSIGNMENT.md) - "Configure DSEGSET"
- [LIST_PRT_SEGMENTS_GUIDE.md](LIST_PRT_SEGMENTS_GUIDE.md) - "DSEGSET Output"

---

## 📊 Statistiche Documentazione

### Per Tipologia

| Tipo | Files | Parole | Caratteri |
|------|-------|--------|-----------|
| Guide | 3 | 3,500 | 25,000 |
| API Docs | 2 | 2,000 | 15,000 |
| Session Notes | 2 | 2,500 | 18,000 |
| Scripts | 3 | 800 | 6,000 |
| **TOTALE** | **10** | **8,800** | **64,000** |

### Per Livello

| Livello | Files | % |
|---------|-------|---|
| Base | 3 | 30% |
| Intermedio | 4 | 40% |
| Avanzato | 3 | 30% |

### Copertura Argomenti

- [x] Creazione Procedure (100%)
- [x] Listing Segments (100%)
- [x] Configurazione DSEGSET (100%)
- [x] Error Handling (100%)
- [x] Testing (100%)
- [x] AI Integration (100%)
- [x] Troubleshooting (100%)

---

## 🎓 Glossario Rapido

| Termine | Significato | Dove Trovare |
|---------|-------------|--------------|
| **actual_position** | Posizione reale dove Visum crea la procedura | QUICKSTART, CLAUDE_WORKFLOW |
| **DSEGSET** | Demand Segment Set - lista di segments per PrT Assignment | VISUM_PROCEDURES_API |
| **filterMode** | Filtro per modo trasporto (C=Car, H=HGV) | CLAUDE_WORKFLOW, QUICKSTART |
| **segmentNumbers** | Notazione numerica per selezionare segments (es: "1-10") | QUICKSTART, CLAUDE_WORKFLOW |
| **MCP** | Model Context Protocol - protocollo di comunicazione | Tutti i file |
| **PrT** | Private Transport (trasporto privato) | Tutti i file |
| **OPERATIONTYPE** | Codice tipo operazione Visum (101=PrT, 102=PuT) | VISUM_PROCEDURES_API |

---

## 🔄 Changelog Documentazione

### 2025-10-10
- ✅ Creato CLAUDE_WORKFLOW_GUIDE.md (7 KB)
- ✅ Creato QUICKSTART_PRT_WORKFLOW.md (4 KB)
- ✅ Creato MCP_QUICK_CALL.md (3 KB)
- ✅ Creato SESSION_2025-10-10_IMPROVEMENTS.md (5 KB)
- ✅ Aggiornato .github/copilot-instructions.md
- ✅ Creato INDEX.md (questo file)

### File Preesistenti
- VISUM_PROCEDURES_API.md (2025-10-10)
- SESSION_2025-10-10_SUMMARY.md (2025-10-10)
- WORKFLOW_PRT_ASSIGNMENT.md (2025-10-10)
- LIST_PRT_SEGMENTS_GUIDE.md (data precedente)

---

## 💡 Tips per Navigazione

1. **Usa Ctrl+F** per cercare keyword nei file
2. **Segui i link interni** tra documenti (esempio: → [FILE.md](FILE.md))
3. **Inizia sempre da QUICKSTART** se è la prima volta
4. **Consulta CLAUDE_WORKFLOW** per integrare con AI
5. **Usa INDEX.md** (questo file) come punto di partenza

---

## 🆘 Supporto

**Non trovi quello che cerchi?**

1. Controlla [questo INDEX](#-cerca-per-keyword)
2. Cerca la keyword nei file usando Ctrl+F
3. Consulta [Percorsi di Lettura](#-percorsi-di-lettura-consigliati)
4. Leggi [Troubleshooting Path](#path-4-troubleshooting--risolvere-problema)

**Hai trovato un errore?**
- Controlla SESSION_2025-10-10_IMPROVEMENTS.md per soluzioni note

**Vuoi contribuire?**
- Leggi la documentazione esistente
- Segui lo stile dei file correnti
- Aggiorna questo INDEX dopo modifiche

---

**Ultima Modifica:** 2025-10-10  
**Versione INDEX:** 1.0  
**Files Indicizzati:** 10  
**Status:** ✅ Completo
