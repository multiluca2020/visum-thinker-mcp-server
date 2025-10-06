# 🛠️ Sistema di Gestione Errori e Prevenzione Istanze Multiple

## 🚨 Problema Risolto

**PROBLEMA:** Claude apriva nuove istanze Visum ogni volta che riceveva un errore, creando conflitti e instabilità.

**SOLUZIONE:** Sistema intelligente di diagnosi e riparazione che previene la creazione di istanze duplicate.

## 🔧 Nuovi Tool di Diagnosi

### **1. 🔍 instance_diagnosis**
**Uso:** `"diagnosi istanze visum"` oppure `"instance diagnosis"`

**Funzione:**
- ✅ **Controlla lo stato** di tutte le istanze attive
- ✅ **Identifica problemi** specifici
- ✅ **Fornisce raccomandazioni** chiare
- ✅ **Previene creazione** di nuove istanze quando non necessario

**Output Esempio:**
```json
{
  "persistent_controller": {"status": "healthy"},
  "project_instances": 2,
  "tcp_servers": 1,
  "issues_found": [
    "❌ Project instance 'campoleone' unhealthy: connection timeout"
  ],
  "repair_actions": [
    "🔧 Consider shutting down and restarting instance 'campoleone'"
  ],
  "recommendations": [
    "⚠️ Issues found - repair before creating new instances",
    "🚫 AVOID creating new instances until issues are resolved"
  ]
}
```

### **2. 🧹 instance_cleanup**
**Uso:** `"pulisci istanze problematiche"` oppure `"instance cleanup"`

**Funzione:**
- 🧹 **Chiude istanze problematiche** in modo sicuro
- 🧹 **Libera risorse** bloccate
- 🧹 **Resetta connessioni** TCP danneggiate
- 🧹 **Prepara ambiente** per nuove operazioni

**Parametri:**
- `force: false` (default) - Solo istanze problematiche
- `force: true` - Tutte le istanze (pulizia completa)

## 🛡️ Prevenzione Automatica

### **project_open Migliorato**
Ora il tool `project_open` include **controlli preliminari**:

```typescript
// Se trova più di 2 istanze attive:
if (totalExistingInstances > 2) {
  return "⚠️ Troppe istanze attive. Esegui instance_diagnosis prima di procedere";
}
```

**Benefici:**
- 🚫 **Previene** creazione istanze duplicate
- 💡 **Guida Claude** verso la soluzione corretta
- 🔧 **Fornisce istruzioni** step-by-step

## 🔄 Workflow Consigliato per Claude

### **❌ Quando Si Riceve un Errore - NON FARE:**
```
❌ Aprire immediatamente una nuova istanza
❌ Ripetere la stessa operazione
❌ Ignorare il messaggio di errore
```

### **✅ Quando Si Riceve un Errore - FARE:**
```
1. ✅ Eseguire `instance_diagnosis`
2. ✅ Leggere i problemi identificati
3. ✅ Eseguire `instance_cleanup` se raccomandato
4. ✅ SOLO DOPO, tentare operazioni normali
```

## 📋 Comandi per Claude

### **Diagnosi Standard:**
```bash
# Prima cosa da fare quando si ricevono errori
"diagnosi istanze visum"
"instance diagnosis"
"controlla lo stato delle istanze"
```

### **Pulizia Selettiva:**
```bash
# Pulisce solo istanze problematiche
"pulisci istanze problematiche"
"instance cleanup"
```

### **Pulizia Completa (Solo se necessario):**
```bash
# Forza pulizia di tutte le istanze
"instance cleanup force"
```

### **Dopo la Pulizia:**
```bash
# Ora è sicuro procedere
"apri progetto visum"
"esegui analisi rete"
```

## 🔧 Risoluzione Problemi Specifici

### **Errore: "SyntaxError: unterminated string literal"**
**Causa:** Stringhe con apostrofi non escapati nel codice Python
**Soluzione:** ✅ RISOLTO - Aggiunta funzione `sanitizeForPython()`

### **Errore: "Connection refused" o timeout**
```bash
1. "instance diagnosis"          # Identifica istanze morte
2. "instance cleanup"            # Rimuove connessioni morte
3. "apri progetto visum"         # Crea nuova istanza pulita
```

### **Errore: "Already connected" o "Port in use"**
```bash
1. "instance diagnosis"          # Mostra istanze attive
2. "instance cleanup force"      # Forza chiusura tutte le istanze  
3. Attendi 10 secondi
4. "apri progetto visum"         # Riavvia con porte libere
```

### **Errore: "Project not found" o "Network not loaded"**
```bash
1. "instance diagnosis"          # Verifica stato istanze
2. Se controller persistente non è healthy:
   - "instance cleanup"
   - "apri progetto visum"
3. Se progetto non è caricato:
   - Usa il path corretto del file .ver
```

## 🎯 Vantaggi del Nuovo Sistema

### **✅ Prevenzione Intelligente**
- **Zero istanze duplicate** non necessarie
- **Controlli preliminari** automatici
- **Guidance proattiva** per Claude

### **✅ Diagnosi Precisa**
- **Identificazione specifica** dei problemi
- **Raccomandazioni actionable**
- **Status completo** del sistema

### **✅ Riparazione Sicura**
- **Cleanup selettivo** delle istanze problematiche
- **Preservazione** istanze sane
- **Recovery automatico** delle risorse

### **✅ Feedback Migliorato**
- **Errori descrittivi** con soluzioni
- **Istruzioni step-by-step** chiare
- **Prevenzione proattiva** di problemi futuri

## 🚨 Note Importanti per Claude

### **🔥 SEMPRE Prima di Creare Nuove Istanze:**
```
⚠️  Se ricevi QUALSIASI errore:
1. NON creare subito una nuova istanza
2. Esegui PRIMA "instance_diagnosis"  
3. Segui le raccomandazioni
4. SOLO DOPO procedi con operazioni normali
```

### **🎯 Riconosci i Segnali di Allarme:**
- `Connection refused`
- `Port already in use` 
- `SyntaxError` nel codice Python
- `Network not loaded`
- `Project not found`

### **💡 Quando È Sicuro Creare Nuove Istanze:**
- ✅ `instance_diagnosis` mostra "All systems healthy"
- ✅ Meno di 2 istanze esistenti attive
- ✅ Nessun errore nei 5 comandi precedenti
- ✅ Dopo cleanup completato con successo

**Il sistema è ora ROBUSTO e RESILIENTE agli errori!** 🛡️