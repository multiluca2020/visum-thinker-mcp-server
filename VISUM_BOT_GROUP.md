# 📦 Visum-BOT Group - Gestione Automatica delle Procedure

## 🎯 Panoramica

Quando crei procedure Visum tramite MCP (Model Context Protocol), tutte le operazioni vengono automaticamente organizzate in un **gruppo dedicato chiamato "Visum-BOT"**. Questo permette una gestione pulita e isolata delle operazioni create automaticamente.

---

## 🔧 Come Funziona

### 1. **Primo Utilizzo: Creazione del Gruppo**

Quando crei la prima procedura (es. PrT Assignment), il sistema:

```python
# 1. Cerca gruppo "Visum-BOT" esistente
# 2. Se NON esiste, lo crea automaticamente
# 3. Posiziona il gruppo alla fine della lista top-level
```

**Risultato in Visum:**
```
Procedures → Operations:
  ...operazioni esistenti...
  Position 577: [GROUP] Visum-BOT
    ├─ Position 578: Initialize Assignment (code 9)
    └─ Position 579: PrT Assignment (code 101)
```

### 2. **Utilizzi Successivi: Riuso del Gruppo**

Nelle chiamate successive, il sistema:

```python
# 1. Trova il gruppo "Visum-BOT" esistente
# 2. Conta le operazioni già presenti nel gruppo
# 3. Aggiunge le nuove operazioni IN FONDO al gruppo
```

**Risultato dopo seconda chiamata:**
```
Position 577: [GROUP] Visum-BOT
  ├─ Position 578: Initialize Assignment (call #1)
  ├─ Position 579: PrT Assignment (call #1)
  ├─ Position 580: Initialize Assignment (call #2) ← NUOVO
  └─ Position 581: PrT Assignment (call #2)       ← NUOVO
```

---

## ✅ Vantaggi di questo Approccio

### Per l'Utente:
- ✅ **Organizzazione:** Tutte le operazioni MCP sono raggruppate
- ✅ **Visibilità:** Facile vedere cosa ha fatto il BOT
- ✅ **Gestione:** Elimina l'intero gruppo per rimuovere tutto
- ✅ **Isolamento:** Non si mischiano con operazioni manuali

### Per Claude/AI:
- ✅ **Controllo:** Può vedere tutte le operazioni create nel gruppo
- ✅ **Debug:** Facile identificare problemi nelle operazioni create
- ✅ **Tracciabilità:** Ogni operazione è tracciabile nel gruppo
- ✅ **Riutilizzo:** Può modificare/cancellare operazioni specifiche nel gruppo

---

## 🔍 Implementazione Tecnica

### Codice di Ricerca del Gruppo

```python
# Cerca gruppo "Visum-BOT" esistente per nome
all_ops = list(operations_container.GetAll)
for op in all_ops:
    op_type = op.AttValue("OPERATIONTYPE")
    if op_type == 75:  # Group type
        group_params = op.GroupParameters
        group_name = group_params.AttValue("Name")
        if group_name == "Visum-BOT":
            visum_bot_group = op
            break
```

### Codice di Creazione del Gruppo

```python
if visum_bot_group is None:
    # Conta operazioni top-level
    top_level_ops = operations_container.GetChildren()
    top_level_count = len(list(top_level_ops)) if top_level_ops else 0
    
    # Crea gruppo alla fine
    visum_bot_group = operations_container.AddOperation(top_level_count + 1)
    visum_bot_group.SetAttValue("OPERATIONTYPE", 75)  # Group type
    
    # Imposta nome del gruppo
    group_params = visum_bot_group.GroupParameters
    group_params.SetAttValue("Name", "Visum-BOT")
```

### Codice di Aggiunta Operazioni

