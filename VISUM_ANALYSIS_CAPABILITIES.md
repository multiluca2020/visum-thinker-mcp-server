# 📊 Visum Analysis Capabilities - Analisi Risultati Assegnazione

## 🎯 Panoramica

Dopo aver eseguito un'assegnazione PrT (Private Transport) in Visum, puoi analizzare i risultati in diversi modi attraverso la **COM API**. Questo documento descrive le capacità di analisi disponibili.

---

## 📈 Tipi di Analisi Disponibili

### 1. **Analisi Attributi dei Links** 🔗

Dopo l'assegnazione, i link hanno diversi attributi calcolati che puoi leggere e analizzare:

#### Attributi Principali (Post-Assegnazione):

| Attributo | Descrizione | Tipo | Esempio |
|-----------|-------------|------|---------|
| `VolVehPrT(AP)` | Volume veicoli PrT (Analysis Period) | Double | 1250.5 |
| `VolCarCur(AP)` | Volume veicoli corrente | Double | 980.2 |
| `CapPrT` | Capacità link per PrT | Double | 2000.0 |
| `VCurPrT_AP` | Volume/Capacity Ratio | Double | 0.625 |
| `TCur_PrT(AP)` | Tempo di percorrenza corrente | Double | 120.5 |
| `tCur` | Tempo corrente totale | Double | 125.0 |
| `Length` | Lunghezza link (km) | Double | 2.5 |

#### Come Leggere gli Attributi:

```python
# Metodo 1: Leggere singolo link
link = Visum.Net.Links.ItemByKey(from_node_no, to_node_no)
volume = link.AttValue("VolVehPrT(AP)")
capacity = link.AttValue("CapPrT")
vc_ratio = link.AttValue("VCurPrT_AP")

print(f"Link {from_node_no}->{to_node_no}:")
print(f"  Volume: {volume:.2f} veh/h")
print(f"  Capacity: {capacity:.2f} veh/h")
print(f"  V/C: {vc_ratio:.3f}")

# Metodo 2: Leggere TUTTI i links (più efficiente!)
all_links = Visum.Net.Links
attributes = ["No", "FromNodeNo", "ToNodeNo", "VolVehPrT(AP)", "CapPrT", "VCurPrT_AP", "Length"]
data = all_links.GetMultipleAttributes(attributes, True)  # True = only active links

# data è una lista di liste:
# [[Link_No1, FromNode1, ToNode1, Volume1, Capacity1, VC1, Length1],
#  [Link_No2, FromNode2, ToNode2, Volume2, Capacity2, VC2, Length2],
#  ...]

# Analisi: trova links congestionati
for row in data:
    link_no, from_node, to_node, volume, capacity, vc_ratio, length = row
    if vc_ratio > 0.85:  # Soglia congestione
        print(f"⚠️ Link {from_node}->{to_node}: V/C = {vc_ratio:.2f} (CONGESTIONATO!)")
```

---

### 2. **Flow Bundle (Flussi Origine-Destinazione)** 🌊

Il **FlowBundle** permette di analizzare i flussi tra specifiche origini e destinazioni:

```python
# Esempio: Flusso da Zona 1 a Zona 2 attraverso specifici link

fb = Visum.Net.FlowBundle
fb.Clear()

# Imposta demand segments
fb.DemandSegments = "C_CORRETTA_AM"  # O qualsiasi demand segment

# Definisci condizione: link specifico
target_link = Visum.Net.Links.ItemByKey(105227631, 105220716)
net_elements = Visum.CreateNetElements()
net_elements.Add(target_link)

# Esegui flow bundle
fb.Execute(net_elements)

# Il flow bundle crea una matrice con i flussi OD che passano per quel link
# Puoi salvarla o analizzarla
flow_matrix = fb.GetOrCreateFlowBundleMatrix(demand_segment)
```

#### Usi del Flow Bundle:
- **Screen line analysis**: Quanti veicoli attraversano una barriera virtuale?
- **Cordon analysis**: Analisi traffico in/out da una zona
- **Origin analysis**: Da dove proviene il traffico su un link congestionato?
- **Destination analysis**: Dove va il traffico che passa per un link?

---

### 3. **Grafici e Visualizzazioni** 🎨

