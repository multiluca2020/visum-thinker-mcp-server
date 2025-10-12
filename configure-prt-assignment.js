/**
 * 🚗 CONFIGURAZIONE PrT ASSIGNMENT CON DSEGSET
 * 
 * Questo script configura una procedura PrT Assignment esistente
 * con i demand segments scelti dall'utente
 */

import net from 'net';

const PORT = 7909;

// DSEGSET con tutti i segments PRT (C + H)
const DSEGSET_ALL = "C_CORRETTA_AM,C_CORRETTA_IP1,C_CORRETTA_IP2,C_CORRETTA_IP3,C_CORRETTA_PM,C_CORRETTA_S,C_INIZIALE_AM,C_INIZIALE_IP1,C_INIZIALE_IP2,C_INIZIALE_IP3,C_INIZIALE_PM,C_INIZIALE_S,C_ITERAZIONE_AM,C_ITERAZIONE_IP1,C_ITERAZIONE_IP2,C_ITERAZIONE_IP3,C_ITERAZIONE_PM,C_ITERAZIONE_S,C_NESTED_AM,C_NESTED_IP1,C_NESTED_IP2,C_NESTED_IP3,C_NESTED_PM,C_NESTED_S,H_CORRETTA_AM,H_CORRETTA_IP1,H_CORRETTA_IP2,H_CORRETTA_IP3,H_CORRETTA_PM,H_CORRETTA_S,H_INIZIALE_AM,H_INIZIALE_IP1,H_INIZIALE_IP2,H_INIZIALE_IP3,H_INIZIALE_PM,H_INIZIALE_S";

const pythonCode = `
import sys

print("=" * 70, file=sys.stderr)
print("  CREAZIONE E CONFIGURAZIONE PrT ASSIGNMENT", file=sys.stderr)
print("=" * 70, file=sys.stderr)

try:
    # STEP 1: Verifica se esiste già una procedura PrT
    print("\\n[STEP 1] Verifica procedura esistente...\\n", file=sys.stderr)
    
    procedures = visum.Procedures.GetAll
    prt_procedure = None
    prt_position = None
    
    for proc in procedures:
        proc_type = proc.AttValue("PROCTYPE")
        if proc_type == 101:  # 101 = PrT Assignment
            prt_position = proc.AttValue("POS")
            prt_procedure = proc
            print(f"  ✓ Trovata procedura PrT alla posizione {prt_position}", file=sys.stderr)
            break
    
    # STEP 2: Crea nuova procedura se non esiste
    if not prt_procedure:
        print("  ℹ️  Nessuna procedura PrT trovata, ne creo una nuova...", file=sys.stderr)
        
        new_proc = visum.Procedures.AddProcedure(101)  # 101 = PrT Assignment
        prt_position = new_proc.AttValue("POS")
        prt_procedure = new_proc
        
        print(f"  ✓ Procedura PrT creata alla posizione {prt_position}", file=sys.stderr)
    
    # STEP 3: Accedi ai parametri PrT
    print(f"\\n{'=' * 70}", file=sys.stderr)
    print("[STEP 2] Configurazione parametri PrT Assignment...", file=sys.stderr)
    
    operation = prt_procedure.Operations.ItemByKey(1)
    prt_params = operation.PrTAssignmentParameters
    
    print("  ✓ Accesso a PrTAssignmentParameters riuscito", file=sys.stderr)
    
    # STEP 4: Configura DSEGSET
    print(f"\\n[STEP 3] Configurazione DSEGSET...\\n", file=sys.stderr)
    
    dsegset = "${DSEGSET_ALL}"
    segment_count = len(dsegset.split(","))
    
    print(f"  Segments da configurare: {segment_count}", file=sys.stderr)
    print(f"  Primi 5: {','.join(dsegset.split(',')[:5])}...", file=sys.stderr)
    
    try:
        prt_params.SetAttValue("DSEGSET", dsegset)
        print("  ✓ DSEGSET configurato con successo!", file=sys.stderr)
    except Exception as e:
        print(f"  ⚠️  Errore DSEGSET: {e}", file=sys.stderr)
        print(f"  Provo metodo alternativo...", file=sys.stderr)
        
        # Metodo alternativo: via attributo diretto
        try:
            operation.SetAttValue("DSEGSET", dsegset)
            print("  ✓ DSEGSET configurato (metodo alternativo)!", file=sys.stderr)
        except Exception as e2:
            print(f"  ❌ Errore anche con metodo alternativo: {e2}", file=sys.stderr)
    
    # STEP 5: Verifica configurazione
    print(f"\\n{'=' * 70}", file=sys.stderr)
    print("[STEP 4] Verifica configurazione finale...", file=sys.stderr)
    
    try:
        current_dsegset = prt_params.AttValue("DSEGSET")
        current_count = len(current_dsegset.split(",")) if current_dsegset else 0
        
        print(f"\\n  DSEGSET attuale: {current_count} segments", file=sys.stderr)
        if current_count > 0:
            print(f"  Primi 5: {','.join(current_dsegset.split(',')[:5])}...", file=sys.stderr)
        
        success = (current_count == segment_count)
        
        if success:
            print(f"\\n  ✅ CONFIGURAZIONE COMPLETATA!", file=sys.stderr)
        else:
            print(f"\\n  ⚠️  Configurazione parziale: {current_count}/{segment_count}", file=sys.stderr)
        
    except Exception as e:
        print(f"  ⚠️  Impossibile verificare: {e}", file=sys.stderr)
        success = False
    
    print(f"{'=' * 70}", file=sys.stderr)
    
    result = {
        "status": "ok",
        "procedure_position": prt_position,
        "segments_configured": segment_count,
        "success": success
    }
    
except Exception as e:
    print(f"\\n❌ ERRORE: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    result = {
        "status": "error",
        "error": str(e)
    }
`;

