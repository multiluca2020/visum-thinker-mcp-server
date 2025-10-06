import net from 'net';

const pythonCode = `
import sys

print("=" * 80, file=sys.stderr)
print("ANALISI COMPLETA: MODES -> TRANSPORT SYSTEMS -> DEMAND SEGMENTS", file=sys.stderr)
print("=" * 80, file=sys.stderr)

# STEP 1: MODES
print("\\nSTEP 1: MODES", file=sys.stderr)
print("-" * 80, file=sys.stderr)

modes_list = []
try:
    all_modes = visum.Net.Modes.GetAll
    for mode in all_modes:
        code = mode.AttValue("CODE")
        name = mode.AttValue("NAME") if mode.AttValue("NAME") else ""
        modes_list.append({"code": code, "name": name})
        print(f"  Mode: {code} - {name}", file=sys.stderr)
except Exception as e:
    print(f"Errore modes: {e}", file=sys.stderr)

# STEP 2: TRANSPORT SYSTEMS con il loro MODE
print("\\nSTEP 2: TRANSPORT SYSTEMS (con MODE)", file=sys.stderr)
print("-" * 80, file=sys.stderr)

tsys_list = []
tsys_by_mode = {}

try:
    all_tsys = visum.Net.TSystems.GetAll
    
    for tsys in all_tsys:
        code = tsys.AttValue("CODE")
        name = tsys.AttValue("NAME") if tsys.AttValue("NAME") else ""
        
        # Trova il MODE associato
        mode_code = "N/A"
        try:
            mode_code = tsys.AttValue("MODE")
        except:
            try:
                mode_code = tsys.AttValue("MODECODE")
            except:
                try:
                    # Prova con l'oggetto Mode diretto
                    mode_obj = tsys.AttValue("Mode")
                    if mode_obj:
                        mode_code = mode_obj.AttValue("CODE")
                except:
                    pass
        
        tsys_info = {
            "code": code,
            "name": name,
            "mode": str(mode_code)
        }
        tsys_list.append(tsys_info)
        
        # Raggruppa per mode
        if mode_code not in tsys_by_mode:
            tsys_by_mode[mode_code] = []
        tsys_by_mode[mode_code].append(tsys_info)
        
        print(f"  TSys: {code} - {name} (Mode: {mode_code})", file=sys.stderr)
        
except Exception as e:
    print(f"Errore tsys: {e}", file=sys.stderr)

# STEP 3: DEMAND SEGMENTS per ogni TRANSPORT SYSTEM
print("\\nSTEP 3: DEMAND SEGMENTS per TRANSPORT SYSTEM", file=sys.stderr)
print("-" * 80, file=sys.stderr)

segments_by_tsys = {}
all_segments = []

try:
    # Prova diversi metodi per accedere ai demand segments
    ds_container = None
    
    try:
        ds_container = visum.Net.DemandSegments
        print(f"Usando visum.Net.DemandSegments", file=sys.stderr)
    except:
        try:
            ds_container = visum.Net.DemandSegment
            print(f"Usando visum.Net.DemandSegment", file=sys.stderr)
        except:
            print(f"ATTENZIONE: Nessun container DemandSegments trovato", file=sys.stderr)
    
    if ds_container:
        segments = ds_container.GetAll
        print(f"Totale demand segments trovati: {len(segments)}", file=sys.stderr)
        
        for seg in segments:
            code = seg.AttValue("CODE")
            name = seg.AttValue("NAME") if seg.AttValue("NAME") else ""
            
            # Trova il TSys associato
            tsys_code = "N/A"
            try:
                tsys_code = seg.AttValue("TSYSCODE")
            except:
                try:
                    tsys_code = seg.AttValue("TSYS")
                except:
                    pass
            
            seg_info = {
                "code": code,
                "name": name,
                "tsys": str(tsys_code)
            }
            all_segments.append(seg_info)
            
            # Raggruppa per tsys
            if tsys_code not in segments_by_tsys:
                segments_by_tsys[tsys_code] = []
            segments_by_tsys[tsys_code].append(seg_info)
            
            print(f"  Segment: {code} - {name} (TSys: {tsys_code})", file=sys.stderr)
    else:
        print(f"Nessun demand segment disponibile", file=sys.stderr)
        
except Exception as e:
    print(f"Errore segments: {e}", file=sys.stderr)

print("\\n" + "=" * 80, file=sys.stderr)
print("RIEPILOGO", file=sys.stderr)
print("=" * 80, file=sys.stderr)

for mode_code, tsys_list_for_mode in tsys_by_mode.items():
    print(f"\\nMode '{mode_code}':", file=sys.stderr)
    for tsys in tsys_list_for_mode:
        segs = segments_by_tsys.get(tsys["code"], [])
        print(f"  TSys '{tsys['code']}' ({tsys['name']}): {len(segs)} segments", file=sys.stderr)
        for seg in segs[:3]:
            print(f"    - {seg['code']}: {seg['name']}", file=sys.stderr)
        if len(segs) > 3:
            print(f"    ... e altri {len(segs)-3}", file=sys.stderr)

result = {
    "status": "ok",
    "modes": modes_list,
    "tsystems": tsys_list,
    "tsys_by_mode": tsys_by_mode,
    "segments": all_segments,
    "segments_by_tsys": segments_by_tsys,
    "summary": {
        "total_modes": len(modes_list),
        "total_tsys": len(tsys_list),
        "total_segments": len(all_segments)
    }
}
`;

