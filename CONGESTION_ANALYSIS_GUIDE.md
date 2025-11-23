# 🚦 Visum Congestion Analysis Scripts

## 📁 Files

1. **`analyze-congestion.py`** - Standalone script (connects to Visum COM)
2. **`analyze-congestion-inline.py`** - Inline script (for Visum console/TCP)
3. **`send-congestion-analysis.js`** - Helper to customize and prepare scripts

## 🚀 Usage Methods

### Method 1: Standalone Script (COM Connection)

Requires Visum to be open with a project:

```powershell
python analyze-congestion.py
```

**Output:**
- Console output with top 10 congested links
- CSV file: `top_congested_links_AP.csv`

---

### Method 2: Visum Python Console (Inline)

From Visum's Python console window:

```python
exec(open('analyze-congestion-inline.py', encoding='utf-8').read())
```

**Note:** Always specify `encoding='utf-8'` to avoid UnicodeDecodeError

**Advantages:**
- No COM connection needed
- Faster execution
- Can be copy-pasted directly

---

### Method 3: Customized Script Generation

Generate a customized version with specific parameters:

```powershell
# Default: AP period, top 10
node send-congestion-analysis.js S000009result_1278407893

# Custom: AM period, top 20
node send-congestion-analysis.js S000009result_1278407893 AM 20
```

**Output:**
- Creates `analyze-congestion-temp.py` with your parameters
- Shows usage instructions

---

### Method 4: Via TCP Server (Future)

When sending Python code via TCP server:

```javascript
// Read the inline script
const script = fs.readFileSync('analyze-congestion-inline.py', 'utf-8');

// Customize parameters
const customScript = script
  .replace(/ANALYSIS_PERIOD = "AP"/, 'ANALYSIS_PERIOD = "AM"')
  .replace(/TOP_N = 10/, 'TOP_N = 20');

// Send via TCP
await serverManager.executeCommand(projectId, customScript, "Congestion Analysis");
```

---

## 📊 Output Format

### Console Output

```
================================================================================
🚦 TOP 10 MOST CONGESTED LINKS (AP)
================================================================================

📊 Statistics:
   • Total links: 227,508
   • Links with traffic: 186,234
   • Congested (V/C > 0.9): 3,421
   • Over-capacity (V/C > 1.0): 1,234

Rank   From       To         V/C     Volume      Capacity      Length
--------------------------------------------------------------------------------
1      12345      12346      2.450     3,456.0      1,410.0      850.0m  [SEVERE]
2      23456      23457      2.120     2,987.0      1,410.0      720.0m  [SEVERE]
3      34567      34568      1.870     2,634.0      1,410.0      950.0m  [OVERCAP]
...
================================================================================
```

### CSV Output (standalone only)

File: `top_congested_links_AP.csv`

```csv
Rank;FromNode;ToNode;Name;VC_Ratio;Volume;Capacity;Length_m;TypeNo;V0Speed;AnalysisPeriod
1;12345;12346;Via Roma;2.4500;3456.00;1410.00;850.00;1;50;AP
2;23456;23457;Via Milano;2.1200;2987.00;1410.00;720.00;1;50;AP
...
```

### JSON Result (inline version)

```json
{
  "status": "success",
  "analysis_period": "AP",
  "total_links": 227508,
  "links_with_traffic": 186234,
  "congested_links": 3421,
  "overcapacity_links": 1234,
  "top_congested": [
    {
      "rank": 1,
      "from_node": 12345,
      "to_node": 12346,
      "name": "Via Roma",
      "vc_ratio": 2.45,
      "volume": 3456.0,
      "capacity": 1410.0,
      "length": 850.0,
      "type_no": 1
    }
  ]
}
```

---

## ⚙️ Configuration

### Change Analysis Period

Edit the script or use send-congestion-analysis.js:

```python
ANALYSIS_PERIOD = "AM"  # or "PM", "IP", "IP1", etc.
```

### Change Number of Top Links

```python
TOP_N = 20  # Instead of 10
```

---

## 🎯 Congestion Levels

| Status | V/C Ratio | Description |
|--------|-----------|-------------|
| **SEVERE** | > 1.5 | Severe congestion, major delays |
| **OVERCAP** | > 1.0 | Over capacity, significant delays |
| **CONG** | > 0.9 | Congested, moderate delays |
| **HIGH** | < 0.9 | High utilization, minor delays |

---

## 🔧 Requirements

### For Standalone Script
- Python with `win32com.client` (pywin32)
- Visum running with project opened
- Completed PrT assignment

### For Inline Script
- Visum project with Python console access
- Completed PrT assignment
- `visum` object available in scope

---

## 💡 Tips

1. **Run after assignment** - Ensure PrT assignment is complete
2. **Check period code** - Use correct analysis period (AP, AM, PM, etc.)
3. **Large networks** - May take 10-30 seconds for 200K+ links
4. **Export CSV** - Only standalone version exports CSV file
5. **Inline for speed** - Inline version is faster (no COM overhead)

---

## 📝 Example Workflows

### Workflow 1: Quick Check in Console

```python
# In Visum Python console
exec(open('analyze-congestion-inline.py', encoding='utf-8').read())
```

### Workflow 2: Generate Report

```powershell
# From PowerShell
python analyze-congestion.py
# Opens: top_congested_links_AP.csv
```

### Workflow 3: Custom Analysis

```powershell
# Generate custom script
node send-congestion-analysis.js S000009result_123 AM 20

# Run generated script in Visum console
exec(open('analyze-congestion-temp.py', encoding='utf-8').read())
```

---

## 🔮 Future: MCP Integration

When a generic `project_execute_python` tool is added to MCP:

```javascript
visum_analyze_congestion({
  projectId: "S000009result_123",
  analysisPeriod: "AM",
  topN: 20
})
```

This would execute the inline script via TCP and return formatted results to Claude.

---

**Created:** 2025-11-07  
**Status:** ✅ Ready to Use  
**Tested:** Pending
