import net from 'net';

const pythonCode = `
import sys

print("RICERCA DEMAND SEGMENTS CON METODI ALTERNATIVI", file=sys.stderr)

# Metodo 1: visum.Net.DemandSegments
try:
    ds1 = visum.Net.DemandSegments.GetAll
    print(f"Metodo 1 (DemandSegments): {len(ds1)} trovati", file=sys.stderr)
except Exception as e:
    print(f"Metodo 1 FALLITO: {e}", file=sys.stderr)
    ds1 = []

# Metodo 2: visum.Net.DemandSegment (singolare)
try:
    ds2 = visum.Net.DemandSegment.GetAll
    print(f"Metodo 2 (DemandSegment singolare): {len(ds2)} trovati", file=sys.stderr)
except Exception as e:
    print(f"Metodo 2 FALLITO: {e}", file=sys.stderr)
    ds2 = []

# Metodo 3: via Procedure parameters
try:
    # Prova a vedere se ci sono demand segments definiti nelle procedure
    print(f"Metodo 3: Controllo struttura...", file=sys.stderr)
    print(f"  Dir visum.Net: {[x for x in dir(visum.Net) if 'demand' in x.lower() or 'dseg' in x.lower()]}", file=sys.stderr)
except Exception as e:
    print(f"Metodo 3 FALLITO: {e}", file=sys.stderr)

# Transport Systems
try:
    tsys = visum.Net.TSystems.GetAll
    tsys_list = []
    for t in tsys:
        tsys_list.append({
            "code": t.AttValue("CODE"),
            "name": t.AttValue("NAME") if t.AttValue("NAME") else ""
        })
    print(f"\\nTransport Systems: {len(tsys_list)}", file=sys.stderr)
    for t in tsys_list:
        print(f"  {t['code']} - {t['name']}", file=sys.stderr)
except Exception as e:
    print(f"TSys error: {e}", file=sys.stderr)
    tsys_list = []

result = {
    "status": "ok",
    "method1_count": len(ds1),
    "method2_count": len(ds2),
    "tsystems": tsys_list
}
`;

const client = new net.Socket();
let welcomeReceived = false;

console.log('🔍 DEBUG: RICERCA DEMAND SEGMENTS');
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
            description: 'Debug demand segments',
            code: pythonCode
        };
        client.write(JSON.stringify(request) + '\n');
    } else {
        if (response.success) {
            const res = response.result;
            console.log(`\nMetodo 1: ${res.method1_count} demand segments`);
            console.log(`Metodo 2: ${res.method2_count} demand segments`);
            console.log(`\nTSystems: ${res.tsystems.length}`);
            res.tsystems.forEach(t => console.log(`  ${t.code} - ${t.name}`));
        } else {
            console.log('❌', response.error);
        }
        console.log(`\n⏱️ ${response.executionTimeMs}ms`);
        client.destroy();
    }
});

client.on('close', () => console.log('\n🔌 Chiuso'));
client.on('error', (err) => console.error('❌', err.message));
