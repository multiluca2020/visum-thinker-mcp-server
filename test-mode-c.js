import net from 'net';

const pythonCode = `
import sys
import json

print("TEST SEMPLICE: Mode C", file=sys.stderr)

try:
    # Prendi mode C
    mode_c = visum.Net.Modes.ItemByKey("C")
    print(f"Mode C trovato", file=sys.stderr)
    
    # Controlla quanti TSys ha
    tsys_count = 0
    tsys_list = []
    try:
        tsys_collection = mode_c.TSystems
        tsys_count = len(tsys_collection)
        print(f"Mode C ha {tsys_count} TSystems", file=sys.stderr)
        
        for tsys in tsys_collection:
            code = tsys.AttValue("CODE")
            tsys_type = tsys.AttValue("TYPE")
            tsys_list.append({"code": code, "type": tsys_type})
            print(f"  - {code} (TYPE={tsys_type})", file=sys.stderr)
    except Exception as e:
        print(f"Errore TSystems: {e}", file=sys.stderr)
    
    # Conta segments mode C
    all_segs = visum.Net.DemandSegments.GetAll
    mode_c_segs = []
    for seg in all_segs:
        if seg.AttValue("MODE") == "C":
            mode_c_segs.append(seg.AttValue("CODE"))
    
    print(f"\\nMode C ha {len(mode_c_segs)} segments", file=sys.stderr)
    print(f"Primi 5: {mode_c_segs[:5]}", file=sys.stderr)
    
    # Verifica se i TSys di mode C sono PrT
    prt_tsys = [t for t in tsys_list if t["type"] == "PRT"]
    print(f"\\nTSys PrT in mode C: {len(prt_tsys)}", file=sys.stderr)
    for t in prt_tsys:
        print(f"  - {t['code']}", file=sys.stderr)
    
    result = {
        "status": "ok",
        "tsys_count": tsys_count,
        "tsys": tsys_list,
        "prt_tsys": prt_tsys,
        "segments_count": len(mode_c_segs),
        "segments": mode_c_segs,
        "dsegset": ",".join(mode_c_segs) if len(prt_tsys) > 0 else ""
    }
    
except Exception as e:
    print(f"ERRORE: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    result = {"status": "error", "error": str(e)}
`;

const client = new net.Socket();
let welcomeReceived = false;

console.log('🧪 TEST MODE C');
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
            description: 'Test mode C',
            code: pythonCode
        };
        client.write(JSON.stringify(request) + '\n');
    } else {
        if (response.success) {
            const res = response.result;
            if (res.status === 'ok') {
                console.log(`\n📊 MODE "C" ANALISI:`);
                console.log('='.repeat(60));
                console.log(`Transport Systems: ${res.tsys_count}`);
                res.tsys.forEach(t => console.log(`  - ${t.code} (TYPE=${t.type})`));
                
                console.log(`\nTSys PrT: ${res.prt_tsys.length}`);
                res.prt_tsys.forEach(t => console.log(`  - ${t.code}`));
                
                console.log(`\nDemand Segments: ${res.segments_count}`);
                console.log(`Primi 10: ${res.segments.slice(0, 10).join(', ')}`);
                
                if (res.dsegset) {
                    console.log('\n' + '='.repeat(60));
                    console.log('✅ DSEGSET (segments con TSys PrT):');
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