```python
# Conta operazioni già nel gruppo
group_children = operations_container.GetChildren(visum_bot_group)
group_children_count = len(list(group_children)) if group_children else 0

# Aggiungi delete operation IN FONDO al gruppo
delete_rel_pos = group_children_count + 1
delete_op = operations_container.AddOperation(delete_rel_pos, visum_bot_group)
delete_op.SetAttValue("OPERATIONTYPE", 9)  # Initialize Assignment

# Aggiungi assignment operation IN FONDO al gruppo
assignment_rel_pos = group_children_count + 2
assignment_op = operations_container.AddOperation(assignment_rel_pos, visum_bot_group)
assignment_op.SetAttValue("OPERATIONTYPE", 101)  # PrT Assignment
```

---

## 📊 Tipi di Operazioni Create

### PrT Assignment

Quando crei una procedura `PrT_Assignment`, vengono create **DUE operazioni**:

1. **Initialize Assignment (code 9)** - Cancella risultati precedenti
2. **PrT Assignment (code 101)** - Esegue l'assegnazione

**Ordine di esecuzione:**
```
1. Initialize Assignment → Pulisce i risultati
2. PrT Assignment → Esegue l'assegnazione
```

### PuT Assignment

Quando crei una procedura `PuT_Assignment`, vengono create **DUE operazioni**:

1. **Initialize Assignment (code 9)** - Cancella risultati precedenti
2. **PuT Assignment (code 100)** - Esegue l'assegnazione

---

## 🎨 Esempio di Output MCP

```json
{
  "status": "success",
  "procedure_type": "PrT_Assignment",
  "operation_code": 101,
  "group_position": 577,
  "group_name": "Visum-BOT",
  "delete_position": 580,
  "actual_position": 581,
  "message": "Visum-BOT group at position 577. Delete operation at 580, PrT_Assignment at 581 (both inside group)"
}
```

**Messaggio per l'utente:**
```
✅ Procedura Visum Creata nel Gruppo "Visum-BOT"

📦 Gruppo: Visum-BOT
   • Posizione gruppo: 577

🗑️ Delete Assignment Results:
   • Posizione: 580
   • Tipo: Initialize Assignment (code 9)
   • Dentro gruppo: Visum-BOT

✅ PrT_Assignment:
   • Posizione: 581
   • Tipo: PrT Assignment (code 101)
   • Dentro gruppo: Visum-BOT
   • Verificata: ✅

⚠️ IMPORTANTE:
• Tutte le operazioni sono nel gruppo Visum-BOT (posizione 577)
• Delete: posizione 580
• Assignment: posizione 581
• Usa posizione 581 per configurare DSEGSET!

💡 Suggerimento: Tutte le operazioni MCP sono organizzate nel gruppo "Visum-BOT" per facile gestione!
```

---

## 🔄 Workflow Completo per Claude

### Scenario: Utente chiede "Crea una procedura PrT Assignment"

```javascript
// Step 1: Claude chiama visum_create_procedure
mcp.call('visum_create_procedure', {
  projectId: "...",
  procedureType: "PrT_Assignment",
  position: 20  // Ignorato, usa posizioni relative nel gruppo
})

// Step 2: Sistema automaticamente:
// ✅ Cerca/crea gruppo "Visum-BOT"
// ✅ Conta operazioni nel gruppo (es. 2 esistenti)
// ✅ Crea Initialize Assignment alla posizione relativa 3 nel gruppo
// ✅ Crea PrT Assignment alla posizione relativa 4 nel gruppo

// Step 3: Claude riceve risposta con:
{
  group_position: 577,      // Posizione del gruppo
  delete_position: 580,     // Posizione assoluta delete
  actual_position: 581,     // Posizione assoluta assignment
  group_name: "Visum-BOT"
}

// Step 4: Claude può ora:
// - Configurare DSEGSET sulla posizione 581
// - Informare l'utente su entrambe le posizioni
// - Suggerire di espandere il gruppo in Visum per vedere le operazioni
```

---

## 🗂️ Gestione del Gruppo

