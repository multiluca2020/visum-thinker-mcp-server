import net from 'net';

const pythonCode = `
import sys

print("ANALISI TSys CAR E SEGMENTS", file=sys.stderr)
print("=" * 60, file=sys.stderr)

try:
    # Cerca TSys CAR
    tsys_car = visum.Net.TSystems.ItemByKey("CAR")
    print(f"\\nTSys CAR trovato!", file=sys.stderr)
    
    # Stampa tutti gli attributi disponibili
    print(f"\\nAttributi TSys CAR:", file=sys.stderr)
    try:
        print(f"  CODE: {tsys_car.AttValue('CODE')}", file=sys.stderr)
    except: pass
    
    try:
        print(f"  ISPRT: {tsys_car.AttValue('ISPRT')}", file=sys.stderr)
    except Exception as e:
        print(f"  ISPRT: non disponibile ({e})", file=sys.stderr)
    
    # Ora cerca segments collegati a CAR
    print(f"\\n{'=' * 60}", file=sys.stderr)
    print("Ricerca segments con TSys=CAR:\\n", file=sys.stderr)
    
    car_segments = []
    all_segments = visum.Net.DemandSegments.GetAll
    
    for seg in all_segments:
        seg_code = seg.AttValue("CODE")
        
        # Metodo 1: via proprietà TSys
        try:
            tsys_obj = seg.TSys
            if tsys_obj:
                tsys_code = tsys_obj.AttValue("CODE")
                if tsys_code == "CAR":
                    car_segments.append(seg_code)
                    print(f"  ✓ {seg_code}", file=sys.stderr)
        except Exception as e:
            # Metodo 2: via TSYSCODE attribute
            try:
                tsys_code = seg.AttValue("TSYSCODE")
                if tsys_code == "CAR":
                    car_segments.append(seg_code)
                    print(f"  ✓ {seg_code} (via TSYSCODE)", file=sys.stderr)
            except:
                pass
    
    dsegset = ",".join(car_segments)
    
    print(f"\\n{'=' * 60}", file=sys.stderr)
    print(f"TOTALE: {len(car_segments)} segments per TSys CAR", file=sys.stderr)
    
    result = {
        "status": "ok",
        "tsys": "CAR",
        "segments": car_segments,
        "dsegset": dsegset,
        "count": len(car_segments)
    }
    
except Exception as e:
    print(f"ERRORE: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    result = {
        "status": "error",
        "error": str(e),
        "segments": [],
        "dsegset": "",
        "count": 0
    }
`;

const client = new net.Socket();
let welcomeReceived = false;

console.log('🚗 ANALISI TSys CAR');
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
            description: 'Analizza TSys CAR',
            code: pythonCode
        };
        client.write(JSON.stringify(request) + '\n');
    } else {
        if (response.success) {
            const res = response.result;
            
            if (res.status === 'ok') {
                console.log(`\n✅ Trovati ${res.count} segments per TSys CAR`);
                
                if (res.count > 0) {
                    console.log('\n📋 SEGMENTS:');
                    res.segments.forEach((seg, i) => {
                        console.log(`  ${i+1}. ${seg}`);
                    });
                    
                    console.log('\n' + '='.repeat(60));
                    console.log('📝 DSEGSET per PrT Assignment:');
                    console.log('='.repeat(60));
                    console.log(res.dsegset);
                } else {
                    console.log('\n⚠️ Nessun segment trovato per TSys CAR');
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
