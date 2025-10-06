"""
Script per creare procedure PrT Assignment via Visum COM API
============================================================

Questo script dimostra come:
1. Creare un'operazione PrT Assignment da zero
2. Configurare i parametri dell'assignment
3. Eseguire la procedura

Documentazione API:
- IOperations.AddOperation(RelPos, [Group]) -> IOperation
- IOperation.SetAttValue("OPERATIONTYPE", 101)  # 101 = OperationTypeAssignmentPrT
- IOperation.PrTAssignmentPara -> IPrTAssignmentPara
"""

import win32com.client
import sys

def create_prt_assignment_procedure(visum, demand_segment="P", 
                                    assignment_variant="Equilibrium",
                                    position=1):
    """
    Crea una procedura PrT Assignment completa
    
    Args:
        visum: Oggetto Visum COM
        demand_segment: Nome del segmento di domanda (default: "P")
        assignment_variant: Tipo di assignment (default: "Equilibrium")
            Opzioni: "Equilibrium", "Incremental", "Stochastic", "FrankWolfe", 
                    "LUCE", "ICA", "SBA", "Bicycle"
        position: Posizione nella sequenza procedure (default: 1)
    
    Returns:
        IOperation: L'operazione creata
    """
    
    print(f"\n🚀 Creazione PrT Assignment alla posizione {position}...")
    
    # 1. Crea nuova operazione
    operation = visum.Procedures.Operations.AddOperation(position)
    print(f"✅ Operazione creata: {operation}")
    
    # 2. Imposta tipo operazione = PrT Assignment (101)
    operation.SetAttValue("OPERATIONTYPE", 101)
    print(f"✅ Tipo operazione impostato: 101 (PrTAssignment)")
    
    # 3. Accedi ai parametri assignment
    assignment_params = operation.PrTAssignmentPara
    print(f"✅ Parametri assignment accessibili: {assignment_params}")
    
    # 4. Imposta segmento domanda
    assignment_params.SetAttValue("DSegSet", demand_segment)
    print(f"✅ Segmento domanda impostato: {demand_segment}")
    
    # 5. Imposta variante assignment
    variant_map = {
        "Incremental": 1,      # PrTAssignmentVariantIncremental
        "Equilibrium": 2,      # PrTAssignmentVariantEquilibrium
        "Tribut": 5,
        "Stochastic": 6,       # PrTAssignmentVariantStochastic
        "DynStochastic": 7,
        "DUE": 8,
        "LUCE": 9,             # PrTAssignmentVariantLUCE
        "ICA": 10,             # PrTAssignmentVariantICA
        "SBA": 11,             # PrTAssignmentVariantSBA
        "FrankWolfe": 12,      # PrTAssignmentVariantFrankWolfe
        "Bicycle": 13          # PrTAssignmentVariantBicycle
    }
    
    variant_value = variant_map.get(assignment_variant, 2)  # Default: Equilibrium
    assignment_params.SetAttValue("PrTAssignmentVariant", variant_value)
    print(f"✅ Variante assignment impostata: {assignment_variant} ({variant_value})")
    
    # 6. Configurazione specifica per Equilibrium
    if assignment_variant == "Equilibrium":
        equilibrium_params = assignment_params.PrTEquilibriumAssignmentParameters
        print(f"✅ Parametri Equilibrium accessibili: {equilibrium_params}")
    
    print(f"\n✅ Procedura PrT Assignment creata con successo!")
    return operation


def create_complete_assignment_sequence(visum, demand_segment="P"):
    """
    Crea una sequenza completa di procedure:
    1. Initialize Assignment
    2. PrT Assignment
    
    Args:
        visum: Oggetto Visum COM
        demand_segment: Segmento di domanda
    
    Returns:
        tuple: (init_operation, assignment_operation)
    """
    
    print("\n" + "="*70)
    print("CREAZIONE SEQUENZA COMPLETA DI ASSIGNMENT")
    print("="*70)
    
    # 1. Crea "Initialize Assignment" (OPERATIONTYPE = 9)
    print("\n📋 Step 1: Initialize Assignment")
    init_op = visum.Procedures.Operations.AddOperation(1)
    init_op.SetAttValue("OPERATIONTYPE", 9)  # OperationTypeInitAssignment
    print("✅ Initialize Assignment creato")
    
    # 2. Crea "PrT Assignment"
    print("\n📋 Step 2: PrT Assignment")
    assignment_op = create_prt_assignment_procedure(visum, demand_segment, position=2)
    
    print("\n" + "="*70)
    print("✅ SEQUENZA COMPLETA CREATA!")
    print("="*70)
    print("\nOperazioni nella sequenza:")
    print("  1. Initialize Assignment")
    print(f"  2. PrT Assignment (Equilibrium, DemandSegment={demand_segment})")
    
    return init_op, assignment_op


