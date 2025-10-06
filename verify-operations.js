/**
 * Script per verificare se le operazioni sono state realmente create
 */

import net from 'net';

const VISUM_SERVER_HOST = 'localhost';
const VISUM_SERVER_PORT = 7901;

async function sendVisumCommand(code, description = 'Query') {
    return new Promise((resolve, reject) => {
        const client = new net.Socket();
        
        const command = {
            type: 'query',
            code: code,
            description: description,
            requestId: Date.now()
        };
        
        client.connect(VISUM_SERVER_PORT, VISUM_SERVER_HOST, () => {
            console.log(`📡 Connesso al server TCP`);
            client.write(JSON.stringify(command) + '\n');
        });
        
        let buffer = '';
        
        client.on('data', (data) => {
            buffer += data.toString();
            const messages = buffer.split('\n');
            buffer = messages.pop() || '';
            
            for (const message of messages) {
                if (message.trim()) {
                    try {
                        const cleanedResponse = message.replace(/\\n$/g, '');
                        const response = JSON.parse(cleanedResponse);
                        
                        if (response.type === 'project_welcome') {
                            continue;
                        }
                        
                        if (response.type === 'query_result' || response.type === 'error' || response.result !== undefined) {
                            client.destroy();
                            resolve(response);
                            return;
                        }
                    } catch (e) {
                        // JSON incompleto
                    }
                }
            }
        });
        
        client.on('close', () => {
            console.log('🔌 Connessione chiusa');
        });
        
        client.on('error', (err) => {
            console.error('❌ Errore TCP:', err.message);
            reject(err);
        });
        
        client.setTimeout(30000, () => {
            client.destroy();
            reject(new Error('TCP timeout'));
        });
    });
}

async function main() {
    console.log('\n' + '═'.repeat(70));
    console.log('🔍 VERIFICA OPERAZIONI VISUM');
    console.log('═'.repeat(70));
    
    try {
        // 1. Conta operazioni alle posizioni 20 e 21
        const code = `
operations = visum.Procedures.Operations

result = {
    'status': 'ok',
    'operations': {}
}

# Verifica posizione 20
try:
    op20 = operations.ItemByKey(20)
    op_type_20 = op20.AttValue("OPERATIONTYPE")
    result['operations']['pos_20'] = {
        'exists': True,
        'type': int(op_type_20)
    }
except Exception as e:
    result['operations']['pos_20'] = {
        'exists': False,
        'error': str(e)
    }

# Verifica posizione 21  
try:
    op21 = operations.ItemByKey(21)
    op_type_21 = op21.AttValue("OPERATIONTYPE")
    result['operations']['pos_21'] = {
        'exists': True,
        'type': int(op_type_21)
    }
    
    # Se è PrT Assignment, verifica parametri
    if op_type_21 == 101:
        try:
            params = op21.PrTAssignmentPara
            dseg = params.AttValue("DSegSet")
            variant = params.AttValue("PrTAssignmentVariant")
            result['operations']['pos_21']['params'] = {
                'DSegSet': str(dseg),
                'Variant': int(variant)
            }
        except Exception as e2:
            result['operations']['pos_21']['params_error'] = str(e2)
            
except Exception as e:
    result['operations']['pos_21'] = {
        'exists': False,
        'error': str(e)
    }

# Conta totale operazioni top-level
count = 0
try:
    while True:
        operations.ItemByKey(count + 1)
        count += 1
except:
    pass
result['total_operations'] = count

# Ritorna result
str(result)
`;

        const response = await sendVisumCommand(code, 'Verify operations');
        
        console.log('\n� RISULTATO:');
        console.log('─'.repeat(70));
        if (response.result) {
            console.log(JSON.stringify(response.result, null, 2));
        } else if (response.error) {
            console.error('❌ ERRORE:', response.error);
        } else {
            console.log('⚠️ Nessun risultato');
            console.log('Response:', JSON.stringify(response, null, 2));
        }
        console.log('─'.repeat(70));
        
    } catch (error) {
        console.error('\n❌ ERRORE:', error);
    }
}

main();
