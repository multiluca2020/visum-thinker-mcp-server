/**
 * Script per creare una procedura PrT Assignment con configurazione DSEGSET
 * Usa la connessione TCP diretta al server Visum esistente sulla porta 7909
 */

const net = require('net');

const SERVER_CONFIG = {
  host: 'localhost',
  port: 7909  // Porta del server Visum attivo
};

// Tutti i 36 segmenti PRT
const ALL_PRT_SEGMENTS = [
  'C_CORRETTA_AM', 'C_CORRETTA_IP1', 'C_CORRETTA_IP2', 'C_CORRETTA_MD',
  'C_CORRETTA_PM1', 'C_CORRETTA_PM2', 'C_CORRETTA_S',
  'C_INIZIALE_AM', 'C_INIZIALE_IP1', 'C_INIZIALE_IP2', 'C_INIZIALE_MD',
  'C_INIZIALE_PM1', 'C_INIZIALE_PM2', 'C_INIZIALE_S',
  'C_NESTED_AM', 'C_NESTED_IP1', 'C_NESTED_IP2', 'C_NESTED_MD',
  'C_NESTED_PM1', 'C_NESTED_PM2', 'C_NESTED_S',
  'C_SOGLIA_AM', 'C_SOGLIA_PM1', 'C_SOGLIA_S',
  'H_CORRETTA_AM', 'H_CORRETTA_IP1', 'H_CORRETTA_IP2', 'H_CORRETTA_MD',
  'H_CORRETTA_PM1', 'H_CORRETTA_PM2', 'H_CORRETTA_S',
  'H_INIZIALE_AM', 'H_INIZIALE_IP1', 'H_INIZIALE_IP2', 'H_INIZIALE_MD',
  'H_INIZIALE_S'
];

const DSEGSET_STRING = ALL_PRT_SEGMENTS.join(',');

const pythonCode = `
# Crea e configura procedura PrT Assignment
try:
    procedures = visum.Procedures
    proc_seq = procedures.ProcedureSequence
    
    print(f"Procedure Sequence attuale: {proc_seq.Count} procedure")
    
    # Accedi alla funzione PrT Assignment BPR
    prt_func = procedures.Functions.PrTAssignmentBPR
    
    # Configura parametri DSEGSET
    dsegset = "${DSEGSET_STRING}"
    print(f"Configurando DSEGSET con {len(dsegset.split(','))} segmenti...")
    
    prt_func.SetAttValue("DSEGSET", dsegset)
    prt_func.SetAttValue("MaxIter", 20)
    prt_func.SetAttValue("GapCriterion", 0.01)
    
    print("Parametri configurati:")
    print(f"  - DSEGSET: {len(dsegset.split(','))} segmenti")
    print(f"  - MaxIter: 20")
    print(f"  - GapCriterion: 0.01")
    
    # Aggiungi alla Procedure Sequence
    proc_seq.AddProcedure(prt_func)
    
    new_position = proc_seq.Count
    print(f"✅ Procedura aggiunta alla posizione {new_position}")
    
    result = {
        'status': 'success',
        'procedure_created': True,
        'dsegset': dsegset,
        'segments_count': len(dsegset.split(',')),
        'procedure_position': new_position,
        'max_iterations': 20,
        'gap_criterion': 0.01
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
      reject(new Error('Timeout: Nessuna risposta dal server dopo 30 secondi'));
    }, 30000);
    
    client.connect(SERVER_CONFIG.port, SERVER_CONFIG.host, () => {
      console.log(`✅ Connesso al server Visum su ${SERVER_CONFIG.host}:${SERVER_CONFIG.port}`);
      
      const command = {
        action: 'execute',
        code: code
      };
      
      client.write(JSON.stringify(command) + '\n');
      console.log('📤 Comando inviato, in attesa risposta...');
    });
    
    client.on('data', (data) => {
      responseData += data.toString();
      
      // Verifica se abbiamo ricevuto un JSON completo
      try {
        const response = JSON.parse(responseData);
        clearTimeout(timeout);
        client.destroy();
        resolve(response);
      } catch (e) {
        // JSON ancora incompleto, continua ad accumulare
      }
    });
    
    client.on('error', (err) => {
      clearTimeout(timeout);
      reject(err);
    });
    
    client.on('close', () => {
      clearTimeout(timeout);
      if (responseData && !responseData.includes('{')) {
        reject(new Error(`Server chiuso senza risposta JSON. Dati ricevuti: ${responseData}`));
      }
    });
  });
}

async function main() {
  console.log('🚀 Creazione Procedura PrT Assignment con DSEGSET');
  console.log('='.repeat(60));
  console.log(`📋 Configurazione:`);
  console.log(`   - Segmenti PRT: ${ALL_PRT_SEGMENTS.length}`);
  console.log(`   - Server: ${SERVER_CONFIG.host}:${SERVER_CONFIG.port}`);
  console.log('='.repeat(60));
  
  try {
    const startTime = Date.now();
    const response = await sendCommand(pythonCode);
    const executionTime = Date.now() - startTime;
    
    console.log('\n📊 RISPOSTA DAL SERVER:');
    console.log('='.repeat(60));
    
    if (response.success) {
      console.log('✅ SUCCESSO!');
      console.log(`⏱️  Tempo esecuzione: ${executionTime}ms`);
      console.log('\n📋 Risultato:');
      console.log(JSON.stringify(response.result, null, 2));
      
      if (response.result.status === 'success') {
        console.log('\n🎉 PROCEDURA PRT ASSIGNMENT CREATA CON SUCCESSO!');
        console.log(`   - Posizione nella Procedure Sequence: ${response.result.procedure_position}`);
        console.log(`   - Segmenti configurati: ${response.result.segments_count}`);
        console.log(`   - MaxIter: ${response.result.max_iterations}`);
        console.log(`   - Gap Criterion: ${response.result.gap_criterion}`);
      } else {
        console.log('\n❌ ERRORE durante la creazione:');
        console.log(response.result.error);
        if (response.result.traceback) {
          console.log('\nTraceback:');
          console.log(response.result.traceback);
        }
      }
      
      if (response.output) {
        console.log('\n📝 Output Python:');
        console.log(response.output);
      }
    } else {
      console.log('❌ ERRORE dal server:');
      console.log(response.error || 'Errore sconosciuto');
    }
    
    console.log('='.repeat(60));
    
  } catch (error) {
    console.error('\n💥 ERRORE FATALE:');
    console.error(error.message);
    process.exit(1);
  }
}

main();
