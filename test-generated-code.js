// Test what Python code is actually generated
const procedureType = "PrT_Assignment";
const position = 20;
const parameters = {};

const operationTypeCodes = {
  "PrT_Assignment": 101,
  "PuT_Assignment": 100,
  "Demand_Model": 103,
  "Matrix_Calculation": 104
};

const operationCode = operationTypeCodes[procedureType];
const needsDeleteBefore = procedureType === "PrT_Assignment" || procedureType === "PuT_Assignment";
const deleteOperationType = 9;

console.log("=== VARIABLE VALUES ===");
console.log(`procedureType: ${procedureType}`);
console.log(`operationCode: ${operationCode}`);
console.log(`deleteOperationType: ${deleteOperationType}`);
console.log(`needsDeleteBefore: ${needsDeleteBefore}`);
console.log("\n=== GENERATED PYTHON CODE ===\n");

const pythonCode = `
try:
    operations_container = visum.Procedures.Operations
    existing_count = len([op for op in operations_container.GetAll])
    
    ${needsDeleteBefore ? `
    # Step 1: Create "Initialize Assignment" operation BEFORE the assignment
    print("📋 Creating Initialize Assignment operation first...")
    delete_op = operations_container.AddOperation(${position})
    delete_op.SetAttValue("OPERATIONTYPE", ${deleteOperationType})
    
    delete_count = len([op for op in operations_container.GetAll])
    delete_position = delete_count
    
    print(f"✅ Initialize Assignment operation created at position {delete_position}")
    print(f"   Type: Initialize Assignment (code ${deleteOperationType})")
    ` : ''}
    
    # Step 2: Create the assignment operation
    print(f"📋 Creating ${procedureType} operation...")
    print(f"   Operation code to set: ${operationCode}")
    new_op = visum.Procedures.Operations.AddOperation(${position})
    
    new_count = len([op for op in operations_container.GetAll])
    actual_position = new_count
    
    # Set operation type
    new_op.SetAttValue("OPERATIONTYPE", ${operationCode})
    
    # VERIFY
    verify_type = new_op.AttValue("OPERATIONTYPE")
    print(f"✅ ${procedureType} operation created at position {actual_position}")
    print(f"   Requested type code: ${operationCode}")
    print(f"   Verified type code: {verify_type}")
    print(f"   Match: {verify_type == ${operationCode}}")
    
    result = {"status": "success", "actual_position": actual_position}
except Exception as e:
    result = {"status": "error", "error": str(e)}
`;

console.log(pythonCode);
