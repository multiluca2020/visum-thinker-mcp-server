# 📋 Quick Reference: Visum-BOT Group per Claude

## 🎯 Cosa Dire all'Utente

### Quando crei una procedura PrT/PuT Assignment:

```
✅ Ho creato la procedura nel gruppo "Visum-BOT"!

📦 Gruppo Visum-BOT (posizione {group_position}):
   • Tutte le operazioni MCP sono organizzate qui
   • Facile da trovare: Procedures → Operations → "Visum-BOT"
   
🗑️ Initialize Assignment (posizione {delete_position}):
   • Cancella i risultati precedenti
   • Si esegue PRIMA dell'assegnazione
   
✅ PrT Assignment (posizione {actual_position}):
   • Esegue l'assegnazione vera e propria
   • Usa questa posizione per configurare DSEGSET
   
💡 Suggerimento: Espandi il gruppo "Visum-BOT" in Visum per vedere tutte le operazioni create!
```

---

## 🔄 Workflow Automatico

### Ogni chiamata a `visum_create_procedure`:

1. **Cerca gruppo "Visum-BOT"**
   - Se esiste → lo riusa
   - Se non esiste → lo crea automaticamente

2. **Aggiunge operazioni IN FONDO al gruppo**
   - Prima: Initialize Assignment (delete)
   - Dopo: PrT/PuT Assignment

3. **Restituisce posizioni**
   - `group_position`: Posizione del gruppo
   - `delete_position`: Posizione operazione delete
   - `actual_position`: Posizione operazione assignment ⚠️ USA QUESTA per DSEGSET!

---

## ⚠️ Punti Critici per Claude

### SEMPRE:
- ✅ Menziona il gruppo "Visum-BOT" nella risposta
- ✅ Fornisci ENTRAMBE le posizioni (delete + assignment)
- ✅ Usa `actual_position` per configurare DSEGSET (NON delete_position!)
- ✅ Spiega che delete viene eseguita PRIMA

### MAI:
- ❌ NON usare la posizione richiesta dall'utente (viene ignorata)
- ❌ NON dimenticare di salvare `actual_position` per step successivi
- ❌ NON configurare DSEGSET su delete_position (usa actual_position!)

---

## 💬 Esempi di Risposta

### Esempio 1: Prima Procedura Creata

```
✅ Ho creato la tua prima procedura PrT Assignment!

Il sistema ha automaticamente:
1. 📦 Creato un gruppo "Visum-BOT" (posizione 577)
2. 🗑️ Aggiunto "Initialize Assignment" per cancellare risultati precedenti (posizione 578)
3. ✅ Aggiunto "PrT Assignment" principale (posizione 579)

Tutte le operazioni sono organizzate nel gruppo "Visum-BOT" per facile gestione!

⚠️ IMPORTANTE: Usa la posizione **579** per configurare DSEGSET nel prossimo step.

Vuoi che configuri ora i demand segments?
```

### Esempio 2: Procedura Aggiuntiva

```
✅ Ho aggiunto un'altra procedura PrT Assignment!

📦 Gruppo "Visum-BOT" (posizione 577):
   • Operazione 1: Initialize Assignment (pos 578)
   • Operazione 2: PrT Assignment (pos 579)
   • Operazione 3: Initialize Assignment (pos 580) ← NUOVO
   • Operazione 4: PrT Assignment (pos 581) ← NUOVO

Il gruppo ora contiene 4 operazioni totali.

⚠️ IMPORTANTE: Usa la posizione **581** per configurare DSEGSET su questa nuova procedura.

💡 Suggerimento: In Visum, espandi il gruppo "Visum-BOT" per vedere tutte le procedure create!
```

### Esempio 3: Utente Confuso sulle Posizioni

```
📍 Riepilogo delle Posizioni:

Gruppo "Visum-BOT": posizione 577
   ├─ Delete (pos 580): Cancella risultati vecchi
   └─ Assignment (pos 581): Esegue l'assegnazione ⭐ USA QUESTA!

Quando configuri DSEGSET, usa sempre la posizione dell'Assignment (581), 
NON quella del Delete!

Ordine di esecuzione:
1° Delete (580) → Pulisce
2° Assignment (581) → Assegna

Vuoi che proceda con la configurazione DSEGSET?
```

---

## 🎨 Template di Risposta Completa

```markdown
✅ **Procedura Visum Creata**

📦 **Organizzazione:**
Tutte le operazioni sono nel gruppo "Visum-BOT" (posizione {group_position})

🔄 **Operazioni Create:**
1. Initialize Assignment (posizione {delete_position})
   • Tipo: Delete results
   • Eseguita per prima
   
2. PrT Assignment (posizione {actual_position})
   • Tipo: Main assignment
   • Eseguita per seconda
   • ⭐ **Usa questa posizione per DSEGSET!**

⏱️ Tempo: {execution_time}ms

💡 **Prossimi Step:**
1. Lista i demand segments disponibili
2. Configura DSEGSET sulla posizione {actual_position}
3. Esegui la procedura

Vuoi che proceda con la configurazione dei demand segments?
```

---

## 🐛 Gestione Errori

### Se l'utente chiede posizioni diverse:

```
⚠️ Nota: La posizione richiesta (20) viene ignorata.

Il sistema usa posizioni relative all'interno del gruppo "Visum-BOT":
• Prima operazione nel gruppo: posizione relativa 1
• Seconda operazione: posizione relativa 2
• E così via...

La posizione ASSOLUTA finale dipende da quante operazioni ci sono già.
Ho creato le operazioni alle posizioni assolute {delete_position} e {actual_position}.
```

### Se l'utente non trova il gruppo:

```
🔍 Per trovare il gruppo "Visum-BOT" in Visum:

1. Apri Visum
2. Vai a Procedures → Operations
3. Scorri la lista fino a trovare un'operazione di tipo "Group"
4. Il nome dovrebbe essere "Visum-BOT"
5. Clicca sul [+] per espandere e vedere le operazioni interne

Se non lo vedi, potrebbe essere collassato. Cerca l'icona di una cartella.
```

---

## 📚 Riferimenti Veloci

- **Documentazione completa:** `VISUM_BOT_GROUP.md`
- **API Procedures:** `VISUM_PROCEDURES_API.md`
- **Workflow PrT:** `WORKFLOW_PRT_ASSIGNMENT.md`
- **Operation codes:**
  - Group: 75
  - Initialize Assignment: 9
  - PrT Assignment: 101
  - PuT Assignment: 100

---

## ✅ Checklist per Claude

Prima di rispondere all'utente:
- [ ] Ho menzionato il gruppo "Visum-BOT"?
- [ ] Ho fornito la posizione del gruppo?
- [ ] Ho fornito ENTRAMBE le posizioni (delete + assignment)?
- [ ] Ho chiarito quale posizione usare per DSEGSET?
- [ ] Ho spiegato l'ordine di esecuzione (delete → assignment)?
- [ ] Ho suggerito di espandere il gruppo in Visum?
- [ ] Ho salvato `actual_position` per step successivi?
