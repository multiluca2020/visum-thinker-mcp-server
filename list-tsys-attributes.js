import net from 'net';

const pythonCode = `
import sys

print("ELENCO COMPLETO ATTRIBUTI TSys", file=sys.stderr)
print("=" * 60, file=sys.stderr)

try:
    # Prendi il primo TSys come esempio
    tsys_car = visum.Net.TSystems.ItemByKey("CAR")
    
    # Lista di possibili attributi da testare
    possible_attrs = [
        # Codici e nomi
        "CODE", "NAME", "NO", "ID", "NUM",
        
        # Tipo e categoria
        "TYPE", "TSYSTYPE", "TRANSPORTTYPE", "CATEGORY",
        
        # PrT related
        "ISPRT", "PRT", "PRTTYPE", "PRTACTIVE", "PRTMODE",
        
        # Mode related
        "MODE", "MODECODE", "MODENO", "MODEID", "MODENAME",
        
        # Altri
        "ACTIVE", "USEPRT", "VEHICLETYPE", "VEHTYPE",
        "DESCRIPTION", "COMMENT", "ADDVAL1", "ADDVAL2",
        "CAPACITYCONSTRAINT", "MAXSPEED", "MINSPEED"
    ]
    
    print(f"\\nTest attributi su TSys CAR:\\n", file=sys.stderr)
    
    found_attrs = {}
    
    for attr_name in possible_attrs:
        try:
            value = tsys_car.AttValue(attr_name)
            found_attrs[attr_name] = str(value) if value is not None else "null"
            print(f"  ✓ {attr_name:25} = {value}", file=sys.stderr)
        except:
            pass
    
    print(f"\\n{'=' * 60}", file=sys.stderr)
    print(f"Attributi trovati: {len(found_attrs)}", file=sys.stderr)
    
    # Test su tutti i TSys PRT
    print(f"\\n{'=' * 60}", file=sys.stderr)
    print("TUTTI I TSys DI TIPO PRT:\\n", file=sys.stderr)
    
    all_tsys = visum.Net.TSystems.GetAll
    prt_data = []
    
    for tsys in all_tsys:
        tsys_type = tsys.AttValue("TYPE")
        
        if tsys_type == "PRT":
            code = tsys.AttValue("CODE")
            
            # Per ogni TSys PRT, estrai gli attributi trovati
            tsys_attrs = {"CODE": code, "TYPE": tsys_type}
            
            for attr in found_attrs.keys():
                if attr not in ["CODE", "TYPE"]:
                    try:
                        val = tsys.AttValue(attr)
                        tsys_attrs[attr] = str(val) if val is not None else "null"
                    except:
                        pass
            
            prt_data.append(tsys_attrs)
            
            print(f"TSys {code}:", file=sys.stderr)
            for k, v in tsys_attrs.items():
                if k not in ["CODE", "TYPE"]:
                    print(f"  {k}: {v}", file=sys.stderr)
            print(file=sys.stderr)
    
    result = {
        "status": "ok",
        "available_attributes": found_attrs,
        "prt_tsys_data": prt_data
    }
    
except Exception as e:
    print(f"\\nERRORE: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    result = {"status": "error", "error": str(e)}
`;

const client = new net.Socket();
let welcomeReceived = false;

console.log('📋 ELENCO ATTRIBUTI TSys');
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
            description: 'List TSys attributes',
            code: pythonCode
        };
        client.write(JSON.stringify(request) + '\n');
    } else {
        if (response.success) {
            const res = response.result;
            if (res.status === 'ok') {
                console.log('\n📊 ATTRIBUTI DISPONIBILI PER TSys:');
                console.log('='.repeat(60));
                
                for (const [attr, value] of Object.entries(res.available_attributes)) {
                    console.log(`  ${attr.padEnd(25)} = ${value}`);
                }
                
                console.log('\n' + '='.repeat(60));
                console.log('🚗 TSys DI TIPO PRT:');
                console.log('='.repeat(60));
                
                res.prt_tsys_data.forEach(tsys => {
                    console.log(`\n${tsys.CODE} (${tsys.TYPE}):`);
                    for (const [k, v] of Object.entries(tsys)) {
                        if (k !== 'CODE' && k !== 'TYPE') {
                            console.log(`  ${k.padEnd(20)} = ${v}`);
                        }
                    }
                });
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
