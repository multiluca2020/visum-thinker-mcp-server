import net from 'net';

const pythonCode = `
# ============================================================================
# CREA PROCEDURA PRT ASSIGNMENT CON DEMAND SEGMENT "C" (Car)
# ============================================================================
import sys

print("=" * 60, file=sys.stderr)
print("CREAZIONE PROCEDURA PRT ASSIGNMENT - DEMAND SEGMENT: C", file=sys.stderr)
print("=" * 60, file=sys.stderr)

# FASE 1: CREA OPERAZIONE IN CODA
new_position = 21
operation = visum.Procedures.Operations.AddOperation(new_position, None)
operation.SetAttValue("OPERATIONTYPE", 101)  # PrT Assignment

print(f"FASE 1: Operazione creata in posizione {new_position}", file=sys.stderr)

# FASE 2: ACCEDI AI PARAMETRI
params = operation.PrTAssignmentParameters

print(f"FASE 2: Parametri PrT Assignment accessibili", file=sys.stderr)

# FASE 3: CONFIGURA DEMAND SEGMENT "C"
try:
    # Dalla documentazione: l'attributo corretto è DSEGSET (DSegSet)
    # Comma-separated list of demand segments
    params.SetAttValue("DSEGSET", "C")
    print(f"FASE 3: DSEGSET = 'C' impostato con successo!", file=sys.stderr)
    method_used = "DSEGSET"
    demand_segment_configured = True
    
except Exception as config_error:
    print(f"ERRORE configurazione demand segment: {config_error}", file=sys.stderr)
    demand_segment_configured = False
    method_used = "error"

# FASE 4: CONFIGURA PARAMETRI EQUILIBRIUM
equilibrium_configured = False
try:
    eq_params = operation.PrTEquilibriumAssignmentParameters
    
    # Configura parametri equilibrium
    eq_params.SetAttValue("NUMITER", 50)  # 50 iterazioni
    eq_params.SetAttValue("PRECISIONDEMAND", 0.01)  # Precisione 0.01
    
    print(f"FASE 4: Parametri Equilibrium configurati (50 iter, 0.01 prec)", file=sys.stderr)
    equilibrium_configured = True
    config_type = "Equilibrium Assignment"
    
except Exception as eq_error:
    print(f"FASE 4: Equilibrium params non disponibili: {eq_error}", file=sys.stderr)
    config_type = "Base PrT Assignment"

# FASE 5: VERIFICA FINALE
print(f"FASE 5: Verifica configurazione...", file=sys.stderr)

operation_type = operation.AttValue("OPERATIONTYPE")
print(f"Tipo operazione: {operation_type}", file=sys.stderr)

# Verifica che l'operazione esista
verification = None
try:
    created_op = visum.Procedures.Operations.ItemByKey(new_position)
    verification = {
        "exists": True,
        "type": created_op.AttValue("OPERATIONTYPE"),
        "params_accessible": True
    }
    print(f"Verifica: OK - operazione {new_position} tipo {verification['type']}", file=sys.stderr)
except Exception as e:
    verification = {
        "exists": False,
        "error": str(e)
    }
    print(f"Verifica: FALLITA - {e}", file=sys.stderr)

print("=" * 60, file=sys.stderr)

# RITORNA RISULTATO
result = {
    "status": "ok",
    "phase_1_creation": "completed",
    "phase_2_parameter_access": "completed",
    "phase_3_demand_segment": "completed" if demand_segment_configured else "failed",
    "phase_4_equilibrium_config": "completed" if equilibrium_configured else "skipped",
    "phase_5_verification": "completed",
    "position": new_position,
    "operation_type": operation_type,
    "config_type": config_type,
    "demand_segment": "C",
    "demand_segment_method": method_used,
    "demand_segment_configured": demand_segment_configured,
    "equilibrium_configured": equilibrium_configured,
    "params_accessible": True,
    "params_type": str(type(params)),
    "verification": verification,
    "ready_to_execute": demand_segment_configured,
    "note": "Procedura PrT Assignment creata con demand segment 'C' (Car). Pronta per esecuzione." if demand_segment_configured else "Procedura creata ma demand segment non configurato correttamente."
}
`;

