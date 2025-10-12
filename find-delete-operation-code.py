"""
Trova il codice OPERATIONTYPE per Delete Assignment Results
"""
import sys
sys.path.append(r"H:\Program Files\PTV Vision\PTV Visum 2025\Exe\Python")

import win32com.client

try:
    # Connetti a Visum già aperto
    visum = win32com.client.Dispatch("Visum.Visum.250")
    
    # Carica progetto se necessario
    try:
        project_path = r"H:\go\italferr2025\Campoleone\100625_Versione_base_v0.3_sub_ok_priv.ver"
        visum.LoadVersion(project_path)
        print(f"✅ Progetto caricato: {project_path}")
    except:
        print("⚠️ Progetto già caricato o errore caricamento")
    
    # Analizza le operations esistenti
    operations = visum.Procedures.Operations
    print(f"\n📋 Totale operazioni esistenti: {len([o for o in operations.GetAll])}")
    print("\nOperazioni trovate:")
    print("=" * 80)
    
    for i in range(1, min(50, len([o for o in operations.GetAll]) + 1)):
        try:
            op = operations.ItemByKey(i)
            op_type = op.AttValue("OPERATIONTYPE")
            
            # Prova a ottenere il nome/descrizione
            try:
                op_name = op.AttValue("NAME")
            except:
                op_name = "N/A"
            
            # Prova a capire il tipo dall'oggetto
            op_str = str(type(op))
            
            print(f"Pos {i:3d}: OPERATIONTYPE={op_type:3d} | NAME={op_name}")
            
            # Se troviamo qualcosa con "Delete" nel nome
            if "delete" in op_name.lower() or "delete" in op_str.lower():
                print(f"  ⭐ FOUND DELETE OPERATION!")
                
        except Exception as e:
            # Fine operazioni
            break
    
    print("\n" + "=" * 80)
    print("\n🔍 Test creazione Delete Assignment Results...")
    
    # Prova codici comuni per Delete
    test_codes = [
        (50, "Delete PrT Results (tentativo 1)"),
        (51, "Delete PuT Results (tentativo 1)"), 
        (150, "Delete Results (tentativo 2)"),
        (200, "Delete Operations (tentativo 3)"),
        (10, "Generic Delete (tentativo 4)"),
    ]
    
    for code, description in test_codes:
        try:
            # Trova ultima posizione disponibile
            last_pos = len([o for o in operations.GetAll])
            
            # Crea operation con questo codice
            new_op = operations.AddOperation(last_pos)
            new_op.SetAttValue("OPERATIONTYPE", code)
            
            # Verifica che sia stato creato
            created = operations.ItemByKey(last_pos + 1)
            created_type = created.AttValue("OPERATIONTYPE")
            
            if created_type == code:
                print(f"\n✅ SUCCESSO! OPERATIONTYPE {code} = {description}")
                print(f"   Posizione: {last_pos + 1}")
                print(f"   Tipo oggetto: {type(created)}")
                
                # Non rimuovere, lascialo per ispezione
                
            else:
                print(f"❌ Codice {code} non corrisponde")
                # Rimuovi
                operations.RemoveOperation(last_pos + 1)
                
        except Exception as e:
            print(f"❌ Codice {code}: {str(e)[:100]}")
    
except Exception as e:
    print(f"❌ Errore: {e}")
    import traceback
    traceback.print_exc()
