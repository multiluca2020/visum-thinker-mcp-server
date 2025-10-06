# 📋 Script: List PRT Demand Segments

## 🎯 Scopo

Questo script identifica automaticamente tutti i **Transport Systems di tipo PRT** in un progetto Visum e i loro **demand segments** associati.

## 🔧 Quando Usarlo

### 1. **Elencare Modi PRT Disponibili**
Quando l'utente chiede:
- "Quali sono i modi PRT nel progetto?"
- "Mostrami i transport systems PRT"
- "Elenca i demand segments disponibili per PRT"

### 2. **Prima di Creare una Procedura PrT Assignment**
Quando Claude deve:
- Creare una nuova procedura di assegnazione al trasporto privato
- Chiedere all'utente quali segments includere
- Configurare l'attributo `DSEGSET`

### 3. **Selezione Interattiva**
Quando l'utente vuole:
- Scegliere specifici demand segments tra quelli disponibili
- Includere solo alcuni modi (es: solo "C" per Car, escludendo "H" per HGV)
- Vedere cosa è disponibile prima di procedere

## 📤 Output

Lo script fornisce:

1. **Lista Transport Systems PRT**
   ```
   CAR   (Nome: Car)
   HGV   (Nome: HGV)
   MOTO  (Nome: Moto)
   ```

2. **Mapping Mode → TSys**
   ```
   Mode "C" (Car) → TSys CAR
   Mode "H" (HGV) → TSys HGV
   ```

3. **Demand Segments per Mode**
   ```
   Mode "C": 24 segments
     - C_CORRETTA_AM
     - C_CORRETTA_IP1
     - ...
   
   Mode "H": 12 segments
     - H_INIZIALE_AM
     - ...
   ```

4. **DSEGSET Completo** (comma-separated)
   ```
   C_CORRETTA_AM,C_CORRETTA_IP1,...,H_INIZIALE_PM,H_INIZIALE_S
   ```

## 🚀 Utilizzo

```bash
node list-prt-demand-segments.js
```

**Prerequisiti:**
- Server Visum TCP in esecuzione sulla porta 7905
- Progetto Visum aperto con almeno un Transport System di tipo PRT

## 📊 Struttura Dati Visum

### Relazioni
```
Transport System (TYPE="PRT")
    ↓ (collegato per nome)
Mode (CODE="C", NAME="Car")
    ↓ (attributo MODE)
Demand Segment (CODE="C_CORRETTA_AM", MODE="C")
```

### Note Importanti
- **Modes e TSys NON sono collegati direttamente** in alcuni progetti Visum
- Il collegamento avviene tramite **match del nome** (es: Mode "Car" → TSys "Car")
- I **demand segments** hanno un attributo `MODE` che li collega ai Modes
- I **Transport Systems** hanno un attributo `TYPE` che identifica se sono PRT

## 🔄 Flusso di Lavoro con Claude

### Scenario 1: Creazione Procedura PrT Assignment

1. **Claude esegue** `list-prt-demand-segments.js`
2. **Claude mostra** all'utente i modi PRT disponibili e i loro segments
3. **Claude chiede**: "Vuoi includere tutti questi segments o solo alcuni?"
4. **Utente risponde**: 
   - "Tutti" → usa DSEGSET completo
   - "Solo C" → usa solo segments con MODE="C"
   - "C e H" → usa segments con MODE="C" e MODE="H"
5. **Claude crea** la procedura con il DSEGSET appropriato

### Scenario 2: Verifica Configurazione

1. Utente chiede: "Quali demand segments sono configurati nella procedura?"
2. Claude esegue `list-prt-demand-segments.js`
3. Claude confronta i segments disponibili con quelli configurati
4. Claude segnala eventuali segments mancanti o non disponibili

## 📝 Esempio di Interazione

```
User: "Voglio creare una procedura PrT Assignment"

Claude: 
1. Esegue list-prt-demand-segments.js
2. Mostra: "Ho trovato 2 modi PRT:
   - Mode C (Car): 24 segments
   - Mode H (HGV): 12 segments
   
   Vuoi includere tutti i 36 segments o solo alcuni?"

User: "Solo il modo C"

Claude:
"Perfetto! Configurerò la procedura con i 24 segments del modo C:
C_CORRETTA_AM,C_CORRETTA_IP1,..."
```

## 🛠️ Modifiche Future

Se la struttura del progetto Visum cambia:

1. **Aggiungere altri attributi di matching**: 
   - Modificare la sezione "STEP 2" per includere altri criteri di match
   
2. **Filtrare segments per criteri specifici**:
   - Aggiungere filtri per time slice (AM, PM, IP1, ...)
   - Filtrare per tipo di scenario (CORRETTA, INIZIALE, ITERAZIONE, ...)

3. **Output personalizzato**:
   - Modificare il formato di output per integrazioni specifiche
   - Esportare in JSON per altre applicazioni

## 📚 File Correlati

- `create-complete-prt-procedure.js` - Crea procedura PrT Assignment
- `search-visum.js` - Cerca progetti Visum
- `test-visum-analysis.js` - Test analisi Visum

## 🐛 Troubleshooting

### Errore: "Nessun Transport System di tipo PRT trovato"
- Verificare che il progetto abbia TSys con `TYPE="PRT"`
- Controllare in Visum GUI: Base Data → Network → Transport Systems

### Errore: "Nessun Mode associato ai Transport Systems PRT"
- I nomi dei Modes potrebbero non corrispondere ai nomi dei TSys
- Verificare in Visum GUI i nomi esatti
- Modificare la logica di matching in STEP 2 dello script

### Errore: "Call was rejected by callee"
- Visum è occupato o in stato non valido
- Chiudere eventuali dialog aperti in Visum
- Riavviare il server TCP se necessario

## 📄 Licenza

MIT License - Parte del progetto Sequential Thinking MCP Server
