# 🌊 IFlowBundle - Guida Completa per Analisi Flusso Origine-Destinazione

## 🎯 Cos'è IFlowBundle?

**IFlowBundle** è l'interfaccia Visum COM per **analizzare i flussi origine-destinazione (OD)** che attraversano specifici elementi di rete (link, nodi, zone, ecc.).

### Caso d'Uso Tipico:
> **Domanda:** "Quanto traffico da Zona A a Zona B passa attraverso il Link X?"
> 
> **IFlowBundle** ti permette di rispondere a questa e molte altre domande sui flussi!

---

## 📊 Cosa Fa IFlowBundle?

### Input:
1. **Demand Segments**: Quali segmenti di domanda analizzare (es. "C_CORRETTA_AM")
2. **Net Elements**: Quali elementi di rete analizzare (link, nodi, zone)
3. **Conditions** (opzionali): Filtri aggiuntivi sul traffico

### Output:
1. **Flow Bundle Matrix**: Matrice OD dei flussi che passano per gli elementi specificati
2. **Link/Node Volumes**: Volumi sui link/nodi coinvolti nel flow bundle

---

## 🔧 Come Implementarlo

### Pattern Base (Minimo Necessario):

```python
# 1. Ottieni riferimento al FlowBundle
fb = Visum.Net.FlowBundle

# 2. ⚠️ SEMPRE inizializzare con Clear()
fb.Clear()

# 3. ⚠️ SEMPRE impostare DemandSegments
fb.DemandSegments = "C_CORRETTA_AM"  # O comma-separated: "C,H"

# 4. Definisci elementi di rete da analizzare
target_link = Visum.Net.Links.ItemByKey(105227631, 105220716)
net_elements = Visum.CreateNetElements()
net_elements.Add(target_link)

# 5. Esegui flow bundle
fb.Execute(net_elements)

# 6. Ottieni matrice risultato
flow_matrix = fb.GetOrCreateFlowBundleMatrix("C_CORRETTA_AM")

# 7. Analizza risultati
total_flow = flow_matrix.GetSum()
print(f"Flusso totale attraverso link: {total_flow:.2f} veicoli")
```

---

## ⚠️ CRITICAL: Cosa NON Dimenticare Mai

### 1. **SEMPRE chiamare `Clear()` prima di iniziare**
```python
fb = Visum.Net.FlowBundle
fb.Clear()  # ⚠️ OBBLIGATORIO! Reset stato precedente
```

**Perché?** IFlowBundle mantiene stato tra chiamate. Se non chiami `Clear()`, condizioni precedenti rimangono attive!

### 2. **SEMPRE impostare `DemandSegments` prima di qualsiasi condizione**
```python
fb.DemandSegments = "C_CORRETTA_AM"  # ⚠️ OBBLIGATORIO!
```

**Perché?** Le condizioni ereditano il demand segment set attivo. Se vuoto, errore!

### 3. **Non confondere `Execute()` con `ExecuteCurrentConditions()`**
- `Execute(netElements)`: Esegue flow bundle per elementi specificati (uso comune)
- `ExecuteCurrentConditions()`: Esegue condizioni definite con `CreateCondition*()` (uso avanzato)

---

## 📝 Workflow Completo

### Scenario: Analizzare Flussi su Screen Line

