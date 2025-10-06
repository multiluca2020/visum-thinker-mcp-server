import net from 'net';

const pythonCode = `
import sys

print("TUTTI I DEMAND SEGMENTS PER MODI PRT", file=sys.stderr)
print("=" * 60, file=sys.stderr)

try:
    # STEP 1: Trova tutti i TSys di tipo PRT
    all_tsys = visum.Net.TSystems.GetAll
    
    prt_tsys = []
    
    print("\\nSTEP 1: TSys di tipo PRT\\n", file=sys.stderr)
    
    for tsys in all_tsys:
        code = tsys.AttValue("CODE")
        name = tsys.AttValue("NAME")
        tsys_type = tsys.AttValue("TYPE")
        
        if tsys_type == "PRT":
            prt_tsys.append({"code": code, "name": name})
            print(f"  TSys PRT: {code} ({name})", file=sys.stderr)
    
    print(f"\\nTrovati {len(prt_tsys)} TSys PRT", file=sys.stderr)
    
    # STEP 2: Trova i Modes corrispondenti
    print(f"\\n{'=' * 60}", file=sys.stderr)
    print("STEP 2: Cerca Modes per TSys PRT\\n", file=sys.stderr)
    
    all_modes = visum.Net.Modes.GetAll
    
    prt_mode_codes = []
    mode_mapping = {}
    
    for mode in all_modes:
        mode_code = mode.AttValue("CODE")
        mode_name = mode.AttValue("NAME")
        
        # Cerca se il nome del mode corrisponde al nome di un TSys PRT
        for tsys in prt_tsys:
            # Match per nome (es: "Car" -> "Car", "HGV" -> "HGV")
            if mode_name.upper() == tsys["name"].upper():
                prt_mode_codes.append(mode_code)
                mode_mapping[mode_code] = {
                    "mode_name": mode_name,
                    "tsys_code": tsys["code"],
                    "tsys_name": tsys["name"]
                }
                print(f"  Mode '{mode_code}' ({mode_name}) -> TSys {tsys['code']} ({tsys['name']})", file=sys.stderr)
                break
    
    # Se non trova match per nome, prova altri metodi
    if len(prt_mode_codes) == 0:
        print(f"\\n  Nessun match per nome, uso tutti i modes con CODE simile ai TSys", file=sys.stderr)
        # Fallback: usa pattern matching (C, H, M per CAR, HGV, MOTO)
        for tsys in prt_tsys:
            tsys_first_letter = tsys["code"][0]
            
            for mode in all_modes:
                mode_code = mode.AttValue("CODE")
                if mode_code.upper() == tsys_first_letter.upper():
                    if mode_code not in prt_mode_codes:
                        prt_mode_codes.append(mode_code)
                        mode_mapping[mode_code] = {
                            "mode_name": mode.AttValue("NAME"),
                            "tsys_code": tsys["code"],
                            "tsys_name": tsys["name"]
                        }
                        print(f"  Mode '{mode_code}' -> TSys {tsys['code']} (pattern match)", file=sys.stderr)
    
    print(f"\\nMode codes PRT: {prt_mode_codes}", file=sys.stderr)
    
    # STEP 3: Raccogli segments per ogni mode PRT
    print(f"\\n{'=' * 60}", file=sys.stderr)
    print("STEP 3: Demand segments per Mode PRT\\n", file=sys.stderr)
    
    all_segments = visum.Net.DemandSegments.GetAll
    
    segments_by_mode = {}
    all_prt_segments = []
    
    for seg in all_segments:
        seg_code = seg.AttValue("CODE")
        seg_mode = seg.AttValue("MODE")
        
        if seg_mode in prt_mode_codes:
            if seg_mode not in segments_by_mode:
                segments_by_mode[seg_mode] = []
            
            segments_by_mode[seg_mode].append(seg_code)
            all_prt_segments.append(seg_code)
    
    # Stampa riepilogo
    for mode_code in prt_mode_codes:
        segs = segments_by_mode.get(mode_code, [])
        print(f"Mode '{mode_code}': {len(segs)} segments", file=sys.stderr)
        for s in segs[:5]:
            print(f"  - {s}", file=sys.stderr)
        if len(segs) > 5:
            print(f"  ... e altri {len(segs) - 5}", file=sys.stderr)
        print(file=sys.stderr)
    
    # DSEGSET completo
    dsegset_value = ",".join(all_prt_segments)
    
    print(f"{'=' * 60}", file=sys.stderr)
    print(f"TOTALE: {len(all_prt_segments)} segments PRT", file=sys.stderr)
    
    result = {
        "status": "ok",
        "prt_tsys": prt_tsys,
        "prt_modes": prt_mode_codes,
        "mode_mapping": mode_mapping,
        "segments_by_mode": segments_by_mode,
        "all_segments": all_prt_segments,
        "dsegset": dsegset_value,
        "total": len(all_prt_segments)
    }
    
except Exception as e:
    print(f"\\nERRORE: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    result = {"status": "error", "error": str(e)}
`;

const client = new net.Socket();
let welcomeReceived = false;

console.log('🎯 TUTTI I SEGMENTS PER MODI PRT (C, H, ...)');
console.log('='.repeat(60));

client.connect(7905, '::1', () => {
    console.log('✅ Connesso\n');
});

client.on('data', (data) => {
    const response = JSON.parse(data.toString());
    
    if (!welcomeReceived && response.type === 'project_welcome') {
        welcomeReceived = true;
        const request = {
            type: 'query',
            requestId: Date.now(),
            description: 'All PRT segments',
            code: pythonCode
        };
        client.write(JSON.stringify(request) + '\n');
    } else {
        if (response.success) {
            const res = response.result;
            if (res.status === 'ok') {
                console.log('\n📊 TSys PRT:');
                res.prt_tsys.forEach(t => console.log(`  - ${t.code} (${t.name})`));
                
                console.log('\n🔗 MAPPING Mode → TSys:');
                console.log('='.repeat(60));
                for (const [modeCode, mapping] of Object.entries(res.mode_mapping)) {
                    console.log(`  Mode "${modeCode}" (${mapping.mode_name}) → TSys ${mapping.tsys_code} (${mapping.tsys_name})`);
                }
                
                console.log('\n📋 SEGMENTS PER MODE:');
                console.log('='.repeat(60));
                for (const [modeCode, segments] of Object.entries(res.segments_by_mode)) {
                    console.log(`\n${modeCode}: ${segments.length} segments`);
                    segments.slice(0, 10).forEach(s => console.log(`  - ${s}`));
                    if (segments.length > 10) {
                        console.log(`  ... e altri ${segments.length - 10}`);
                    }
                }
                
                console.log('\n' + '='.repeat(60));
                console.log(`✅ TOTALE: ${res.total} segments PRT`);
                
                console.log('\n📝 DSEGSET COMPLETO:');
                console.log('='.repeat(60));
                console.log(res.dsegset);
                
                console.log('\n💡 Usa questo per configurare PrT Assignment con TUTTI i modi PRT!');
            } else {
                console.log(`\n❌ ${res.error}`);
            }
        } else {
            console.log('❌', response.error);
        }
        console.log(`\n⏱️ ${response.executionTimeMs}ms`);
        client.destroy();
    }
});

client.on('close', () => console.log('\n🔌 Chiuso'));
client.on('error', (err) => console.error('❌', err.message));
