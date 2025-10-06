import net from 'net';

const pythonCode = `
import sys

print("RICERCA TSys PrT E SEGMENTS", file=sys.stderr)
print("=" * 60, file=sys.stderr)

prt_tsys_codes = []
segments_by_tsys = {}

try:
    # STEP 1: Trova TSys di tipo PrT
    all_tsys = visum.Net.TSystems.GetAll
    print(f"\\nSTEP 1: Analisi {len(all_tsys)} TSystems\\n", file=sys.stderr)
    
    for tsys in all_tsys:
        code = tsys.AttValue("CODE")
        
        # Controlla attributi PrT
        is_prt = False
        try:
            if tsys.AttValue("ISPRT") == True:
                is_prt = True
        except:
            pass
        
        if is_prt:
            print(f"  PrT TSys trovato: {code}", file=sys.stderr)
            prt_tsys_codes.append(code)
            segments_by_tsys[code] = []
    
    print(f"\\nTrovati {len(prt_tsys_codes)} TSys PrT: {prt_tsys_codes}", file=sys.stderr)
    
    # STEP 2: Trova segments per ogni TSys PrT
    print(f"\\n{'=' * 60}", file=sys.stderr)
    print("STEP 2: Ricerca segments\\n", file=sys.stderr)
    
    all_segments = visum.Net.DemandSegments.GetAll
    
    for seg in all_segments:
        seg_code = seg.AttValue("CODE")
        
        # Prova ad accedere al TSys
        tsys_code = None
        try:
            tsys_obj = seg.TSys
            tsys_code = tsys_obj.AttValue("CODE")
        except:
            try:
                tsys_code = seg.AttValue("TSYSCODE")
                if not tsys_code or tsys_code == "N/A":
                    tsys_code = None
            except:
                pass
        
        if tsys_code and tsys_code in prt_tsys_codes:
            segments_by_tsys[tsys_code].append(seg_code)
            print(f"  {seg_code} -> {tsys_code}", file=sys.stderr)
    
    # STEP 3: Risultati
    print(f"\\n{'=' * 60}", file=sys.stderr)
    print("RISULTATI:\\n", file=sys.stderr)
    
    all_prt_segments = []
    for tsys_code in prt_tsys_codes:
        seg_list = segments_by_tsys[tsys_code]
        print(f"  {tsys_code}: {len(seg_list)} segments", file=sys.stderr)
        all_prt_segments.extend(seg_list)
    
    dsegset_value = ",".join(all_prt_segments) if all_prt_segments else ""
    
    print(f"\\nTOTALE: {len(all_prt_segments)} segments PrT", file=sys.stderr)
    
except Exception as e:
    print(f"ERRORE: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    prt_tsys_codes = []
    all_prt_segments = []
    dsegset_value = ""
    segments_by_tsys = {}

result = {
    "status": "ok",
    "prt_tsys": prt_tsys_codes,
    "segments_by_tsys": segments_by_tsys,
    "all_segments": all_prt_segments,
    "dsegset": dsegset_value,
    "total": len(all_prt_segments)
}
`;

const client = new net.Socket();
let welcomeReceived = false;

console.log('🔍 RICERCA TSys PrT E SEGMENTS');
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
            description: 'Trova TSys PrT',
            code: pythonCode
        };
        client.write(JSON.stringify(request) + '\n');
    } else {
        if (response.success && response.result.status === 'ok') {
            const res = response.result;
            
            console.log(`\n✅ TSys PrT trovati: ${res.prt_tsys.join(', ')}`);
            
            console.log('\n📋 SEGMENTS PER TSys:');
            for (const [tsys, segs] of Object.entries(res.segments_by_tsys)) {
                console.log(`\n  ${tsys}: ${segs.length} segments`);
                if (segs.length > 0 && segs.length <= 20) {
                    segs.forEach(s => console.log(`    - ${s}`));
                } else if (segs.length > 20) {
                    segs.slice(0, 10).forEach(s => console.log(`    - ${s}`));
                    console.log(`    ... e altri ${segs.length - 10}`);
                }
            }
            
            console.log(`\n${'='.repeat(60)}`);
            console.log(`✅ TOTALE: ${res.total} segments PrT`);
            
            if (res.total > 0) {
                console.log('\n📝 DSEGSET:');
                console.log(res.dsegset);
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
