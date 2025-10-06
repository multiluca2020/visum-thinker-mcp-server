import net from 'net';

const pythonCode = `
import sys

print("SOLUZIONE FINALE: Segments MODE=C per PrT", file=sys.stderr)
print("=" * 60, file=sys.stderr)

try:
    all_segments = visum.Net.DemandSegments.GetAll
    
    mode_c_segments = []
    
    for seg in all_segments:
        code = seg.AttValue("CODE")
        mode = seg.AttValue("MODE")
        
        if mode == "C":
            mode_c_segments.append(code)
            print(f"  {code}", file=sys.stderr)
    
    dsegset_value = ",".join(mode_c_segments)
    
    print(f"\\n{'=' * 60}", file=sys.stderr)
    print(f"TOTALE: {len(mode_c_segments)} segments MODE=C", file=sys.stderr)
    print(f"\\nDSEGSET:\\n{dsegset_value}", file=sys.stderr)
    
    result = {
        "status": "ok",
        "segments": mode_c_segments,
        "dsegset": dsegset_value,
        "count": len(mode_c_segments)
    }
    
except Exception as e:
    print(f"ERRORE: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    result = {"status": "error", "error": str(e)}
`;

const client = new net.Socket();
let welcomeReceived = false;

console.log('✅ SOLUZIONE: SEGMENTS MODE="C" PER PrT ASSIGNMENT');
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
            description: 'Segments MODE=C',
            code: pythonCode
        };
        client.write(JSON.stringify(request) + '\n');
    } else {
        if (response.success) {
            const res = response.result;
            if (res.status === 'ok') {
                console.log(`\n✅ ${res.count} segments MODE="C":\n`);
                res.segments.forEach((s, i) => console.log(`${(i+1).toString().padStart(2)}. ${s}`));
                
                console.log('\n' + '='.repeat(60));
                console.log('📝 DSEGSET PER PrT ASSIGNMENT:');
                console.log('='.repeat(60));
                console.log(res.dsegset);
                console.log('\n💡 Usa questo valore per configurare la procedura!');
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