const client = new net.Socket();
let welcomeReceived = false;

console.log('🔍 ANALISI COMPLETA: MODES -> TSYS -> SEGMENTS');
console.log('='.repeat(80));

client.connect(7905, '::1', () => {
    console.log('✅ Connesso sulla porta 7905\n');
});

client.on('data', (data) => {
    const response = JSON.parse(data.toString());
    
    if (!welcomeReceived && response.type === 'project_welcome') {
        welcomeReceived = true;
        
        const request = {
            type: 'query',
            requestId: Date.now(),
            description: 'Analisi completa Modes-TSys-Segments',
            code: pythonCode
        };
        client.write(JSON.stringify(request) + '\n');
    } else {
        console.log('\n📊 RISULTATO:\n');
        
        if (response.success && response.result.status === 'ok') {
            const res = response.result;
            
            console.log(`✅ Modes: ${res.summary.total_modes}`);
            console.log(`✅ Transport Systems: ${res.summary.total_tsys}`);
            console.log(`✅ Demand Segments: ${res.summary.total_segments}\n`);
            
            console.log('📋 STRUTTURA GERARCHICA:\n');
            
            for (const [modeCode, tsysList] of Object.entries(res.tsys_by_mode)) {
                console.log(`MODE "${modeCode}":`);
                
                for (const tsys of tsysList) {
                    const segments = res.segments_by_tsys[tsys.code] || [];
                    console.log(`  ├─ TSys "${tsys.code}" (${tsys.name})`);
                    console.log(`  │  └─ ${segments.length} demand segments`);
                    
                    segments.forEach((seg, i) => {
                        const prefix = i === segments.length - 1 ? '     └─' : '     ├─';
                        console.log(`  │  ${prefix} ${seg.code} - ${seg.name}`);
                    });
                }
                console.log('');
            }
            
            // Identifica segments PrT (mode C o simili)
            const modeCTsys = res.tsys_by_mode['C'] || [];
            if (modeCTsys.length > 0) {
                console.log('\n🎯 MODE "C" (probabilmente PrT):');
                let allCSegments = [];
                modeCTsys.forEach(tsys => {
                    const segs = res.segments_by_tsys[tsys.code] || [];
                    allCSegments.push(...segs.map(s => s.code));
                });
                if (allCSegments.length > 0) {
                    console.log(`   Segments totali: ${allCSegments.length}`);
                    console.log(`   Codici: ${JSON.stringify(allCSegments)}`);
                    console.log(`   DSEGSET per assignment: "${allCSegments.join(',')}"`);
                }
            }
            
        } else {
            console.log('❌ Errore:', response.error || response.result?.error);
        }
        
        console.log(`\n⏱️ Tempo analisi: ${response.executionTimeMs}ms`);
        console.log('='.repeat(80));
        client.destroy();
    }
});

client.on('close', () => console.log('\n🔌 Chiuso'));
client.on('error', (err) => console.error('❌', err.message));
