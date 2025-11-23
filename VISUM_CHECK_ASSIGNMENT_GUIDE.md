# 🔍 Visum Check Assignment Tool Guide

## Overview

The `visum_check_assignment` tool verifies if a **PrT (Private Transport) assignment** has been successfully executed in Visum by checking for volume data on network links.

## Tool Definition

```typescript
visum_check_assignment({
  projectId: string,           // Project ID from project_open
  analysisPeriod?: string      // Optional: "AP" (default), "AM", "PM", etc.
})
```

## What It Checks

The tool verifies assignment execution by checking:

1. **Attribute Existence:** `VolVehPrT(AP)` - Volume Veicoli PrT
2. **Data Availability:** Links have non-zero volume values
3. **Network Statistics:** Total volume, traffic distribution, congestion

## ✅ Verified Attributes

Based on testing with real Visum projects:

| Attribute | Status | Description |
|-----------|--------|-------------|
| `VolVehPrT(AP)` | ✅ **EXISTS** | Vehicle volume (PrT assignment result) |
| `VolPersPrT(AP)` | ✅ **EXISTS** | Person volume |
| `VolCapRatioPrT(AP)` | ✅ **EXISTS** | Volume/Capacity ratio (0-1 normal, >1 congested) |
| `V0PRT` | ✅ **EXISTS** | Free flow speed (base attribute) |
| `VOLPRT(AP)` | ❌ **DOES NOT EXIST** | Incorrect attribute name |

**⚠️ IMPORTANT:** Attribute names are **case-sensitive** and require period suffix: `(AP)`, `(AM)`, etc.

## Usage Examples

### Basic Check

```javascript
// Check if default AP assignment exists
visum_check_assignment({
  projectId: "S000009result_1278407893"
})
```

### Custom Analysis Period

```javascript
// Check AM peak hour assignment
visum_check_assignment({
  projectId: "S000009result_1278407893",
  analysisPeriod: "AM"
})
```

## Response Examples

### ✅ Assignment Found (Success)

```markdown
✅ **Assegnazione PrT Trovata**

**Periodo di analisi:** AP
**Archi totali:** 227,508
**Archi con traffico:** 186,234 (81.8%)

**Statistiche Volume:**
• Volume totale: 1,234,567 veicoli
• Volume massimo: 5,432
• Volume medio: 853.94
**Archi congestionati (V/C > 0.9):** 3,421

✅ Assignment found with traffic on 186,234/227,508 links

⏱️ **Tempo verifica:** 2,340ms
```

### ⚠️ Assignment Not Executed

```markdown
⚠️ **Assegnazione PrT Non Trovata**

**Motivo:** Attribute VolVehPrT(AP) not found - assignment not executed
**Archi nella rete:** 227,508

💡 **L'assegnazione non è stata ancora eseguita.**

**Per eseguire l'assegnazione:**
1. Crea procedura PrT con `visum_create_procedure`
2. Configura segments con `visum_configure_dsegset`
3. Esegui la procedura in Visum

⏱️ **Tempo verifica:** 450ms
```

## Technical Implementation

### Python Code Logic

```python
# 1. Check if network has links
links = visum.Net.Links
link_count = links.Count

if link_count == 0:
    return {"exists": False, "reason": "No links in network"}

# 2. Try to get volume attribute
attr_name = f"VolVehPrT({analysisPeriod})"

try:
    # Use GetMultiAttValues for efficiency (single API call)
    volumes_data = links.GetMultiAttValues(attr_name)
    # Returns: (keys, values) tuple
    # keys = [(FromNode, ToNode), ...]
    # values = [volume1, volume2, ...]
    
    volumes = volumes_data[1]
    
    # 3. Calculate statistics
    total_volume = sum(volumes)
    links_with_traffic = sum(1 for v in volumes if v > 0)
    max_volume = max(volumes)
    avg_volume = total_volume / len(volumes)
    
    # 4. Check congestion (optional)
    vc_ratios = links.GetMultiAttValues(f"VolCapRatioPrT({analysisPeriod})")
    congested_links = sum(1 for vc in vc_ratios[1] if vc > 0.9)
    
    return {
        "exists": True,
        "total_volume": total_volume,
        "links_with_traffic": links_with_traffic,
        # ... more stats
    }
    
except Exception:
    # Attribute doesn't exist = assignment not executed
    return {"exists": False, "reason": "Attribute not found"}
```

### Why GetMultiAttValues?

**✅ Correct Method:**
```python
volumes = links.GetMultiAttValues("VolVehPrT(AP)")
# Returns all values in ONE API call
```

