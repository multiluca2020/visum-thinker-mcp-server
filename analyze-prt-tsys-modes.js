import net from 'net';

const pythonCode = `
import sys

print("ANALISI TSys TYPE=PRT E LORO MODES", file=sys.stderr)
print("=" * 60, file=sys.stderr)

try:
    # STEP 1: Trova tutti i TSys di tipo PRT
    all_tsys = visum.Net.TSystems.GetAll
    
    prt_tsys_data = []
    
    print("\\nSTEP 1: TSys di tipo PRT\\n", file=sys.stderr)
    
    for tsys in all_tsys:
        code = tsys.AttValue("CODE")
        tsys_type = tsys.AttValue("TYPE")
        
        if tsys_type == "PRT":
            print(f"TSys PRT trovato: {code}", file=sys.stderr)
            
            # Cerca il Mode associato
            mode_code = None
            
            # Prova diversi attributi
            for attr in ["MODECODE", "MODE"]:
                try:
                    val = tsys.AttValue(attr)
                    if val and val != "N/A":
                        mode_code = val
                        print(f"  {attr}: {val}", file=sys.stderr)
                        break
                except:
                    pass
            
            prt_tsys_data.append({
                "tsys_code": code,
                "mode_code": mode_code
            })
    
    print(f"\\n{'=' * 60}", file=sys.stderr)
    print(f"Trovati {len(prt_tsys_data)} TSys PRT\\n", file=sys.stderr)
    
    # STEP 2: Per ogni Mode trovato, raccogli i segments
    print("STEP 2: Segments per Mode\\n", file=sys.stderr)
    
    all_segments = visum.Net.DemandSegments.GetAll
    
    segments_by_mode = {}
    
    for seg in all_segments:
        seg_code = seg.AttValue("CODE")
        seg_mode = seg.AttValue("MODE")
        
        if seg_mode not in segments_by_mode:
            segments_by_mode[seg_mode] = []
        
        segments_by_mode[seg_mode].append(seg_code)
    
    # STEP 3: Combina i risultati
    print(f"{'=' * 60}", file=sys.stderr)
    print("STEP 3: Risultati finali\\n", file=sys.stderr)
    
    all_prt_segments = []
    results = []
    
    for tsys_info in prt_tsys_data:
        tsys_code = tsys_info["tsys_code"]
        mode_code = tsys_info["mode_code"]
        
        if mode_code and mode_code in segments_by_mode:
            segs = segments_by_mode[mode_code]
            print(f"TSys {tsys_code} (Mode {mode_code}): {len(segs)} segments", file=sys.stderr)
            
            results.append({
                "tsys": tsys_code,
                "mode": mode_code,
                "segments": segs,
                "count": len(segs)
            })
            
            all_prt_segments.extend(segs)
        else:
            print(f"TSys {tsys_code}: Mode non trovato o nessun segment", file=sys.stderr)
            results.append({
                "tsys": tsys_code,
                "mode": mode_code,
                "segments": [],
                "count": 0
            })
    
    # Rimuovi duplicati
    all_prt_segments = list(set(all_prt_segments))
    dsegset_value = ",".join(sorted(all_prt_segments))
    
    print(f"\\n{'=' * 60}", file=sys.stderr)
    print(f"TOTALE SEGMENTS PrT (unici): {len(all_prt_segments)}", file=sys.stderr)
    
    result = {
        "status": "ok",
        "prt_tsys": results,
        "all_segments": sorted(all_prt_segments),
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

console.log('🎯 ANALISI TSys PRT → Mode → Segments');
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
            description: 'TSys PRT modes',
            code: pythonCode
        };
        client.write(JSON.stringify(request) + '\n');
    } else {
        if (response.success) {
            const res = response.result;
            if (res.status === 'ok') {
                console.log('\n📊 TSys PRT E LORO MODES:');
                console.log('='.repeat(60));
                
                res.prt_tsys.forEach(item => {
                    console.log(`\n🚗 TSys: ${item.tsys}`);
                    console.log(`   Mode: ${item.mode || 'N/A'}`);
                    console.log(`   Segments: ${item.count}`);
                    
                    if (item.count > 0 && item.count <= 15) {
                        item.segments.forEach(s => console.log(`     - ${s}`));
                    } else if (item.count > 15) {
                        item.segments.slice(0, 10).forEach(s => console.log(`     - ${s}`));
                        console.log(`     ... e altri ${item.count - 10}`);
                    }
                });
                
                console.log('\n' + '='.repeat(60));
                console.log(`✅ TOTALE SEGMENTS PrT (unici): ${res.total}`);
                
                if (res.total > 0) {
                    console.log('\n📝 DSEGSET PER PrT ASSIGNMENT:');
                    console.log('='.repeat(60));
                    console.log(res.dsegset);
                    console.log('\n💡 Usa questo valore per configurare la procedura!');
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
