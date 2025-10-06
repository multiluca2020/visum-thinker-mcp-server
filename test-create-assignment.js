/**
 * Test completo: Creazione PrT Assignment via TCP Server
 * =============================    // DEBUG: Mostra risposta completa
    console.log('🐛 DEBUG Response type:', response.type);
    console.log('🐛 DEBUG Success:', response.success);
    console.log('🐛 DEBUG Has output:', !!response.output);
    console.log('🐛 DEBUG Has result:', !!response.result);
    if (response.output) {
        console.log('🐛 DEBUG Output length:', response.output.length);
    }
    
    if (response.type === 'query_result' && response.success) {
        console.log('✅ Esecuzione completata');
        if (response.output) {
            console.log('📄 Output:');
            console.log(response.output);
        }
        if (response.result && Object.keys(response.result).length > 0) {
            console.log('📊 Risultato:', response.result);
        }
    } else if (response.type === 'error') {=================
 * 
 * Questo script testa la creazione di procedure PrT Assignment
 * usando il server TCP già avviato con Claude Desktop.
 */

import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import { spawn } from 'child_process';
import net from 'net';

const VISUM_SERVER_HOST = 'localhost';
const VISUM_SERVER_PORT = 7901;  // Porta corrente dal registry

/**
 * Invia comando al server TCP Visum
 */
async function sendVisumCommand(code, description = 'Python execution') {
    return new Promise((resolve, reject) => {
        const client = new net.Socket();
        
        const command = {
            type: 'query',
            code: code,
            description: description,
            requestId: Date.now()
        };
        
        client.connect(VISUM_SERVER_PORT, VISUM_SERVER_HOST, () => {
            console.log(`📡 Connesso al server TCP Visum su ${VISUM_SERVER_HOST}:${VISUM_SERVER_PORT}`);
            client.write(JSON.stringify(command) + '\n');
        });
        
        let buffer = '';
        
        client.on('data', (data) => {
            buffer += data.toString();
            
            // Dividi per newlines
            const messages = buffer.split('\n');
            buffer = messages.pop() || ''; // Mantieni l'ultimo pezzo
            
            for (const message of messages) {
                if (message.trim()) {
                    try {
                        const cleanedResponse = message.replace(/\\n$/g, '');
                        const response = JSON.parse(cleanedResponse);
                        
                        // Ignora welcome message
                        if (response.type === 'project_welcome') {
                            console.log('👋 Welcome message ricevuto');
                            continue;
                        }
                        
                        // Risposta vera
                        if (response.type === 'query_result' || response.type === 'error' || response.result !== undefined) {
                            client.destroy();
                            resolve(response);
                            return;
                        }
                    } catch (e) {
                        // JSON incompleto
                    }
                }
            }
        });
        
        client.on('close', () => {
            console.log('🔌 Connessione TCP chiusa');
        });
        
        client.on('error', (err) => {
            console.error('❌ Errore TCP:', err.message);
            reject(err);
        });
        
        // Timeout dopo 30 secondi
        client.setTimeout(30000, () => {
            console.log('⏱️  Timeout TCP');
            client.destroy();
            reject(new Error('TCP timeout'));
        });
    });
}

/**
 * Esegue codice Python nel contesto Visum
 */
async function executeVisumPython(code, description = 'Python execution') {
    console.log('\n📝 Esecuzione codice Python...');
    console.log('─'.repeat(70));
    
    const response = await sendVisumCommand(code, description);
    
    if (response.type === 'query_result' && response.success) {
        console.log('✅ Esecuzione completata');
        if (response.output) {
            console.log('� Output:');
            console.log(response.output);
        }
        if (response.result && Object.keys(response.result).length > 0) {
            console.log('� Risultato:', response.result);
        }
    } else if (response.type === 'error') {
        console.error('❌ Errore:', response.error);
        throw new Error(response.error);
    } else if (!response.success) {
        console.error('❌ Errore:', response.error || 'Unknown error');
        throw new Error(response.error || 'Unknown error');
    }
    
    console.log('─'.repeat(70));
    return response;
}

/**
 * Elenca procedure esistenti
 */
