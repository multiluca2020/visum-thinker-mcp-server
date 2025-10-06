import net from 'net';

const pythonCode = `
import sys

print("ELENCO DETTAGLIATO DEI 60 DEMAND SEGMENTS", file=sys.stderr)
print("=" * 80, file=sys.stderr)

segments_list = []

try:
    all_segments = visum.Net.DemandSegments.GetAll
    print(f"Totale: {len(all_segments)} demand segments\\n", file=sys.stderr)
    
    for i, seg in enumerate(all_segments, 1):
        code = seg.AttValue("CODE")
        name = seg.AttValue("NAME") if seg.AttValue("NAME") else ""
        
        # Prova tutti i possibili attributi
        attrs = {}
        for attr_name in ["TSYSCODE", "TSYS", "MODE", "MODECODE", "DEMANDTYPE", "CODE"]:
            try:
                val = seg.AttValue(attr_name)
                attrs[attr_name] = str(val) if val is not None else "N/A"
            except:
                pass
        
        segments_list.append({
            "code": code,
            "name": name,
            "attributes": attrs
        })
        
        print(f"{i:2}. {code:15} - {name:30} | {attrs}", file=sys.stderr)
        
except Exception as e:
    print(f"Errore: {e}", file=sys.stderr)

# Raggruppa per TSYSCODE se esiste
by_tsys = {}
for seg in segments_list:
    tsys = seg["attributes"].get("TSYSCODE", "N/A")
    if tsys not in by_tsys:
        by_tsys[tsys] = []
    by_tsys[tsys].append(seg["code"])

print(f"\\n{'=' * 80}", file=sys.stderr)
print("RIEPILOGO PER TSYSCODE:", file=sys.stderr)
for tsys_code, seg_codes in by_tsys.items():
    print(f"  {tsys_code}: {len(seg_codes)} segments - {seg_codes[:5]}", file=sys.stderr)

result = {
    "status": "ok",
    "segments": segments_list,
    "by_tsys": by_tsys,
    "total": len(segments_list)
}
`;

const client = new net.Socket();
let welcomeReceived = false;

console.log('📋 ELENCO DETTAGLIATO 60 DEMAND SEGMENTS');
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
            description: 'Elenco dettagliato 60 demand segments',
            code: pythonCode
        };
        client.write(JSON.stringify(request) + '\n');
    } else {
        if (response.success && response.result.status === 'ok') {
            const res = response.result;
            console.log(`\n✅ Trovati ${res.total} demand segments\n`);
            
            // Mostra primi 10
            res.segments.slice(0, 10).forEach((seg, i) => {
                console.log(`${i+1}. ${seg.code} - ${seg.name}`);
                console.log(`   Attributes: ${JSON.stringify(seg.attributes)}`);
            });
            
            if (res.total > 10) {
                console.log(`\n... e altri ${res.total - 10} segments`);
            }
            
            console.log('\n📊 RAGGRUPPAMENTO PER TSYSCODE:');
            for (const [tsysCode, segCodes] of Object.entries(res.by_tsys)) {
                console.log(`\n  TSys "${tsysCode}": ${segCodes.length} segments`);
                console.log(`    ${JSON.stringify(segCodes.slice(0, 10))}`);
                if (segCodes.length > 10) {
                    console.log(`    ... e altri ${segCodes.length - 10}`);
                }
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
