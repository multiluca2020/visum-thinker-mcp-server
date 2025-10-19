# 🎨 Global Layouts Workflow - Complete Guide

## Overview

This guide documents the **complete workflow** for managing Visum Global Layout files (.lay) through the MCP server. Global Layouts are visual presentation configurations stored in `.lay` files that define how Visum displays network data, tables, and analysis results.

---

## 📋 Table of Contents

1. [Available MCP Tools](#available-mcp-tools)
2. [Complete Workflow](#complete-workflow)
3. [API Discovery Process](#api-discovery-process)
4. [Usage Examples for Claude](#usage-examples-for-claude)
5. [Technical Details](#technical-details)
6. [Troubleshooting](#troubleshooting)

---

## 🛠️ Available MCP Tools

### 1. `project_list_available_layouts`

**Purpose:** List all `.lay` files available in the project directory.

**When to use:**
- User asks "What layouts are available?"
- Before loading a layout (to show options to user)
- To verify a specific .lay file exists

**Parameters:**
- `projectId`: Project identifier from `project_open` (e.g., `S000009result_1278407893`)

**Returns:**
- List of all `.lay` files found in project directory
- Filename, size (MB), and full path for each file
- Total count of available layouts

**Example Response:**
```
📂 **File Global Layout Disponibili**

📁 Directory: H:\go\reports\Input
📊 Totale file .lay trovati: 1

**File disponibili:**

1. **tabelle_report.lay**
   📏 Dimensione: 11.36 MB
   📍 Path: H:\go\reports\Input\tabelle_report.lay

💡 **Per caricare un layout:** Usa `project_load_global_layout` con il nome del file
```

---

### 2. `project_load_global_layout`

**Purpose:** Load a Global Layout file into the active Visum project.

**When to use:**
- After user selects a layout from the available list
- User requests "Load layout X" or "Open tabelle_report.lay"

**Parameters:**
- `projectId`: Project identifier from `project_open`
- `layoutFile`: Either:
  - Just the filename (e.g., `"tabelle_report.lay"`) - searches in project directory
  - Full path (e.g., `"H:\\path\\to\\layout.lay"`)

**Returns:**
- Success confirmation with file details
- File size and path
- Error message if file not found or load fails

**Example Response (Success):**
```
✅ **Global Layout Caricato**

📂 **File:** tabelle_report.lay
📍 **Path:** H:\go\reports\Input\tabelle_report.lay
📊 **Dimensione:** 11.36 MB

🎨 Il layout è ora attivo nel progetto Visum.
```

**Example Response (File Not Found):**
```
❌ **File non trovato**

File .lay non trovato: H:\go\reports\Input\missing.lay

💡 **Suggerimento:** Usa `project_list_available_layouts` per vedere i file .lay disponibili.
```

---

### 3. `project_list_global_layouts` (DEPRECATED - NOT WORKING)

**Status:** ⚠️ **NOT FUNCTIONAL** - API path `visum.GlobalLayouts` not accessible in Visum 2025

**Why it doesn't work:**
- The COM API documentation mentions `IProject.GlobalLayouts` collection
- However, this collection is not accessible via standard Python VisumPy interface
- Attempting to access `visum.Net.Project.GlobalLayouts` or `visum.Project.GlobalLayouts` fails

**Alternative:** Use `project_list_available_layouts` to find .lay files via filesystem search instead.

---

## 🔄 Complete Workflow

### Interactive Workflow with Claude

**Step 1: Open Project**

User: "Open the S000009result.ver project"

Claude uses:
```json
{
  "method": "tools/call",
  "params": {
    "name": "project_open",
    "arguments": {
      "projectPath": "H:\\go\\reports\\Input\\S000009result.ver"
    }
  }
}
```

Save the returned `projectId` (e.g., `S000009result_1278407893`)

---

**Step 2: List Available Layouts**

User: "What layouts are available?" or Claude proactively asks: "Would you like to see available layouts?"

Claude uses:
```json
{
  "method": "tools/call",
  "params": {
    "name": "project_list_available_layouts",
    "arguments": {
      "projectId": "S000009result_1278407893"
    }
  }
}
```

Claude presents results to user:
> "I found 1 Global Layout file available:
> 1. **tabelle_report.lay** (11.36 MB)
> 
> Would you like to load this layout?"

---

**Step 3: User Selects Layout**

User: "Yes, load tabelle_report" or "Load the first one"

Claude uses:
```json
{
  "method": "tools/call",
  "params": {
    "name": "project_load_global_layout",
    "arguments": {
      "projectId": "S000009result_1278407893",
      "layoutFile": "tabelle_report.lay"
    }
  }
}
```

Claude confirms:
> "✅ Successfully loaded **tabelle_report.lay** (11.36 MB). The layout is now active in your Visum project."

---

### Automated Workflow (No User Interaction Needed)

If user requests directly: "Load the tabelle_report layout from S000009result project"

Claude can execute all steps automatically:

```typescript
// 1. Open project (if not already open)
const openResult = await project_open({ 
  projectPath: "H:\\go\\reports\\Input\\S000009result.ver" 
});
const projectId = openResult.projectId;

// 2. Load layout directly (skip listing if filename known)
const loadResult = await project_load_global_layout({
  projectId: projectId,
  layoutFile: "tabelle_report.lay"
});
```

---

## 🔍 API Discovery Process

### What We Discovered

Through systematic exploration, we found the correct Visum API for loading Global Layouts:

#### ❌ Methods That DON'T Work:

1. **`visum.IO.LoadGlobalLayout()`** - Method doesn't exist on IIO interface
2. **`visum.Graphics.AssociateGlobalLayoutFile()`** - `visum.Graphics` doesn't exist
3. **`visum.AddGlobalLayout()`** - Method doesn't exist on IVisum interface
4. **`visum.Net.Project.GlobalLayouts`** - Collection not accessible
5. **`visum.Project.GlobalLayouts`** - Collection not accessible

#### ✅ Method That WORKS:

**`visum.LoadGlobalLayout(filename)`**

- Direct method on the main `visum` object (IVisum interface)
- Takes full path to .lay file as parameter
- Loads the layout into the active project
- Companion method: `visum.SaveGlobalLayout(filename)` for saving layouts

### Discovery Command

To explore available methods on `visum` object:

```python
# List all methods with "Layout" or "Global" in the name
visum_methods = [m for m in dir(visum) if not m.startswith('_')]
layout_methods = [m for m in visum_methods if 'Layout' in m or 'Global' in m]
# Returns: ['LoadGlobalLayout', 'LoadQuickViewLayout', 'SaveGlobalLayout', 'SaveQuickViewLayout']
```

---

## 💡 Usage Examples for Claude

### Example 1: Simple Layout Load

**User:** "Load the tabelle_report layout"

**Claude Response:**
```
I'll help you load the tabelle_report layout. First, let me check what layouts are available.

[Calls project_list_available_layouts]

I found the layout file. Loading it now...

[Calls project_load_global_layout with "tabelle_report.lay"]

✅ Successfully loaded tabelle_report.lay (11.36 MB). The layout is now active in your Visum project.
```

---

### Example 2: User Doesn't Know Layout Name

**User:** "Show me available layouts and load one"

**Claude Response:**
```
Let me check what Global Layout files are available in your project.

[Calls project_list_available_layouts]

I found 1 layout file:
1. **tabelle_report.lay** (11.36 MB) - Located at H:\go\reports\Input\

Which layout would you like to load? (Enter the number or name)
```

**User:** "Load number 1"

**Claude:**
```
[Calls project_load_global_layout with "tabelle_report.lay"]

✅ Successfully loaded tabelle_report.lay. The layout is now active.
```

---

### Example 3: Error Handling

**User:** "Load missing_layout.lay"

**Claude:**
```
[Calls project_load_global_layout with "missing_layout.lay"]

❌ The file missing_layout.lay was not found in the project directory.

Would you like me to show you the available layout files?

[If user says yes, call project_list_available_layouts]
```

---

## � Tested JSON Commands

### List Available Layouts
```json
{"method":"tools/call","params":{"name":"project_list_available_layouts","arguments":{"projectId":"S000009result_1278407893"}},"jsonrpc":"2.0","id":1}
```

**Result:**
```
📂 Global Layout Files Disponibili
📍 Directory: H:\go\reports\Input
📊 Totale file .lay: 1

1. tabelle_report.lay
   📏 Dimensione: 11.36 MB (11,909,589 bytes)
   📂 Path: H:\go\reports\Input\tabelle_report.lay
```

### Load Global Layout
```json
{"method":"tools/call","params":{"name":"project_load_global_layout","arguments":{"projectId":"S000009result_1278407893","layoutFile":"tabelle_report.lay"}},"jsonrpc":"2.0","id":2}
```

**Result:**
```
✅ Global Layout Caricato

📂 File: tabelle_report.lay
📍 Path: H:\go\reports\Input\tabelle_report.lay
📊 Dimensione: 11.36 MB

🎨 Il layout è ora attivo nel progetto Visum.
```

**Loading Time:** ~7 seconds for 11.9 MB file (tested successfully)

---

## �🔧 Technical Details

### File Location

- Global Layout files (.lay) are typically stored in the same directory as the .ver project file
- If a relative filename is provided, the tool automatically searches in the project directory
- Full absolute paths can also be provided

### Python API Used

```python
import os

# Get project directory
project_path = visum.GetPath()  # Returns full path to .ver file
project_dir = os.path.dirname(project_path)

# Construct full path to layout file
layout_file = os.path.join(project_dir, "tabelle_report.lay")

# Verify file exists
if os.path.exists(layout_file):
    # Load the layout into active Visum project
    visum.LoadGlobalLayout(layout_file)  # ✅ This is the correct method
```

### Performance

- Listing available layouts: **~1-5ms** (filesystem scan)
- Loading a layout: **~6 seconds** for 11MB file (one-time operation)
  - Large layouts contain extensive network visualization settings
  - Loading time scales with file size

### Visum Version

- Tested on: **PTV Visum 2025 (64-bit)**
- COM Library: `PTV Visum Object Library 25.0 64 Bit`
- Python path: `H:\Program Files\PTV Vision\PTV Visum 2025\Exe\Python\python.exe`

---

## 🚨 Troubleshooting

### Problem: "File not found" error

**Possible causes:**
1. Filename typo or incorrect case
2. File is not in project directory
3. Full path has incorrect backslashes

**Solutions:**
- Always run `project_list_available_layouts` first to verify filename
- Use exact filename from the list (case-sensitive on some systems)
- For full paths, use double backslashes: `"H:\\path\\to\\file.lay"`

---

### Problem: "GlobalLayouts collection not available"

**This is expected!** The old `project_list_global_layouts` tool tried to access:
- `visum.Net.Project.GlobalLayouts` ❌
- `visum.Project.GlobalLayouts` ❌

Both paths are documented in COM API but not accessible in practice.

**Solution:** Use filesystem-based `project_list_available_layouts` instead.

---

### Problem: Layout loads but doesn't appear active

**Possible causes:**
- Visum GUI not refreshed
- Layout contains settings not compatible with current project
- Layout file corrupted

**Solutions:**
- In Visum GUI, manually refresh views (F5)
- Try loading a different layout to verify system works
- Check layout file integrity (should be ~1-20 MB typically)

---

## 📚 Related Documentation

- **COM API Reference:** `VISUMLIB~IVisum.html` - Documents `LoadGlobalLayout` method
- **File Types:** Global Layout = Type 93 in Visum COM API
- **Project Documentation:** `GLOBAL_LAYOUTS_GUIDE.md` - Original COM API exploration
- **MCP Commands:** `MCP_COMMANDS_ONELINE.md` - JSON command examples

---

## 🎯 Summary for Claude

**When user asks about Global Layouts:**

1. ✅ **List available:** Use `project_list_available_layouts`
2. ✅ **Load a layout:** Use `project_load_global_layout`
3. ❌ **Don't use:** `project_list_global_layouts` (doesn't work)

**Typical conversation flow:**

```
User: "I need to work with layouts"
Claude: Lists available layouts → User selects → Claude loads it → Confirms success
```

**Key API discovery:**
- Correct method: `visum.LoadGlobalLayout(full_path)`
- Companion method: `visum.SaveGlobalLayout(full_path)`
- Located on main `visum` object, NOT on `visum.IO` or `visum.Graphics`

---

**Document Version:** 1.0  
**Last Updated:** 2025-10-19  
**Author:** Visum MCP Server Development Team  
**Status:** ✅ Production Ready