```python
# ===== STEP 1: Inizializzazione =====
fb = Visum.Net.FlowBundle
fb.Clear()  # ⚠️ SEMPRE!

# ===== STEP 2: Imposta Demand Segments =====
# Opzione A: Singolo segment
fb.DemandSegments = "C_CORRETTA_AM"

# Opzione B: Multipli segments (comma-separated)
fb.DemandSegments = "C_CORRETTA_AM,C_CORRETTA_IP1,H_INIZIALE_AM"

# ===== STEP 3: Definisci Screen Line (Links da Analizzare) =====
screen_line_links = [
    (105227631, 105220716),
    (105220716, 105230821),
    (105230821, 105240932)
]

net_elements = Visum.CreateNetElements()
for from_node, to_node in screen_line_links:
    link = Visum.Net.Links.ItemByKey(from_node, to_node)
    net_elements.Add(link)

print(f"Screen line definita con {len(screen_line_links)} link")

# ===== STEP 4: Esegui Flow Bundle =====
print("Calcolo flow bundle in corso...")
fb.Execute(net_elements)
print("✅ Flow bundle calcolato!")

# ===== STEP 5: Ottieni Matrice OD =====
demand_segment = "C_CORRETTA_AM"
flow_matrix = fb.GetOrCreateFlowBundleMatrix(demand_segment)

# ===== STEP 6: Analisi Risultati =====
# A. Statistiche generali
total_flow = flow_matrix.GetSum()
avg_flow = flow_matrix.GetAverage()
max_flow = flow_matrix.GetMax()

print(f"\n📊 Statistiche Flow Bundle:")
print(f"  Flusso totale: {total_flow:,.0f} veicoli")
print(f"  Flusso medio OD: {avg_flow:.2f} veicoli")
print(f"  Flusso massimo OD: {max_flow:.2f} veicoli")

# B. Analisi per coppia OD specifica
zone_origin = 1
zone_dest = 100
od_flow = flow_matrix.GetValue(zone_origin, zone_dest)
print(f"\n🔍 Flusso Zona {zone_origin} → Zona {zone_dest}: {od_flow:.2f} veicoli")

# C. Export matrice
flow_matrix.SaveToFile("C:\\output\\screen_line_flow.mtx")
print(f"✅ Matrice salvata in screen_line_flow.mtx")

# ===== STEP 7: Analisi Volumi sui Link =====
# Dopo Execute(), i link hanno attributi FlowBundle aggiornati
print("\n📋 Volumi sui link della screen line:")
for from_node, to_node in screen_line_links:
    link = Visum.Net.Links.ItemByKey(from_node, to_node)
    
    # Volume totale del link (da assegnazione)
    total_vol = link.AttValue("VolVehPrT(AP)")
    
    # Volume flow bundle (solo traffico che attraversa screen line)
    # Nota: attributo specifico creato dal flow bundle
    fb_vol = link.AttValue("VolVehPrT_FlowBundle(AP)")  # Se disponibile
    
    percentage = (fb_vol / total_vol * 100) if total_vol > 0 else 0
    
    print(f"  Link {from_node}→{to_node}:")
    print(f"    Volume totale: {total_vol:,.0f} veh/h")
    print(f"    Volume flow bundle: {fb_vol:,.0f} veh/h ({percentage:.1f}%)")
```

---

## 🎓 Casi d'Uso Avanzati

### 1. **Screen Line Analysis (Barriera Virtuale)**

Analizza quanti veicoli attraversano una linea immaginaria nella rete:

```python
fb.Clear()
fb.DemandSegments = "C_CORRETTA_AM,H_INIZIALE_AM"

# Definisci screen line (es. autostrada A1 all'altezza di Roma)
screen_line = [
    Visum.Net.Links.ItemByKey(n1, n2),
    Visum.Net.Links.ItemByKey(n3, n4),
    # ... altri link della barriera
]

net_elements = Visum.CreateNetElements()
for link in screen_line:
    net_elements.Add(link)

fb.Execute(net_elements)
flow_matrix = fb.GetOrCreateFlowBundleMatrix("C_CORRETTA_AM")
print(f"Traffico attraverso screen line: {flow_matrix.GetSum():,.0f} veicoli")
```

### 2. **Cordon Analysis (Traffico in/out Zona)**

Analizza traffico entrante/uscente da un'area:

