# Global Layouts Management - Quick Reference

## 🎯 Quick Start

### For Claude AI Assistants

When user mentions Global Layouts:

```
User: "Show me available layouts"
↓
1. Call: project_list_available_layouts
2. Show list to user
3. User selects
4. Call: project_load_global_layout
5. Confirm success
```

---

## 🛠️ Available Tools

### ✅ Use These Tools

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `project_list_available_layouts` | List .lay files | Always first - show options to user |
| `project_load_global_layout` | Load a layout | After user selects from list |

### ❌ Don't Use These

| Tool | Status | Reason |
|------|--------|--------|
| `project_list_global_layouts` | DEPRECATED | API not accessible in Visum 2025 |

---

## 📋 Tool Signatures

### project_list_available_layouts

```typescript
{
  projectId: string  // From project_open (e.g., "S000009result_1278407893")
}
```

**Returns:**
- List of .lay files with filename, size (MB), full path
- Total count
- Project directory path

---

### project_load_global_layout

```typescript
{
  projectId: string,       // From project_open
  layoutFile: string       // Filename or full path
}
```

**Examples:**
- `"tabelle_report.lay"` - searches in project dir
- `"H:\\full\\path\\to\\layout.lay"` - absolute path

**Returns:**
- Success confirmation
- File details (name, path, size)
- Error if file not found

---

## 🔍 API Discovery Summary

**What Works:**
```python
visum.LoadGlobalLayout(full_path_to_lay_file)  # ✅ Correct!
```

**What Doesn't Work:**
```python
visum.IO.LoadGlobalLayout(file)                    # ❌ Method doesn't exist
visum.Graphics.AssociateGlobalLayoutFile(file)     # ❌ visum.Graphics doesn't exist
visum.AddGlobalLayout()                             # ❌ Method doesn't exist
visum.Net.Project.GlobalLayouts                     # ❌ Collection not accessible
```

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `GLOBAL_LAYOUTS_WORKFLOW.md` | Complete guide with examples |
| `GLOBAL_LAYOUTS_QUICK_TEST.md` | Test commands and benchmarks |
| `.github/copilot-instructions.md` | Copilot integration guide |

---

## ⚡ Quick Test

```powershell
# 1. List layouts
echo '{"method":"tools/call","params":{"name":"project_list_available_layouts","arguments":{"projectId":"S000009result_1278407893"}},"jsonrpc":"2.0","id":1}' | node build/index.js

# 2. Load layout
echo '{"method":"tools/call","params":{"name":"project_load_global_layout","arguments":{"projectId":"S000009result_1278407893","layoutFile":"tabelle_report.lay"}},"jsonrpc":"2.0","id":2}' | node build/index.js
```

---

## 🎓 Key Learnings

1. **Filesystem approach works** - API collection approach doesn't
2. **visum.LoadGlobalLayout()** is on main visum object, not visum.IO
3. **Always list first** - let user choose from available files
4. **Performance** - Loading takes ~6s for 11MB file (acceptable for one-time operation)

---

## ✅ Implementation Status

- [x] Implemented `project_list_available_layouts` tool
- [x] Implemented `project_load_global_layout` tool
- [x] Created comprehensive documentation
- [x] Created test commands
- [x] Updated Copilot instructions
- [x] Deprecated `project_list_global_layouts` (non-functional)

---

**Version:** 1.0  
**Last Updated:** 2025-10-19  
**Status:** Production Ready ✅
