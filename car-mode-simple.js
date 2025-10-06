import net from 'net';

const pythonCode = `
import sys

print("TSys CAR: attributi MODE", file=sys.stderr)

try:
    tsys_car = visum.Net.TSystems.ItemByKey("CAR")
    
    print(f"TSys CAR:", file=sys.stderr)
    print(f"  CODE: {tsys_car.AttValue('CODE')}", file=sys.stderr)
    print(f"  TYPE: {tsys_car.AttValue('TYPE')}", file=sys.stderr)
    
    # Test tutti i possibili attributi MODE
    mode_attrs = ["MODE", "MODECODE", "MODENO", "MODEID"]
    
    car_mode = None
    for attr in mode_attrs:
        try:
            val = tsys_car.AttValue(attr)
            print(f"  {attr}: {val}", file=sys.stderr)
            if attr == "MODECODE" or attr == "MODE":
                car_mode = val
        except:
            print(f"  {attr}: non esiste", file=sys.stderr)
    
    # Se abbiamo trovato il mode, cerca i segments
    segments = []
    dsegset = ""
    
    if car_mode:
        print(f"\\nMode trovato: {car_mode}", file=sys.stderr)
        print(f"Ricerca segments MODE={car_mode}...\\n", file=sys.stderr)
        
        all_segs = visum.Net.DemandSegments.GetAll
        for seg in all_segs:
            if seg.AttValue("MODE") == car_mode:
                code = seg.AttValue("CODE")
                segments.append(code)
                print(f"  {code}", file=sys.stderr)
        
        dsegset = ",".join(segments)
        print(f"\\nTotale: {len(segments)} segments", file=sys.stderr)
    
    result = {
        "status": "ok",
        "car_mode": car_mode,
        "segments": segments,
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

console.log('🔍 TSys CAR -> Mode');
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
            description: 'TSys CAR mode',
            code: pythonCode
        };
        client.write(JSON.stringify(request) + '\n');
    } else {
        if (response.success) {
            const res = response.result;
            if (res.status === 'ok') {
                console.log(`\n✅ TSys CAR Mode: "${res.car_mode}"`);
                
                if (res.segments.length > 0) {
                    console.log(`\n📋 ${res.segments.length} segments:\n`);
                    res.segments.forEach((s, i) => console.log(`${(i+1).toString().padStart(2)}. ${s}`));
                    
                    console.log('\n' + '='.repeat(60));
                    console.log('📝 DSEGSET:');
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
