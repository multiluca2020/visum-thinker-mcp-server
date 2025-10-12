"""
Check all operations in the Visum project
"""
import win32com.client

# Connect to running Visum instance
visum = win32com.client.Dispatch("Visum.Visum.250")

# Get all operations
ops = list(visum.Procedures.Operations.GetAll)

print(f"\n📊 Total operations: {len(ops)}")
print("\n🔍 Last 15 operations:\n")

for op in ops[-15:]:
    op_num = op.AttValue("NO")
    op_type = op.AttValue("OPERATIONTYPE")
    
    # Map common operation types
    type_names = {
        9: "Initialize Assignment (DELETE)",
        100: "PuT Assignment",
        101: "PrT Assignment",
        102: "Demand Model",
        103: "Calculate Skim Matrix PrT",
        104: "Matrix Calculation"
    }
    
    type_name = type_names.get(op_type, f"Unknown ({op_type})")
    
    print(f"  Position {op_num}: Type {op_type} - {type_name}")

# Count how many Initialize Assignment operations exist
init_count = sum(1 for op in ops if op.AttValue("OPERATIONTYPE") == 9)
prt_count = sum(1 for op in ops if op.AttValue("OPERATIONTYPE") == 101)

print(f"\n📈 Summary:")
print(f"   • Initialize Assignment (9): {init_count}")
print(f"   • PrT Assignment (101): {prt_count}")
