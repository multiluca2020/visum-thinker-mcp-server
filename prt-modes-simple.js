import net from 'net';

const pythonCode = `
import sys

print("TSys PRT e Modes - Versione semplice", file=sys.stderr)
print("=" * 60, file=sys.stderr)

try:
    # Lista TSys PRT
    prt_tsys = []
    
    all_tsys = visum.Net.TSystems.GetAll
    print(f"\\nTotale TSys: {len(all_tsys)}", file=sys.stderr)
    
    for tsys in all_tsys:
        code = tsys.AttValue("CODE")
        tsys_type = tsys.AttValue("TYPE")
        
        if tsys_type == "PRT":
            prt_tsys.append(code)
            print(f"  PRT: {code}", file=sys.stderr)
    
    print(f"\\nTSys PRT trovati: {prt_tsys}", file=sys.stderr)
    
    # Ora per ogni TSys PRT, cerca MODECODE
    tsys_modes = {}
    
    for tsys_code in prt_tsys:
        tsys_obj = visum.Net.TSystems.ItemByKey(tsys_code)
        
        mode = None
        try:
            mode = tsys_obj.AttValue("MODECODE")
        except:
            try:
                mode = tsys_obj.AttValue("MODE")
            except:
                mode = None
        
        tsys_modes[tsys_code] = mode
        print(f"{tsys_code} -> Mode: {mode}", file=sys.stderr)
    
    result = {
        "status": "ok",
        "prt_tsys": prt_tsys,
        "tsys_modes": tsys_modes
    }
    
except Exception as e:
    print(f"ERRORE: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    result = {"status": "error", "error": str(e)}
`;

const client = new net.Socket();
let welcomeReceived = false;

console.log('🔍 TSys PRT e Modes (semplice)');
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
            description: 'TSys PRT modes simple',
            code: pythonCode
        };
        client.write(JSON.stringify(request) + '\n');
    } else {
        if (response.success) {
            const res = response.result;
            if (res.status === 'ok') {
                console.log('\n✅ TSys PRT:');
                res.prt_tsys.forEach(t => console.log(`  - ${t}`));
                
                console.log('\n📊 TSys → Mode:');
                for (const [tsys, mode] of Object.entries(res.tsys_modes)) {
                    console.log(`  ${tsys} → ${mode || 'N/A'}`);
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
