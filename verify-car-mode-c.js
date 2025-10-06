import net from 'net';

const pythonCode = `
import sys

print("ANALISI RELAZIONE: TSys CAR <-> Mode C", file=sys.stderr)
print("=" * 60, file=sys.stderr)

try:
    # STEP 1: Prendi TSys CAR
    tsys_car = visum.Net.TSystems.ItemByKey("CAR")
    print("\\nTSys CAR trovato", file=sys.stderr)
    print(f"  CODE: {tsys_car.AttValue('CODE')}", file=sys.stderr)
    print(f"  TYPE: {tsys_car.AttValue('TYPE')}", file=sys.stderr)
    
    # STEP 2: Cerca il Mode associato a CAR
    car_mode = None
    car_mode_code = None
    
    # Metodo 1: via proprietà Mode
    try:
        car_mode = tsys_car.Mode
        if car_mode:
            car_mode_code = car_mode.AttValue("CODE")
            print(f"  MODE (via .Mode): {car_mode_code}", file=sys.stderr)
    except Exception as e:
        print(f"  MODE (via .Mode): errore - {e}", file=sys.stderr)
    
    # Metodo 2: via attributo MODECODE
    if not car_mode_code:
        try:
            car_mode_code = tsys_car.AttValue("MODECODE")
            print(f"  MODE (via MODECODE): {car_mode_code}", file=sys.stderr)
        except Exception as e:
            print(f"  MODE (via MODECODE): errore - {e}", file=sys.stderr)
    
    # Metodo 3: via attributo MODE
    if not car_mode_code:
        try:
            car_mode_code = tsys_car.AttValue("MODE")
            print(f"  MODE (via MODE): {car_mode_code}", file=sys.stderr)
        except Exception as e:
            print(f"  MODE (via MODE): errore - {e}", file=sys.stderr)
    
    # STEP 3: Verifica inversa - Mode C ha TSys CAR?
    print(f"\\n{'=' * 60}", file=sys.stderr)
    print("Verifica inversa: Mode C -> TSys", file=sys.stderr)
    
    mode_c = visum.Net.Modes.ItemByKey("C")
    mode_c_tsys = []
    
    try:
        tsys_collection = mode_c.TSystems
        print(f"\\nMode C.TSystems.Count: {len(tsys_collection)}", file=sys.stderr)
        
        for tsys in tsys_collection:
            code = tsys.AttValue("CODE")
            mode_c_tsys.append(code)
            print(f"  - {code}", file=sys.stderr)
    except Exception as e:
        print(f"Errore: {e}", file=sys.stderr)
    
    # STEP 4: Se il link esiste, trova i segments
    print(f"\\n{'=' * 60}", file=sys.stderr)
    
    if car_mode_code == "C":
        print(f"✓ CONFERMATO: TSys CAR appartiene a Mode C!", file=sys.stderr)
        print(f"\\nRicerca segments per Mode C:", file=sys.stderr)
        
        all_segments = visum.Net.DemandSegments.GetAll
        mode_c_segments = []
        
        for seg in all_segments:
            if seg.AttValue("MODE") == "C":
                code = seg.AttValue("CODE")
                mode_c_segments.append(code)
                print(f"  {code}", file=sys.stderr)
        
        dsegset = ",".join(mode_c_segments)
        
        print(f"\\n{'=' * 60}", file=sys.stderr)
        print(f"TOTALE: {len(mode_c_segments)} segments", file=sys.stderr)
        
        result = {
            "status": "ok",
            "car_mode": car_mode_code,
            "mode_c_tsys": mode_c_tsys,
            "segments": mode_c_segments,
            "dsegset": dsegset,
            "count": len(mode_c_segments)
        }
    else:
        print(f"✗ TSys CAR mode: {car_mode_code} (non 'C')", file=sys.stderr)
        result = {
            "status": "ok",
            "car_mode": car_mode_code,
            "mode_c_tsys": mode_c_tsys,
            "segments": [],
            "dsegset": "",
            "count": 0
        }
    
except Exception as e:
    print(f"\\nERRORE: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    result = {"status": "error", "error": str(e)}
`;

const client = new net.Socket();
let welcomeReceived = false;

console.log('🔗 VERIFICA RELAZIONE TSys CAR ↔ Mode C');
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
            description: 'Verifica CAR-Mode C',
            code: pythonCode
        };
        client.write(JSON.stringify(request) + '\n');
    } else {
        if (response.success) {
            const res = response.result;
            if (res.status === 'ok') {
                console.log('\n📊 RISULTATI:');
                console.log('='.repeat(60));
                console.log(`TSys CAR -> Mode: "${res.car_mode}"`);
                console.log(`Mode C -> TSys: [${res.mode_c_tsys.join(', ')}]`);
                
                if (res.count > 0) {
                    console.log(`\n✅ ${res.count} segments MODE="C":\n`);
                    res.segments.forEach((s, i) => {
                        console.log(`${(i+1).toString().padStart(2)}. ${s}`);
                    });
                    
                    console.log('\n' + '='.repeat(60));
                    console.log('📝 DSEGSET:');
                    console.log('='.repeat(60));
                    console.log(res.dsegset);
                } else {
                    console.log('\n⚠️ Relazione non trovata o segments assenti');
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
