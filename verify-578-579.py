"""
Direct verification of operations 578 and 579 in Visum
Run this in base environment with pywin32 installed
"""
import win32com.client

visum = win32com.client.Dispatch("Visum.Visum.250")

print("\n" + "="*60)
print("VERIFICA OPERAZIONI 578-579")
print("="*60 + "\n")

for pos in [575, 576]:
    try:
        op = visum.Procedures.Operations.ItemByKey(pos)
        op_type = op.AttValue("OPERATIONTYPE")
        
        type_names = {
            9: "Initialize Assignment (DELETE)",
            100: "PuT Assignment",
            101: "PrT Assignment"
        }
        
        type_name = type_names.get(op_type, f"Unknown ({op_type})")
        
        print(f"Position {pos}:")
        print(f"  OPERATIONTYPE = {op_type}")
        print(f"  Nome: {type_name}")
        
        if pos == 578:
            if op_type == 9:
                print("  ✅ CORRETTO - Initialize Assignment")
            else:
                print(f"  ❌ ERRORE - Dovrebbe essere 9, è {op_type}")
        elif pos == 579:
            if op_type == 101:
                print("  ✅ CORRETTO - PrT Assignment")
            else:
                print(f"  ❌ ERRORE - Dovrebbe essere 101, è {op_type}")
        
        print()
    except Exception as e:
        print(f"Position {pos}: ERRORE - {e}\n")

print("="*60)
