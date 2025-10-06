# FASE 2 - Guida Rapida per Claude

## 🚀 **FUNZIONI DISPONIBILI**

### **ASSIGNMENT**
- `"esegui assegnazione trasporto privato"` → PrT Assignment BPR
- `"fai assegnazione auto"` → PrT Assignment  
- `"esegui assegnazione trasporto pubblico"` → PuT Assignment
- `"transit assignment"` → PuT Assignment

### **PERCORSI**  
- `"analizza percorsi minimi"` → Shortest Path Analysis
- `"shortest path analysis"` → Path Analysis
- `"confronta percorsi"` → Route Comparison

### **MATRICI**
- `"crea matrici skim"` → Travel Time + Distance + Cost Matrices
- `"travel time matrix"` → Skim Matrix Creation
- `"distance matrix"` → Distance Skim
- `"cost matrix"` → Generalized Cost Skim

### **CRITICAL LINK ANALYSIS**
- `"analisi link critici"` → Critical Link Analysis with Flow Bundle
- `"cla analysis"` → Critical Link Analysis
- `"flow bundle"` → Flow Concentration Analysis  
- `"network vulnerability"` → Network Vulnerability Assessment
- `"bottleneck analysis"` → Bottleneck Identification

### **STATISTICHE BASE (Fase 1)**
- `"network statistics"` → Basic Network Stats
- `"analizza nodi"` → Node Analysis
- `"analizza link"` → Link Analysis
- `"analizza zone"` → Zone Analysis
- `"analisi completa"` → Comprehensive Analysis

---

## 📋 **TEST SEQUENCE SUGGERITA**

1. **Verifica preliminare:**
   ```
   Claude, ottieni le statistiche base della rete
   ```

2. **Test Assignment:**
   ```
   Claude, esegui un'assegnazione del trasporto privato
   ```

3. **Test Critical Links:**
   ```
   Claude, fai un'analisi dei link critici
   ```

4. **Test Skim Matrices:**
   ```
   Claude, crea le matrici skim per tempi e distanze
   ```

5. **Test Percorsi:**
   ```
   Claude, analizza i percorsi minimi tra le zone
   ```

---

## ⚡ **PERFORMANCE ATTESE**

- **PrT Assignment**: 30-60 secondi (Campoleone)
- **Critical Link Analysis**: 15-45 secondi  
- **Skim Matrices**: 15-30 secondi
- **Shortest Path**: 10-20 secondi
- **Network Statistics**: 2-5 secondi

---

## 🔧 **TROUBLESHOOTING**

### Se un test fallisce:
1. Verificare che l'istanza del progetto sia attiva
2. Controllare che esistano matrici OD caricate
3. Verificare connessioni zona-rete
4. Ridurre dimensioni campioni per test

### Comandi di debug:
- `"verifica stato istanze"`
- `"network statistics"`  
- `"health check progetto"`

---

## 📊 **OUTPUT EXAMPLES**

### Successful PrT Assignment:
```json
{
  "assignment_type": "PrT_BPR",
  "status": "completed", 
  "network_performance": {
    "total_volume": 25000,
    "total_vmt": 450000.5,
    "average_speed": 45.2,
    "congested_links": 15
  }
}
```

### Successful Critical Link Analysis:
```json
{
  "analysis_type": "critical_link_analysis",
  "status": "completed",
  "network_vulnerability": {
    "critical_links_count": 25,
    "vulnerability_ratio": 0.045
  },
  "top_critical_links": [...]
}
```

La **Fase 2** è ora completamente implementata e testabile!