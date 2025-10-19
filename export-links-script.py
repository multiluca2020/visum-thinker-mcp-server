import os
import csv
import xml.etree.ElementTree as ET

result = {}

try:
    ver_path = visum.GetPath(1)
    project_dir = os.path.dirname(ver_path)
    project_name = os.path.splitext(os.path.basename(ver_path))[0]
    lay_file = os.path.join(project_dir, 'tabelle_report.lay')
    
    tree = ET.parse(lay_file)
    root = tree.getroot()
    
    for list_item in root.iter('listLayoutItem'):
        graphic = list_item.find('.//listGraphicParameterLayoutItems')
        if graphic is None:
            continue
        
        net_type = graphic.get('netObjectType', '')
        if net_type != 'LINK':
            continue
        
        # Get all columns
        all_columns = []
        for attr_def in list_item.iter('attributeDefinition'):
            attr_id = attr_def.get('attributeID')
            if attr_id:
                all_columns.append(attr_id)
        
        result['total_columns'] = len(all_columns)
        
        # Filter valid columns
        links = visum.Net.Links
        valid_columns = []
        
        for col in all_columns:
            try:
                test = links.GetMultipleAttributes([col])
                if test:
                    valid_columns.append(col)
            except:
                pass
        
        result['valid_columns'] = len(valid_columns)
        result['columns'] = valid_columns
        
        # Get data for valid columns
        if valid_columns:
            mydata = links.GetMultipleAttributes(valid_columns)
            
            # Write CSV
            csv_file = os.path.join(project_dir, project_name + '_Links.csv')
            
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(valid_columns)
                
                num_rows = len(mydata[0]) if mydata else 0
                max_rows = min(1000, num_rows)
                
                for row_idx in range(max_rows):
                    row = []
                    for col_idx in range(len(valid_columns)):
                        row.append(mydata[col_idx][row_idx])
                    writer.writerow(row)
            
            result['file'] = os.path.basename(csv_file)
            result['rows'] = max_rows
            result['size_kb'] = round(os.path.getsize(csv_file) / 1024, 2)
        
        result['status'] = 'SUCCESS'
        break

except Exception as e:
    result['status'] = 'ERROR'
    result['error'] = str(e)
    import traceback
    result['traceback'] = traceback.format_exc()

result
