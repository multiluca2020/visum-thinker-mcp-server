# MCP Quick Call - Comandi Rapidi

Quando testi il server MCP manualmente da terminale, usa `mcp-quick-call.js` che **termina automaticamente** dopo la risposta invece di rimanere appeso.

## Problema

Il server MCP è progettato per rimanere in ascolto su stdin/stdout, quindi quando fai:
```powershell
echo '{"jsonrpc":"2.0",...}' | node build/index.js
```
Il server risponde ma **non termina** (rimane in attesa di altri comandi).

## Soluzione: mcp-quick-call.js

```powershell
# Sintassi
node mcp-quick-call.js <tool_name> '<json_arguments>'

# Oppure usa npm
npm run call <tool_name> '<json_arguments>'
```

## Esempi

### 1. Lista Demand Segments
```powershell
node mcp-quick-call.js visum_list_demand_segments '{\"projectId\":\"100625_Versione_base_v0.3_sub_ok_priv_10176442\"}'
```

### 2. Crea Procedura PrT Assignment
```powershell
node mcp-quick-call.js visum_create_procedure '{\"projectId\":\"100625_Versione_base_v0.3_sub_ok_priv_10176442\",\"procedureType\":\"PrT_Assignment\"}'
```

### 3. Configura DSEGSET con numeri
```powershell
node mcp-quick-call.js visum_configure_dsegset '{\"projectId\":\"100625_Versione_base_v0.3_sub_ok_priv_10176442\",\"procedurePosition\":578,\"segmentNumbers\":\"1-10\"}'
```

### 4. Configura DSEGSET per modo specifico
```powershell
node mcp-quick-call.js visum_configure_dsegset '{\"projectId\":\"100625_Versione_base_v0.3_sub_ok_priv_10176442\",\"procedurePosition\":578,\"filterMode\":\"C\"}'
```

### 5. Apri Progetto Visum
```powershell
node mcp-quick-call.js project_open '{\"projectPath\":\"H:\\\\go\\\\italferr2025\\\\Campoleone\\\\100625_Versione_base_v0.3_sub_ok_priv.ver\"}'
```

## Come Funziona

Lo script:
1. ✅ Avvia il server MCP come processo figlio
2. ✅ Invia il comando JSON-RPC
3. ✅ Aspetta la risposta
4. ✅ **Termina automaticamente** il server dopo la risposta
5. ✅ Timeout di 30 secondi per sicurezza

## Workflow Completo di Test

```powershell
# 1. Compila il progetto
npm run build

# 2. Apri il progetto Visum (se necessario)
node mcp-quick-call.js project_open '{\"projectPath\":\"H:\\\\go\\\\italferr2025\\\\Campoleone\\\\100625_Versione_base_v0.3_sub_ok_priv.ver\"}'

# 3. Lista i demand segments con numerazione
node mcp-quick-call.js visum_list_demand_segments '{\"projectId\":\"100625_Versione_base_v0.3_sub_ok_priv_10176442\"}'

# 4. Crea una nuova procedura PrT Assignment
node mcp-quick-call.js visum_create_procedure '{\"projectId\":\"100625_Versione_base_v0.3_sub_ok_priv_10176442\",\"procedureType\":\"PrT_Assignment\"}'
# ⚠️ Nota la "Posizione Effettiva" restituita (es: 578)

# 5. Configura i demand segments (usa la posizione dalla risposta precedente)
node mcp-quick-call.js visum_configure_dsegset '{\"projectId\":\"100625_Versione_base_v0.3_sub_ok_priv_10176442\",\"procedurePosition\":578,\"segmentNumbers\":\"1-10\"}'

# 6. Verifica in Visum: Procedures → Operations → Posizione 578
```

## Nota per PowerShell

In PowerShell devi **escapare le virgolette** nel JSON:
```powershell
# ✅ Corretto
'{\"key\":\"value\"}'

# ❌ Errato
'{"key":"value"}'
```

Oppure usa backtick:
```powershell
"{`"key`":`"value`"}"
```

## Alternative

Se preferisci non usare lo script wrapper, puoi:

1. **Terminare manualmente** con Ctrl+C dopo la risposta
2. **Usare Claude Desktop** o altro client MCP che gestisce la connessione
3. **Creare script Python** che chiamano il server MCP via subprocess

## Uso in Produzione

In produzione (con Claude Desktop, Cline, ecc.), il server MCP viene avviato automaticamente e rimane attivo per gestire più richieste. Questo comportamento è **corretto e desiderato**.

Lo script `mcp-quick-call.js` è **solo per test manuali**.