### Visualizzare il Contenuto

In Visum:
1. Vai a **Procedures → Operations**
2. Cerca il gruppo **"Visum-BOT"**
3. Clicca sul `+` per espandere il gruppo
4. Vedi tutte le operazioni create dal BOT

### Eliminare Tutte le Operazioni BOT

Metodo 1: **Elimina tutto il gruppo**
```
Click destro su "Visum-BOT" → Delete
```
Questo elimina il gruppo e TUTTE le operazioni al suo interno.

Metodo 2: **Elimina operazioni singole**
```
Espandi "Visum-BOT" → Seleziona operazione → Delete
```

### Riordinare Operazioni

Le operazioni nel gruppo vengono sempre aggiunte **in fondo**. Per riordinarle:
1. Espandi il gruppo "Visum-BOT"
2. Trascina e rilascia le operazioni nell'ordine desiderato
3. Il sistema usa posizioni relative all'interno del gruppo

---

## 🐛 Troubleshooting

### Problema: "Non vedo il gruppo Visum-BOT"

**Causa:** Il gruppo potrebbe essere collassato.

**Soluzione:** 
- Cerca un'operazione di tipo "Group" nella lista
- Clicca sul `+` per espandere
- Verifica che il nome sia "Visum-BOT"

### Problema: "Le operazioni sono create fuori dal gruppo"

**Causa:** Errore nel codice o gruppo non trovato correttamente.

**Soluzione:**
- Verifica che il gruppo esista e abbia il nome esatto "Visum-BOT"
- Riavvia Visum e riprova
- Controlla i log del server MCP per errori

### Problema: "Troppe operazioni nel gruppo"

**Causa:** Multiple chiamate hanno creato operazioni duplicate.

**Soluzione:**
- Espandi il gruppo "Visum-BOT"
- Elimina le operazioni duplicate manualmente
- O elimina tutto il gruppo e ricrea

---

## 📚 Riferimenti API

### Visum COM API
- **OperationType 75**: Group
- **OperationType 9**: Initialize Assignment (Delete)
- **OperationType 101**: PrT Assignment
- **OperationType 100**: PuT Assignment

### IGroupPara Attributes
- **Name** (string): Nome del gruppo (es. "Visum-BOT")
- **IsExpanded** (bool): Gruppo espanso o collassato

### IOperations Methods
- `AddOperation(RelPos, Group)`: Aggiunge operazione in posizione relativa dentro un gruppo
- `GetChildren(Group)`: Ottiene operazioni figlie di un gruppo
- `ItemByKey(Position)`: Accede a operazione per posizione assoluta

---

## 💡 Best Practices

### Per Claude/AI Assistant:

1. **Sempre informare l'utente del gruppo**: "Le operazioni sono state create nel gruppo Visum-BOT"
2. **Fornire entrambe le posizioni**: Gruppo e operazioni individuali
3. **Spiegare l'ordine di esecuzione**: Delete prima, poi Assignment
4. **Suggerire di espandere il gruppo**: "Vai in Visum → Procedures → Operations → espandi Visum-BOT"

### Per l'Utente:

1. **Controllare il gruppo regolarmente**: Evita accumulo di operazioni duplicate
2. **Non rinominare il gruppo**: Il sistema cerca il nome "Visum-BOT"
3. **Espandere per vedere i dettagli**: Il gruppo potrebbe essere collassato di default
4. **Eliminare il gruppo quando non serve**: Pulisce il progetto

---

## 🎓 Conclusione

Il sistema **Visum-BOT Group** fornisce:
- ✅ Organizzazione automatica delle procedure MCP
- ✅ Isolamento dalle operazioni manuali
- ✅ Facile gestione e pulizia
- ✅ Tracciabilità completa delle operazioni create

Tutte le procedure create tramite MCP sono sicure, organizzate e facili da gestire nel gruppo dedicato "Visum-BOT"! 🚀
