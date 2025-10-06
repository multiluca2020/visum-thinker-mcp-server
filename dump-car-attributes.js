import net from 'net';

const pythonCode = `
import sys
import json

print("DUMP COMPLETO ATTRIBUTI TSys CAR", file=sys.stderr)
print("=" * 60, file=sys.stderr)

try:
    # Prendi TSys CAR
    tsys_car = visum.Net.TSystems.ItemByKey("CAR")
    print("\\nTSys CAR trovato!\\n", file=sys.stderr)
    
    # Lista di possibili attributi da testare
    possible_attrs = [
        "CODE", "NAME", "TSYSTYPE", "TYPE", "ISPRT", "PRT", 
        "PRTTYPE", "PRTACTIVE", "PRTMODE", "MODE", "MODECODE",
        "TRANSPORTTYPE", "VEHICLETYPE", "ID", "NO", "NUM"
    ]
    
    attributes = {}
    
    print("Test attributi:", file=sys.stderr)
    for attr_name in possible_attrs:
        try:
            value = tsys_car.AttValue(attr_name)
            attributes[attr_name] = str(value) if value is not None else "null"
            print(f"  ✓ {attr_name:20} = {value}", file=sys.stderr)
        except Exception as e:
            print(f"  ✗ {attr_name:20} - non esiste", file=sys.stderr)
    
    # Prova anche a vedere la collezione di attributi
    print(f"\\n{'=' * 60}", file=sys.stderr)
    print("Tentativo di enumerare attributi dinamicamente:", file=sys.stderr)
    
    try:
        # Alcuni oggetti COM hanno un metodo GetAttributes
        if hasattr(tsys_car, 'GetAttributes'):
            attrs_list = tsys_car.GetAttributes()
            print(f"GetAttributes: {attrs_list}", file=sys.stderr)
    except:
        pass
    
    try:
        # Prova a vedere i metodi disponibili
        if hasattr(tsys_car, '__dir__'):
            methods = [m for m in dir(tsys_car) if not m.startswith('_')]
            print(f"\\nMetodi disponibili: {methods[:20]}", file=sys.stderr)
    except:
        pass
    
    result = {
        "status": "ok",
        "tsys": "CAR",
        "attributes": attributes
    }
    
except Exception as e:
    print(f"\\nERRORE: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    result = {
        "status": "error",
        "error": str(e),
        "attributes": {}
    }
`;

const client = new net.Socket();
let welcomeReceived = false;

console.log('🔍 DUMP ATTRIBUTI TSys CAR');
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
            description: 'Dump attributi CAR',
            code: pythonCode
        };
        client.write(JSON.stringify(request) + '\n');
    } else {
        if (response.success) {
            const res = response.result;
            
            if (res.status === 'ok') {
                console.log('\n📊 ATTRIBUTI TSys CAR:');
                console.log('='.repeat(60));
                
                for (const [attr, value] of Object.entries(res.attributes)) {
                    console.log(`  ${attr.padEnd(20)} = ${value}`);
                }
                
                console.log('\n💡 Cerca attributi con "PRT" o "TYPE" per identificare il tipo');
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
