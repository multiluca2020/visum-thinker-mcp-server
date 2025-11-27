"""
Script per filtrare i file *_ODPAIR.csv nella cartella config_tests
usando le coppie OD valide da odpair_list__r7.csv
"""

import os
import csv
from pathlib import Path

def filter_odpair_csv(input_file, output_file, valid_pairs):
    """
    Filtra un file ODPAIR.csv mantenendo solo le righe con coppie OD valide
    
    Args:
        input_file: Path al file CSV di input
        output_file: Path al file CSV di output
        valid_pairs: Set di tuple (zona_o, zona_d) valide
    
    Returns:
        dict con statistiche
    """
    print(f"\nProcessando: {os.path.basename(input_file)}")
    
    try:
        # Leggi file input
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if len(lines) == 0:
            print("  ERRORE: File vuoto")
            return {'status': 'ERROR', 'reason': 'Empty file'}
        
        # Parse header
        header = lines[0].strip()
        headers = header.split(';')
        
        # Trova indici colonne FROMZONENO e TOZONENO
        from_idx = None
        to_idx = None
        
        for i, h in enumerate(headers):
            h_upper = h.upper()
            if h_upper == 'FROMZONENO':
                from_idx = i
            elif h_upper == 'TOZONENO':
                to_idx = i
        
        if from_idx is None or to_idx is None:
            print("  ERRORE: Colonne FROMZONENO/TOZONENO non trovate")
            print(f"  Header disponibili: {headers}")
            return {'status': 'ERROR', 'reason': 'Missing columns'}
        
        print(f"  FROMZONENO: colonna {from_idx}")
        print(f"  TOZONENO: colonna {to_idx}")
        
        # Filtra righe
        filtered_lines = [header]
        total_rows = len(lines) - 1
        filtered_count = 0
        
        for line_num, line in enumerate(lines[1:], start=2):
            line = line.strip()
            if not line:
                continue
            
            parts = line.split(';')
            
            if len(parts) <= max(from_idx, to_idx):
                print(f"  WARNING: Riga {line_num} ha solo {len(parts)} colonne, skip")
                continue
            
            try:
                # Converti float -> int per confronto
                from_zone = int(float(parts[from_idx]))
                to_zone = int(float(parts[to_idx]))
                
                if (from_zone, to_zone) in valid_pairs:
                    filtered_lines.append(line)
                    filtered_count += 1
            
            except (ValueError, IndexError) as e:
                print(f"  WARNING: Errore riga {line_num}: {e}")
                continue
        
        # Scrivi file output
        output_text = '\n'.join(filtered_lines)
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            f.write(output_text)
        
        # Statistiche
        size_mb = os.path.getsize(output_file) / (1024 * 1024)
        percentage = (100.0 * filtered_count / total_rows) if total_rows > 0 else 0
        
        print(f"  ✓ Filtrate: {filtered_count}/{total_rows} righe ({percentage:.1f}%)")
        print(f"  ✓ Output: {output_file}")
        print(f"  ✓ Dimensione: {size_mb:.2f} MB")
        
        return {
            'status': 'SUCCESS',
            'input_file': input_file,
            'output_file': output_file,
            'total_rows': total_rows,
            'filtered_rows': filtered_count,
            'percentage': round(percentage, 1),
            'size_mb': round(size_mb, 2)
        }
    
    except Exception as e:
        print(f"  ERRORE: {e}")
        return {'status': 'ERROR', 'reason': str(e)}


def main():
    # Configurazione
    odpair_filter_file = r"h:\go\trenord_2025\odpair_list__r7.csv"
    config_tests_dir = r"h:\go\trenord_2025\config_tests"
    
    print("=" * 80)
    print("FILTRO ODPAIR CSV")
    print("=" * 80)
    print(f"\nFile filtro: {odpair_filter_file}")
    print(f"Directory:   {config_tests_dir}")
    
    # Verifica esistenza directory
    if not os.path.exists(config_tests_dir):
        print(f"\nERRORE: Directory non trovata: {config_tests_dir}")
        return
    
    # Carica coppie OD valide
    print("\n" + "-" * 80)
    print("CARICAMENTO COPPIE OD VALIDE")
    print("-" * 80)
    
    valid_pairs = set()
    
    try:
        with open(odpair_filter_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                zona_o = int(row['Zona_o'])
                zona_d = int(row['Zona_d'])
                valid_pairs.add((zona_o, zona_d))
        
        print(f"✓ Coppie OD valide caricate: {len(valid_pairs)}")
    
    except Exception as e:
        print(f"ERRORE: Impossibile caricare filtro: {e}")
        return
    
    # Trova tutti i file *_ODPAIR.csv
    print("\n" + "-" * 80)
    print("RICERCA FILE ODPAIR.CSV")
    print("-" * 80)
    
    odpair_files = []
    for filename in os.listdir(config_tests_dir):
        if filename.upper().endswith('_ODPAIR.CSV'):
            full_path = os.path.join(config_tests_dir, filename)
            odpair_files.append(full_path)
    
    print(f"\n✓ File ODPAIR trovati: {len(odpair_files)}")
    for f in odpair_files:
        print(f"  - {os.path.basename(f)}")
    
    if len(odpair_files) == 0:
        print("\nNessun file da processare!")
        return
    
    # Processa ogni file
    print("\n" + "-" * 80)
    print("FILTRO FILE")
    print("-" * 80)
    
    results = []
    
    for input_file in odpair_files:
        # Output file: stesso nome con _FILTERED
        base_name = os.path.basename(input_file)
        name_without_ext = os.path.splitext(base_name)[0]
        output_name = f"{name_without_ext}_FILTERED.csv"
        output_file = os.path.join(config_tests_dir, output_name)
        
        result = filter_odpair_csv(input_file, output_file, valid_pairs)
        results.append(result)
    
    # Riepilogo
    print("\n" + "=" * 80)
    print("RIEPILOGO")
    print("=" * 80)
    
    success_count = sum(1 for r in results if r['status'] == 'SUCCESS')
    error_count = sum(1 for r in results if r['status'] == 'ERROR')
    
    print(f"\nFile processati: {len(results)}")
    print(f"  Successo: {success_count}")
    print(f"  Errori:   {error_count}")
    
    if success_count > 0:
        print("\nStatistiche:")
        total_input_rows = sum(r.get('total_rows', 0) for r in results if r['status'] == 'SUCCESS')
        total_output_rows = sum(r.get('filtered_rows', 0) for r in results if r['status'] == 'SUCCESS')
        
        print(f"  Righe totali input:  {total_input_rows:,}")
        print(f"  Righe totali output: {total_output_rows:,}")
        
        if total_input_rows > 0:
            avg_percentage = 100.0 * total_output_rows / total_input_rows
            print(f"  Percentuale media:   {avg_percentage:.1f}%")
    
    print("\n✓ Completato!")


if __name__ == '__main__':
    main()
