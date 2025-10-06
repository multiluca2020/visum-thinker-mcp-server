import net from 'net';

const pythonCode = `
import sys

print("DEBUG: Modes, TSys e Segments", file=sys.stderr)
print("=" * 60, file=sys.stderr)

try:
    # STEP 1: Modes e loro TSys
    all_modes = visum.Net.Modes.GetAll
    print(f"\\n{len(all_modes)} Modes:\\n", file=sys.stderr)
    
    modes_info = {}
    
    for mode in all_modes:
        code = mode.AttValue("CODE")
        print(f"Mode '{code}':", file=sys.stderr)
        
        # Conta TSys
        tsys_list = []
        try:
            tsys_coll = mode.TSystems
            print(f"  TSystems count: {len(tsys_coll)}", file=sys.stderr)
            for tsys in tsys_coll:
                tc = tsys.AttValue("CODE")
                tt = tsys.AttValue("TYPE")
                tsys_list.append({"code": tc, "type": tt})
                print(f"    - {tc} (TYPE={tt})", file=sys.stderr)
        except Exception as e:
            print(f"  Errore TSystems: {e}", file=sys.stderr)
        
        modes_info[code] = {"tsys": tsys_list, "segments": []}
    
    # STEP 2: Segments per mode
    print(f"\\n{'=' * 60}", file=sys.stderr)
    print("Segments per Mode:\\n", file=sys.stderr)
    
    all_segs = visum.Net.DemandSegments.GetAll
    
    for seg in all_segs:
        sc = seg.AttValue("CODE")
        sm = seg.AttValue("MODE")
        
        if sm in modes_info:
            modes_info[sm]["segments"].append(sc)
    
    for mode_code, info in modes_info.items():
        print(f"Mode '{mode_code}': {len(info['segments'])} segments", file=sys.stderr)
    
    # STEP 3: Filtra modes con TSys PrT
    print(f"\\n{'=' * 60}", file=sys.stderr)
    print("Modes con TSys TYPE=PRT:\\n", file=sys.stderr)
    
    prt_segs = []
    for mode_code, info in modes_info.items():
        has_prt = any(t["type"] == "PRT" for t in info["tsys"])
        if has_prt:
            print(f"Mode '{mode_code}': {len(info['segments'])} segs", file=sys.stderr)
            prt_segs.extend(info["segments"])
    
    dsegset = ",".join(prt_segs)
    
    result = {
        "status": "ok",
        "modes": modes_info,
        "prt_segments": prt_segs,
        "dsegset": dsegset
    }
    
except Exception as e:
    print(f"ERRORE: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    result = {"status": "error", "error": str(e)}
`;

const client = new net.Socket();
let welcomeReceived = false;

console.log('🐛 DEBUG MODE-TSYS-SEGMENTS');
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
            description: 'Debug modes',
            code: pythonCode
        };
        client.write(JSON.stringify(request) + '\n');
    } else {
        if (response.success) {
            const res = response.result;
            if (res.status === 'ok') {
                console.log(`\n✅ Trovati ${res.prt_segments.length} segments PrT`);
                
                if (res.prt_segments.length > 0) {
                    console.log('\n📝 DSEGSET:');
                    console.log('='.repeat(60));
                    console.log(res.dsegset);
                }
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
