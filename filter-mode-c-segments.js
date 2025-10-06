import net from 'net';

const pythonCode = `
import sys

print("FILTRAGGIO DEMAND SEGMENTS DEL MODO 'C' (PrT)", file=sys.stderr)
print("=" * 80, file=sys.stderr)

mode_c_segments = []

try:
    all_segments = visum.Net.DemandSegments.GetAll
    
    for seg in all_segments:
        code = seg.AttValue("CODE")
        mode = seg.AttValue("MODE")
        name = seg.AttValue("NAME") if seg.AttValue("NAME") else ""
        
        # Filtra solo modo "C"
        if mode == "C":
            mode_c_segments.append({
                "code": code,
                "name": name,
                "mode": mode
            })
    
    print(f"\\nTrovati {len(mode_c_segments)} segments del modo 'C':\\n", file=sys.stderr)
    
    for i, seg in enumerate(mode_c_segments, 1):
        print(f"{i:2}. {seg['code']:20} - {seg['name']}", file=sys.stderr)
    
    # Crea la stringa comma-separated per DSEGSET
    dsegset_value = ",".join([seg["code"] for seg in mode_c_segments])
    
    print(f"\\n{'=' * 80}", file=sys.stderr)
    print(f"DSEGSET VALUE (comma-separated):", file=sys.stderr)
    print(f"{dsegset_value}", file=sys.stderr)
    print(f"\\nTotale segments: {len(mode_c_segments)}", file=sys.stderr)
    
except Exception as e:
    print(f"Errore: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    mode_c_segments = []
    dsegset_value = ""

result = {
    "status": "ok",
    "segments": mode_c_segments,
    "dsegset": dsegset_value,
    "count": len(mode_c_segments)
}
`;

const client = new net.Socket();
let welcomeReceived = false;

console.log('🎯 FILTRAGGIO SEGMENTS DEL MODO "C"');
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
            description: 'Filtra segments modo C',
            code: pythonCode
        };
        client.write(JSON.stringify(request) + '\n');
    } else {
        if (response.success && response.result.status === 'ok') {
            const res = response.result;
            console.log(`\n✅ Trovati ${res.count} segments del modo 'C'\n`);
            
            res.segments.forEach((seg, i) => {
                console.log(`${i+1}. ${seg.code} - ${seg.name}`);
            });
            
            console.log('\n' + '='.repeat(60));
            console.log('📝 VALORE DSEGSET (comma-separated):');
            console.log('='.repeat(60));
            console.log(res.dsegset);
            console.log('\n💡 Usa questo valore per configurare DSEGSET nel PrT Assignment!');
        } else {
            console.log('❌', response.error || response.result?.error);
        }
        console.log(`\n⏱️ ${response.executionTimeMs}ms`);
        client.destroy();
    }
});

client.on('close', () => console.log('\n🔌 Chiuso'));
client.on('error', (err) => console.error('❌', err.message));
