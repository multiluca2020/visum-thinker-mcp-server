# Global Layouts - Quick Test Commands

## Prerequisites

1. Build the project: `npm run build`
2. Have a Visum project with .lay files

## Test Commands (PowerShell - One Line)

### 1. List Available Layout Files

```powershell
echo '{"method":"tools/call","params":{"name":"project_list_available_layouts","arguments":{"projectId":"S000009result_1278407893"}},"jsonrpc":"2.0","id":1}' | node build/index.js
```

**Expected Output:**
```
📂 **File Global Layout Disponibili**

📁 Directory: H:\go\reports\Input
📊 Totale file .lay trovati: 1

**File disponibili:**

1. **tabelle_report.lay**
   📏 Dimensione: 11.36 MB
   📍 Path: H:\go\reports\Input\tabelle_report.lay
```

---

### 2. Load a Global Layout

```powershell
echo '{"method":"tools/call","params":{"name":"project_load_global_layout","arguments":{"projectId":"S000009result_1278407893","layoutFile":"tabelle_report.lay"}},"jsonrpc":"2.0","id":2}' | node build/index.js
```

**Expected Output:**
```
✅ **Global Layout Caricato**

📂 **File:** tabelle_report.lay
📍 **Path:** H:\go\reports\Input\tabelle_report.lay
📊 **Dimensione:** 11.36 MB

🎨 Il layout è ora attivo nel progetto Visum.
```

**Performance:** ~6 seconds for 11MB file

---

### 3. Complete Workflow (Open + List + Load)

**Step 1: Open Project**
```powershell
echo '{"method":"tools/call","params":{"name":"project_open","arguments":{"projectPath":"H:\\go\\reports\\Input\\S000009result.ver"}},"jsonrpc":"2.0","id":1}' | node build/index.js
```

Save the `projectId` from response (e.g., `S000009result_1278407893`)

**Step 2: List Layouts**
```powershell
echo '{"method":"tools/call","params":{"name":"project_list_available_layouts","arguments":{"projectId":"S000009result_1278407893"}},"jsonrpc":"2.0","id":2}' | node build/index.js
```

**Step 3: Load Selected Layout**
```powershell
echo '{"method":"tools/call","params":{"name":"project_load_global_layout","arguments":{"projectId":"S000009result_1278407893","layoutFile":"tabelle_report.lay"}},"jsonrpc":"2.0","id":3}' | node build/index.js
```

---

## Test Files (JSON Format)

### test-list-layouts.json
```json
{
  "method": "tools/call",
  "params": {
    "name": "project_list_available_layouts",
    "arguments": {
      "projectId": "S000009result_1278407893"
    }
  },
  "jsonrpc": "2.0",
  "id": 1
}
```

**Usage:**
```powershell
Get-Content test-list-layouts.json | node build/index.js
```

---

### test-load-layout.json
```json
{
  "method": "tools/call",
  "params": {
    "name": "project_load_global_layout",
    "arguments": {
      "projectId": "S000009result_1278407893",
      "layoutFile": "tabelle_report.lay"
    }
  },
  "jsonrpc": "2.0",
  "id": 2
}
```

**Usage:**
```powershell
Get-Content test-load-layout.json | node build/index.js
```

---

## Error Testing

### Test: File Not Found

```powershell
echo '{"method":"tools/call","params":{"name":"project_load_global_layout","arguments":{"projectId":"S000009result_1278407893","layoutFile":"nonexistent.lay"}},"jsonrpc":"2.0","id":99}' | node build/index.js
```

**Expected Output:**
```
❌ **File non trovato**

File .lay non trovato: H:\go\reports\Input\nonexistent.lay

💡 **Suggerimento:** Usa `project_list_available_layouts` per vedere i file .lay disponibili.
```

---

### Test: Invalid Project ID

```powershell
echo '{"method":"tools/call","params":{"name":"project_list_available_layouts","arguments":{"projectId":"invalid_project_123"}},"jsonrpc":"2.0","id":98}' | node build/index.js
```

**Expected Output:**
```
❌ Impossibile listare file .lay per progetto invalid_project_123: Server progetto non trovato
```

---

## Performance Benchmarks

| Operation | File Size | Time | Notes |
|-----------|-----------|------|-------|
| List Layouts | N/A | 1-5ms | Filesystem scan |
| Load Layout | 11.36 MB | ~6s | One-time operation |
| Load Layout | 1 MB | ~1s | Smaller layouts faster |

---

## Cleanup

Close project when done:
```powershell
echo '{"method":"tools/call","params":{"name":"project_close","arguments":{"projectId":"S000009result_1278407893","save":false}},"jsonrpc":"2.0","id":999}' | node build/index.js
```

---

## Notes

1. **Project ID Format:** Generated as `{projectName}_{hash}` (e.g., `S000009result_1278407893`)
2. **Layout Files:** Must be in same directory as .ver file or provide full path
3. **Case Sensitivity:** Filenames are case-sensitive on some systems
4. **File Size:** Typical range 1-20 MB depending on network complexity and visualization settings

---

**Quick Reference:**
- ✅ List: `project_list_available_layouts`
- ✅ Load: `project_load_global_layout`
- ❌ Don't use: `project_list_global_layouts` (deprecated)