#### A. **Bandwidth Graphics (Mappe con Larghezza Proporzionale ai Volumi)**

Visum permette di visualizzare i link con **larghezza proporzionale ai volumi** attraverso i **GraphicParameters**:

```python
# Accedi ai parametri grafici dei link
link_gpar = Visum.Graphics.Links

# Imposta visualizzazione classificata per volume
display = link_gpar.Display

# Attiva la visualizzazione
display.AttValue("Active") = True

# Accedi ai parametri di classificazione
classified_gpar = display.Marked.Classified

# Imposta attributo da visualizzare
classified_gpar.AttValue("Attribute") = "VolVehPrT(AP)"

# Imposta modalità: larghezza proporzionale
classified_gpar.AttValue("ClassificationMode") = 1  # 1 = By attribute

# Definisci classi di larghezza (bandwidth)
classes = classified_gpar.Classes

# Esempio: 5 classi di volume
class_breaks = [0, 500, 1000, 1500, 2000, 99999]
widths = [1, 2, 4, 6, 8]  # Larghezze in pixel
colors = [RGB(0,255,0), RGB(255,255,0), RGB(255,128,0), RGB(255,0,0), RGB(128,0,0)]

for i in range(5):
    class_obj = classes.ItemByKey(i+1)
    class_obj.AttValue("UpperBound") = class_breaks[i+1]
    class_obj.AttValue("Width") = widths[i]
    class_obj.AttValue("Color") = colors[i]

# Aggiorna la visualizzazione
Visum.Graphic.Draw()
```

#### B. **Node Flow Charts (Diagrammi di Flusso ai Nodi)**

```python
# Attiva visualizzazione node flows
node_flows = Visum.Graphic.NodeFlows
node_flows.AttValue("Active") = True

# Configura parametri
node_flows.AttValue("DisplayMode") = 1  # 1 = Bar charts
node_flows.AttValue("Attribute") = "VolVehPrT(AP)"
node_flows.AttValue("ScaleFactor") = 0.5  # Dimensione diagrammi

# Esporta node flow graphic per un nodo specifico
node = Visum.Net.Nodes.ItemByKey(12345)
Visum.Graphic.ExportNodeFlowGraphic(node, "C:\\output\\node_12345_flow.png")
```

#### C. **Turn Volume Charts (Volumi di Svolta)**

```python
# Accedi ai parametri grafici delle svolte
turn_gpar = Visum.Graphics.Turns.TurnVolumes

# Attiva visualizzazione
turn_gpar.General.AttValue("Active") = True

# Configura attributo
turn_gpar.General.AttValue("Attribute") = "VolVehPrT(AP)"

# Modalità di visualizzazione
turn_gpar.General.AttValue("DisplayType") = 2  # 2 = Circle display (diagrammi circolari)

# Aggiorna
Visum.Graphic.Draw()
```

---

### 4. **Export e Screenshot** 📸

#### A. **Export Immagini**

```python
# Screenshot della finestra corrente
Visum.Graphic.Screenshot("C:\\output\\network_volumes.png")

# Export con coordinate specifiche
Visum.Graphic.ExportNetworkImageFile(
    "C:\\output\\detail_area.png",
    min_x=123000, min_y=456000,
    max_x=125000, max_y=458000,
    width=1920, height=1080
)

# Export SVG (vettoriale)
Visum.Graphic.ExportSVG("C:\\output\\network_volumes.svg")
```

#### B. **Export Liste e Tabelle**

```python
# Crea lista dei link con attributi
link_list = Visum.Lists.CreateLinkList()
link_list.AddColumn("No")
link_list.AddColumn("FromNodeNo")
link_list.AddColumn("ToNodeNo")
link_list.AddColumn("VolVehPrT(AP)", decplaces=2)
link_list.AddColumn("CapPrT", decplaces=2)
link_list.AddColumn("VCurPrT_AP", decplaces=3)
link_list.AddColumn("Length", decplaces=3)

# Salva in file
link_list.SaveToAttributeFile("C:\\output\\link_volumes.att")

# O mostra a schermo
link_list.Show()
```

---

## 🔍 Analisi Avanzate

### 5. **Shortest Path Analysis (Analisi Percorsi)**

