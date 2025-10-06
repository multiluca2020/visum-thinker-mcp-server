import net from 'net';

const pythonCode = `
import sys

print("ANALISI MODES E LORO TSys", file=sys.stderr)
print("=" * 60, file=sys.stderr)

try:
    all_modes = visum.Net.Modes.GetAll
    
    print(f"\\nTotale Modes: {len(all_modes)}\\n", file=sys.stderr)
    
    modes_info = []
    
    for mode in all_modes:
        mode_code = mode.AttValue("CODE")
        
        print(f"Mode: {mode_code}", file=sys.stderr)
        
        # Accedi alla collezione TSystems
        mode_tsys = []
        try:
            tsys_collection = mode.TSystems
            
            if tsys_collection:
                for tsys in tsys_collection:
                    tsys_code = tsys.AttValue("CODE")
                    tsys_type = tsys.AttValue("TYPE")
                    
                    mode_tsys.append({
                        "code": tsys_code,
                        "type": tsys_type
                    })
                    
                    print(f"  -> TSys: {tsys_code} (TYPE={tsys_type})", file=sys.stderr)
        except Exception as e:
            print(f"  Errore TSystems: {e}", file=sys.stderr)
        
        modes_info.append({
            "mode": mode_code,
            "tsys": mode_tsys
        })
    
    # Trova quali modes hanno TSys PRT
    print(f"\\n{'=' * 60}", file=sys.stderr)
    print("MODES CON TSys PRT:\\n", file=sys.stderr)
    
    prt_modes = []
    
    for mode_info in modes_info:
        prt_tsys = [t for t in mode_info["tsys"] if t["type"] == "PRT"]
        
        if prt_tsys:
            print(f"Mode {mode_info['mode']}:", file=sys.stderr)
            for t in prt_tsys:
                print(f"  - TSys {t['code']} (PRT)", file=sys.stderr)
            
            prt_modes.append({
                "mode": mode_info["mode"],
                "prt_tsys": [t["code"] for t in prt_tsys]
            })
    
    result = {
        "status": "ok",
        "all_modes": modes_info,
        "prt_modes": prt_modes
    }
    
except Exception as e:
    print(f"\\nERRORE: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    result = {"status": "error", "error": str(e)}
`;

const client = new net.Socket();
let welcomeReceived = false;

console.log('🔍 MODES → TSys (inclusi PRT)');
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
            description: 'Modes and TSys',
            code: pythonCode
        };
        client.write(JSON.stringify(request) + '\n');
    } else {
        if (response.success) {
            const res = response.result;
            if (res.status === 'ok') {
                console.log('\n📊 TUTTI I MODES:');
                console.log('='.repeat(60));
                
                res.all_modes.forEach(m => {
                    console.log(`\n${m.mode}: ${m.tsys.length} TSys`);
                    m.tsys.forEach(t => console.log(`  - ${t.code} (${t.type})`));
                });
                
                if (res.prt_modes.length > 0) {
                    console.log('\n' + '='.repeat(60));
                    console.log('✅ MODES CON TSys PRT:');
                    console.log('='.repeat(60));
                    
                    res.prt_modes.forEach(pm => {
                        console.log(`\n${pm.mode}: TSys PRT = [${pm.prt_tsys.join(', ')}]`);
                    });
                } else {
                    console.log('\n⚠️ Nessun Mode ha TSys PRT associati');
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
