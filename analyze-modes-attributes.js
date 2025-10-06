import net from 'net';

const pythonCode = `
import sys

print("=" * 80, file=sys.stderr)
print("ANALISI MODES - TUTTI GLI ATTRIBUTI", file=sys.stderr)
print("=" * 80, file=sys.stderr)

try:
    modes = visum.Net.Modes.GetAll
    
    modes_data = []
    for mode in modes:
        mode_code = mode.AttValue("CODE")
        mode_name = mode.AttValue("NAME") if mode.AttValue("NAME") else ""
        
        print(f"\\nMode: {mode_code} - {mode_name}", file=sys.stderr)
        
        # Prova a leggere diversi attributi possibili
        attributes = {}
        attr_names = ["MODETYPE", "TSYSTYPE", "TYPE", "TRANSPORTTYPE", "CATEGORYCODE"]
        
        for attr in attr_names:
            try:
                val = mode.AttValue(attr)
                attributes[attr] = str(val)
                print(f"  {attr}: {val}", file=sys.stderr)
            except:
                pass
        
        modes_data.append({
            "code": mode_code,
            "name": mode_name,
            "attributes": attributes
        })
    
    result = {
        "status": "ok",
        "modes": modes_data,
        "total": len(modes_data)
    }
    
except Exception as e:
    result = {
        "status": "error",
        "error": str(e)
    }
`;

const client = new net.Socket();
let welcomeReceived = false;

console.log('🔍 ANALISI MODES CON ATTRIBUTI');
console.log('='.repeat(60));

client.connect(7904, '::1', () => {
    console.log('✅ Connesso sulla porta 7904\n');
});

client.on('data', (data) => {
    const response = JSON.parse(data.toString());
    
    if (!welcomeReceived && response.type === 'project_welcome') {
        welcomeReceived = true;
        
        const request = {
            type: 'query',
            requestId: Date.now(),
            description: 'Analisi modes con tutti gli attributi',
            code: pythonCode
        };
        client.write(JSON.stringify(request) + '\n');
    } else {
        console.log('\n📊 RISULTATO:\n');
        
        if (response.success && response.result.status === 'ok') {
            const modes = response.result.modes;
            console.log(`Trovati ${modes.length} modes:\n`);
            
            modes.forEach((mode, i) => {
                console.log(`${i+1}. MODE: "${mode.code}" - ${mode.name}`);
                Object.entries(mode.attributes).forEach(([key, val]) => {
                    console.log(`   ${key}: ${val}`);
                });
                console.log('');
            });
            
        } else {
            console.log('❌ Errore:', response.error || response.result?.error);
        }
        
        console.log(`\n⏱️ Tempo: ${response.executionTimeMs}ms`);
        client.destroy();
    }
});

client.on('close', () => console.log('\n🔌 Chiuso'));
client.on('error', (err) => console.error('❌', err.message));
