# PrT Skim Matrix Configuration Guide

## Panoramica

Questa guida documenta la configurazione corretta per creare skim matrices PrT in Visum usando l'API COM. È basata sulla documentazione HTML ufficiale di Visum e risolve i problemi riscontrati con implementazioni precedenti che assumevano API inesistenti.

## Problema Risolto

**Tentativo Errato #1:**
```python
# ❌ NON FUNZIONA - AddProcedure non esiste
skim_proc = visum.Procedures.AddProcedure(14)
```

**Tentativo Errato #2:**
```python
# ❌ NON FUNZIONA - PrTSkimPara non esiste
skim_op = operations.AddOperation(position)
skim_op.SetAttValue("OPERATIONTYPE", 103)
skim_params = skim_op.PrTSkimPara  # Errore: attributo inesistente
```

**Tentativo Errato #3:**
```python
# ❌ NON FUNZIONA - TSysCode non esiste su operazione 103
skim_op.SetAttValue("TSysCode", "CAR")
skim_op.SetAttValue("LinkImpedance", "T0")
```

**Implementazione Corretta:**
```python
# ✅ FUNZIONA - API verificata da documentazione HTML
skim_op = operations.AddOperation(position)
skim_op.SetAttValue("OPERATIONTYPE", 103)

# Accedi ai parametri (nome corretto dalla doc)
skim_params = skim_op.PrTSkimMatrixParameters  # IPrTSkimMatrixPara

# Configura demand segment
skim_params.SetAttValue("DSeg", "CAR_ATTUALE_AM")

# Configura criterio di ricerca (impedance)
skim_params.SetAttValue("SearchCriterion", "criteria_t0")

# Seleziona quali skim calcolare
skim_t0 = skim_params.SingleSkimMatrixParameters("T0")
skim_t0.SetAttValue("Calculate", True)
```

## Struttura API Completa

### 1. Gerarchia degli Oggetti

```
IOperation (operation type 103)
    └─> PrTSkimMatrixParameters : IPrTSkimMatrixPara
        ├─> AttValue("DSeg")
        ├─> AttValue("SearchCriterion")  
        ├─> AttValue("Weighting")
        └─> SingleSkimMatrixParameters(name) : ISingleSkimMatrixPara
            ├─> AttValue("Calculate")
            ├─> AttValue("SaveToFile")
            └─> AttValue("Name")
```

### 2. Attributi IPrTSkimMatrixPara

| Attributo | Tipo | Descrizione |
|-----------|------|-------------|
| `DSeg` | string | Demand segment code (es: "CAR_ATTUALE_AM") |
| `SearchCriterion` | PrTSearchCriterionT | Criterio per ricerca percorso minimo |
| `Filename` | string | Base filename per matrici salvate su file |
| `Format` | MatrixFormat | Formato output matrici su file |
| `OnlyRelationsWithDemand` | bool | Calcola solo relazioni con domanda > 0 |
| `SelectODRelationType` | AssignmentSelectODRelation | Tipo relazioni O-D da considerare |
| `Separator` | string | Separatore per file output |
| `SumUpLinks` | bool | Somma attributi link |
| `SumUpOrigConns` | bool | Somma connettori origine |
| `SumUpDestConns` | bool | Somma connettori destinazione |
| `SumUpTurns` | bool | Somma svolte |
| `SumUpResTrafAreas` | bool | Somma aree traffico ristrette |
| `UseExistingPaths` | bool | Usa percorsi esistenti |
| `Weighting` | string | Ponderazione |

**Fonte:** `VISUMLIB~IPrTSkimMatrixPara_attributes.html`

### 3. Enum PrTSearchCriterionT

| Valore | Codice | Descrizione |
|--------|--------|-------------|
| `criteria_t0` | 0 | Free flow speed (t₀) |
| `criteria_tCur` | 1 | Current speed (t_cur) |
| `criteria_Impedance` | 2 | Impedance |
| `criteria_Distance` | 3 | Link length |
| `criteria_AddVal1` | 4 | AddVal 1 |
| `criteria_AddVal2` | 5 | AddVal 2 |
| `criteria_AddVal3` | 6 | AddVal 3 |

**Fonte:** `VISUMLIB~PrTSearchCriterionT.html`

### 4. Skim Matrix Names