const client = new net.Socket();
let welcomeReceived = false;

console.log('\n🚗 CONFIGURAZIONE PrT ASSIGNMENT');
console.log('='.repeat(70));
console.log(`📍 Porta: ${PORT}`);
console.log(`📦 Segments da configurare: 36 (Mode C + H)`);
console.log('');

client.connect(PORT, '::1', () => {
    console.log('✅ Connesso al server Visum\n');
});

client.on('data', (data) => {
    const response = JSON.parse(data.toString());
    
    if (!welcomeReceived && response.type === 'project_welcome') {
        welcomeReceived = true;
        console.log('📥 Progetto pronto, invio configurazione...\\n');
        
        const request = {
            type: 'query',
            requestId: Date.now(),
            description: 'Configure PrT Assignment',
            code: pythonCode
        };
        client.write(JSON.stringify(request) + '\\n');
    } else {
        if (response.success) {
            const res = response.result;
            
            if (res.status === 'ok') {
                console.log('\\n✅ PROCEDURA CONFIGURATA CON SUCCESSO!');
                console.log('='.repeat(70));
                console.log(`📍 Posizione procedura: ${res.procedure_position}`);
                console.log(`📦 Segments configurati: ${res.segments_configured}`);
                console.log(`✔️  Stato: ${res.success ? 'Completato' : 'Parziale'}`);
                
                if (res.success) {
                    console.log('\n💡 La procedura PrT Assignment è pronta per l\'esecuzione!');
                }
            } else {
                console.log(`\\n❌ Errore: ${res.error}`);
            }
        } else {
            console.log(`\\n❌ Errore di esecuzione: ${response.error}`);
        }
        
        console.log(`\\n⏱️  Tempo: ${response.executionTimeMs}ms`);
        client.destroy();
    }
});

client.on('close', () => {
    console.log('\\n🔌 Connessione chiusa');
});

client.on('error', (err) => {
    console.error(`\\n❌ Errore: ${err.message}`);
});
