// SERVER TCP VISUM - Comunicazione reale inter-processo
import { PersistentVisumController } from './build/persistent-visum-controller.js';
import { createServer } from 'net';
import { writeFileSync } from 'fs';

console.log('🖥️ SERVER TCP VISUM');
console.log('=' .repeat(40));

const TCP_PORT = 7892;
const SERVER_INFO_FILE = 'tcp-server-info.json';

class VisumTcpServer {
  constructor() {
    this.controller = null;
    this.server = null;
    this.clients = new Map();
    this.nextClientId = 1;
  }

  async start() {
    console.log('🚀 Inizializzazione server TCP...');
    
    // Inizializza controller Visum
    this.controller = PersistentVisumController.getInstance();
    const result = await this.controller.startPersistentVisumProcess();
    
    if (!result.success) {
      throw new Error(`Errore inizializzazione Visum: ${result.message}`);
    }
    
    console.log('✅ Visum inizializzato:');
    console.log(`   📊 ${result.nodes} nodi, ${result.links} link, ${result.zones} zone`);
    
    // Crea server TCP
    this.server = createServer((socket) => {
      const clientId = this.nextClientId++;
      this.clients.set(clientId, socket);
      
      console.log(`🔌 Client ${clientId} connesso da ${socket.remoteAddress}:${socket.remotePort}`);
      
      // Invia messaggio di benvenuto
      this.sendToClient(socket, {
        type: 'welcome',
        clientId: clientId,
        message: 'Connesso al server Visum',
        network: {
          nodes: result.nodes,
          links: result.links,
          zones: result.zones
        }
      });
      
      // Gestisce messaggi dal client
      let buffer = '';
      
      socket.on('data', async (data) => {
        try {
          buffer += data.toString();
          
          // Processa messaggi completi (divisi da newline)
          let newlineIndex;
          while ((newlineIndex = buffer.indexOf('\n')) !== -1) {
            const messageStr = buffer.slice(0, newlineIndex).trim();
            buffer = buffer.slice(newlineIndex + 1);
            
            if (messageStr) {
              console.log(`📨 Raw message from Client ${clientId}: ${messageStr}`);
              const message = JSON.parse(messageStr);
              console.log(`📨 Parsed message from Client ${clientId}:`, message.type);
              
              await this.handleClientMessage(clientId, socket, message);
            }
          }
        } catch (error) {
          console.error(`❌ Errore parsing messaggio da Client ${clientId}:`, error.message);
          console.error(`❌ Buffer content: "${buffer}"`);
          this.sendToClient(socket, {
            type: 'error',
            message: 'Formato messaggio non valido: ' + error.message
          });
        }
      });
      
      socket.on('close', () => {
        console.log(`🔌 Client ${clientId} disconnesso`);
        this.clients.delete(clientId);
      });
      
      socket.on('error', (error) => {
        console.error(`❌ Errore Client ${clientId}:`, error.message);
        this.clients.delete(clientId);
      });
    });
    
    // Avvia server TCP
    this.server.listen(TCP_PORT, 'localhost', () => {
      console.log(`🌐 Server TCP in ascolto su porta ${TCP_PORT}`);
      console.log(`🔗 Client possono connettersi a localhost:${TCP_PORT}`);
      
      // Salva info server
      const serverInfo = {
        pid: process.pid,
        port: TCP_PORT,
        host: 'localhost',
        startTime: Date.now(),
        startTimeString: new Date().toLocaleString('it-IT'),
        nodes: result.nodes,
        links: result.links,
        zones: result.zones,
        status: 'listening'
      };
      
      writeFileSync(SERVER_INFO_FILE, JSON.stringify(serverInfo, null, 2));
      console.log(`📝 Info server salvate in ${SERVER_INFO_FILE}`);
      console.log('\\n🟢 SERVER PRONTO PER CLIENT TCP!');
    });
    
    // Gestione shutdown
    process.on('SIGINT', () => {
      console.log('\\n🛑 Shutdown server...');
      this.server.close(() => {
        console.log('✅ Server TCP chiuso');
        process.exit(0);
      });
    });
  }
  
  sendToClient(socket, message) {
    const jsonStr = JSON.stringify(message);
    console.log(`📤 Sending to client: ${jsonStr}`);
    const data = jsonStr + '\n';
    socket.write(data);
  }
  
  async handleClientMessage(clientId, socket, message) {
    const startTime = Date.now();
    
    try {
      switch (message.type) {
        case 'ping':
          console.log(`🏓 Ping da Client ${clientId}`);
          this.sendToClient(socket, {
            type: 'pong',
            requestId: message.requestId,
            timestamp: Date.now()
          });
          break;
          
        case 'query':
          console.log(`🔍 Query da Client ${clientId}: ${message.description}`);
          
          const queryResult = await this.controller.executeCustomCode(
            message.code,
            message.description
          );
          
          const responseTime = Date.now() - startTime;
          
          this.sendToClient(socket, {
            type: 'query_result',
            requestId: message.requestId,
            success: queryResult.success,
            result: queryResult.result,
            error: queryResult.error,
            responseTimeMs: responseTime,
            executionTimeMs: queryResult.executionTimeMs
          });
          
          console.log(`⚡ Query Client ${clientId} completata in ${responseTime}ms`);
          break;
          
        case 'network_stats':
          console.log(`📊 Richiesta stats da Client ${clientId}`);
          
          const statsResult = await this.controller.executeCustomCode(`
result = {
    'nodes': visum.Net.Nodes.Count,
    'links': visum.Net.Links.Count,
    'zones': visum.Net.Zones.Count,
    'timestamp': time.time()
}
`, 'Network Stats Request');
          
          const statsResponseTime = Date.now() - startTime;
          
          this.sendToClient(socket, {
            type: 'stats_result',
            requestId: message.requestId,
            success: statsResult.success,
            stats: statsResult.result,
            responseTimeMs: statsResponseTime
          });
          
          console.log(`📊 Stats Client ${clientId} inviate in ${statsResponseTime}ms`);
          break;
          
        default:
          console.log(`⚠️ Tipo messaggio sconosciuto da Client ${clientId}: ${message.type}`);
          this.sendToClient(socket, {
            type: 'error',
            requestId: message.requestId,
            message: `Tipo messaggio non supportato: ${message.type}`
          });
      }
    } catch (error) {
      console.error(`❌ Errore gestione messaggio Client ${clientId}:`, error.message);
      this.sendToClient(socket, {
        type: 'error',
        requestId: message.requestId,
        message: error.message
      });
    }
  }
}

// Avvia server
const server = new VisumTcpServer();
server.start().catch(console.error);