| Nome | Descrizione | Unità |
|------|-------------|-------|
| `T0` | Free flow travel time | secondi |
| `TCur` | Travel time in loaded network | secondi |
| `V0` | Free flow speed | km/h |
| `VCur` | Speed in a loaded network | km/h |
| `Impedance` | Impedance = f(tCur) | - |
| `TripDist` | Trip distance | metri |
| `DirectDist` | Direct distance | metri |
| `Addval1` | AddValue 1 | - |
| `Addval2` | AddValue 2 | - |
| `Toll` | Toll amounts by link along the route | - |
| `Userdef` | User-defined | - |

**Fonte:** `VISUMLIB~IPrTSkimMatrixPara~SingleSkimMatrixParameters.html`

### 5. Attributi ISingleSkimMatrixPara

| Attributo | Tipo | Default | Descrizione |
|-----------|------|---------|-------------|
| `Calculate` | bool | false | Calcola questa skim |
| `Name` | string | - | Nome skim (read-only) |
| `SaveToFile` | bool | false | Salva su file |

**Fonte:** `VISUMLIB~ISingleSkimMatrixPara_attributes.html`

## Implementazione Completa

### Script Python per Console Visum

```python
def create_skim_matrices_t0(demand_segment="CAR_ATTUALE_AM", matrix_no=1):
    """
    Crea skim matrices con tempi T0 (flusso libero)
    
    Args:
        demand_segment: Demand segment code (UN SOLO segment!)
        matrix_no: Matrix number (default: 1)
    """
    visum = Visum  # Console Visum
    
    # Trova posizione libera
    operations = visum.Procedures.Operations
    last_pos = 0
    for i in range(1, 101):
        try:
            operations.ItemByKey(i)
            last_pos = i
        except:
            break
    
    new_pos = last_pos + 1
    
    # Crea operazione skim
    skim_op = operations.AddOperation(new_pos)
    skim_op.SetAttValue("OPERATIONTYPE", 103)
    
    # Configura parametri
    skim_params = skim_op.PrTSkimMatrixParameters
    
    # Demand segment
    skim_params.SetAttValue("DSeg", demand_segment)
    
    # Criterio ricerca: T0 (tempi flusso libero)
    skim_params.SetAttValue("SearchCriterion", "criteria_t0")
    
    # Configura skim da calcolare
    
    # T0: Tempi flusso libero
    skim_t0 = skim_params.SingleSkimMatrixParameters("T0")
    skim_t0.SetAttValue("Calculate", True)
    skim_t0.SetAttValue("SaveToFile", False)
    
    # TripDist: Distanza percorso
    skim_dist = skim_params.SingleSkimMatrixParameters("TripDist")
    skim_dist.SetAttValue("Calculate", True)
    skim_dist.SetAttValue("SaveToFile", False)
    
    # V0: Velocità flusso libero (opzionale)
    skim_v0 = skim_params.SingleSkimMatrixParameters("V0")
    skim_v0.SetAttValue("Calculate", True)
    skim_v0.SetAttValue("SaveToFile", False)
    
    print("✓ Operazione skim configurata alla posizione {}".format(new_pos))
    print("  - DSeg: {}".format(demand_segment))
    print("  - SearchCriterion: criteria_t0")
    print("  - Skim attive: T0, TripDist, V0")
    
    # Esegui calcolo
    visum.Procedures.Execute()
    
    print("✓ Calcolo completato")
```

### Uso da Console Visum

```python
# 1. Carica script
exec(open(r"H:\visum-thinker-mcp-server\import-osm-network.py", encoding='utf-8').read())

# 2. Crea skim con tutti i segments MODE='C'
result = create_skim_matrices(matrix_no=1)

# 3. Oppure specifica demand segment
result = create_skim_matrices(
    matrix_no=1, 
    demand_segments="CAR_ATTUALE_AM"
)

# 4. Verifica risultato
print(result)
```

## Test della Configurazione

Prima di eseguire il calcolo completo, verifica che l'API funzioni:

```bash
python test-skim-config.py
```

Questo script testa:
- Accesso a `PrTSkimMatrixParameters`
- Configurazione `DSeg`
- Configurazione `SearchCriterion`
- Accesso a `SingleSkimMatrixParameters()`
- Impostazione `Calculate`

Se tutti i test sono ✓, l'implementazione è corretta.

## Risoluzione Problemi

### Errore: "AttValue failed: The referenced network object does not exist"

