# FASE 2 - Test Suite Completa
## Assignment, Percorsi e Critical Link Analysis

Questa è la suite di test esaustiva per verificare tutte le funzionalità implementate nella Fase 2. Ogni test può essere eseguito da Claude usando il MCP server.

---

## 🚀 **PRE-REQUISITI**
1. **Progetto Visum attivo**: Assicurati che un'istanza del progetto sia attiva
2. **Matrici OD caricate**: Il progetto deve avere matrici di domanda
3. **Connessioni zona-rete**: Zone collegate alla rete stradale

### Verifica Pre-requisiti:
```
Claude, esegui: "get network statistics" 
```

---

## 📋 **TEST CATEGORIA 1: PrT ASSIGNMENT**

### Test 1.1: Basic PrT Assignment
**Comando per Claude:**
```
Esegui un'assegnazione del trasporto privato sul progetto Campoleone
```

**Pattern riconosciuti:**
- "prt assignment"
- "car assignment" 
- "private transport assignment"
- "bpr assignment"

**Output atteso:**
- ✅ Status: completed
- ✅ Total volume > 0
- ✅ Total VMT > 0
- ✅ Congested links identificati
- ✅ Convergenza configurata (20 iter, gap 0.01)

### Test 1.2: Assignment Results Analysis
**Comando per Claude:**
```
Dopo l'assegnazione, fai un'analisi dei volumi per identificare i link congestionati
```

**Verifica:**
- V/C ratios calcolati
- Link con V/C > 0.8 identificati
- Performance network metrics

---

## 🚌 **TEST CATEGORIA 2: PuT ASSIGNMENT**

### Test 2.1: Basic PuT Assignment
**Comando per Claude:**
```
Esegui un'assegnazione del trasporto pubblico
```

**Pattern riconosciuti:**
- "put assignment"
- "transit assignment"
- "public transport assignment"

**Output atteso:**
- ✅ Status: completed
- ✅ Total passengers > 0
- ✅ Total boardings > 0
- ✅ Lines e stops conteggiati

### Test 2.2: Transit Performance
**Comando per Claude:**
```
Analizza le performance del trasporto pubblico dopo l'assegnazione
```

---

## 🛣️ **TEST CATEGORIA 3: SHORTEST PATH**

### Test 3.1: Basic Shortest Path
**Comando per Claude:**
```
Fai un'analisi dei percorsi minimi tra le zone principali
```

**Pattern riconosciuti:**
- "shortest path"
- "path analysis"
- "route analysis"
- "percorso minimo"

**Output atteso:**
- ✅ Sample paths calcolati
- ✅ Distance, travel time, generalized cost
- ✅ Origine e destinazione per ogni percorso

### Test 3.2: Path Comparison
**Comando per Claude:**
```
Confronta i percorsi tra diverse coppie origine-destinazione
```

---

## 📊 **TEST CATEGORIA 4: SKIM MATRICES**

### Test 4.1: Create All Skim Matrices
**Comando per Claude:**
```
Crea le matrici skim per tempi di viaggio, distanze e costi generalizzati
```

**Pattern riconosciuti:**
- "skim matrix"
- "travel time matrix"
- "distance matrix"
- "cost matrix"

**Output atteso:**
- ✅ 3 matrici create (901, 902, 903)
- ✅ Travel Time Skim (901)
- ✅ Distance Skim (902)
- ✅ Generalized Cost Skim (903)
- ✅ Statistics per ogni matrice

### Test 4.2: Matrix Statistics Analysis
**Comando per Claude:**
```
Analizza le statistiche delle matrici skim create
```

---

## 🔗 **TEST CATEGORIA 5: CRITICAL LINK ANALYSIS**

### Test 5.1: Basic CLA Analysis
**Comando per Claude:**
```
Fai un'analisi dei link critici della rete usando flow bundle
```

**Pattern riconosciuti:**
- "critical link analysis"
- "cla analysis"
- "flow bundle"
- "network vulnerability"
- "bottleneck analysis"

**Output atteso:**
- ✅ Flow Bundle eseguito
- ✅ Critical links identificati
- ✅ Criticality index calcolato
- ✅ Network vulnerability metrics
- ✅ Top 10 link critici

