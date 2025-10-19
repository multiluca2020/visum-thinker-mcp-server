"""
Export Links table from Visum to CSV
Maintains exact column order as defined in tabelle_report.lay

Usage:
1. Open Visum project
2. Run this script in VisumPy console or via project_execute
"""

import xml.etree.ElementTree as ET
import os

# Configuration
layout_file = r'H:\go\reports\Input\tabelle_report.lay'
output_file = r'H:\go\reports\Input\S000009result_Links_Fast.csv'

# Parse XML to get column definitions
tree = ET.parse(layout_file)
root = tree.getroot()

# Find Links table definition
all_cols = []
for list_item in root.iter('listLayoutItem'):
    graphic = list_item.find('.//listGraphicParameterLayoutItems')
    if graphic is not None and graphic.get('netObjectType') == 'LINK':
        # Extract all column IDs in order
        for attr_def in list_item.iter('attributeDefinition'):
            attr_id = attr_def.get('attributeID')
            if attr_id:
                all_cols.append(attr_id)
        break

print(f"Found {len(all_cols)} columns in layout: {all_cols[:10]}...")

# Get Links collection
lks = visum.Net.Links

# Filter valid columns (test each one)
valid_cols = []
for col in all_cols:
    try:
        # Test if column works
        test_data = lks.GetMultipleAttributes([col])
        if test_data and len(test_data) > 0:
            valid_cols.append(col)
            print(f"✓ {col}")
    except Exception as e:
        print(f"✗ {col}: {str(e)[:50]}")

print(f"\n{len(valid_cols)} valid columns: {valid_cols}")

# Get all data for valid columns
print(f"\nRetrieving data for {lks.Count} links...")
data = lks.GetMultipleAttributes(valid_cols)
nr = lks.Count

print(f"Building CSV with {nr} rows...")

# Build CSV content
lines = []

# Header
lines.append(';'.join(valid_cols))

# Data rows - using explicit loops to avoid Python scope issues
for ri in range(nr):
    row_parts = []
    for ci in range(len(valid_cols)):
        row_parts.append(str(data[ci][ri]))
    lines.append(';'.join(row_parts))
    
    # Progress indicator
    if ri % 50000 == 0 and ri > 0:
        print(f"  Processed {ri} rows...")

# Join all lines
print(f"Writing to file...")
text = '\r\n'.join(lines)

# Write to file
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(text)

file_size = os.path.getsize(output_file) / (1024 * 1024)
print(f"\n✅ Export complete!")
print(f"   File: {output_file}")
print(f"   Size: {file_size:.2f} MB")
print(f"   Rows: {nr + 1} (including header)")
print(f"   Columns: {len(valid_cols)}")