```python
# Shortest path searcher (molto veloce per query multiple)
searcher = Visum.Analysis.TSysSet.ItemByKey("C").CreatePrTShortestPathSearch()

# Configura origine e destinazione
origin_zone = Visum.Net.Zones.ItemByKey(1)
destination_zone = Visum.Net.Zones.ItemByKey(100)

# Esegui ricerca
searcher.SetOrigin(origin_zone)
searcher.SetDestination(destination_zone)
path_found = searcher.Execute()

if path_found:
    # Leggi risultati
    path_length = searcher.AttValue("PathLength")  # km
    path_time = searcher.AttValue("PathTravelTime")  # minuti
    path_cost = searcher.AttValue("PathImpedance")
    
    print(f"Percorso da {origin_zone} a {destination_zone}:")
    print(f"  Lunghezza: {path_length:.2f} km")
    print(f"  Tempo: {path_time:.2f} min")
    print(f"  Costo: {path_cost:.2f}")
    
    # Ottieni links del percorso
    path_links = searcher.GetPath()
    for link in path_links:
        print(f"  Link: {link.AttValue('FromNodeNo')}->{link.AttValue('ToNodeNo')}")
```

### 6. **Matrix Analysis (Analisi Matrici)**

```python
# Leggi matrice di skim (tempi di viaggio)
demand_segment = Visum.Net.DemandSegments.ItemByKey("C_CORRETTA_AM")
skim_matrix = demand_segment.GetMatrix("tCur")

# Statistiche sulla matrice
total_trips = skim_matrix.GetSum()
avg_time = skim_matrix.GetAverage()
max_time = skim_matrix.GetMax()

print(f"Matrice Tempi di Viaggio:")
print(f"  Totale spostamenti: {total_trips:.0f}")
print(f"  Tempo medio: {avg_time:.2f} min")
print(f"  Tempo massimo: {max_time:.2f} min")

# Leggi valore specifico OD
time_1_to_100 = skim_matrix.GetValue(zone_1_no, zone_100_no)
print(f"Tempo da zona 1 a zona 100: {time_1_to_100:.2f} min")
```

---

## 🛠️ Tool MCP da Creare

### Idee per Nuovi Tool:

#### 1. **`visum_analyze_assignment_results`**
```json
{
  "name": "visum_analyze_assignment_results",
  "description": "Analizza risultati di un'assegnazione PrT",
  "parameters": {
    "projectId": "string",
    "analysisType": "volumes|congestion|flows|statistics",
    "filters": {
      "minVC": 0.0,
      "maxVC": 1.5,
      "linkTypes": ["1", "2", "3"]
    }
  },
  "returns": {
    "summary": {
      "total_links": 15234,
      "congested_links": 87,
      "avg_volume": 456.7,
      "avg_vc_ratio": 0.45
    },
    "congested_links": [
      {"from": 123, "to": 456, "volume": 1850, "capacity": 2000, "vc": 0.925},
      ...
    ]
  }
}
```

#### 2. **`visum_create_bandwidth_map`**
```json
{
  "name": "visum_create_bandwidth_map",
  "description": "Crea mappa con larghezza link proporzionale ai volumi",
  "parameters": {
    "projectId": "string",
    "attribute": "VolVehPrT(AP)",
    "classBreaks": [0, 500, 1000, 1500, 2000, 99999],
    "widths": [1, 2, 4, 6, 8],
    "colors": ["green", "yellow", "orange", "red", "darkred"],
    "exportPath": "C:\\output\\bandwidth_map.png"
  }
}
```

#### 3. **`visum_export_results`**
```json
{
  "name": "visum_export_results",
  "description": "Esporta risultati assegnazione in formato CSV/Excel",
  "parameters": {
    "projectId": "string",
    "exportType": "links|nodes|turns|matrices",
    "attributes": ["No", "VolVehPrT(AP)", "CapPrT", "VCurPrT_AP"],
    "filters": {"Active": true},
    "outputPath": "C:\\output\\results.csv"
  }
}
```

#### 4. **`visum_flow_bundle_analysis`**
```json
{
  "name": "visum_flow_bundle_analysis",
  "description": "Analizza flussi OD attraverso specifici link/aree",
  "parameters": {
    "projectId": "string",
    "demandSegments": "C_CORRETTA_AM",
    "screenLine": {
      "linkKeys": [[123, 456], [456, 789]]
    },
    "exportMatrixPath": "C:\\output\\flow_matrix.mtx"
  }
}
```

