# 📊 Table Export Workflow

## Overview

The `project_export_visible_tables` tool exports **only the tables visible in the user's Visum GUI** to CSV files, maintaining:
- ✅ Exact column order as displayed in layout
- ✅ Sub-attributes (formula columns) with proper formatting
- ✅ All rows for each table  
- ✅ UTF-8 encoding with semicolon delimiter

## How It Works

### 1. XML Layout File Parsing

Global Layout files (`.lay`) are XML files containing complete definitions of all visible tables and their columns.

**XML Structure (Simple Attributes):**
```xml
<layout version="2">
  <listLayoutItem>
    <caption text="Lista (Archi)"/>
    <listGraphicParameterLayoutItems 
      netObjectType="LINK"/>
    <attributeDefinition 
      attributeID="NO"
      subAttributeID1=""
      subAttributeID2=""
      subAttributeID3=""/>
    <attributeDefinition 
      attributeID="LENGTH"
      subAttributeID1=""
      subAttributeID2=""
      subAttributeID3=""/>
  </listLayoutItem>
</layout>
```

**XML Structure (Sub-Attributes / Formula Columns):**
```xml
<attributeDefinition 
  attributeID="VEHKMTRAVPRT_DSEG"
  subAttributeID1="C_CORRETTA_FERIALE"
  subAttributeID2="AP"
  subAttributeID3=""/>
```

This becomes:
- Visum API: `VEHKMTRAVPRT_DSEG(C_CORRETTA_FERIALE,AP)`
- CSV Header: `VEHKMTRAVPRT_DSEG_C_CORRETTA_FERIALE_AP`

### 2. Tool Workflow

```
1. Parse .lay XML file (default: tabelle_report.lay)
   ↓
2. Extract each <listLayoutItem>:
   - listTitle: Table name (e.g., "Lista (Archi)")
   - netObjectType: Collection type (e.g., "LINK", "ZONE")
   - attributeDefinition elements: Column names in exact order
   ↓
3. For each table:
   - Map netObjectType → visum.Net collection
   - Create CSV file: {projectName}_{tableName}.csv
   - Export all rows with columns from XML
   ↓
4. Return summary with file statistics
```

### 3. Collection Mapping

```python
collection_mapping = {
    'LINK': ('Links', 'No'),
    'NODE': ('Nodes', 'No'),
    'ZONE': ('Zones', 'No'),
    'ODPAIR': ('ODPairs', 'No'),
    'LINE': ('Lines', 'Name'),
    'LINEROUTE': ('LineRoutes', 'Name'),
    'STOP': ('StopPoints', 'No'),
    'TURN': ('Turns', 'No')
}
```

## Usage

### Basic Usage

```javascript
// Export all tables from default layout (tabelle_report.lay)
project_export_visible_tables({
  projectId: "S000009result_1278407893"
})
```

### Custom Layout File

```javascript
// Export from specific layout file
project_export_visible_tables({
  projectId: "S000009result_1278407893",
  layoutFile: "my_custom_layout.lay"
})
```

## Example Output

```
✅ **Tabelle Visibili Esportate**

📂 **Progetto:** S000009result
🎨 **Layout:** tabelle_report.lay
📁 **Directory:** H:\Progetti\Visum\

📊 **Tabelle trovate nel layout:** 4
📄 **File CSV creati:** 4
📝 **Totale righe esportate:** 331,750

**File esportati:**

✅ **Lista (Archi)**
   📄 S000009result_Lista_Archi.csv
   📊 227,508 righe × 29 colonne
   💾 45,234 KB

✅ **Lista (Relazioni OD)**
   📄 S000009result_Lista_Relazioni_OD.csv
   📊 70,225 righe × 15 colonne
   💾 12,456 KB

✅ **Lista (Linee)**
   📄 S000009result_Lista_Linee.csv
   📊 450 righe × 22 colonne
   💾 234 KB

✅ **Lista (Percorsi di linea)**
   📄 S000009result_Lista_Percorsi_di_linea.csv
   📊 33,567 righe × 18 colonne
   💾 8,901 KB
```

## CSV File Format

- **Delimiter:** `;` (semicolon)
- **Encoding:** UTF-8
- **Headers:** First row contains column names from XML
- **Data:** Exact values from Visum with same order as GUI display

**Example CSV:**
```csv
NO;LENGTH;VOLCAPRATIOPRT;TSYSSET;TYPENO
1;1250.5;0.85;C;1
2;890.2;0.92;C,H;2
...
```

## Key Features

### ✅ Advantages

1. **GUI Accuracy**: Exports exactly what user sees in Visum
2. **Column Order**: Maintains exact column order from layout
3. **Multiple Tables**: Processes all visible tables automatically
4. **Fast Parsing**: Uses native Python XML parser
5. **Error Handling**: Continues even if some tables fail

### ⚠️ Limitations

1. **Layout Required**: Must have a Global Layout loaded
2. **Collection Mapping**: Only supports predefined netObjectTypes
3. **Missing Attributes**: Empty cells for unavailable attributes
4. **Large Files**: May take time for projects with millions of rows

## Interactive Workflow for AI Assistants

When user requests table export:

```
1. First, list available layouts:
   project_list_available_layouts({projectId: "..."})

2. Show layouts to user and ask which to use

3. Export tables from selected layout:
   project_export_visible_tables({
     projectId: "...",
     layoutFile: "user_selected.lay"
   })

4. Show export summary to user
```

## Troubleshooting

### "Layout file non trovato"

**Problem:** Layout file doesn't exist in project directory

**Solution:**
- Use `project_list_available_layouts` to see available files
- Load layout first with `project_load_global_layout`
- Check filename spelling (case-sensitive)

### "Collection mapping not found"

**Problem:** netObjectType not recognized (e.g., "VEHJOURNEYSECTION")

**Solution:**
- Add mapping to `collection_mapping` dictionary
- Find correct collection name in Visum COM API documentation
- Test with `visum.Net.{CollectionName}.Count`

### "No data" for table

**Problem:** Collection exists but is empty (e.g., no Turns defined)

**Solution:**
- Normal behavior for empty collections
- Check in Visum GUI if table has data
- Export will skip empty tables with warning

## Technical Details

### XML Parsing

```python
import xml.etree.ElementTree as ET

tree = ET.parse('tabelle_report.lay')
root = tree.getroot()

for list_item in root.iter('listLayoutItem'):
    # Extract metadata
    common = list_item.find('.//listLayoutCommonEntries')
    title = common.get('listTitle')
    
    graphic = list_item.find('.//listGraphicParameterLayoutItems')
    net_type = graphic.get('netObjectType')
    
    # Extract columns
    for attr_def in list_item.iter('attributeDefinition'):
        column = attr_def.get('attributeID')
```

### CSV Export

```python
import csv

with open(csv_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow(columns)  # From XML
    
    for i in range(collection.Count):
        item = collection.ItemByKey(i+1)
        row = [item.AttValue(col) for col in columns]
        writer.writerow(row)
```

## Related Tools

- `project_list_available_layouts` - List available .lay files
- `project_load_global_layout` - Load layout into Visum
- `project_export_all_tables` - Export predefined tables (old method)

## See Also

- `GLOBAL_LAYOUTS_WORKFLOW.md` - How to manage Global Layouts
- `VISUM_BOT_GROUP.md` - Visum automation patterns
- `CLAUDE_WORKFLOW_GUIDE.md` - Interactive AI assistant patterns
