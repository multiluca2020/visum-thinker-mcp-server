# Comandi MCP su Una Linea - Global Layouts Test

## Step 1: Apri Progetto S000009result.ver

```json
{"method":"tools/call","params":{"name":"project_open","arguments":{"projectPath":"H:\\go\\reports\\Input\\S000009result.ver"}},"jsonrpc":"2.0","id":1}
```

## Step 2: Lista Global Layouts (sostituisci PROJECT_ID)

```json
{"method":"tools/call","params":{"name":"project_list_global_layouts","arguments":{"projectId":"SOSTITUISCI_CON_PROJECT_ID"}},"jsonrpc":"2.0","id":2}
```

## Esempio con Project ID reale

Se il project ID è `S000009result_87654321`:

```json
{"method":"tools/call","params":{"name":"project_list_global_layouts","arguments":{"projectId":"S000009result_87654321"}},"jsonrpc":"2.0","id":2}
```

---

## Alternative - Altri Progetti

### Campoleone Project

Apri:
```json
{"method":"tools/call","params":{"name":"project_open","arguments":{"projectPath":"H:\\go\\italferr2025\\Campoleone\\100625_Versione_base_v0.3_sub_ok_priv.ver"}},"jsonrpc":"2.0","id":1}
```

Lista layouts (con project ID: `100625_Versione_base_v0_3_sub_ok_priv_10176442`):
```json
{"method":"tools/call","params":{"name":"project_list_global_layouts","arguments":{"projectId":"100625_Versione_base_v0_3_sub_ok_priv_10176442"}},"jsonrpc":"2.0","id":2}
```
