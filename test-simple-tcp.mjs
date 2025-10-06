// Test con JSON correttamente formattato per il server TCP
import { createConnection } from 'net';

const serverPort = 7904;
const serverHost = 'localhost';

console.log(`🔌 Test comando con JSON corretto su porta ${serverPort}...`);

const client = createConnection(serverPort, serverHost);

client.on('connect', () => {
  console.log('✅ Connesso!');
  
  // Codice Python senza newlines problematici
  const pythonCode = 'print("Test base..."); print(f"Nodi: {Visum.Net.Nodes.Count}"); print(f"Link: {Visum.Net.Links.Count}")';
  
  const command = {
    type: 'query',
    code: pythonCode,
    description: 'Test semplice',
    requestId: Date.now()
  };
  
  const message = JSON.stringify(command) + '\n';
  console.log('📤 Comando (senza newlines):', pythonCode);
  client.write(message);
});

let buffer = '';

client.on('data', (data) => {
  buffer += data.toString();
  
  // Dividi per newlines per separare i messaggi
  const messages = buffer.split('\n');
  buffer = messages.pop(); // Mantieni l'ultimo pezzo (potrebbe essere incompleto)
  
  messages.forEach((message, i) => {
    if (message.trim()) {
      const cleaned = message.replace(/\\n$/g, '');
      try {
        const parsed = JSON.parse(cleaned);
        console.log(`📋 Messaggio ${i+1} (${parsed.type}):`, JSON.stringify(parsed, null, 2));
        
        if (parsed.type === 'success' || parsed.type === 'error') {
          console.log('🏁 Ricevuta risposta finale, chiudo...');
          client.end();
        }
      } catch (error) {
        console.log(`❌ Errore messaggio ${i+1}:`, error.message);
      }
    }
  });
});

client.on('error', (error) => {
  console.error('❌ Errore:', error.message);
});

setTimeout(() => client.end(), 5000);