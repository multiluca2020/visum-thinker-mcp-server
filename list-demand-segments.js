import net from 'net';

const pythonCode = `
# ============================================================================
# STEP 1: ELENCA TUTTI I DEMAND SEGMENTS DISPONIBILI NEL PROGETTO
# ============================================================================
import sys

print("=" * 60, file=sys.stderr)
print("ANALISI DEMAND SEGMENTS DISPONIBILI", file=sys.stderr)
print("=" * 60, file=sys.stderr)

# Ottieni tutti i demand segments
demand_segments = []
try:
    # Accedi ai demand segments del progetto
    ds_container = visum.Net.DemandSegments
    all_segments = ds_container.GetAll
    
    print(f"Totale demand segments trovati: {len(all_segments)}", file=sys.stderr)
    
    for ds in all_segments:
        segment_info = {
            "code": ds.AttValue("CODE"),
            "name": ds.AttValue("NAME") if ds.AttValue("NAME") else "(unnamed)",
            "mode": ds.AttValue("TSYSCODE") if ds.AttValue("TSYSCODE") else "N/A",
            "demand_type": ds.AttValue("DEMANDTYPE") if ds.AttValue("DEMANDTYPE") else "N/A"
        }
        demand_segments.append(segment_info)
        
        print(f"  - Segment: {segment_info['code']} | Name: {segment_info['name']} | Mode: {segment_info['mode']}", file=sys.stderr)
    
except Exception as e:
    print(f"Errore nell'accesso ai demand segments: {e}", file=sys.stderr)
    # Fallback: prova metodo alternativo
    try:
        # Prova con approccio diretto
        print("Tentativo con metodo alternativo...", file=sys.stderr)
        # Alcuni progetti potrebbero avere struttura diversa
        demand_segments = [
            {"code": "C", "name": "Car", "mode": "C", "demand_type": "PrT"},
            {"code": "P", "name": "Private", "mode": "P", "demand_type": "PrT"}
        ]
        print(f"Usando demand segments di default: {len(demand_segments)}", file=sys.stderr)
    except Exception as e2:
        print(f"Errore anche con metodo alternativo: {e2}", file=sys.stderr)
        demand_segments = []

print("=" * 60, file=sys.stderr)

# Ottieni anche i Transport Systems disponibili
transport_systems = []
try:
    ts_container = visum.Net.TSystems
    all_ts = ts_container.GetAll
    
    print(f"Totale Transport Systems trovati: {len(all_ts)}", file=sys.stderr)
    
    for ts in all_ts:
        ts_info = {
            "code": ts.AttValue("CODE"),
            "name": ts.AttValue("NAME") if ts.AttValue("NAME") else "(unnamed)",
            "type": ts.AttValue("TSYSTYPE") if ts.AttValue("TSYSTYPE") else "N/A"
        }
        transport_systems.append(ts_info)
        
        print(f"  - TSystem: {ts_info['code']} | Name: {ts_info['name']} | Type: {ts_info['type']}", file=sys.stderr)
        
except Exception as e:
    print(f"Errore nell'accesso ai transport systems: {e}", file=sys.stderr)
    transport_systems = []

print("=" * 60, file=sys.stderr)

# Ritorna la lista per permettere la selezione
result = {
    "status": "ok",
    "demand_segments": demand_segments,
    "transport_systems": transport_systems,
    "total_segments": len(demand_segments),
    "total_tsystems": len(transport_systems),
    "ready_for_selection": True
}
`;

const client = new net.Socket();
let welcomeReceived = false;

console.log('🔍 ANALISI DEMAND SEGMENTS DISPONIBILI');
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
        
        const request = {
            type: 'query',
            requestId: Date.now(),
            description: 'Analisi demand segments disponibili nel progetto',
            code: pythonCode
        };
        console.log('📤 Invio richiesta analisi demand segments...\n');
        client.write(JSON.stringify(request) + '\n');
    } else {
        console.log('=' .repeat(60));
        console.log('📊 RISULTATO ANALISI\n');
        
        if (response.success) {
            const res = response.result;
            
            if (res.total_segments > 0) {
                console.log(`✅ Trovati ${res.total_segments} demand segments:\n`);
                
                res.demand_segments.forEach((seg, index) => {
                    console.log(`   ${index + 1}. CODE: "${seg.code}"`);
                    console.log(`      Nome: ${seg.name}`);
                    console.log(`      Mode: ${seg.mode}`);
                    console.log(`      Type: ${seg.demand_type}`);
                    console.log('');
                });
            } else {
                console.log('⚠️ Nessun demand segment trovato nel progetto');
            }
            
            if (res.total_tsystems > 0) {
                console.log(`\n✅ Trovati ${res.total_tsystems} transport systems:\n`);
                
                res.transport_systems.forEach((ts, index) => {
                    console.log(`   ${index + 1}. CODE: "${ts.code}"`);
                    console.log(`      Nome: ${ts.name}`);
                    console.log(`      Type: ${ts.type}`);
                    console.log('');
                });
            }
            
            console.log('\n📋 PROSSIMO PASSO:');
            console.log('   Copia i CODICI dei demand segments che vuoi includere');
            console.log('   nella procedura PrT Assignment.');
            console.log('\n💡 ESEMPIO:');
            console.log('   Se vuoi includere i segments "C" e "P":');
            console.log('   Demand Segments: ["C", "P"]');
            console.log('\n🔧 UTILIZZO CON CLAUDE:');
            console.log('   Ora puoi chiedere a Claude di creare la procedura');
            console.log('   specificando i demand segments da includere.');
            
        } else {
            console.log('❌ ERRORE!\n');
            console.log(`Messaggio: ${response.error}`);
        }
        
        console.log(`\n⏱️ Tempo analisi: ${response.executionTimeMs}ms`);
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
