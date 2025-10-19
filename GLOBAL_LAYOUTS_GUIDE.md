# Global Layouts (.lay) - Guida Completa

## 📋 Panoramica

I **Global Layouts** (.lay) in Visum sono configurazioni salvate dell'interfaccia grafica che includono:
- Posizioni e dimensioni delle finestre
- Colonne visibili nelle liste
- Impostazioni di visualizzazione della rete
- Configurazioni delle viste

## 🔑 Concetti Chiave

### ⚠️ IMPORTANTE: I .lay NON si "Caricano"

A differenza dei file progetto (.ver), i file Global Layout (.lay):
- **NON** hanno un metodo `LoadFile` o `OpenFile`
- **SONO ASSOCIAZIONI** che Visum applica automaticamente
- Si gestiscono tramite `AssociateGlobalLayoutFile()`
- Vengono applicati all'apertura del progetto se associati

## 🛠️ API Visum per Global Layouts

### Collection: IGlobalLayouts

**Accesso:**
```python
# Via Visum.Net.Project
layouts = Visum.Net.Project.GlobalLayouts

# Oppure (dipende dalla versione)
layouts = Visum.Project.GlobalLayouts
```

**Metodi Disponibili:**
- `Count` - Numero totale di layouts
- `GetMultipleAttributes(attrs)` - Ottiene attributi multipli
- `ItemByKey(key)` - Ottiene layout specifico
- `Iterator` - Itera su tutti i layouts

### Attributi GlobalLayout

| Attributo | Tipo | Descrizione |
|-----------|------|-------------|
| `No` | Integer | Numero identificativo |
| `Name` | String | Nome del layout |
| `GlobalLayoutFile` | String | Path del file .lay associato |
| `GlobalLayoutFileVersionNo` | String | Versione del file .lay |

### Metodi IGlobalLayout

**`AssociateGlobalLayoutFile(FileName)`**
- Associa un file .lay a un Global Layout
- **Parametro:** `FileName` (String) - path completo del file .lay
- **Esempio:**
  ```python
  layout = Visum.Net.Project.GlobalLayouts.ItemByKey(1)
  layout.AssociateGlobalLayoutFile(r"C:\path\to\my_layout.lay")
  ```

**`StartEditGlobalLayout()` / `EndEditGlobalLayout()`**
- Inizia/termina editing del layout
- Permette modifiche programmatiche

## 📡 Tool MCP: project_list_global_layouts

### Uso

**Prerequisito:** Progetto deve essere aperto con `project_open`

**JSON Command:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "project_list_global_layouts",
    "arguments": {
      "projectId": "100625_Versione_base_v0_3_sub_ok_priv_10176442"
    }
  },
  "jsonrpc": "2.0",
  "id": 1
}
```

**Parametri:**
- `projectId` (required) - ID progetto da `project_open`

### Output

```
🗂️ Global Layouts (progetto: 100625_Versione_base_v0_3_sub_ok_priv_10176442)

Totale: 3
Associati a file .lay: 2
Non associati: 1

1. #1 | Default Layout
   File: C:\Users\...\default.lay
   Versione: 25.00
   Associato: ✅

2. #2 | Analysis View
   File: (not associated)
   Versione: N/A
   Associato: ❌

3. #3 | Report Layout
   File: C:\Users\...\report.lay
   Versione: 25.00
   Associato: ✅
```

## 🔄 Workflow Completo

### 1. Aprire Progetto
```json
{
  "method": "tools/call",
  "params": {
    "name": "project_open",
    "arguments": {
      "projectPath": "H:\\path\\to\\project.ver"
    }
  },
  "jsonrpc": "2.0",
  "id": 1
}
```

**Response:**
```json
{
  "result": {
    "content": [{
      "type": "text",
      "text": "✅ Progetto aperto\nID: project_12345\n..."
    }]
  }
}
```

### 2. Listare Global Layouts
```json
{
  "method": "tools/call",
  "params": {
    "name": "project_list_global_layouts",
    "arguments": {
      "projectId": "project_12345"
    }
  },
  "jsonrpc": "2.0",
  "id": 2
}
```

### 3. (Futuro) Associare File .lay
Tool da implementare: `project_associate_layout`
```python
# Codice che verrà usato:
layout = Visum.Net.Project.GlobalLayouts.ItemByKey(layout_no)
layout.AssociateGlobalLayoutFile(r"C:\path\to\file.lay")
```

## 🎯 Casi d'Uso

### Scenario 1: Verificare Layout Disponibili
**Quando:** Dopo apertura progetto, prima di generare report
**Azione:** `project_list_global_layouts`
**Risultato:** Vedi quali layout sono configurati e associati

### Scenario 2: Report Automation
**Quando:** Script di generazione report automatici
**Workflow:**
1. Apri progetto
2. Lista layouts
3. Verifica layout "Report" sia associato
4. Procedi con export/screenshot

### Scenario 3: Configurazione Batch
**Quando:** Setup multipli progetti con stesso layout
**Workflow:**
1. Crea layout master (.lay)
2. Per ogni progetto:
   - Apri progetto
   - Lista layouts
   - Associa layout master a layout #1

## 📝 Note Tecniche

### File Type Code
- **93** = `filetype_GlobalLayout` (*.lay)
- Altri layout types:
  - 20 = List Layout (*.lla)
  - 74 = Matrix Editor Layout (*.mly)
  - 63 = Quick View Layout (*.qla)

### Limitazioni
- I .lay sono specifici della versione Visum
- Layout creati in Visum 2025 potrebbero non funzionare in 2024
- L'associazione è salvata nel file .ver

### Performance
- `GetMultipleAttributes()` è molto efficiente
- Lettura tipica: < 10ms per 10 layouts
- Usa TCP server dedicato per ogni progetto

## 🚀 Tool Futuri da Implementare

### project_associate_layout
```typescript
{
  projectId: string,
  layoutNo: number,
  layoutFilePath: string
}
```

### project_create_layout
```typescript
{
  projectId: string,
  layoutName: string,
  layoutFilePath?: string  // Optional save path
}
```

### project_export_layout
```typescript
{
  projectId: string,
  layoutNo: number,
  outputPath: string
}
```

## 🔗 Riferimenti

- **COM Documentation:** `VISUMLIB~IGlobalLayout.html`
- **Collection:** `VISUMLIB~IGlobalLayouts.html`
- **Referenced By:** `IProject.GlobalLayouts`
- **File Types:** `VISUMLIB~FileTypeT.html` (code 93)

## ✅ Checklist Implementazione

- [x] Ricerca API COM
- [x] Tool `project_list_global_layouts`
- [x] Documentazione workflow
- [ ] Tool `project_associate_layout`
- [ ] Tool `project_create_layout`
- [ ] Test automatici
- [ ] Esempi pratici script

---

**Ultima modifica:** 2025-10-19  
**Autore:** Visum MCP Server Team
