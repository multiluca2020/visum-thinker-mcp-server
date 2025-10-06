import net from 'net';

const pythonCode = `
# ============================================================================
# ANALISI COMPLETA: MODES PRT E DEMAND SEGMENTS ASSOCIATI
# ============================================================================
import sys

print("=" * 80, file=sys.stderr)
print("ANALISI COMPLETA STRUTTURA PRT", file=sys.stderr)
print("=" * 80, file=sys.stderr)

# STEP 1: Trova tutti i MODES di tipo PrT
print("\\nSTEP 1: ANALISI MODES DI TIPO PRT", file=sys.stderr)
print("-" * 80, file=sys.stderr)

prt_modes = []
try:
    modes_container = visum.Net.Modes
    all_modes = modes_container.GetAll
    
    print(f"Totale modes nel progetto: {len(all_modes)}", file=sys.stderr)
    
    for mode in all_modes:
        try:
            mode_code = mode.AttValue("CODE")
            mode_name = mode.AttValue("NAME") if mode.AttValue("NAME") else "(unnamed)"
            mode_type = mode.AttValue("MODETYPE") if mode.AttValue("MODETYPE") else "N/A"
            
            # Verifica se è PrT
            is_prt = False
            try:
                # Diversi modi per identificare PrT
                if mode_type == "PrT" or mode_type == "P" or mode_type == 1:
                    is_prt = True
                # Prova anche attributi alternativi
                transport_type = mode.AttValue("TRANSPORTTYPE") if mode.AttValue("TRANSPORTTYPE") else None
                if transport_type and "PrT" in str(transport_type):
                    is_prt = True
            except:
                pass
            
            mode_info = {
                "code": mode_code,
                "name": mode_name,
                "type": str(mode_type),
                "is_prt": is_prt
            }
            
            if is_prt:
                prt_modes.append(mode_info)
                print(f"  ✓ PrT Mode: {mode_code} | Name: {mode_name} | Type: {mode_type}", file=sys.stderr)
            else:
                print(f"    Mode: {mode_code} | Name: {mode_name} | Type: {mode_type} (NON PrT)", file=sys.stderr)
                
        except Exception as e:
            print(f"  Errore lettura mode: {e}", file=sys.stderr)
            
except Exception as e:
    print(f"Errore accesso modes: {e}", file=sys.stderr)
    # Fallback basato su conoscenza comune
    prt_modes = [{"code": "C", "name": "Car", "type": "PrT", "is_prt": True}]

print(f"\\nTotale PrT Modes trovati: {len(prt_modes)}", file=sys.stderr)

# STEP 2: Per ogni MODE PrT, trova i DEMAND SEGMENTS associati
print("\\n\\nSTEP 2: DEMAND SEGMENTS PER OGNI MODE PRT", file=sys.stderr)
print("-" * 80, file=sys.stderr)

mode_segments_map = {}

try:
    ds_container = visum.Net.DemandSegments
    all_segments = ds_container.GetAll
    
    print(f"Totale demand segments nel progetto: {len(all_segments)}", file=sys.stderr)
    print("", file=sys.stderr)
    
    for mode in prt_modes:
        mode_code = mode["code"]
        mode_segments_map[mode_code] = []
        
        print(f"Mode '{mode_code}' ({mode['name']}):", file=sys.stderr)
        
        for ds in all_segments:
            try:
                ds_code = ds.AttValue("CODE")
                ds_name = ds.AttValue("NAME") if ds.AttValue("NAME") else "(unnamed)"
                ds_mode = ds.AttValue("MODECODE") if ds.AttValue("MODECODE") else None
                ds_tsys = ds.AttValue("TSYSCODE") if ds.AttValue("TSYSCODE") else None
                
                # Verifica se questo segment appartiene a questo mode
                belongs_to_mode = False
                if ds_mode == mode_code or ds_tsys == mode_code:
                    belongs_to_mode = True
                
                if belongs_to_mode:
                    segment_info = {
                        "code": ds_code,
                        "name": ds_name,
                        "mode": str(ds_mode),
                        "tsys": str(ds_tsys)
                    }
                    mode_segments_map[mode_code].append(segment_info)
                    
                    print(f"  ✓ Segment: {ds_code} | Name: {ds_name} | Mode: {ds_mode} | TSys: {ds_tsys}", file=sys.stderr)
                    
            except Exception as e:
                print(f"  Errore lettura segment: {e}", file=sys.stderr)
        
        if len(mode_segments_map[mode_code]) == 0:
            print(f"  (nessun demand segment trovato per questo mode)", file=sys.stderr)
        print("", file=sys.stderr)
        
except Exception as e:
    print(f"Errore accesso demand segments: {e}", file=sys.stderr)

# STEP 3: Analisi Transport Systems
print("\\nSTEP 3: TRANSPORT SYSTEMS PRT", file=sys.stderr)
print("-" * 80, file=sys.stderr)

prt_tsystems = []
try:
    ts_container = visum.Net.TSystems
    all_ts = ts_container.GetAll
    
    print(f"Totale Transport Systems: {len(all_ts)}", file=sys.stderr)
    
    for ts in all_ts:
        try:
            ts_code = ts.AttValue("CODE")
            ts_name = ts.AttValue("NAME") if ts.AttValue("NAME") else "(unnamed)"
            ts_mode = ts.AttValue("MODECODE") if ts.AttValue("MODECODE") else None
            
            # Verifica se appartiene a un mode PrT
            is_prt_tsys = any(ts_mode == mode["code"] for mode in prt_modes)
            
            if is_prt_tsys:
                ts_info = {
                    "code": ts_code,
                    "name": ts_name,
                    "mode": str(ts_mode)
                }
                prt_tsystems.append(ts_info)
                print(f"  ✓ TSys: {ts_code} | Name: {ts_name} | Mode: {ts_mode}", file=sys.stderr)
                
        except Exception as e:
            print(f"  Errore lettura tsystem: {e}", file=sys.stderr)
            
except Exception as e:
    print(f"Errore accesso transport systems: {e}", file=sys.stderr)

print("\\n" + "=" * 80, file=sys.stderr)

# RISULTATO FINALE
result = {
    "status": "ok",
    "prt_modes": prt_modes,
    "mode_segments_map": mode_segments_map,
    "prt_tsystems": prt_tsystems,
    "summary": {
        "total_prt_modes": len(prt_modes),
        "total_segments_by_mode": {mode: len(segments) for mode, segments in mode_segments_map.items()},
        "total_prt_tsystems": len(prt_tsystems)
    }
}
`;