---

## 📊 Workflow Tipico di Analisi

### Step 1: Esegui Assegnazione
```python
# Usa tool esistente visum_create_procedure
procedure = visum_create_procedure({
    "projectId": project_id,
    "procedureType": "PrT_Assignment",
    "position": 10
})

# Configura DSEGSET
visum_configure_dsegset({
    "projectId": project_id,
    "procedurePosition": procedure["actual_position"],
    "segmentNumbers": "1-10"
})

# Esegui procedura
# (tramite Visum.Procedures.Execute() o operationExecutor)
```

### Step 2: Leggi Risultati
```python
# Ottieni tutti i link con volumi
all_links = Visum.Net.Links
data = all_links.GetMultipleAttributes([
    "No", "FromNodeNo", "ToNodeNo", 
    "VolVehPrT(AP)", "CapPrT", "VCurPrT_AP", "Length"
], True)
```

### Step 3: Analizza
```python
# Trova links congestionati
congested = []
for row in data:
    link_no, from_n, to_n, vol, cap, vc, length = row
    if vc > 0.85:
        congested.append({
            "link": f"{from_n}->{to_n}",
            "volume": vol,
            "capacity": cap,
            "vc_ratio": vc,
            "length": length
        })

# Ordina per VC ratio
congested.sort(key=lambda x: x["vc_ratio"], reverse=True)
```

### Step 4: Visualizza
```python
# Crea bandwidth map
# (usando visum_create_bandwidth_map quando implementato)

# O export screenshot
Visum.Graphic.Screenshot("C:\\output\\congestion_map.png")
```

### Step 5: Export
```python
# Export lista links congestionati
with open("C:\\output\\congested_links.csv", "w") as f:
    f.write("Link,Volume,Capacity,VC_Ratio,Length\n")
    for item in congested:
        f.write(f"{item['link']},{item['volume']:.2f},"
                f"{item['capacity']:.2f},{item['vc_ratio']:.3f},"
                f"{item['length']:.3f}\n")
```

---

## 🎯 Conclusioni

### Cosa Puoi Fare:
✅ **Leggere attributi** di tutti i link (volumi, capacità, V/C ratio)
✅ **Analizzare flussi OD** con Flow Bundles
✅ **Creare mappe bandwidth** con larghezza proporzionale ai volumi
✅ **Visualizzare node flows** e turn volumes
✅ **Export immagini e dati** in vari formati
✅ **Analisi percorsi** origine-destinazione
✅ **Statistiche matrici** di skim

### Cosa Serve Implementare (Tool MCP):
🔧 `visum_analyze_assignment_results` - Analisi automatica risultati
🔧 `visum_create_bandwidth_map` - Creazione mappe bandwidth
🔧 `visum_export_results` - Export dati in CSV/Excel
🔧 `visum_flow_bundle_analysis` - Analisi flow bundles
🔧 `visum_get_link_attributes` - Lettura attributi multipli link

---

## 📚 Riferimenti API

### Interfaces Chiave:
- **ILinks**: Collezione di tutti i link
- **ILink**: Singolo link
- **IFlowBundle**: Analisi flussi OD
- **IGraphic**: Funzioni grafiche
- **IGraphicParameters**: Parametri visualizzazione (non trovato in docs ma referenziato)
- **INodeFlows**: Diagrammi di flusso ai nodi
- **IPrTShortestPathSearch**: Ricerca percorsi

### Metodi Chiave:
- `GetMultipleAttributes(attributes, onlyActive)` - Lettura efficiente di molti attributi
- `SetAttValue(attribute, value)` - Imposta valore attributo
- `AttValue(attribute)` - Leggi valore attributo
- `FlowBundle.Execute(netElements)` - Calcola flow bundle
- `Graphic.Screenshot(path)` - Screenshot
- `Graphic.ExportNetworkImageFile(...)` - Export con coordinate

---

🎉 **Visum offre potenti capacità di analisi post-assegnazione!** 🚀

Per implementare questi tool MCP, basta estendere `src/index.ts` con nuovi handler che utilizzano questi metodi API.
