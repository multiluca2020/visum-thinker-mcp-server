// Test diretto della connessione TCP al server Visum
import { createConnection } from 'net';

const serverPort = 7904;
const serverHost = 'localhost';

console.log(`🔌 Connessione diretta al server TCP su ${serverHost}:${serverPort}...`);

const client = createConnection(serverPort, serverHost);

client.on('connect', () => {
  console.log('✅ Connesso al server TCP!');
  
  // Invia comando di test
  const command = {
    type: 'query',
    code: 'print("Test connessione diretta...")\nprint(f"Numero di nodi: {Visum.Net.Nodes.Count}")\nprint(f"Numero di link: {Visum.Net.Links.Count}")',
    description: 'Test connessione diretta TCP',
    requestId: Date.now()
  };
  
  const message = JSON.stringify(command) + '\n';
  console.log('📤 Invio comando:', JSON.stringify(command, null, 2));
  client.write(message);
});

client.on('data', (data) => {
  const response = data.toString().trim();
  console.log('📥 Risposta ricevuta:');
  console.log('RAW:', JSON.stringify(response));
  
  try {
    const parsed = JSON.parse(response);
    console.log('✅ JSON valido:', JSON.stringify(parsed, null, 2));
  } catch (error) {
    console.log('❌ Errore parsing JSON:', error.message);
    console.log('❌ Contenuto:', response);
  }
  
  client.end();
});

client.on('error', (error) => {
  console.error('❌ Errore connessione:', error.message);
});

client.on('end', () => {
  console.log('🔚 Connessione chiusa');
});

setTimeout(() => {
  console.log('⏰ Timeout - chiudo connessione');
  client.end();
}, 10000);