**Causa:** Tentativo di impostare DSeg con una lista di segments (es: "CAR_ATTUALE_AM,HGV_AM") o segment inesistente

**Soluzione:**
```python
# ❌ Errato - DSeg non accetta liste
skim_params.SetAttValue("DSeg", "CAR_ATTUALE_AM,HGV_AM")

# ✅ Corretto - un solo segment
skim_params.SetAttValue("DSeg", "CAR_ATTUALE_AM")

# ✅ Se hai più segments, usa solo il primo
segments = "CAR_ATTUALE_AM,HGV_AM"
first_segment = segments.split(",")[0]
skim_params.SetAttValue("DSeg", first_segment)
```

### Errore: "object has no attribute 'PrTSkimMatrixParameters'"

**Causa:** Nome property errato o operazione non di tipo 103

**Soluzione:**
```python
# Verifica tipo operazione
print(skim_op.AttValue("OPERATIONTYPE"))  # Deve essere 103

# Verifica property disponibili
for attr in dir(skim_op):
    if "skim" in attr.lower():
        print(attr)
```

### Errore: "Could not find attribute with ID SearchCriterion"

**Causa:** Tentativo di impostare SearchCriterion direttamente su operation invece che su parameters

**Soluzione:**
```python
# ❌ Errato
skim_op.SetAttValue("SearchCriterion", "criteria_t0")

# ✅ Corretto
skim_params = skim_op.PrTSkimMatrixParameters
skim_params.SetAttValue("SearchCriterion", "criteria_t0")
```

### Errore: "Call was rejected by callee"

**Causa:** Tentativo di accedere a proprietà durante operazioni COM intensive

**Soluzione:** Usa documentazione HTML invece di esplorazione runtime con `dir()`

## Riferimenti Documentazione

- **IOperation:** `VISUMLIB~IOperation.html`
- **IPrTSkimMatrixPara:** `VISUMLIB~IPrTSkimMatrixPara.html`
- **IPrTSkimMatrixPara Attributes:** `VISUMLIB~IPrTSkimMatrixPara_attributes.html`
- **ISingleSkimMatrixPara:** `VISUMLIB~ISingleSkimMatrixPara.html`
- **ISingleSkimMatrixPara Attributes:** `VISUMLIB~ISingleSkimMatrixPara_attributes.html`
- **PrTSearchCriterionT:** `VISUMLIB~PrTSearchCriterionT.html`
- **SingleSkimMatrixParameters Property:** `VISUMLIB~IPrTSkimMatrixPara~SingleSkimMatrixParameters.html`

## Storico Modifiche

- **2024-02-13:** Implementazione iniziale con API errata (AddProcedure)
- **2024-02-13:** Correzione a Operations.AddOperation con OPERATIONTYPE 103
- **2024-02-13:** Tentativo fallito con attributi diretti (TSysCode, LinkImpedance)
- **2024-02-13:** Scoperta demand segments tramite MODE='C'
- **2024-02-13:** Lettura documentazione HTML e scoperta API corretta
- **2024-02-13:** ✅ Implementazione finale con PrTSkimMatrixParameters

## Note Importanti

1. **SEMPRE usa documentazione HTML** - Non assumere nomi di property/metodi
2. **SearchCriterion predefinito:** `CriteriaImpedance` - sovrascrivi con `criteria_t0` per T0
3. **Calculate predefinito:** `false` - DEVE essere impostato a `True` per ogni skim
4. **Operazioni eseguono sequenzialmente** - `visum.Procedures.Execute()` esegue TUTTE le operations
5. **Demand segments PrT** - Identificati da MODE attribute (es: MODE='C' per Car)
6. **⚠️ LIMITAZIONE: DSeg accetta UN SOLO segment** - Non è possibile passare una lista separata da virgole. Per calcolare skim per più segments, crea operazioni separate o usa un loop.

## Validazione API

Lo script `test-skim-config.py` implementa una validazione completa dell'API senza eseguire il calcolo. Esegui sempre questo test prima di procedere con l'implementazione completa.

**Test Coverage:**
- ✓ Creazione operazione tipo 103
- ✓ Accesso a PrTSkimMatrixParameters
- ✓ Configurazione DSeg
- ✓ Configurazione SearchCriterion con diversi formati
- ✓ Accesso a SingleSkimMatrixParameters per T0, TCur, TripDist
- ✓ Impostazione Calculate=True
- ✓ Cleanup operazione test
