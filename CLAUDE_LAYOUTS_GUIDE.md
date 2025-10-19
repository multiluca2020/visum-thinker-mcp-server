# 🤖 Claude Workflow Guide - Global Layouts

## Quick Reference for AI Assistants

### When User Mentions Layouts

**Trigger phrases:**
- "load layout"
- "show layouts"
- "available layouts"
- "open .lay file"
- "tabelle_report"

### Standard Response Pattern

```
User: "Load the global layout"

Claude:
1. 📂 LIST: Call project_list_available_layouts
2. 👤 ASK: "I found X layouts. Which one would you like to load?"
3. 🎨 LOAD: Call project_load_global_layout with selected file
4. ✅ CONFIRM: "Layout loaded successfully!"
```

## JSON Command Templates

### Step 1: List Available Layouts

```json
{
  "method": "tools/call",
  "params": {
    "name": "project_list_available_layouts",
    "arguments": {
      "projectId": "PROJECT_ID_HERE"
    }
  },
  "jsonrpc": "2.0",
  "id": 1
}
```

**Response Format:**
```
📂 Global Layout Files Disponibili
📍 Directory: H:\go\reports\Input
📊 Totale file .lay: 1

1. tabelle_report.lay
   📏 Dimensione: 11.36 MB
   📂 Path: H:\go\reports\Input\tabelle_report.lay
```

### Step 2: Load Selected Layout

```json
{
  "method": "tools/call",
  "params": {
    "name": "project_load_global_layout",
    "arguments": {
      "projectId": "PROJECT_ID_HERE",
      "layoutFile": "tabelle_report.lay"
    }
  },
  "jsonrpc": "2.0",
  "id": 2
}
```

**Success Response:**
```
✅ Global Layout Caricato

📂 File: tabelle_report.lay
📍 Path: H:\go\reports\Input\tabelle_report.lay
📊 Dimensione: 11.36 MB

🎨 Il layout è ora attivo nel progetto Visum.
```

## Conversation Examples

### Example 1: Standard Flow

```
User: "Show me available layouts and load one"

Claude:
→ Calls: project_list_available_layouts
← Result: 1 file found (tabelle_report.lay, 11.36 MB)

Claude: "I found 1 layout available:
        • tabelle_report.lay (11.36 MB)
        
        Would you like to load this layout?"

User: "Yes"

Claude:
→ Calls: project_load_global_layout("tabelle_report.lay")
← Result: SUCCESS

Claude: "✅ Successfully loaded tabelle_report.lay (11.36 MB).
        The layout is now active in your Visum project."
```

### Example 2: Direct Request

```
User: "Load tabelle_report layout"

Claude:
→ Calls: project_load_global_layout("tabelle_report.lay")
← Result: SUCCESS

Claude: "✅ Loaded tabelle_report.lay (11.36 MB) successfully.
        The layout is now active."
```

### Example 3: File Not Found

```
User: "Load missing_layout.lay"

Claude:
→ Calls: project_load_global_layout("missing_layout.lay")
← Result: FILE_NOT_FOUND

Claude: "❌ The file missing_layout.lay was not found.
        
        Would you like me to show you available layouts?"

User: "Yes"

Claude:
→ Calls: project_list_available_layouts
← Shows available files
```

## Important Notes for Claude

### ✅ DO:
- Always list layouts first before asking user to choose
- Use exact filename from list (case-sensitive)
- Mention file size when presenting options
- Confirm success with file details
- Suggest listing if file not found

### ❌ DON'T:
- Don't use deprecated `project_list_global_layouts` tool
- Don't guess layout filenames
- Don't try to use COM API methods directly
- Don't forget to ask user which layout to load

## Technical Reference

### Working API:
```python
visum.LoadGlobalLayout(file_path)  # ✅ Correct
```

### NOT Working:
```python
visum.IO.LoadGlobalLayout()  # ❌ Doesn't exist
visum.Graphics.AssociateGlobalLayoutFile()  # ❌ Doesn't exist
visum.Net.Project.GlobalLayouts  # ❌ Not accessible
```

## Performance Expectations

- **Listing:** Instant (~1-5ms)
- **Loading:** ~7 seconds for 11.9 MB file (inform user to wait)

## Error Handling

### File Not Found
→ Suggest using `project_list_available_layouts`

### Path Error
→ Try with just filename instead of full path

### Load Failed
→ Check file size (corrupt if too small/large)
→ Try different layout file

## Full Documentation

- **Complete Guide:** `GLOBAL_LAYOUTS_WORKFLOW.md`
- **Quick Reference:** `GLOBAL_LAYOUTS_README.md`
- **Copilot Instructions:** `.github/copilot-instructions.md`

---

**For Claude:** This is your quick reference. Follow the patterns above for consistent user experience.

**Status:** ✅ Production Ready  
**Last Updated:** October 19, 2025
