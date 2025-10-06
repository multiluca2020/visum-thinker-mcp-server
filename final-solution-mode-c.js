import net from 'net';

const pythonCode = `
import sys

print("SOLUZIONE: Segments MODE=C per PrT Assignment", file=sys.stderr)
print("=" * 60, file=sys.stderr)

try:
    # Raccogli tutti i segments con MODE="C"
    all_segments = visum.Net.DemandSegments.GetAll
    
    mode_c_segments = []
    
    print("\\nSegments MODE=C:\\n", file=sys.stderr)
    
    for seg in all_segments:
        seg_code = seg.AttValue("CODE")
        seg_mode = seg.AttValue("MODE")
        
        if seg_mode == "C":
            mode_c_segments.append(seg_code)
            print(f"  {seg_code}", file=sys.stderr)
    
    # Crea DSEGSET
    dsegset_value = ",".join(mode_c_segments)
    
    print(f"\\n{'=' * 60}", file=sys.stderr)
    print(f"TOTALE: {len(mode_c_segments)} segments MODE=C", file=sys.stderr)
    print(f"\\nDSEGSET (comma-separated):", file=sys.stderr)
    print(f"{dsegset_value}", file=sys.stderr)
    
    result = {
        "status": "ok",
        "mode": "C",
        "segments": mode_c_segments,
        "dsegset": dsegset_value,
        "count": len(mode_c_segments)
    }
    
except Exception as e:
    print(f"\\nERRORE: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    result = {"status": "error", "error": str(e)}
`;

const client = new net.Socket();
let welcomeReceived = false;

console.log('✅ SOLUZIONE FINALE');
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
            description: 'Final solution MODE C',
            code: pythonCode
        };
        client.write(JSON.stringify(request) + '\n');
    } else {
        if (response.success) {
            const res = response.result;
            if (res.status === 'ok') {
                console.log(`\n✅ TROVATI ${res.count} SEGMENTS MODE="${res.mode}":\n`);
                
                res.segments.forEach((s, i) => {
                    console.log(`${(i+1).toString().padStart(2)}. ${s}`);
                });
                
                console.log('\n' + '='.repeat(60));
                console.log('📝 VALORE DSEGSET PER PrT ASSIGNMENT:');
                console.log('='.repeat(60));
                console.log(res.dsegset);
                
                console.log('\n' + '='.repeat(60));
                console.log('💡 PROSSIMO PASSO:');
                console.log('='.repeat(60));
                console.log('Configurare la procedura PrT Assignment con questo DSEGSET');
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