```python
fb.Clear()
fb.DemandSegments = "C_CORRETTA_AM"

# Definisci cordon: tutti i link che entrano in una zona
zone_id = 25
cordon_links = []

# Trova tutti i link che entrano nella zona
for link in Visum.Net.Links:
    to_node = link.ToNode
    if to_node.AttValue("ZoneNo") == zone_id:
        cordon_links.append(link)

print(f"Cordon definito con {len(cordon_links)} link")

net_elements = Visum.CreateNetElements()
for link in cordon_links:
    net_elements.Add(link)

fb.Execute(net_elements)
flow_matrix = fb.GetOrCreateFlowBundleMatrix("C_CORRETTA_AM")
print(f"Traffico entrante in zona {zone_id}: {flow_matrix.GetSum():,.0f} veicoli")
```

### 3. **Origin Analysis (Da Dove Viene il Traffico?)**

Scopri le origini del traffico su un link congestionato:

```python
fb.Clear()
fb.DemandSegments = "C_CORRETTA_AM"

# Link congestionato da analizzare
congested_link = Visum.Net.Links.ItemByKey(123456, 789012)

net_elements = Visum.CreateNetElements()
net_elements.Add(congested_link)

fb.Execute(net_elements)
flow_matrix = fb.GetOrCreateFlowBundleMatrix("C_CORRETTA_AM")

# Analizza righe della matrice (origini)
print(f"\n🔍 Top 10 Origini del traffico sul link congestionato:")
origins_flows = []

zones = Visum.Net.Zones
for zone in zones:
    zone_no = zone.AttValue("No")
    # Somma flussi da questa origine a tutte le destinazioni
    total_from_zone = 0
    for dest_zone in zones:
        dest_no = dest_zone.AttValue("No")
        flow = flow_matrix.GetValue(zone_no, dest_no)
        total_from_zone += flow
    
    if total_from_zone > 0:
        origins_flows.append((zone_no, total_from_zone))

# Ordina e mostra top 10
origins_flows.sort(key=lambda x: x[1], reverse=True)
for i, (zone_no, flow) in enumerate(origins_flows[:10], 1):
    print(f"  {i}. Zona {zone_no}: {flow:,.0f} veicoli")
```

### 4. **Alternative Routes Analysis**

Analizza traffico che usa percorsi alternativi:

```python
fb.Clear()
fb.DemandSegments = "C_CORRETTA_AM"

# ⚠️ Abilita percorsi alternativi
fb.SetAlternativeRoutes(True)

# Definisci link principale
main_link = Visum.Net.Links.ItemByKey(123, 456)
net_elements = Visum.CreateNetElements()
net_elements.Add(main_link)

fb.Execute(net_elements)
flow_matrix = fb.GetOrCreateFlowBundleMatrix("C_CORRETTA_AM")
print(f"Traffico su percorso principale: {flow_matrix.GetSum():,.0f} veicoli")

# Ora analizza link alternativo
fb.Clear()  # ⚠️ Ricomincia!
fb.DemandSegments = "C_CORRETTA_AM"
fb.SetAlternativeRoutes(True)

alt_link = Visum.Net.Links.ItemByKey(789, 012)
net_elements2 = Visum.CreateNetElements()
net_elements2.Add(alt_link)

fb.Execute(net_elements2)
flow_matrix2 = fb.GetOrCreateFlowBundleMatrix("C_CORRETTA_AM")
print(f"Traffico su percorso alternativo: {flow_matrix2.GetSum():,.0f} veicoli")
```

---

## 🚫 Cosa NON Fare (Errori Comuni)

### ❌ 1. Dimenticare `Clear()`
```python
# SBAGLIATO!
fb = Visum.Net.FlowBundle
fb.DemandSegments = "C_CORRETTA_AM"  # ❌ Stato precedente ancora attivo!
fb.Execute(net_elements)

# CORRETTO!
fb = Visum.Net.FlowBundle
fb.Clear()  # ✅ Reset completo
fb.DemandSegments = "C_CORRETTA_AM"
fb.Execute(net_elements)
```

### ❌ 2. Non impostare `DemandSegments`
```python
# SBAGLIATO!
fb.Clear()
fb.Execute(net_elements)  # ❌ ERRORE: DemandSegments vuoto!

# CORRETTO!
fb.Clear()
fb.DemandSegments = "C_CORRETTA_AM"  # ✅ Obbligatorio!
fb.Execute(net_elements)
```