**❌ Incorrect Method:**
```python
link = links.ItemByKey(1)  # ERROR: Requires TWO keys (FromNode, ToNode)!
volume = link.AttValue("VolVehPrT(AP)")
```

**Error Details:**
```
pywintypes.com_error: (-2147352567, 'Exception occurred.', 
  (0, 'Visum.Visum.2501', 
   'CComLinks::ItemByKey failed: link does not exist', 
   None, 0, -2147352567), None)
```

**Reason:** Links collection uses **composite keys** (FromNode, ToNode), not sequential indices.

## Statistics Provided

| Statistic | Description | Formula |
|-----------|-------------|---------|
| `total_links` | Total number of links in network | `links.Count` |
| `links_with_traffic` | Links with volume > 0 | `sum(v > 0)` |
| `total_volume` | Sum of all vehicle volumes | `sum(volumes)` |
| `max_volume` | Maximum volume on any link | `max(volumes)` |
| `avg_volume` | Average volume per link | `total / count` |
| `congested_links` | Links with V/C > 0.9 | `sum(vc > 0.9)` |

## Use Cases

### 1. Pre-Export Validation

```javascript
// Before exporting tables, verify assignment exists
const checkResult = await visum_check_assignment({
  projectId: "S000009result_1278407893"
});

if (checkResult.exists) {
  // Proceed with table export
  await project_export_visible_tables({
    projectId: "S000009result_1278407893",
    layoutFile: "tabelle_report.lay"
  });
}
```

### 2. Assignment Progress Monitoring

```javascript
// Check multiple analysis periods
for (const period of ["AM", "IP", "PM"]) {
  const result = await visum_check_assignment({
    projectId: "S000009result_1278407893",
    analysisPeriod: period
  });
  console.log(`${period}: ${result.exists ? '✅' : '❌'}`);
}
```

### 3. Quality Assurance

```javascript
// Verify assignment has reasonable traffic distribution
const result = await visum_check_assignment({
  projectId: "S000009result_1278407893"
});

const trafficCoverage = result.links_with_traffic / result.total_links;
if (trafficCoverage < 0.5) {
  console.warn("Low traffic coverage - check demand data!");
}

if (result.congested_links > result.total_links * 0.1) {
  console.warn("High congestion - consider capacity improvements!");
}
```

## Workflow Integration

### Complete Assignment Workflow

```
1. Create PrT Assignment Procedure
   └─> visum_create_procedure({procedureType: "PrT_Assignment"})
   
2. List Available Demand Segments
   └─> visum_list_demand_segments({projectId: "..."})
   
3. Configure Segments
   └─> visum_configure_dsegset({
         procedurePosition: actual_position,
         segmentNumbers: "1-10"
       })
   
4. Execute Procedure in Visum GUI
   └─> (User action: Run procedure)
   
5. ✅ Verify Execution Success
   └─> visum_check_assignment({projectId: "..."})
   
6. Export Results
   └─> project_export_visible_tables({
         layoutFile: "tabelle_report.lay"
       })
```

## Error Handling

### No Links in Network

```json
{
  "status": "no_data",
  "exists": false,
  "reason": "No links in network",
  "link_count": 0
}
```

**Solution:** Verify network is loaded correctly.

### Attribute Not Found

```json
{
  "status": "not_executed",
  "exists": false,
  "reason": "Attribute VolVehPrT(AP) not found - assignment not executed",
  "link_count": 227508
}
```

**Solution:** Execute PrT assignment procedure in Visum.

### Wrong Analysis Period

```json
{
  "status": "not_executed",
  "exists": false,
  "reason": "Attribute VolVehPrT(XYZ) not found",
  "link_count": 227508
}
```

**Solution:** Use correct period code: "AP", "AM", "PM", etc.

## Performance

| Network Size | Links | Execution Time |
|--------------|-------|----------------|
| Small | 1,000 | ~100ms |
| Medium | 50,000 | ~500ms |
| Large | 227,508 | ~2,340ms |
| Very Large | 500,000+ | ~5,000ms |

**Optimization:** Uses `GetMultiAttValues()` for single-call retrieval instead of iterating through links.

## Related Tools

- `visum_create_procedure` - Create PrT Assignment procedures
- `visum_list_demand_segments` - List available demand segments
- `visum_configure_dsegset` - Configure segments on procedures
- `project_export_visible_tables` - Export assignment results to CSV

## See Also

- `WORKFLOW_PRT_ASSIGNMENT.md` - Complete PrT workflow guide
- `VISUM_PROCEDURES_API.md` - Procedure creation documentation
- `TABLE_EXPORT_WORKFLOW.md` - Table export guide
- `CLAUDE_WORKFLOW_GUIDE.md` - Interactive AI patterns
