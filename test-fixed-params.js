import net from 'net';

const pythonCode = `
# Test con la proprietà corretta: PrTAssignmentParameters
# Prima conta quante operazioni ci sono
ops = visum.Procedures.Operations.GetAll
total_ops = len(ops)

# Usa l'ultima operazione esistente (dovrebbe essere quella di tipo 101 che abbiamo già creato)
if total_ops >= 21:
    operation = visum.Procedures.Operations.ItemByKey(21)
else:
    # Altrimenti crea a posizione totale+1
    operation = visum.Procedures.Operations.AddOperation(total_ops + 1)
    operation.SetAttValue("OPERATIONTYPE", 101)

# PROVA 1: PrTAssignmentParameters
try:
    params = operation.PrTAssignmentParameters
    result = {
        "status": "ok",
        "message": "PrTAssignmentParameters FUNZIONA!",
        "type": str(type(params)),
        "operation_type": operation.AttValue("OPERATIONTYPE")
    }
except AttributeError as e1:
    # PROVA 2: Prova altri nomi possibili
    try:
        params = operation.PrtAssignmentParameters  # senza T maiuscola
        result = {
            "status": "ok",
            "message": "PrtAssignmentParameters FUNZIONA!",
            "type": str(type(params))
        }
    except AttributeError as e2:
        result = {
            "status": "error",
            "error1": str(e1),
            "error2": str(e2),
            "available_attrs": [attr for attr in dir(operation) if 'assign' in attr.lower()]
        }
`;

const client = new net.Socket();
let welcomeReceived = false;

client.connect(7901, '::1', () => {
    console.log('✅ Connected to TCP server on port 7901');
});

client.on('data', (data) => {
    const response = JSON.parse(data.toString());
    
    if (!welcomeReceived && response.type === 'project_welcome') {
        console.log('\n📊 Welcome message received');
        welcomeReceived = true;
        
        // Now send the Python command
        const request = {
            type: 'query',
            requestId: Date.now(),
            description: 'Test PrTAssignmentParameters property',
            code: pythonCode
        };
        console.log('📤 Sending Python command...\n');
        client.write(JSON.stringify(request) + '\n');
    } else {
        console.log('\n📊 Response from server:');
        console.log(JSON.stringify(response, null, 2));
        client.destroy();
    }
});

client.on('close', () => {
    console.log('🔌 Connection closed');
});

client.on('error', (err) => {
    console.error('❌ Error:', err.message);
});