const client = new net.Socket();
let welcomeReceived = false;

console.log('🚀 CREAZIONE PROCEDURA PRT ASSIGNMENT - DEMAND SEGMENT: C');
console.log('=' .repeat(60));

client.connect(7901, '::1', () => {
    console.log('✅ Connesso al server TCP sulla porta 7901\n');
});

client.on('data', (data) => {
    const response = JSON.parse(data.toString());
    
    if (!welcomeReceived && response.type === 'project_welcome') {
        console.log('📊 Welcome message ricevuto');
        console.log(`   Progetto: ${response.projectName}\n`);
        welcomeReceived = true;
        
        const request = {
            type: 'query',
            requestId: Date.now(),
            description: 'Crea procedura PrT Assignment con demand segment C',
            code: pythonCode
        };
        console.log('📤 Creazione procedura in corso...\n');
        client.write(JSON.stringify(request) + '\n');
    } else {
        console.log('=' .repeat(60));
        console.log('📊 RISULTATO CREAZIONE\n');
        
        if (response.success) {
            const res = response.result;
            
            console.log('✅ PROCEDURA CREATA CON SUCCESSO!\n');
            
            console.log('📋 FASI COMPLETATE:');
            console.log(`   ✅ FASE 1 (Creazione operazione): ${res.phase_1_creation}`);
            console.log(`   ✅ FASE 2 (Accesso parametri): ${res.phase_2_parameter_access}`);
            console.log(`   ${res.phase_3_demand_segment === 'completed' ? '✅' : '❌'} FASE 3 (Config demand segment): ${res.phase_3_demand_segment}`);
            console.log(`   ${res.phase_4_equilibrium_config === 'completed' ? '✅' : '⏭️'} FASE 4 (Config equilibrium): ${res.phase_4_equilibrium_config}`);
            console.log(`   ✅ FASE 5 (Verifica): ${res.phase_5_verification}`);
            
            console.log('\n📊 CONFIGURAZIONE:');
            console.log(`   📍 Posizione: ${res.position} (in coda)`);
            console.log(`   🔧 Tipo operazione: ${res.operation_type} (${res.config_type})`);
            console.log(`   🎯 Demand Segment: "${res.demand_segment}" (${res.demand_segment_configured ? 'CONFIGURATO' : 'NON CONFIGURATO'})`);
            if (res.demand_segment_configured) {
                console.log(`   📝 Metodo usato: ${res.demand_segment_method}`);
            }
            console.log(`   ⚙️ Equilibrium: ${res.equilibrium_configured ? '50 iter, 0.01 prec' : 'Non configurato'}`);
            
            if (res.verification) {
                console.log('\n🔍 VERIFICA:');
                console.log(`   Operazione esiste: ${res.verification.exists ? '✅ SI' : '❌ NO'}`);
                if (res.verification.exists) {
                    console.log(`   Tipo verificato: ${res.verification.type}`);
                }
            }
            
            console.log('\n💡 STATO:');
            if (res.ready_to_execute) {
                console.log('   🟢 PRONTA PER ESECUZIONE');
                console.log('   Per eseguire: visum.Procedures.Execute()');
            } else {
                console.log('   🟡 CREATA MA RICHIEDE CONFIGURAZIONE MANUALE');
                console.log('   Verifica i demand segments in Visum');
            }
            
            console.log(`\n📝 NOTA: ${res.note}`);
            
        } else {
            console.log('❌ ERRORE!\n');
            console.log(`Messaggio: ${response.error}`);
        }
        
        console.log(`\n⏱️ Tempo esecuzione: ${response.executionTimeMs}ms`);
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
