# 📊 Gestione Demand Segments - Sistema MCP Visum

## 🎯 Come Funziona la Gestione dei Segmenti di Domanda

### **✅ DETECTION AUTOMATICO**
Il sistema **rileva automaticamente** i segmenti di domanda disponibili nel progetto Visum e li configura per l'assegnazione.

### **🔍 Processo di Rilevamento**

#### **1. Scansione Segmenti**
```python
# Il sistema scandisce tutti i demand segments disponibili
all_segments = list(visum.Net.DemandSegments)
prt_segments = [seg for seg in all_segments if seg.GetAttValue('Code').startswith('P') or 'PrT' in seg.GetAttValue('Code')]
```

#### **2. Classificazione Automatica**
- **PrT Segments**: Segmenti per trasporto privato
- **PuT Segments**: Segmenti per trasporto pubblico  
- **Other Segments**: Altri segmenti definiti dall'utente

#### **3. Selezione Intelligente**
- **Priorità PrT**: Per assegnazioni trasporto privato
- **Limite di 5 segmenti**: Per evitare sovraccarico computazionale
- **Fallback robusto**: Usa tutti i segmenti se non trova PrT specifici

## 📋 Comandi Disponibili

### **🔎 Analisi Demand Segments**
```bash
# Analizza la configurazione dei segmenti
"analizza i segmenti di domanda"
"demand segments analysis"  
"segments configuration"
"segmenti matrice"
```

### **🚗 Assegnazione con Segmenti**
```bash
# L'assegnazione rileva automaticamente i segmenti
"esegui un'assegnazione equilibrio"
"prt assignment con segmenti configurati"
"assignment trasporto privato"
```

## 📊 Output Esempio - Demand Segments Analysis

```json
{
  "analysis_type": "demand_segments",
  "status": "completed", 
  "segment_configuration": {
    "total_segments": 4,
    "prt_segments": [
      {
        "code": "P",
        "name": "Private Transport",
        "mode": "PrT",
        "demand_matrices": [100, 101, 102]
      },
      {
        "code": "P_CAR",
        "name": "Car Segment",
        "mode": "PrT", 
        "demand_matrices": [110]
      }
    ],
    "put_segments": [
      {
        "code": "PuT",
        "name": "Public Transport",
        "mode": "PuT",
        "demand_matrices": [200, 201]
      }
    ],
    "segments_by_mode": {
      "private_transport": 2,
      "public_transport": 1,
      "other": 1
    }
  },
  "recommendations": {
    "assignment_ready": true,
    "suggested_segments": ["P", "P_CAR"],
    "configuration_notes": [
      "PrT segments found",
      "Multiple segments available", 
      "Matrix configuration seems valid"
    ]
  }
}
```

## 📊 Output Esempio - Assignment con Demand Segments

```json
{
  "assignment_type": "PrTAssignmentBPR",
  "method_description": "BPR (Bureau of Public Roads)",
  "status": "completed",
  "demand_segments": {
    "segments_found": 2,
    "segments_selected": [
      {
        "code": "P",
        "name": "Private Transport",
        "mode": "PrT"
      },
      {
        "code": "P_CAR", 
        "name": "Car Segment",
        "mode": "PrT"
      }
    ],
    "auto_detected": true
  },
  "network_performance": {
    "total_volume": 125000,
    "total_vmt": 850000.50,
    "average_speed": 45.2
  },
  "convergence_info": {
    "segments_processed": 2,
    "method_used": "BPR (Bureau of Public Roads)"
  }
}
```

## 🔧 Configurazione Flessibile

### **🎯 Comportamento Intelligente**

#### **Se Trova Segmenti PrT**
- ✅ Usa automaticamente i segmenti PrT rilevati
- ✅ Mostra informazioni sui segmenti selezionati
- ✅ Limita a 5 segmenti per performance ottimale

#### **Se Non Trova Segmenti PrT**  
- 🔄 Usa i primi 3 segmenti disponibili
- 🔄 Informa l'utente della selezione automatica
- 🔄 Procede con configurazione di fallback

#### **Se Non Trova Nessun Segmento**
- ⚠️ Usa configurazione default di Visum
- ⚠️ Informa l'utente della situazione
- ⚠️ Procede comunque con l'assegnazione

### **📝 Note di Configurazione**

#### **✅ Automatic Detection**
```python
print(f"Found {len(demand_segments)} demand segments for assignment:")
for seg in demand_segments:
    print(f"  - {seg['code']}: {seg['name']} ({seg['mode']})")
```

#### **⚙️ Fallback Strategy**
```python
if not prt_segments:
    # If no PrT segments found, use all segments
    prt_segments = all_segments[:3]  # Limit to first 3
```

#### **🔧 User Override**
Il sistema **rispetta sempre** la configurazione esistente del progetto Visum. Se l'utente ha già configurato manualmente i segmenti di domanda nelle impostazioni di Visum, il sistema li userà.

## 🎯 Vantaggi del Sistema

### **✅ Automazione Intelligente**
- **Zero configurazione manuale** richiesta dall'utente
- **Detection automatico** dei segmenti appropriati
- **Selezione intelligente** basata sul tipo di assegnazione

### **✅ Flessibilità**
- **Supporta qualsiasi configurazione** di segmenti Visum
- **Fallback robusto** per progetti atipici
- **Compatibilità completa** con setup esistenti

### **✅ Trasparenza**
- **Report dettagliato** dei segmenti utilizzati
- **Informazioni complete** su selezione automatica
- **Raccomandazioni** per configurazione ottimale

### **✅ Performance**
- **Limite intelligente** a 5 segmenti max
- **Evita sovraccarico** computazionale
- **Ottimizzazione automatica** per reti grandi

## 🚨 Situazioni Speciali

### **⚠️ Progetti Senza Segmenti PrT**
Se il progetto non ha segmenti PrT specifici, il sistema:
- Usa i primi segmenti disponibili
- Informa l'utente della situazione  
- Procede con l'assegnazione usando configurazione Visum default

### **⚠️ Progetti con Molti Segmenti**
Se il progetto ha >5 segmenti PrT, il sistema:
- Seleziona i primi 5 segmenti PrT
- Informa l'utente della limitazione
- Fornisce raccomandazioni per configurazione manuale

### **⚠️ Configurazioni Atipiche**
Per configurazioni speciali, l'utente può:
- Pre-configurare i segmenti in Visum GUI
- Il sistema rispetterà la configurazione esistente
- Usare il comando di analisi per verificare la configurazione

## 🎉 Conclusione

Il sistema **gestisce automaticamente** i segmenti di domanda senza richiedere input manuale dall'utente, ma fornisce **trasparenza completa** su quali segmenti vengono utilizzati e perché, permettendo all'utente di verificare e modificare la configurazione se necessario.