import net from 'net';

const pythonCode = `
import sys

print("ANALISI GERARCHIA: Modes -> TSys e Modes -> Segments", file=sys.stderr)
print("=" * 60, file=sys.stderr)

try:
    # STEP 1: Analizza Modes
    all_modes = visum.Net.Modes.GetAll
    print(f"\\nSTEP 1: {len(all_modes)} Modes nel progetto\\n", file=sys.stderr)
    
    modes_data = {}
    
    for mode in all_modes:
        mode_code = mode.AttValue("CODE")
        
        print(f"Mode: {mode_code}", file=sys.stderr)
        
        # Trova TSys per questo mode
        mode_tsys = []
        try:
            tsys_collection = mode.TSystems
            for tsys in tsys_collection:
                tsys_code = tsys.AttValue("CODE")
                tsys_type = tsys.AttValue("TYPE")
                mode_tsys.append({"code": tsys_code, "type": tsys_type})
                print(f"  -> TSys: {tsys_code} (TYPE={tsys_type})", file=sys.stderr)
        except Exception as e:
            print(f"  -> Errore TSys: {e}", file=sys.stderr)
        
        modes_data[mode_code] = {
            "name": "",
            "tsys": mode_tsys,
            "segments": []
        }
    
    # STEP 2: Associa segments ai modes
    print(f"\\n{'=' * 60}", file=sys.stderr)
    print("STEP 2: Segments per Mode\\n", file=sys.stderr)
    
    all_segments = visum.Net.DemandSegments.GetAll
    
    for seg in all_segments:
        seg_code = seg.AttValue("CODE")
        seg_mode = seg.AttValue("MODE")
        
        if seg_mode in modes_data:
            modes_data[seg_mode]["segments"].append(seg_code)
    
    # STEP 3: Identifica mode con TSys PrT
    print(f"{'=' * 60}", file=sys.stderr)
    print("STEP 3: Modes con TSys PrT\\n", file=sys.stderr)
    
    prt_segments = []
    
    for mode_code, mode_info in modes_data.items():
        # Controlla se ha TSys di tipo PRT
        has_prt = any(t["type"] == "PRT" for t in mode_info["tsys"])
        
        if has_prt:
            prt_tsys_codes = [t["code"] for t in mode_info["tsys"] if t["type"] == "PRT"]
            seg_count = len(mode_info["segments"])
            
            print(f"Mode '{mode_code}': {seg_count} segments", file=sys.stderr)
            print(f"  TSys PrT: {prt_tsys_codes}", file=sys.stderr)
            print(f"  Primi 5 segments: {mode_info['segments'][:5]}", file=sys.stderr)
            
            prt_segments.extend(mode_info["segments"])
    
    dsegset_value = ",".join(prt_segments)
    
    print(f"\\n{'=' * 60}", file=sys.stderr)
    print(f"TOTALE SEGMENTS PrT: {len(prt_segments)}", file=sys.stderr)
    
    result = {
        "status": "ok",
        "modes": modes_data,
        "prt_segments": prt_segments,
        "dsegset": dsegset_value,
        "total": len(prt_segments)
    }
    
except Exception as e:
    print(f"\\nERRORE: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    result = {
        "status": "error",
        "error": str(e)
    }
`;

const client = new net.Socket();
let welcomeReceived = false;

console.log('🔍 ANALISI MODE → TSys → SEGMENTS');
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
            description: 'Analizza Mode-TSys-Segments',
            code: pythonCode
        };
        client.write(JSON.stringify(request) + '\n');
    } else {
        if (response.success && response.result.status === 'ok') {
            const res = response.result;
            
            console.log('\n📊 MODES CON TSys PrT:');
            console.log('='.repeat(60));
            
            for (const [modeCode, modeInfo] of Object.entries(res.modes)) {
                const hasPrt = modeInfo.tsys.some(t => t.type === 'PRT');
                if (hasPrt) {
                    console.log(`\n✅ Mode "${modeCode}": ${modeInfo.segments.length} segments`);
                    const prtTsys = modeInfo.tsys.filter(t => t.type === 'PRT').map(t => t.code);
                    console.log(`   TSys PrT: ${prtTsys.join(', ')}`);
                    
                    if (modeInfo.segments.length <= 20) {
                        modeInfo.segments.forEach(s => console.log(`   - ${s}`));
                    } else {
                        modeInfo.segments.slice(0, 10).forEach(s => console.log(`   - ${s}`));
                        console.log(`   ... e altri ${modeInfo.segments.length - 10}`);
                    }
                }
            }
            
            console.log('\n' + '='.repeat(60));
            console.log(`✅ TOTALE: ${res.total} segments PrT`);
            
            if (res.total > 0) {
                console.log('\n📝 DSEGSET:');
                console.log('='.repeat(60));
                console.log(res.dsegset);
                console.log('\n💡 Questo è il valore da usare per configurare PrT Assignment!');
            }
        } else {
            console.log('❌', response.error || response.result?.error);
        }
        console.log(`\n⏱️ ${response.executionTimeMs}ms`);
        client.destroy();
    }
});

client.on('close', () => console.log('\n🔌 Chiuso'));
client.on('error', (err) => console.error('❌', err.message));
