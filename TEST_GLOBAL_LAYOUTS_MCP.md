# Test Global Layouts via Claude MCP

## Step 1: Apri il progetto S000009result.ver

Invia questo comando a Claude Desktop (via MCP):

```json
{
  "method": "tools/call",
  "params": {
    "name": "project_open",
    "arguments": {
      "projectPath": "H:\\go\\reports\\Input\\S000009result.ver"
    }
  },
  "jsonrpc": "2.0",
  "id": 1
}
```

**Risposta attesa:**
Claude ti restituirà un messaggio tipo:
```
🚀 Progetto Aperto con Server TCP

✅ Server progetto avviato su porta 7XXX

📊 Dettagli Server:
- ID Progetto: S000009result_12345678
- Nome: S000009result
- Porta TCP: 7XXX
- PID: XXXXX
- Status: ready
```

**IMPORTANTE:** Copia il **ID Progetto** dalla risposta (es: `S000009result_12345678`)

---

## Step 2: Lista Global Layouts

Usa l'ID progetto ottenuto nello Step 1:

```json
{
  "method": "tools/call",
  "params": {
    "name": "project_list_global_layouts",
    "arguments": {
      "projectId": "S000009result_12345678"
    }
  },
  "jsonrpc": "2.0",
  "id": 2
}
```

**Sostituisci** `S000009result_12345678` con l'ID reale ricevuto!

**Risposta attesa:**
```
🗂️ Global Layouts (progetto: S000009result_12345678)

Totale: X
Associati a file .lay: X
Non associati: X

1. #1 | Nome Layout
   File: C:\path\to\file.lay
   Versione: 25.00
   Associato: ✅

...
```

---

## Workflow Completo in Claude Chat

Puoi anche semplicemente chiedere a Claude:

**Messaggio 1:**
```
Apri il progetto Visum: H:\go\reports\Input\S000009result.ver
```

Claude userà automaticamente `project_open` e ti mostrerà l'ID progetto.

**Messaggio 2:**
```
Lista i Global Layouts di questo progetto
```

Claude userà automaticamente `project_list_global_layouts` con l'ID del progetto aperto.

---

## File JSON Pronti (se preferisci copia-incolla)

### test-open-s000009.json
```json
{
  "method": "tools/call",
  "params": {
    "name": "project_open",
    "arguments": {
      "projectPath": "H:\\go\\reports\\Input\\S000009result.ver"
    }
  },
  "jsonrpc": "2.0",
  "id": 1
}
```

### test-list-layouts-s000009.json (DOPO aver ottenuto projectId)
```json
{
  "method": "tools/call",
  "params": {
    "name": "project_list_global_layouts",
    "arguments": {
      "projectId": "INSERISCI_QUI_PROJECT_ID_RICEVUTO"
    }
  },
  "jsonrpc": "2.0",
  "id": 2
}
```

---

## Note

- Il projectId viene generato automaticamente da `project_open`
- È basato su: `<nome_file>_<hash_path>`
- Esempio: `S000009result_87654321`
- Ogni progetto ha un ID univoco e persistente
- Il server TCP rimane attivo finché non chiudi il progetto
