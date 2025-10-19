"""
Export all visible tables from a Visum Global Layout (.lay) to CSV files
Supports:
- Simple attributes (NO, LENGTH, etc.)
- Attributes with sub-attributes (VEHKMTRAVPRT_DSEG(C_CORRETTA_FERIALE,AP))
- Formula columns defined in layout
- Multiple tables in one layout file

Usage:
    python export-all-tables-from-layout.py

Or via project_execute MCP tool
"""

import xml.etree.ElementTree as ET
import os

# Configuration
layout_file = r'H:\go\reports\Input\tabelle_report.lay'
output_dir = r'H:\go\reports\Input'
project_name = 'S000009result'

# Parse layout XML
print(f"📖 Parsing layout: {layout_file}")
tree = ET.parse(layout_file)
root = tree.getroot()

# Find all visible tables
tables_info = []
for list_item in root.iter('listLayoutItem'):
    graphic = list_item.find('.//listGraphicParameterLayoutItems')
    if graphic is not None:
        net_obj_type = graphic.get('netObjectType')
        if net_obj_type:
            # Get table name
            table_name_elem = list_item.find('.//caption')
            table_name = table_name_elem.get('text', net_obj_type) if table_name_elem is not None else net_obj_type
            
            # Get all column definitions
            col_defs = []
            for attr_def in list_item.iter('attributeDefinition'):
                col_defs.append(attr_def.attrib)
            
            tables_info.append({
                'name': table_name,
                'type': net_obj_type,
                'columns': col_defs
            })

print(f"\n✅ Found {len(tables_info)} tables:")
for t in tables_info:
    print(f"   - {t['name']} ({t['type']}): {len(t['columns'])} columns")

# Map net object types to Visum collections
type_to_collection = {
    'LINK': 'visum.Net.Links',
    'NODE': 'visum.Net.Nodes',
    'ZONE': 'visum.Net.Zones',
    'ODPAIR': 'visum.Net.ODPairs',
    'LINE': 'visum.Net.Lines',
    'LINEROUTE': 'visum.Net.LineRoutes',
    'TIMEPROFILE': 'visum.Net.TimeProfiles',
    'TIMEPROFILEITEM': 'visum.Net.TimeProfileItems',
    'VEHJOURNEYSECTION': 'visum.Net.VehicleJourneySections',
    'STOP': 'visum.Net.Stops',
    'STOPPOINTAREA': 'visum.Net.StopPointAreas',
    'CONNECTOR': 'visum.Net.Connectors'
}

# Export each table
results = []
for table in tables_info:
    table_type = table['type']
    table_name = table['name']
    
    print(f"\n🔄 Processing: {table_name} ({table_type})")
    
    # Get collection
    collection_path = type_to_collection.get(table_type)
    if not collection_path:
        print(f"   ⚠️ Unknown type {table_type}, skipping...")
        results.append({'table': table_name, 'status': 'SKIPPED', 'reason': 'Unknown type'})
        continue
    
    try:
        collection = eval(collection_path)
        count = collection.Count
        print(f"   📊 {count} objects found")
    except Exception as e:
        print(f"   ❌ Cannot access collection: {e}")
        results.append({'table': table_name, 'status': 'ERROR', 'reason': str(e)})
        continue
    
    # Build attribute list with sub-attributes
    full_attrs = []
    headers = []
    
    for col in table['columns']:
        attr_id = col['attributeID']
        sub1 = col.get('subAttributeID1', '')
        sub2 = col.get('subAttributeID2', '')
        sub3 = col.get('subAttributeID3', '')
        
        # Build full attribute name
        if sub1 or sub2 or sub3:
            subs = [s for s in [sub1, sub2, sub3] if s]
            full_attr = attr_id + '(' + ','.join(subs) + ')'
            # Create readable header
            header = attr_id + '_' + '_'.join(subs)
        else:
            full_attr = attr_id
            header = attr_id
        
        full_attrs.append(full_attr)
        headers.append(header)
    
    print(f"   📝 Columns: {len(full_attrs)}")
    print(f"      First 5: {full_attrs[:5]}")
    
    # Get data
    try:
        print(f"   ⏳ Retrieving data...")
        data = collection.GetMultipleAttributes(full_attrs)
        
        # Build CSV
        print(f"   📄 Building CSV...")
        lines = [';'.join(headers)]
        
        for row_tuple in data:
            lines.append(';'.join(str(v) for v in row_tuple))
        
        # Write file
        safe_name = table_name.replace('/', '_').replace('\\', '_').replace(' ', '_')
        output_file = os.path.join(output_dir, f'{project_name}_{safe_name}.csv')
        
        text = '\n'.join(lines)
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            f.write(text)
        
        size_mb = os.path.getsize(output_file) / (1024 * 1024)
        
        print(f"   ✅ Exported: {output_file}")
        print(f"      Size: {size_mb:.2f} MB")
        print(f"      Rows: {len(data):,} + header")
        
        results.append({
            'table': table_name,
            'type': table_type,
            'status': 'SUCCESS',
            'file': output_file,
            'rows': len(data),
            'cols': len(full_attrs),
            'size_mb': round(size_mb, 2)
        })
        
    except Exception as e:
        print(f"   ❌ Export failed: {e}")
        results.append({
            'table': table_name,
            'status': 'ERROR',
            'reason': str(e)[:100]
        })

# Summary
print("\n" + "="*60)
print("📊 EXPORT SUMMARY")
print("="*60)

success = [r for r in results if r['status'] == 'SUCCESS']
errors = [r for r in results if r['status'] == 'ERROR']
skipped = [r for r in results if r['status'] == 'SKIPPED']

print(f"\n✅ Successful: {len(success)}")
for r in success:
    print(f"   - {r['table']}: {r['rows']:,} rows × {r['cols']} cols = {r['size_mb']} MB")

if errors:
    print(f"\n❌ Errors: {len(errors)}")
    for r in errors:
        print(f"   - {r['table']}: {r['reason']}")

if skipped:
    print(f"\n⚠️ Skipped: {len(skipped)}")
    for r in skipped:
        print(f"   - {r['table']}: {r['reason']}")

print(f"\n📁 Output directory: {output_dir}")
print("\n✨ Export complete!")

# Return results for MCP
result = {
    'total_tables': len(tables_info),
    'successful': len(success),
    'errors': len(errors),
    'skipped': len(skipped),
    'details': results
}