async function listExistingProcedures() {
    const code = `
# Elenca operazioni esistenti
operations_list = visum.Procedures.Operations.GetAll
count = len(operations_list)

result = {
    'count': count,
    'operations': []
}

if count > 0:
    for i, op in enumerate(operations_list, 1):
        op_type = op.AttValue("OPERATIONTYPE")
        
        op_info = {
            'index': i,
            'type': op_type,
            'type_name': 'Unknown'
        }
        
        # Mappa tipo operazione
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
        
        op_info['type_name'] = op_type_names.get(op_type, f"Unknown ({op_type})")
        
        # Dettagli PrT Assignment
        if op_type == 101:
            try:
                params = op.PrTAssignmentPara
                op_info['demand_segment'] = params.AttValue("DSegSet")
                op_info['variant'] = params.AttValue("PrTAssignmentVariant")
            except:
                pass
        
        result['operations'].append(op_info)

print(str(result))
`;

    console.log('\n' + '═'.repeat(70));
    console.log('📋 OPERAZIONI ESISTENTI NELLA SEQUENZA PROCEDURE');
    console.log('═'.repeat(70));
    
    const response = await executeVisumPython(code);
    
    if (response.output) {
        try {
            // Parse il risultato Python (dict convertito a stringa)
            const resultStr = response.output.trim();
            console.log('\n📊 Risultato:', resultStr);
        } catch (e) {
            console.log('Output grezzo:', response.output);
        }
    }
}

/**
 * Test API PrT Assignment
 */
async function testPrTAssignmentAPI() {
    const code = `
import traceback

print("="*70)
print("TEST API PrT ASSIGNMENT")
print("="*70)

try:
    # 1. Crea operazione alla posizione 21
    print("\\n[1] Creazione operazione alla posizione 21...")
    operation = visum.Procedures.Operations.AddOperation(21)
    print(f"    OK - Operazione creata")
    
    # 2. Imposta tipo PrT Assignment
    print("\\n[2] Impostazione tipo operazione...")
    operation.SetAttValue("OPERATIONTYPE", 101)
    print(f"    OK - Tipo 101 (PrT Assignment) impostato")
    
    # 3. Test accesso parametri - Metodo 1
    print("\\n[3] Test accesso parametri (Metodo 1: property)...")
    try:
        params = operation.PrTAssignmentPara
        print(f"    OK - Params: {type(params)}")
        
        # Prova a impostare DSegSet
        print("\\n[4] Impostazione DSegSet...")
        params.SetAttValue("DSegSet", "P")
        print("    OK - DSegSet impostato")
        
        # Prova a impostare PrTAssignmentVariant
        print("\\n[5] Impostazione PrTAssignmentVariant...")
        params.SetAttValue("PrTAssignmentVariant", 2)
        print("    OK - Variant Equilibrium impostato")
        
        print("\\n" + "="*70)
        print("SUCCESSO! API FUNZIONANTE!")
        print("="*70)
        
    except Exception as e:
        print(f"    ERRORE: {e}")
        print(f"    Traceback: {traceback.format_exc()}")
    
    # Cleanup
    print("\\n[CLEANUP] Rimozione operazione di test...")
    visum.Procedures.Operations.RemoveOperation(21)
    print("    OK - Operazione rimossa")
    
except Exception as main_error:
    print(f"\\nERRORE PRINCIPALE: {main_error}")
    print(f"Traceback: {traceback.format_exc()}")
`;

    await executeVisumPython(code, 'Test PrT Assignment API');
}

/**
 * Conta le operazioni top-level
 */
async function getOperationCount() {
    const code = `
# Conta operazioni top-level
operations = visum.Procedures.Operations

# Prova a contare quante operazioni top-level ci sono
count = 0
try:
    while True:
        op = operations.ItemByKey(count + 1)
        count += 1
except:
    pass

print(f"Operazioni top-level: {count}")
result = count
`;

    const response = await executeVisumPython(code, 'Count operations');
    
    // Estrai il numero dalle righe di output
    if (response.output) {
        const match = response.output.match(/Operazioni top-level: (\d+)/);
        if (match) {
            return parseInt(match[1]);
        }
    }
    
    return 0;
}

/**
 * Mostra solo le ultime N operazioni
 */
async function listLastOperations(n = 5) {
    const code = `
# Mostra ultime operazioni
operations = visum.Procedures.Operations

# Conta operazioni
count = 0
try:
    while True:
        op = operations.ItemByKey(count + 1)
        count += 1
except:
    pass

print(f"\\nUltime {min(${n}, count)} di {count} operazioni:")

# Mostra le ultime N
start = max(1, count - ${n} + 1)
for i in range(start, count + 1):
    op = operations.ItemByKey(i)
    op_type = op.AttValue("OPERATIONTYPE")
    
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
`;

    await executeVisumPython(code, 'List last operations');
}

/**
 * Crea operazione Initialize Assignment
 */
async function createInitializeAssignment(position = 1) {
    const code = `
# Crea Initialize Assignment
print("\\nCreazione Initialize Assignment alla posizione ${position}...")

operation = visum.Procedures.Operations.AddOperation(${position})
operation.SetAttValue("OPERATIONTYPE", 9)  # OperationTypeInitAssignment

print(f"OK - Initialize Assignment creato alla posizione ${position}")
`;

    console.log('\n' + '═'.repeat(70));
    console.log(`📋 STEP 1: INITIALIZE ASSIGNMENT (posizione ${position})`);
    console.log('═'.repeat(70));
    
    await executeVisumPython(code);
}

