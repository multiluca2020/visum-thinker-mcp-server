// CLIENT TCP VISUM - Si connette al server TCP
import { createConnection } from 'net';
import { readFileSync, existsSync } from 'fs';

console.log('💻 CLIENT TCP VISUM');
console.log('=' .repeat(30));

const SERVER_INFO_FILE = 'tcp-server-info.json';

class VisumTcpClient {
  constructor() {
    this.socket = null;
    this.connected = false;
    this.requestId = 1;
    this.pendingRequests = new Map();
  }

  async connect() {
    // Leggi info server
    if (!existsSync(SERVER_INFO_FILE)) {
      throw new Error('Server non trovato! Avvia prima tcp-server.mjs');
    }
    
    const serverInfo = JSON.parse(readFileSync(SERVER_INFO_FILE, 'utf8'));
    console.log(`🔍 Server trovato: ${serverInfo.host}:${serverInfo.port} (PID ${serverInfo.pid})`);
    
    return new Promise((resolve, reject) => {
      this.socket = createConnection(serverInfo.port, serverInfo.host);
      
      this.socket.on('connect', () => {
        console.log(`✅ Connesso al server TCP ${serverInfo.host}:${serverInfo.port}`);
        this.connected = true;
        resolve();
      });
      
      this.socket.on('data', (data) => {
        // Gestisce buffer per messaggi multipli
        const lines = data.toString().split('\n').filter(line => line.trim());
        
        lines.forEach(line => {
          try {
            console.log(`📨 Raw server message: ${line.trim()}`);
            const message = JSON.parse(line);
            this.handleServerMessage(message);
          } catch (error) {
            console.error('❌ Errore parsing messaggio server:', error.message);
            console.error('❌ Raw data:', line);
          }
        });
      });
      
      this.socket.on('close', () => {
        console.log('🔌 Connessione chiusa');
        this.connected = false;
      });
      
      this.socket.on('error', (error) => {
        console.error('❌ Errore connessione:', error.message);
        this.connected = false;
        reject(error);
      });
    });
  }
  
  handleServerMessage(message) {
    console.log(`📨 Ricevuto dal server: ${message.type}`);
    
    switch (message.type) {
      case 'welcome':
        console.log(`🎉 Benvenuto! Client ID: ${message.clientId}`);
        console.log(`📊 Network: ${message.network.nodes} nodi, ${message.network.links} link, ${message.network.zones} zone`);
        break;
        
      case 'pong':
        if (this.pendingRequests.has(message.requestId)) {
          const request = this.pendingRequests.get(message.requestId);
          const responseTime = Date.now() - request.startTime;
          console.log(`🏓 Pong ricevuto in ${responseTime}ms`);
          this.pendingRequests.delete(message.requestId);
          request.resolve(message);
        }
        break;
        
      case 'query_result':
        if (this.pendingRequests.has(message.requestId)) {
          const request = this.pendingRequests.get(message.requestId);
          console.log(`🔍 Risultato query ricevuto in ${message.responseTimeMs}ms`);
          if (message.success) {
            console.log(`   ⚡ Esecuzione VisumPy: ${message.executionTimeMs}ms`);
            console.log(`   📊 Risultato:`, message.result);
          } else {
            console.log(`   ❌ Errore:`, message.error);
          }
          this.pendingRequests.delete(message.requestId);
          request.resolve(message);
        }
        break;
        
      case 'stats_result':
        if (this.pendingRequests.has(message.requestId)) {
          const request = this.pendingRequests.get(message.requestId);
          console.log(`📊 Stats ricevute in ${message.responseTimeMs}ms`);
          console.log(`   📊 Network:`, message.stats);
          this.pendingRequests.delete(message.requestId);
          request.resolve(message);
        }
        break;
        
      case 'error':
        console.log(`❌ Errore server:`, message.message);
        if (message.requestId && this.pendingRequests.has(message.requestId)) {
          const request = this.pendingRequests.get(message.requestId);
          this.pendingRequests.delete(message.requestId);
          request.reject(new Error(message.message));
        }
        break;
        
      default:
        console.log(`⚠️ Tipo messaggio sconosciuto: ${message.type}`);
    }
  }
  
