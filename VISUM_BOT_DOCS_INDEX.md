# 📚 Documentazione Visum-BOT Group

## 🎯 Per Iniziare

Quando crei procedure Visum tramite MCP, tutte le operazioni vengono **automaticamente organizzate nel gruppo "Visum-BOT"**.

---

## 📖 Documenti Disponibili

### 1. **VISUM_BOT_GROUP.md** - Documentazione Completa
**Per:** Sviluppatori e utenti tecnici
**Contiene:**
- 🔧 Come funziona il sistema
- 💻 Implementazione tecnica completa
- 📊 Tipi di operazioni create
- 🐛 Troubleshooting
- 📚 Riferimenti API Visum

**Quando usarlo:**
- Vuoi capire l'implementazione tecnica
- Stai debuggando un problema
- Vuoi modificare il codice
- Hai bisogno dei riferimenti API

---

### 2. **CLAUDE_VISUM_BOT_GUIDE.md** - Quick Reference per Claude
**Per:** AI Assistant (Claude, ChatGPT, etc.)
**Contiene:**
- 💬 Template di risposta per l'utente
- ⚠️ Punti critici da non dimenticare
- 🎨 Esempi di messaggi
- ✅ Checklist pre-risposta
- 🐛 Gestione errori comuni

**Quando usarlo:**
- Stai interagendo con l'utente
- Devi spiegare cosa è successo
- Vuoi usare template pronti
- Hai bisogno di esempi di risposta

---

### 3. **README.md** - Overview del Progetto
**Per:** Tutti
**Contiene:**
- ✨ Novità e features
- 🎯 Quick start
- 🔗 Link ai documenti principali

**Quando usarlo:**
- Primo accesso al progetto
- Vuoi una panoramica veloce
- Cerchi link alla documentazione

---

### 4. **.github/copilot-instructions.md** - Istruzioni Copilot
**Per:** GitHub Copilot
**Contiene:**
- 🔧 Linee guida del progetto
- 🛠️ Tools MCP disponibili
- ⚠️ Avvisi critici
- 🔗 Riferimenti documentazione

**Quando usarlo:**
- Stai sviluppando con Copilot
- Vuoi sapere quali tool sono disponibili
- Hai bisogno delle linee guida del progetto

---

## 🚀 Quick Reference

### Cosa fa il sistema?

**Quando crei una procedura PrT/PuT Assignment:**

1. ✅ Cerca o crea gruppo "Visum-BOT"
2. ✅ Aggiunge "Initialize Assignment" (delete) nel gruppo
3. ✅ Aggiunge "PrT/PuT Assignment" nel gruppo
4. ✅ Restituisce 3 posizioni:
   - `group_position`: Posizione del gruppo
   - `delete_position`: Posizione delete operation
   - `actual_position`: Posizione assignment operation ⭐

### Posizioni chiave

```
Position 577: [GROUP] Visum-BOT
  ├─ Position 580: Initialize Assignment (code 9)
  └─ Position 581: PrT Assignment (code 101) ⭐ USA QUESTA per DSEGSET!
```

---

## 💡 Per l'Utente

### Come vedere il gruppo in Visum?

1. Apri Visum
2. Vai a **Procedures → Operations**
3. Cerca il gruppo **"Visum-BOT"**
4. Clicca **[+]** per espandere
5. Vedi tutte le operazioni create!

### Come eliminare tutto?

**Metodo 1:** Elimina il gruppo completo
```
Click destro su "Visum-BOT" → Delete
```

**Metodo 2:** Elimina operazioni singole
```
Espandi "Visum-BOT" → Seleziona operazione → Delete
```

---

## 🤖 Per Claude/AI Assistant

### Template Risposta Base

```
✅ Ho creato la procedura nel gruppo "Visum-BOT"!

📦 Gruppo: posizione {group_position}
🗑️ Delete: posizione {delete_position}
✅ Assignment: posizione {actual_position} ⭐ Usa questa per DSEGSET!

💡 Espandi il gruppo "Visum-BOT" in Visum per vedere le operazioni!
```

### Checklist Prima di Rispondere

- [ ] Menzionato gruppo "Visum-BOT"?
- [ ] Fornite TUTTE e 3 le posizioni?
- [ ] Chiarito quale usare per DSEGSET?
- [ ] Spiegato ordine esecuzione (delete → assignment)?

---

## 🔗 Link Rapidi

- **Documentazione completa:** [VISUM_BOT_GROUP.md](VISUM_BOT_GROUP.md)
- **Guide per Claude:** [CLAUDE_VISUM_BOT_GUIDE.md](CLAUDE_VISUM_BOT_GUIDE.md)
- **API Procedures:** [VISUM_PROCEDURES_API.md](VISUM_PROCEDURES_API.md)
- **Workflow PrT:** [WORKFLOW_PRT_ASSIGNMENT.md](WORKFLOW_PRT_ASSIGNMENT.md)
- **Quick Start:** [QUICKSTART_PRT_WORKFLOW.md](QUICKSTART_PRT_WORKFLOW.md)

---

## 📊 Codici Operazione

| Tipo | Code | Descrizione |
|------|------|-------------|
| Group | 75 | Gruppo contenitore |
| Initialize Assignment | 9 | Cancella risultati (delete) |
| PrT Assignment | 101 | Assegnazione trasporto privato |
| PuT Assignment | 100 | Assegnazione trasporto pubblico |

---

## ✅ Best Practices

### Per Claude:
1. Sempre menzionare il gruppo nella risposta
2. Fornire tutte e 3 le posizioni
3. Chiarire quale usare per operazioni successive
4. Suggerire di espandere il gruppo in Visum

### Per l'Utente:
1. Controllare il gruppo regolarmente
2. Non rinominare il gruppo "Visum-BOT"
3. Espandere per vedere i dettagli
4. Eliminare quando non serve più

---

🎉 **Sistema pronto e documentato!** Tutte le operazioni MCP sono organizzate automaticamente! 🚀