### Test 5.2: Vulnerability Assessment
**Comando per Claude:**
```
Valuta la vulnerabilità della rete identificando i bottleneck principali
```

### Test 5.3: Flow Concentration Analysis
**Comando per Claude:**
```
Analizza la concentrazione dei flussi sulla rete stradale
```

---

## 🧪 **TEST CATEGORIA 6: INTEGRATION TESTS**

### Test 6.1: Complete Workflow Test
**Sequenza completa da eseguire con Claude:**

1. ```
   Esegui un'assegnazione del trasporto privato
   ```

2. ```
   Crea le matrici skim per tempi e distanze
   ```

3. ```
   Fai un'analisi dei link critici
   ```

4. ```
   Analizza i percorsi minimi tra le zone
   ```

**Verifica:**
- ✅ Tutti i 4 step completati senza errori
- ✅ Risultati coerenti tra i diversi step
- ✅ Performance accettabili (< 30 secondi per step)

### Test 6.2: Error Handling Test
**Comando per Claude su progetto inattivo:**
```
Esegui un'assegnazione senza istanza attiva
```

**Output atteso:**
- ❌ Errore chiaro: istanza non attiva
- ❌ Nessun auto-restart
- ✅ Messaggio di errore comprensibile

---

## 📈 **TEST CATEGORIA 7: PERFORMANCE TESTS**

### Test 7.1: Large Network Test (Campoleone)
**Comando per Claude:**
```
Fai un'analisi completa della rete: assegnazione, skim e link critici
```

**Benchmark attesi per Campoleone (166K nodes, 409K links):**
- ⏱️ PrT Assignment: < 60 secondi
- ⏱️ Skim Matrices: < 30 secondi
- ⏱️ Critical Link Analysis: < 45 secondi
- ⏱️ Shortest Path: < 15 secondi

### Test 7.2: Memory Usage Test
Monitorare uso memoria durante test su Campoleone

---

## 🔄 **TEST CATEGORIA 8: COMBO TESTS**

### Test 8.1: Mixed Analysis
**Comando per Claude:**
```
Combina analisi network statistics con critical link analysis
```

### Test 8.2: Progressive Analysis
**Sequenza progressiva:**

1. ```
   Ottieni statistiche base della rete
   ```

2. ```
   Esegui assegnazione trasporto privato
   ```

3. ```
   Identifica link critici dopo assegnazione
   ```

4. ```
   Crea matrici skim basate sui risultati
   ```

---

## 📝 **CHECKLIST FINALE**

### ✅ Functionality Tests
- [ ] PrT Assignment (BPR) funziona
- [ ] PuT Assignment funziona
- [ ] Shortest Path Analysis funziona
- [ ] Skim Matrix Creation funziona
- [ ] Critical Link Analysis funziona

### ✅ Integration Tests
- [ ] Workflow completo funziona
- [ ] Error handling corretto
- [ ] Performance accettabili

### ✅ Pattern Recognition Tests
- [ ] Tutti i pattern italiani riconosciuti
- [ ] Tutti i pattern inglesi riconosciuti
- [ ] Pattern alternativi funzionano

### ✅ Output Quality Tests
- [ ] JSON output ben formato
- [ ] Metriche numeriche corrette
- [ ] Status e errori chiari
- [ ] Nomi comprensibili

---

## 🚨 **TROUBLESHOOTING**

### Problemi Comuni:
1. **"Matrix not found"**: Verificare che esistano matrici OD
2. **"No zones connected"**: Verificare connessioni zona-rete
3. **"Assignment failed"**: Verificare parametri rete (capacità, velocità)
4. **"Timeout"**: Ridurre campioni o iterazioni per reti grandi

### Debug Commands:
```
Claude, verifica lo stato delle istanze del progetto
Claude, ottieni statistiche base della rete
Claude, controlla se ci sono errori nella rete
```

---

## 📊 **REPORT FINALE**

Dopo aver completato tutti i test, creare report con:
- ✅ Test passati/falliti
- ⏱️ Tempi di esecuzione
- 📈 Performance metrics
- 🐛 Problemi riscontrati
- 💡 Suggerimenti miglioramenti

**La Fase 2 è completa quando tutti i test di questa suite passano con successo!**