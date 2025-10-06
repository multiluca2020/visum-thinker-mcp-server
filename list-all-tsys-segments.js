import net from 'net';

const pythonCode = `
import sys

print("=" * 80, file=sys.stderr)
print("ELENCO COMPLETO TRANSPORT SYSTEMS E DEMAND SEGMENTS", file=sys.stderr)
print("=" * 80, file=sys.stderr)

# STEP 1: Elenca TUTTI i Transport Systems (solo CODE e NAME)
print("\\nTRANSPORT SYSTEMS:", file=sys.stderr)
tsys_list = []

try:
    all_tsys = visum.Net.TSystems.GetAll
    
    for tsys in all_tsys:
        code = tsys.AttValue("CODE")
        name = tsys.AttValue("NAME") if tsys.AttValue("NAME") else ""
        
        tsys_list.append({"code": code, "name": name})
        print(f"  {code} - {name}", file=sys.stderr)
        
except Exception as e:
    print(f"Errore: {e}", file=sys.stderr)

# STEP 2: Elenca TUTTI i Demand Segments con il loro TSYSCODE
print("\\nDEMAND SEGMENTS:", file=sys.stderr)
segments_list = []
segments_by_tsys = {}

try:
    all_segments = visum.Net.DemandSegments.GetAll
    
    for seg in all_segments:
        code = seg.AttValue("CODE")
        name = seg.AttValue("NAME") if seg.AttValue("NAME") else ""
        tsys = seg.AttValue("TSYSCODE") if seg.AttValue("TSYSCODE") else "N/A"
        
        segments_list.append({
            "code": code,
            "name": name,
            "tsys": tsys
        })
        
        # Raggruppa per TSys
        if tsys not in segments_by_tsys:
            segments_by_tsys[tsys] = []
        segments_by_tsys[tsys].append({"code": code, "name": name})
        
        print(f"  {code} - {name} (TSys: {tsys})", file=sys.stderr)
        
except Exception as e:
    print(f"Errore: {e}", file=sys.stderr)

print("\\n" + "=" * 80, file=sys.stderr)
print("RIEPILOGO PER TSYS:", file=sys.stderr)
print("=" * 80, file=sys.stderr)

for tsys_code in sorted(segments_by_tsys.keys()):
    segs = segments_by_tsys[tsys_code]
    print(f"\\nTSys '{tsys_code}': {len(segs)} demand segments", file=sys.stderr)
    for seg in segs[:5]:  # Mostra max 5
        print(f"  - {seg['code']}: {seg['name']}", file=sys.stderr)
    if len(segs) > 5:
        print(f"  ... e altri {len(segs)-5}", file=sys.stderr)

result = {
    "status": "ok",
    "tsystems": tsys_list,
    "segments": segments_list,
    "segments_by_tsys": segments_by_tsys,
    "summary": {
        "total_tsys": len(tsys_list),
        "total_segments": len(segments_list)
    }
}
`;

const client = new net.Socket();
let welcomeReceived = false;

console.log('📋 ELENCO COMPLETO TSYS E DEMAND SEGMENTS');
console.log('='.repeat(60));

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
            description: 'Elenco completo TSys e Demand Segments',
            code: pythonCode
        };
        client.write(JSON.stringify(request) + '\n');
    } else {
        console.log('\n📊 RISULTATO:\n');
        
        if (response.success && response.result.status === 'ok') {
            const res = response.result;
            
            console.log(`✅ Transport Systems: ${res.summary.total_tsys}`);
            console.log(`✅ Demand Segments: ${res.summary.total_segments}\n`);
            
            console.log('📋 RIEPILOGO PER TRANSPORT SYSTEM:\n');
            
            for (const [tsysCode, segments] of Object.entries(res.segments_by_tsys)) {
                console.log(`TSys "${tsysCode}": ${segments.length} segments`);
                segments.forEach(seg => {
                    console.log(`  • ${seg.code} - ${seg.name}`);
                });
                console.log('');
            }
            
            // Identifica quale TSys è PrT (basandosi sul nome o codice "C")
            const segmentsC = res.segments_by_tsys['C'] || [];
            if (segmentsC.length > 0) {
                const codes = segmentsC.map(s => s.code);
                console.log('\n🎯 PER ASSIGNMENT CON TSYS "C" (Car/PrT):');
                console.log(`   Segments: ${JSON.stringify(codes)}`);
                console.log(`   DSEGSET: "${codes.join(',')}"`);
            }
            
        } else {
            console.log('❌ Errore:', response.error || response.result?.error);
        }
        
        console.log(`\n⏱️ Tempo: ${response.executionTimeMs}ms`);
        client.destroy();
    }
});

client.on('close', () => console.log('\n🔌 Chiuso'));
client.on('error', (err) => console.error('❌', err.message));
