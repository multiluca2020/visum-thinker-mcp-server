/**
 * Script semplice per aggiungere PrT Assignment alla Procedure Sequence
 * SENZA configurare segmenti di domanda - usa default di Visum
 */

const net = require('net');

const SERVER_CONFIG = {
  host: 'localhost',
  port: 7909
};

const pythonCode = `
# Aggiungi PrT Assignment alla Procedure Sequence
try:
    print("Accesso a Procedures...")
    procedures = visum.Procedures
    proc_seq = procedures.ProcedureSequence
    
    print(f"Procedure Sequence attuale: {proc_seq.Count} procedure")
    
    print("Accesso a PrTAssignmentBPR...")
    prt_func = procedures.Functions.PrTAssignmentBPR
    
    print("Aggiunta procedura alla sequenza...")
    proc_seq.AddProcedure(prt_func)
    
    new_position = proc_seq.Count
    print(f"Procedura aggiunta alla posizione {new_position}")
    
    result = {
        'status': 'success',
        'procedure_added': True,
        'position': new_position,
        'total_procedures': new_position,
        'note': 'Procedura creata senza configurare DSEGSET - usa impostazioni default'
    }
    
except Exception as e:
    import traceback
    result = {
        'status': 'error',
        'error': str(e),
        'traceback': traceback.format_exc()
    }
`;

function sendCommand(code) {
  return new Promise((resolve, reject) => {
    const client = new net.Socket();
    let responseData = '';
    
    const timeout = setTimeout(() => {
      client.destroy();
      reject(new Error('Timeout dopo 30 secondi'));
    }, 30000);
    
    client.connect(SERVER_CONFIG.port, SERVER_CONFIG.host, () => {
      console.log(`✅ Connesso a ${SERVER_CONFIG.host}:${SERVER_CONFIG.port}`);
      
      const command = { action: 'execute', code: code };
      client.write(JSON.stringify(command) + '\n');
      console.log('📤 Comando inviato...');
    });
    
    client.on('data', (data) => {
      responseData += data.toString();
      try {
        const response = JSON.parse(responseData);
        clearTimeout(timeout);
        client.destroy();
        resolve(response);
      } catch (e) {
        // JSON incompleto
      }
    });
    
    client.on('error', (err) => {
      clearTimeout(timeout);
      reject(err);
    });
  });
}

async function main() {
  console.log('🚀 Aggiunta PrT Assignment alla Procedure Sequence');
  console.log('='.repeat(60));
  
  try {
    const response = await sendCommand(pythonCode);
    
    console.log('\n📊 RISPOSTA:');
    console.log('='.repeat(60));
    
    if (response.success) {
      console.log('✅ SUCCESSO!');
      console.log(JSON.stringify(response.result, null, 2));
      
      if (response.output) {
        console.log('\n📝 Output:');
        console.log(response.output);
      }
    } else {
      console.log('❌ ERRORE:');
      console.log(response.error);
    }
    
  } catch (error) {
    console.error('💥 ERRORE:', error.message);
    process.exit(1);
  }
}

main();
