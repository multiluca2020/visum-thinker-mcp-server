# Visum Procedures API - Documentazione Completa

## ✅ COMANDI VERIFICATI E FUNZIONANTI

### 1. Creare una Procedura PrT Assignment

**Metodo corretto scoperto il 2025-10-10:**

```python
# Crea operazione alla posizione specificata (1-20 valide)
new_op = visum.Procedures.Operations.AddOperation(20)

# Imposta il tipo di operazione (101 = PrT Assignment)
new_op.SetAttValue("OPERATIONTYPE", 101)

# Accedi ai parametri specifici
params = new_op.PrTAssignmentParameters

# Configura parametri equilibrium
equilibrium_params = new_op.PrTEquilibriumAssignmentParameters
equilibrium_params.SetAttValue("NUMITER", 50)
equilibrium_params.SetAttValue("PRECISIONDEMAND", 0.01)
```

**Comando JSON MCP funzionante:**

```bash
echo '{"jsonrpc":"2.0","id":100,"method":"tools/call","params":{"name":"project_execute","arguments":{"projectId":"PROJECT_ID_QUI","code":"try:\n    new_op = visum.Procedures.Operations.AddOperation(20)\n    new_op.SetAttValue(\"OPERATIONTYPE\", 101)\n    result = {\"status\": \"success\", \"message\": \"PrT Assignment creata\"}\nexcept Exception as e:\n    result = {\"error\": str(e)}","description":"Crea PrT Assignment"}}}' | node build/index.js
```

## 📋 Tipi di Operazioni (OPERATIONTYPE)

| Codice | Tipo Operazione | Parametri Accessibili |
|--------|----------------|----------------------|
| 101 | PrT Assignment | `PrTAssignmentParameters`, `PrTEquilibriumAssignmentParameters` |
| 102 | PuT Assignment | `PuTAssignmentParameters` |
| 103 | Demand Model | Da documentare |
| 104 | Matrix Calculation | Da documentare |

## 🔑 API Chiave

### visum.Procedures.Operations

```python
# Struttura Operations
visum.Procedures.Operations.AddOperation(position)  # Crea nuova operazione
visum.Procedures.Operations.ItemByKey(position)     # Accedi operazione esistente
visum.Procedures.Operations.RemoveOperation(position) # Rimuovi operazione

# NOTA: Le posizioni valide sono da 1 a N (numero corrente di operazioni)
# Per aggiungere in coda, usa l'ultima posizione valida
```

### visum.Procedures.Functions

```python
# Accesso diretto alle funzioni (NON FUNZIONA come ci si aspetterebbe)
# NON USARE: visum.Procedures.Functions.PrTAssignmentBPR
# INVECE: Crea Operation e imposta OPERATIONTYPE

# NOTA: Functions esiste ma non ha i metodi che ci si aspetta
# Usa sempre Operations.AddOperation() + SetAttValue("OPERATIONTYPE", code)
```

### Parametri Operazioni

```python
# Dopo aver creato un'operazione con OPERATIONTYPE = 101:
operation = visum.Procedures.Operations.ItemByKey(20)

# Accedi ai parametri base
params = operation.PrTAssignmentParameters

# Accedi ai parametri equilibrium
eq_params = operation.PrTEquilibriumAssignmentParameters
eq_params.SetAttValue("NUMITER", 50)
eq_params.SetAttValue("PRECISIONDEMAND", 0.01)
```

## ⚠️ ERRORI COMUNI

### 1. ProcedureSequence non esiste
```python
# ❌ NON FUNZIONA:
proc_seq = visum.Procedures.ProcedureSequence

# ✅ ESISTE MA NON È QUELLO CHE SERVE:
proc_seq = visum.PostPauseProcedureSequence  # Per pause/post-processing

# ✅ USA INVECE:
operations = visum.Procedures.Operations
```

### 2. Functions non ha metodi diretti
```python
# ❌ NON FUNZIONA:
assignment = visum.Procedures.Functions.PrTAssignmentBPR

# ✅ USA INVECE:
operation = visum.Procedures.Operations.AddOperation(20)
operation.SetAttValue("OPERATIONTYPE", 101)
```

### 3. Posizioni invalide
```python
# ❌ ERRORE: "Valid position are from 1 up to 20"
new_op = visum.Procedures.Operations.AddOperation(21)  # Fallisce se ci sono solo 20 ops

# ✅ SOLUZIONE: Usa posizione <= numero corrente operazioni
# Per aggiungere in coda, usa l'ultima posizione disponibile
```

## 📚 Riferimenti

- File: `create-complete-prt-procedure.js` - Script completo funzionante
- File: `create-prt-with-segment-C.js` - Con configurazione segmenti
- Cartella: `visum-com-docs/` - Documentazione HTML Visum COM

## 🎯 Pattern per Nuove Operazioni

```python
# Template generico per creare qualsiasi operazione
try:
    # 1. Crea operazione
    new_op = visum.Procedures.Operations.AddOperation(POSITION)
    
    # 2. Imposta tipo
    new_op.SetAttValue("OPERATIONTYPE", TYPE_CODE)
    
    # 3. Accedi parametri specifici (varia per tipo)
    params = new_op.SPECIFIC_PARAMETERS_OBJECT
    
    # 4. Configura parametri
    params.SetAttValue("PARAM_NAME", value)
    
    # 5. Verifica creazione
    created = visum.Procedures.Operations.ItemByKey(POSITION)
    
    result = {"status": "success", "position": POSITION}
except Exception as e:
    result = {"error": str(e)}
```

## 🚀 Prossimi Passi

- [ ] Documentare altri tipi di operazioni (102, 103, 104, ...)
- [ ] Creare tool MCP dedicato `visum_create_procedure`
- [ ] Testare configurazione DSEGSET per demand segments
- [ ] Documentare parametri VDF (Volume Delay Functions)
