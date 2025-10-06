import net from 'net';

const pythonCode = `
# ============================================================================
# CREA PROCEDURA PRT ASSIGNMENT COMPLETA IN CODA A TUTTE LE PROCEDURE
# ============================================================================

# 1. AGGIUNGI DOPO LA POSIZIONE 21 (IN CODA)
import sys
# AddOperation(pos) aggiunge PRIMA della posizione specificata
# Per aggiungere in coda dopo la 21, usiamo posizione 21 che inserisce DOPO la 20
# Ma vogliamo dopo la 21, quindi... forse AddOperation aggiunge IN quella posizione?
# Proviamo con il secondo parametro (gruppo) = None esplicito
new_position = 21

print(f"Aggiunta operazione dopo posizione {new_position}", file=sys.stderr)

# 2. CREA NUOVA OPERAZIONE - AddOperation(position, group)
# Dalla documentazione: AddOperation aggiunge un'operazione
# Se position = 22 e ci sono 21 ops, dovrebbe aggiungere in coda
# Ma l'errore dice "valid 1 to 21" - forse il range è inclusivo?
# Proviamo con position 21 + group None
operation = visum.Procedures.Operations.AddOperation(21, None)
operation.SetAttValue("OPERATIONTYPE", 101)  # PrT Assignment

print(f"Operazione creata in posizione {new_position} (tipo 101)", file=sys.stderr)

# 3. ACCEDI AI PARAMETRI PRT ASSIGNMENT (proprieta corretta!)
params = operation.PrTAssignmentParameters

print(f"Parametri PrT Assignment accessibili!", file=sys.stderr)

# 4. CONFIGURA PARAMETRI DI BASE
# Non configuriamo VRCODE e TSYSSET perche potrebbero non esistere in questo progetto
# Useremo solo i parametri equilibrium

# Configura tipo di assignment
# OperationTypeAssignmentPrT = 101 include vari sotto-tipi
# Per Equilibrium assignment, accedi ai parametri specifici
try:
    equilibrium_params = operation.PrTEquilibriumAssignmentParameters
    
    # Parametri equilibrium
    equilibrium_params.SetAttValue("NUMITER", 50)  # Numero iterazioni
    equilibrium_params.SetAttValue("PRECISIONDEMAND", 0.01)  # Precisione
    
    print(f"Parametri Equilibrium configurati (50 iter, prec 0.01)", file=sys.stderr)
    config_type = "Equilibrium Assignment"
except:
    print(f"Equilibrium params non disponibili, uso config base", file=sys.stderr)
    config_type = "Base PrT Assignment"

# 5. VERIFICA CONFIGURAZIONE
operation_type = operation.AttValue("OPERATIONTYPE")
operation_name = "PrT Assignment (auto-created)"

print(f"Operazione configurata: {operation_name}", file=sys.stderr)

# 6. ESEGUI LA PROCEDURA
print(f"Esecuzione procedura PrT Assignment...", file=sys.stderr)

try:
    # Esegui l'intera sequenza di procedure
    visum.Procedures.Execute()
    
    execution_result = "success"
    print(f"Procedura eseguita con successo!", file=sys.stderr)
except Exception as exec_error:
    execution_result = f"error: {str(exec_error)}"
    print(f"Errore esecuzione: {exec_error}", file=sys.stderr)

# 7. RITORNA RISULTATO COMPLETO
result = {
    "status": "ok",
    "created": True,
    "position": new_position,
    "operation_type": operation_type,
    "operation_name": operation_name,
    "config_type": config_type,
    "execution": execution_result,
    "params_accessible": True,
    "params_type": str(type(params))
}
`;

const client = new net.Socket();
let welcomeReceived = false;

console.log('🚀 CREAZIONE PROCEDURA PRT ASSIGNMENT COMPLETA');
console.log('=' .repeat(60));

client.connect(7901, '::1', () => {
    console.log('✅ Connesso al server TCP sulla porta 7901\n');
});

client.on('data', (data) => {
    const response = JSON.parse(data.toString());
    
    if (!welcomeReceived && response.type === 'project_welcome') {
        console.log('📊 Welcome message ricevuto');
        console.log(`   Progetto: ${response.projectName}`);
        console.log(`   Nodi: ${response.network.nodes}, Links: ${response.network.links}\n`);
        welcomeReceived = true;
        
        // Invia comando Python
        const request = {
            type: 'query',
            requestId: Date.now(),
            description: 'Crea e configura procedura PrT Assignment completa',
            code: pythonCode
        };
        console.log('📤 Invio comando per creare procedura PrT Assignment...\n');
        client.write(JSON.stringify(request) + '\n');
    } else {
        console.log('=' .repeat(60));
        console.log('📊 RISULTATO OPERAZIONE\n');
        
        if (response.success) {
            const res = response.result;
            console.log('✅ SUCCESSO!\n');
            console.log(`📍 Posizione: ${res.position}`);
            console.log(`🔧 Tipo operazione: ${res.operation_type} (${res.config_type})`);
            console.log(`📝 Nome: ${res.operation_name}`);
            console.log(`⚙️ Parametri accessibili: ${res.params_accessible ? '✅ SI' : '❌ NO'}`);
            console.log(`🚀 Esecuzione: ${res.execution === 'success' ? '✅ COMPLETATA' : '⚠️ ' + res.execution}`);
            console.log(`\n📋 Tipo parametri: ${res.params_type}`);
            
            console.log('\n🎉 PROCEDURA PRT ASSIGNMENT CREATA E CONFIGURATA!');
        } else {
            console.log('❌ ERRORE!\n');
            console.log(`Messaggio: ${response.error}`);
        }
        
        console.log(`\n⏱️ Tempo esecuzione: ${response.executionTimeMs}ms`);
        console.log(`⏱️ Tempo risposta: ${response.responseTimeMs}ms`);
        console.log('=' .repeat(60));
        
        client.destroy();
    }
});

client.on('close', () => {
    console.log('\n🔌 Connessione chiusa');
});

client.on('error', (err) => {
    console.error('❌ Errore:', err.message);
});