const client = new net.Socket();
let welcomeReceived = false;

console.log('🔍 ANALISI COMPLETA: PRT MODES E DEMAND SEGMENTS');
console.log('=' .repeat(80));

client.connect(7904, '::1', () => {
    console.log('✅ Connesso al server TCP sulla porta 7904\n');
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
            description: 'Analisi completa PrT modes e demand segments associati',
            code: pythonCode
        };
        console.log('📤 Invio richiesta analisi completa...\n');
        client.write(JSON.stringify(request) + '\n');
    } else {
        console.log('=' .repeat(80));
        console.log('📊 RISULTATO ANALISI COMPLETA\n');
        
        if (response.success) {
            const res = response.result;
            
            console.log(`✅ PRT MODES TROVATI: ${res.summary.total_prt_modes}\n`);
            
            res.prt_modes.forEach((mode, index) => {
                console.log(`${index + 1}. MODE: "${mode.code}" - ${mode.name}`);
                console.log(`   Type: ${mode.type}`);
                
                const segments = res.mode_segments_map[mode.code] || [];
                console.log(`   Demand Segments associati: ${segments.length}`);
                
                if (segments.length > 0) {
                    segments.forEach(seg => {
                        console.log(`     • "${seg.code}" - ${seg.name} (Mode: ${seg.mode}, TSys: ${seg.tsys})`);
                    });
                } else {
                    console.log(`     (nessun demand segment trovato)`);
                }
                console.log('');
            });
            
            if (res.prt_tsystems.length > 0) {
                console.log(`\n🚗 TRANSPORT SYSTEMS PRT: ${res.prt_tsystems.length}\n`);
                res.prt_tsystems.forEach((ts, index) => {
                    console.log(`${index + 1}. TSYS: "${ts.code}" - ${ts.name} (Mode: ${ts.mode})`);
                });
            }
            
            console.log('\n📋 RIEPILOGO PER CONFIGURAZIONE ASSIGNMENT:');
            console.log('-' .repeat(80));
            
            let allSegmentCodes = [];
            Object.values(res.mode_segments_map).forEach(segments => {
                segments.forEach(seg => allSegmentCodes.push(seg.code));
            });
            
            if (allSegmentCodes.length > 0) {
                console.log(`\n✅ Demand Segments PrT da includere nell'assignment:`);
                console.log(`   Codici: ${JSON.stringify(allSegmentCodes)}`);
                console.log(`   Formato Visum: "${allSegmentCodes.join(',')}"`);
            } else {
                console.log(`\n⚠️ ATTENZIONE: Nessun demand segment PrT trovato!`);
                console.log(`   Potrebbe essere necessario creare i demand segments prima dell'assignment.`);
            }
            
        } else {
            console.log('❌ ERRORE!\n');
            console.log(`Messaggio: ${response.error}`);
        }
        
        console.log(`\n⏱️ Tempo analisi: ${response.executionTimeMs}ms`);
        console.log('=' .repeat(80));
        
        client.destroy();
    }
});

client.on('close', () => {
    console.log('\n🔌 Connessione chiusa');
});

client.on('error', (err) => {
    console.error('❌ Errore:', err.message);
});