  sendMessage(message) {
    if (!this.connected) {
      throw new Error('Non connesso al server');
    }
    
    const jsonStr = JSON.stringify(message);
    console.log(`📤 Sending to server: ${jsonStr}`);
    const data = jsonStr + '\n';
    this.socket.write(data);
  }
  
  async sendRequest(message) {
    const requestId = this.requestId++;
    message.requestId = requestId;
    
    return new Promise((resolve, reject) => {
      this.pendingRequests.set(requestId, {
        startTime: Date.now(),
        resolve,
        reject
      });
      
      this.sendMessage(message);
      
      // Timeout dopo 10 secondi
      setTimeout(() => {
        if (this.pendingRequests.has(requestId)) {
          this.pendingRequests.delete(requestId);
          reject(new Error('Timeout richiesta'));
        }
      }, 10000);
    });
  }
  
  async ping() {
    return await this.sendRequest({ type: 'ping' });
  }
  
  async query(code, description) {
    return await this.sendRequest({
      type: 'query',
      code: code,
      description: description
    });
  }
  
  async getNetworkStats() {
    return await this.sendRequest({ type: 'network_stats' });
  }
  
  disconnect() {
    if (this.socket) {
      this.socket.end();
    }
  }
}

// Test client
async function runClientTest() {
  const client = new VisumTcpClient();
  
  try {
    await client.connect();
    
    console.log('\\n🧪 ESECUZIONE TEST CLIENT...');
    
    // Test 1: Ping
    console.log('\\n📋 Test 1: Ping server');
    await client.ping();
    
    // Test 2: Network stats
    console.log('\\n📋 Test 2: Richiesta network stats');
    await client.getNetworkStats();
    
    // Test 3: Query personalizzata
    console.log('\\n📋 Test 3: Query personalizzata');
    await client.query(`
import time
start_time = time.time()

# Query su prime 3 zone
zone_sample = []
for zone_id in list(visum.Net.Zones.Keys)[:3]:
    zone = visum.Net.Zones.ItemByKey(zone_id)
    zone_sample.append({
        'id': zone_id,
        'name': zone.AttValue('Name') or f'Zone_{zone_id}'
    })

result = {
    'test_type': 'zone_sample',
    'total_zones': visum.Net.Zones.Count,
    'sample_zones': zone_sample,
    'query_time_ms': (time.time() - start_time) * 1000
}
    `, 'Zone Sample Query');
    
    // Test 4: Performance test
    console.log('\\n📋 Test 4: Performance test (5 query veloci)');
    const performanceTimes = [];
    
    for (let i = 1; i <= 5; i++) {
      const startTime = Date.now();
      await client.query(`
result = {
    'performance_test': ${i},
    'nodes': visum.Net.Nodes.Count,
    'timestamp': time.time()
}
      `, `Performance Test ${i}`);
      const responseTime = Date.now() - startTime;
      performanceTimes.push(responseTime);
    }
    
    const avgTime = performanceTimes.reduce((a, b) => a + b, 0) / performanceTimes.length;
    console.log(`\\n📊 Performance Summary:`);
    console.log(`   • Media: ${avgTime.toFixed(1)}ms`);
    console.log(`   • Min: ${Math.min(...performanceTimes)}ms`);
    console.log(`   • Max: ${Math.max(...performanceTimes)}ms`);
    
    console.log('\\n🎉 TUTTI I TEST COMPLETATI CON SUCCESSO!');
    console.log('✅ COMUNICAZIONE CLIENT-SERVER TCP FUNZIONANTE!');
    
    setTimeout(() => {
      client.disconnect();
      process.exit(0);
    }, 1000);
    
  } catch (error) {
    console.error('❌ Errore test client:', error.message);
    client.disconnect();
    process.exit(1);
  }
}

runClientTest();