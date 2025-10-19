# 📚 Global Layouts Documentation Index

Complete documentation for Global Layouts (.lay file) management in Visum MCP Server.

---

## 🎯 Quick Start (Start Here!)

**For Claude/AI Assistants:**
- **[CLAUDE_LAYOUTS_GUIDE.md](CLAUDE_LAYOUTS_GUIDE.md)** - Quick reference with conversation patterns

**For Developers:**
- **[GLOBAL_LAYOUTS_README.md](GLOBAL_LAYOUTS_README.md)** - Quick commands and API reference

---

## 📖 Complete Documentation

### 1. Workflow Guide (Most Comprehensive)
**[GLOBAL_LAYOUTS_WORKFLOW.md](GLOBAL_LAYOUTS_WORKFLOW.md)**
- Complete step-by-step workflow
- API discovery process
- All tested methods (working and non-working)
- Troubleshooting guide
- Performance benchmarks

### 2. Claude Quick Reference
**[CLAUDE_LAYOUTS_GUIDE.md](CLAUDE_LAYOUTS_GUIDE.md)**
- Conversation patterns for AI assistants
- JSON command templates
- Example dialogues
- Do's and Don'ts
- Error handling patterns

### 3. Quick Reference
**[GLOBAL_LAYOUTS_README.md](GLOBAL_LAYOUTS_README.md)**
- Fast command lookup
- Working API methods
- One-line JSON commands
- Performance metrics

### 4. Test Results
**[GLOBAL_LAYOUTS_TEST_RESULTS.md](GLOBAL_LAYOUTS_TEST_RESULTS.md)**
- All test results
- Verified methods
- Performance data
- Test files listing

### 5. Copilot Instructions
**[.github/copilot-instructions.md](.github/copilot-instructions.md)**
- MCP tool descriptions
- Integrated workflow
- Tool parameters

---

## 🧪 Test Files

Located in project root:

1. **test-list-layouts.json** - List available layouts
2. **test-load-layout.json** - Load specific layout
3. **test-explore-all-methods.json** - API method discovery
4. **test-find-lay-files.json** - Filesystem search
5. **test-debug-loadlayout.json** - Debug method signature

**Usage:**
```powershell
Get-Content test-list-layouts.json | node build/index.js
Get-Content test-load-layout.json | node build/index.js
```

---

## 🛠️ MCP Tools

### Working Tools (Use These!)

#### `project_list_available_layouts`
Lists all .lay files in project directory.

**Parameters:**
- `projectId`: string

**Returns:** List of layouts with filename, size, path

#### `project_load_global_layout`
Loads a .lay file into active Visum project.

**Parameters:**
- `projectId`: string
- `layoutFile`: string (filename or full path)

**Returns:** Success confirmation or error message

### Deprecated Tools (Don't Use!)

#### `project_list_global_layouts` ⚠️
- **Status:** DEPRECATED - COM API not accessible
- **Replacement:** Use `project_list_available_layouts`

---

## 🔧 Technical Reference

### Working API Methods:
```python
# ✅ VERIFIED WORKING
visum.LoadGlobalLayout(file_path)  # Load layout
visum.SaveGlobalLayout(file_path)  # Save layout (exists, not tested)
visum.GetPath(1)  # Get project path (1 = .ver file type)
```

### Non-Working Methods:
```python
# ❌ DON'T USE - These don't work
visum.IO.LoadGlobalLayout()  # Doesn't exist
visum.Graphics.AssociateGlobalLayoutFile()  # Graphics doesn't exist
visum.AddGlobalLayout()  # Doesn't exist
visum.Net.Project.GlobalLayouts  # Not accessible
visum.Project.GlobalLayouts  # Not accessible
visum.GetPath()  # Requires parameter
```

---

## 📊 Performance Metrics

- **List layouts:** 1-5ms (filesystem scan)
- **Load layout:** ~7 seconds for 11.9 MB file
- **Total workflow:** ~8-10 seconds

---

## ✅ Test Status

**All Tests:** PASSING  
**Production Ready:** YES  
**Visum Version:** PTV Visum 2025 64-bit  
**Last Tested:** October 19, 2025

---

## 🎓 Key Learnings

1. **COM API Documentation ≠ Reality**
   - Documented collections may not be accessible
   - Always verify with actual testing

2. **Filesystem > COM for .lay files**
   - More reliable than COM collections
   - Faster and simpler

3. **Method Discovery**
   - Use `dir(visum)` to find available methods
   - Test systematically to verify parameters

4. **Error Handling**
   - Always try/except for version compatibility
   - Provide helpful error messages

---

## 🚀 Workflow Summary

```
┌─────────────────────────────────────────┐
│  USER: "Load global layout"            │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  CLAUDE: List available layouts         │
│  Tool: project_list_available_layouts   │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  CLAUDE: Show options to user           │
│  "Found: tabelle_report.lay (11.36 MB)" │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  USER: "Load it"                        │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  CLAUDE: Load layout                    │
│  Tool: project_load_global_layout       │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  CLAUDE: Confirm success                │
│  "✅ Layout loaded successfully!"       │
└─────────────────────────────────────────┘
```

---

## 📝 Document History

- **v1.0** - October 19, 2025 - Initial release
  - Created 5 documentation files
  - Created 5 test files
  - Verified all workflows
  - Production ready

---

## 🔗 Related Documentation

- **Visum Procedures:** `VISUM_PROCEDURES_API.md`
- **Demand Segments:** `WORKFLOW_PRT_ASSIGNMENT.md`
- **MCP Server:** `README.md`

---

**Status:** ✅ Complete and Production Ready  
**Maintained By:** Visum MCP Server Development Team  
**Last Updated:** October 19, 2025

---

## Need Help?

1. **For AI Assistants:** Start with `CLAUDE_LAYOUTS_GUIDE.md`
2. **For Quick Commands:** Check `GLOBAL_LAYOUTS_README.md`
3. **For Deep Dive:** Read `GLOBAL_LAYOUTS_WORKFLOW.md`
4. **For Testing:** See `GLOBAL_LAYOUTS_TEST_RESULTS.md`