def list_existing_procedures(visum):
    """
    Elenca tutte le operazioni esistenti nella sequenza procedure
    """
    print("\n" + "="*70)
    print("OPERAZIONI ESISTENTI NELLA SEQUENZA PROCEDURE")
    print("="*70)
    
    operations = visum.Procedures.Operations
    count = operations.Count
    
    if count == 0:
        print("❌ Nessuna operazione trovata nella sequenza procedure")
        return
    
    print(f"\n📊 Totale operazioni: {count}\n")
    
    for i in range(1, count + 1):
        op = operations.ItemByKey(i)
        op_type = op.AttValue("OPERATIONTYPE")
        
        # Mappa tipo operazione a nome leggibile
        op_type_names = {
            9: "Initialize Assignment",
            101: "PrT Assignment",
            100: "PuT Assignment",
            103: "Calculate PrT Skim Matrix",
            46: "Trip Distribution",
            45: "Trip Generation",
            47: "Mode Choice",
            65: "Run Script",
            75: "Group"
        }
        
        op_name = op_type_names.get(op_type, f"Unknown ({op_type})")
        print(f"  {i}. {op_name}")
        
        # Se è PrT Assignment, mostra dettagli
        if op_type == 101:
            try:
                params = op.PrTAssignmentPara
                dseg = params.AttValue("DSegSet")
                variant = params.AttValue("PrTAssignmentVariant")
                print(f"     └─ DemandSegment: {dseg}, Variant: {variant}")
            except:
                pass
    
    print()


def clear_all_procedures(visum):
    """
    Rimuove tutte le operazioni dalla sequenza procedure
    """
    print("\n🗑️  Rimozione operazioni esistenti...")
    operations = visum.Procedures.Operations
    
    # Rimuovi dal fondo verso l'alto per evitare problemi di indice
    while operations.Count > 0:
        operations.RemoveOperation(operations.Count)
    
    print("✅ Tutte le operazioni rimosse")


def execute_procedures(visum):
    """
    Esegue la sequenza di procedure
    """
    print("\n" + "="*70)
    print("ESECUZIONE SEQUENZA PROCEDURE")
    print("="*70)
    
    try:
        print("\n⚙️  Esecuzione in corso...")
        visum.Procedures.Execute()
        print("\n✅ ESECUZIONE COMPLETATA CON SUCCESSO!")
    except Exception as e:
        print(f"\n❌ ERRORE durante l'esecuzione: {e}")
        raise


def main():
    """
    Script principale
    """
    
    print("\n" + "="*70)
    print("VISUM COM API - CREAZIONE PrT ASSIGNMENT PROCEDURE")
    print("="*70)
    
    try:
        # Connetti a Visum
        print("\n🔌 Connessione a Visum...")
        visum = win32com.client.Dispatch("Visum.Visum.250")
        print("✅ Connessione stabilita")
        
        # Mostra operazioni esistenti
        list_existing_procedures(visum)
        
        # Opzione: pulisci procedure esistenti
        response = input("\n❓ Vuoi rimuovere le operazioni esistenti? (s/N): ").strip().lower()
        if response == 's':
            clear_all_procedures(visum)
        
        # Crea sequenza completa
        init_op, assignment_op = create_complete_assignment_sequence(visum, demand_segment="P")
        
        # Mostra nuova sequenza
        list_existing_procedures(visum)
        
        # Opzione: esegui procedure
        response = input("\n❓ Vuoi eseguire la sequenza di procedure? (s/N): ").strip().lower()
        if response == 's':
            execute_procedures(visum)
        else:
            print("\n✅ Procedure create ma NON eseguite")
        
        print("\n" + "="*70)
        print("SCRIPT COMPLETATO CON SUCCESSO!")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ ERRORE: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
