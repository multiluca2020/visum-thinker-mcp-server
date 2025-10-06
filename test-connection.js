import net from 'net';

const pythonCode = `
import sys

print("Test base connessione", file=sys.stderr)

try:
    # Solo un test basico
    num_zones = visum.Net.Zones.Count
    print(f"Zone: {num_zones}", file=sys.stderr)
    
    result = {"status": "ok", "zones": num_zones}
    
except Exception as e:
    print(f"ERRORE: {e}", file=sys.stderr)
    result = {"status": "error", "error": str(e)}
`;

const client = new net.Socket();
let welcomeReceived = false;

console.log('🩺 Test connessione base');

client.connect(7905, '::1', () => {
    console.log('✅ Connesso');
});

client.on('data', (data) => {
    const response = JSON.parse(data.toString());
    
    if (!welcomeReceived && response.type === 'project_welcome') {
        welcomeReceived = true;
        const request = {
            type: 'query',
            requestId: Date.now(),
            description: 'Test base',
            code: pythonCode
        };
        client.write(JSON.stringify(request) + '\n');
    } else {
        console.log(response.success ? `✅ OK - ${JSON.stringify(response.result)}` : `❌ ${response.error}`);
        console.log(`⏱️ ${response.executionTimeMs}ms`);
        client.destroy();
    }
});

client.on('close', () => console.log('🔌 Chiuso'));
client.on('error', (err) => console.error('❌', err.message));
