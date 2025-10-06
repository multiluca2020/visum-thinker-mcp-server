import net from 'net';

const pythonCode = `
import sys

print("RICERCA TSys TYPE=PRT E LORO SEGMENTS", file=sys.stderr)
print("=" * 60, file=sys.stderr)

prt_tsys_codes = []
segments_by_tsys = {}

try:
    # STEP 1: Trova tutti i TSys con TYPE="PRT"
    all_tsys = visum.Net.TSystems.GetAll
    print(f"\\nSTEP 1: Analisi {len(all_tsys)} Transport Systems\\n", file=sys.stderr)
    
    for tsys in all_tsys:
        code = tsys.AttValue("CODE")
        try:
            tsys_type = tsys.AttValue("TYPE")
            print(f"  {code:10} TYPE={tsys_type}", file=sys.stderr)
            
            if tsys_type == "PRT":
                print(f"    --> PrT TSys!", file=sys.stderr)
                prt_tsys_codes.append(code)
                segments_by_tsys[code] = []
        except:
            print(f"  {code:10} TYPE=N/A", file=sys.stderr)
    
    print(f"\\n{'=' * 60}", file=sys.stderr)
    print(f"Trovati {len(prt_tsys_codes)} TSys PrT: {prt_tsys_codes}\\n", file=sys.stderr)
    
    # STEP 2: Trova segments per ogni TSys PrT
    print("STEP 2: Ricerca segments per TSys PrT\\n", file=sys.stderr)
    
    all_segments = visum.Net.DemandSegments.GetAll
    print(f"Totale demand segments: {len(all_segments)}\\n", file=sys.stderr)
    
    for seg in all_segments:
        seg_code = seg.AttValue("CODE")
        
        # Metodo 1: via proprietà .TSys
        tsys_code = None
        try:
            tsys_obj = seg.TSys
            if tsys_obj:
                tsys_code = tsys_obj.AttValue("CODE")
        except:
            pass
        
        # Metodo 2: via attributo TSYSCODE
        if not tsys_code:
            try:
                tsys_code = seg.AttValue("TSYSCODE")
                if not tsys_code or tsys_code == "N/A":
                    tsys_code = None
            except:
                pass
        
        # Se appartiene a un TSys PrT, aggiungilo
        if tsys_code and tsys_code in prt_tsys_codes:
            segments_by_tsys[tsys_code].append(seg_code)
            print(f"  ✓ {seg_code:25} -> {tsys_code}", file=sys.stderr)
    
    # STEP 3: Risultati e DSEGSET
    print(f"\\n{'=' * 60}", file=sys.stderr)
    print("RISULTATI:\\n", file=sys.stderr)
    
    all_prt_segments = []
    for tsys_code in prt_tsys_codes:
        seg_list = segments_by_tsys[tsys_code]
        print(f"  TSys {tsys_code}: {len(seg_list)} segments", file=sys.stderr)
        all_prt_segments.extend(seg_list)
    
    dsegset_value = ",".join(all_prt_segments)
    
    print(f"\\n{'=' * 60}", file=sys.stderr)
    print(f"TOTALE: {len(all_prt_segments)} segments PrT", file=sys.stderr)
    print(f"\\nDSEGSET:\\n{dsegset_value}", file=sys.stderr)
    
except Exception as e:
    print(f"\\nERRORE: {e}", file=sys.stderr)
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

console.log('🎯 RICERCA TSys PrT (TYPE="PRT") E SEGMENTS');
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
            description: 'Trova TSys PrT via TYPE',
            code: pythonCode
        };
        client.write(JSON.stringify(request) + '\n');
    } else {
        if (response.success && response.result.status === 'ok') {
            const res = response.result;
            
            console.log(`\n✅ TSys PrT trovati (${res.prt_tsys.length}): ${res.prt_tsys.join(', ')}`);
            
            console.log('\n📋 SEGMENTS PER TSys:');
            console.log('='.repeat(60));
            for (const [tsys, segs] of Object.entries(res.segments_by_tsys)) {
                console.log(`\n  ${tsys}: ${segs.length} segments`);
                if (segs.length > 0 && segs.length <= 15) {
                    segs.forEach(s => console.log(`    - ${s}`));
                } else if (segs.length > 15) {
                    segs.slice(0, 10).forEach(s => console.log(`    - ${s}`));
                    console.log(`    ... e altri ${segs.length - 10} segments`);
                }
            }
            
            console.log('\n' + '='.repeat(60));
            console.log(`✅ TOTALE: ${res.total} segments PrT`);
            
            if (res.total > 0) {
                console.log('\n📝 VALORE DSEGSET PER PrT ASSIGNMENT:');
                console.log('='.repeat(60));
                console.log(res.dsegset);
                console.log('\n💡 Usa questo valore per configurare la procedura!');
            } else {
                console.log('\n⚠️ Nessun segment trovato collegato ai TSys PrT');
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