### ❌ 3. Mescolare PrT e PuT
```python
# SBAGLIATO!
fb.DemandSegments = "C_CORRETTA_AM,PT_LINE_1"  # ❌ Mix PrT/PuT non permesso!

# CORRETTO - Opzione A: Solo PrT
fb.DemandSegments = "C_CORRETTA_AM,H_INIZIALE_AM"  # ✅ Solo PrT

# CORRETTO - Opzione B: Solo PuT
fb.DemandSegments = "PT_LINE_1,PT_LINE_2"  # ✅ Solo PuT
```

### ❌ 4. Riutilizzare `net_elements` senza ricreare
```python
# SBAGLIATO!
net_elements = Visum.CreateNetElements()
net_elements.Add(link1)
fb.Execute(net_elements)

# Seconda analisi
net_elements.Add(link2)  # ❌ Potrebbe causare problemi
fb.Execute(net_elements)

# CORRETTO!
# Prima analisi
net_elements1 = Visum.CreateNetElements()
net_elements1.Add(link1)
fb.Execute(net_elements1)

# Seconda analisi
fb.Clear()  # ✅ Reset!
fb.DemandSegments = "C_CORRETTA_AM"
net_elements2 = Visum.CreateNetElements()  # ✅ Nuovo container
net_elements2.Add(link2)
fb.Execute(net_elements2)
```

### ❌ 5. Non salvare la matrice
```python
# SBAGLIATO!
fb.Execute(net_elements)
# ... non salvi la matrice ...
# ❌ Risultati persi alla prossima Execute()!

# CORRETTO!
fb.Execute(net_elements)
flow_matrix = fb.GetOrCreateFlowBundleMatrix("C_CORRETTA_AM")  # ✅ Ottieni matrice
flow_matrix.SaveToFile("results.mtx")  # ✅ Salva se necessario
```

---

## 🛠️ Tool MCP da Implementare

### `visum_flow_bundle_analysis`

```typescript
interface FlowBundleParams {
  projectId: string;
  demandSegments: string;  // "C_CORRETTA_AM" o "C,H"
  analysisType: "screen_line" | "cordon" | "link" | "custom";
  elements: {
    linkKeys?: [number, number][];  // [[from1, to1], [from2, to2]]
    nodeNos?: number[];
    zoneNos?: number[];
  };
  options?: {
    alternativeRoutes?: boolean;
    exportMatrix?: boolean;
    outputPath?: string;
  };
}

interface FlowBundleResult {
  success: boolean;
  statistics: {
    total_flow: number;
    avg_flow: number;
    max_flow: number;
    elements_count: number;
  };
  matrix_path?: string;  // Se exportMatrix=true
  top_od_pairs?: {
    origin: number;
    destination: number;
    flow: number;
  }[];
}
```

### Implementazione Python:

```python
def flow_bundle_analysis(params):
    """
    Esegue analisi flow bundle
    
    ⚠️ CHECKLIST:
    1. [ ] Clear() all'inizio
    2. [ ] Imposta DemandSegments
    3. [ ] Verifica PrT/PuT separati
    4. [ ] Crea net_elements correttamente
    5. [ ] Execute()
    6. [ ] GetOrCreateFlowBundleMatrix()
    7. [ ] Calcola statistiche
    8. [ ] Export se richiesto
    """
    
    try:
        # 1. ⚠️ SEMPRE Clear()
        fb = visum.Net.FlowBundle
        fb.Clear()
        
        # 2. ⚠️ SEMPRE imposta DemandSegments
        fb.DemandSegments = params["demandSegments"]
        
        # 3. Opzioni
        if params.get("options", {}).get("alternativeRoutes", False):
            fb.SetAlternativeRoutes(True)
        
        # 4. Crea net_elements
        net_elements = visum.CreateNetElements()
        elements_count = 0
        
        # Aggiungi link
        if "linkKeys" in params["elements"]:
            for from_node, to_node in params["elements"]["linkKeys"]:
                link = visum.Net.Links.ItemByKey(from_node, to_node)
                net_elements.Add(link)
                elements_count += 1
        
        # Aggiungi nodi
        if "nodeNos" in params["elements"]:
            for node_no in params["elements"]["nodeNos"]:
                node = visum.Net.Nodes.ItemByKey(node_no)
                net_elements.Add(node)
                elements_count += 1
        
        # Aggiungi zone
        if "zoneNos" in params["elements"]:
            for zone_no in params["elements"]["zoneNos"]:
                zone = visum.Net.Zones.ItemByKey(zone_no)
                net_elements.Add(zone)
                elements_count += 1
        
        # 5. Execute
        fb.Execute(net_elements)
        
        # 6. Ottieni matrice
        first_segment = params["demandSegments"].split(",")[0]
        flow_matrix = fb.GetOrCreateFlowBundleMatrix(first_segment)
        
        # 7. Calcola statistiche
        total_flow = flow_matrix.GetSum()
        avg_flow = flow_matrix.GetAverage()
        max_flow = flow_matrix.GetMax()
        
        result = {
            "success": True,
            "statistics": {
                "total_flow": total_flow,
                "avg_flow": avg_flow,
                "max_flow": max_flow,
                "elements_count": elements_count
            }
        }
        
        # 8. Export se richiesto
        if params.get("options", {}).get("exportMatrix", False):
            output_path = params.get("options", {}).get("outputPath", "flow_bundle.mtx")
            flow_matrix.SaveToFile(output_path)
            result["matrix_path"] = output_path
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
```

---

## 📚 Riferimenti API

### Metodi Principali:
- `Clear()` - ⚠️ SEMPRE chiamare prima!
- `Execute(INetElements)` - Esegue flow bundle
- `GetOrCreateFlowBundleMatrix(demandSegment)` - Ottiene matrice OD
- `SetAlternativeRoutes(bool)` - Abilita percorsi alternativi

### Proprietà:
- `DemandSegments` (string) - ⚠️ SEMPRE impostare!
- `ConditionDefined` (bool) - Check se condizioni definite

### Metodi Avanzati (Condizioni Custom):
- `CreateCondition()` - Condizione con activity type set
- `CreateConditionActiveLinks()` - Solo link attivi
- `CreateNewGroup()` - Gruppo condizioni con OR
- `ExecuteCurrentConditions()` - Esegue condizioni definite

---

## ✅ Checklist Implementazione

Quando implementi flow bundle, verifica:

- [ ] **Clear()** chiamato all'inizio
- [ ] **DemandSegments** impostato (non vuoto)
- [ ] **PrT e PuT separati** (non mescolare)
- [ ] **net_elements** creato correttamente
- [ ] **Execute()** chiamato
- [ ] **GetOrCreateFlowBundleMatrix()** per ottenere risultati
- [ ] **Statistiche** calcolate (GetSum, GetAverage, etc.)
- [ ] **Export matrice** se necessario (SaveToFile)
- [ ] **Gestione errori** implementata

---

## 🎯 Conclusioni

### IFlowBundle È Essenziale Per:
✅ **Screen line analysis** - Traffico attraverso barriere
✅ **Cordon analysis** - Traffico in/out zone
✅ **Origin/Destination analysis** - Da dove/verso dove
✅ **Link volume decomposition** - Componenti di flusso
✅ **Alternative routes** - Analisi percorsi alternativi

### Ricorda SEMPRE:
⚠️ **Clear() + DemandSegments = Coppia Inseparabile!**

```python
# Il pattern che non devi MAI dimenticare:
fb.Clear()
fb.DemandSegments = "YOUR_SEGMENTS_HERE"
fb.Execute(net_elements)
```

---

🎉 **Con IFlowBundle puoi fare analisi OD potentissime!** 🚀