/**
 * Crea operazione PrT Assignment
 */
async function createPrTAssignment(demandSegment = 'P', assignmentVariant = 'Equilibrium', position = 2) {
    const variantMap = {
        'Incremental': 1,
        'Equilibrium': 2,
        'Tribut': 5,
        'Stochastic': 6,
        'DynStochastic': 7,
        'DUE': 8,
        'LUCE': 9,
        'ICA': 10,
        'SBA': 11,
        'FrankWolfe': 12,
        'Bicycle': 13
    };
    
    const variantValue = variantMap[assignmentVariant] || 2;
    
    const code = `
# Crea PrT Assignment
print("\\nCreazione PrT Assignment alla posizione ${position}...")

# 1. Aggiungi operazione
operation = visum.Procedures.Operations.AddOperation(${position})
print(f"  [1] Operazione aggiunta alla posizione ${position}")

# 2. Imposta tipo = PrT Assignment (101)
operation.SetAttValue("OPERATIONTYPE", 101)
print(f"  [2] Tipo operazione impostato: 101 (PrT Assignment)")

# 3. Accedi parametri
assignment_params = operation.PrTAssignmentPara
print(f"  [3] Parametri assignment accessibili")

# 4. Imposta segmento domanda
assignment_params.SetAttValue("DSegSet", "${demandSegment}")
print(f"  [4] Segmento domanda impostato: ${demandSegment}")

# 5. Imposta variante
assignment_params.SetAttValue("PrTAssignmentVariant", ${variantValue})
print(f"  [5] Variante impostata: ${assignmentVariant} (${variantValue})")

# 6. Accedi parametri Equilibrium (se applicabile)
if ${variantValue} == 2:  # Equilibrium
    try:
        equilibrium_params = assignment_params.PrTEquilibriumAssignmentParameters
        print(f"  [6] Parametri Equilibrium accessibili")
    except Exception as e:
        print(f"  [!] Parametri Equilibrium non accessibili: {e}")

print(f"\\nOK - PrT Assignment creato con successo!")
`;

    console.log('\n' + '═'.repeat(70));
    console.log(`📋 STEP 2: PrT ASSIGNMENT (posizione ${position})`);
    console.log('═'.repeat(70));
    console.log(`   Demand Segment: ${demandSegment}`);
    console.log(`   Variant: ${assignmentVariant} (${variantValue})`);
    console.log('═'.repeat(70));
    
    await executeVisumPython(code);
}

/**
 * Esegue la sequenza di procedure
 */
async function executeProcedures() {
    const code = `
# Esegui sequenza procedure
print("\\nEsecuzione sequenza procedure...")
print("-" * 70)

try:
    visum.Procedures.Execute()
    print("\\nOK - ESECUZIONE COMPLETATA CON SUCCESSO!")
except Exception as e:
    print(f"\\nERRORE durante l'esecuzione: {e}")
    raise
`;

    console.log('\n' + '═'.repeat(70));
    console.log('⚙️  ESECUZIONE SEQUENZA PROCEDURE');
    console.log('═'.repeat(70));
    
    await executeVisumPython(code);
}

/**
 * Main
 */
async function main() {
    console.log('\n' + '═'.repeat(70));
    console.log('🚀 TEST CREAZIONE PrT ASSIGNMENT VIA TCP SERVER');
    console.log('═'.repeat(70));
    console.log(`\n🌐 Server TCP: ${VISUM_SERVER_HOST}:${VISUM_SERVER_PORT}`);
    
    try {
        // 1. Test semplice: crea operazione e accedi ai parametri
        console.log(`\n🧪 Test API PrT Assignment...`);
        await testPrTAssignmentAPI();
        
        // 5. Mostra nuova sequenza (solo le ultime operazioni)
        console.log('\n📋 Verifica operazioni aggiunte...');
        await listLastOperations(5);
        
        // 6. Esegui procedure (opzionale - commentato per sicurezza)
        // console.log('\n❓ Esecuzione procedure...');
        // await executeProcedures();
        
        console.log('\n' + '═'.repeat(70));
        console.log('✅ TEST COMPLETATO CON SUCCESSO!');
        console.log('═'.repeat(70));
        
    } catch (error) {
        console.error('\n' + '═'.repeat(70));
        console.error('❌ ERRORE DURANTE IL TEST');
        console.error('═'.repeat(70));
        console.error(error);
        process.exit(1);
    }
}

// Esegui
main();
