// PROJECT TCP SERVER - Server dedicato per un progetto specifico
import { PersistentVisumController } from './build/persistent-visum-controller.js';
import { createServer } from 'net';
import { basename } from 'path';

// Argomenti: node project-tcp-server.mjs <projectPath> <port> <projectId>
const projectPath = process.argv[2];
const port = parseInt(process.argv[3]);
const projectId = process.argv[4];

if (!projectPath || !port || !projectId) {
  console.error('Uso: node project-tcp-server.mjs <projectPath> <port> <projectId>');
  process.exit(1);
}

console.log(`🖥️ PROJECT TCP SERVER: ${basename(projectPath)}`);
console.log(`📡 Porta: ${port} | ID: ${projectId}`);
console.log('=' .repeat(50));

class ProjectTcpServer {
  constructor(projectPath, port, projectId) {
    this.projectPath = projectPath;
    this.projectName = basename(projectPath, '.ver');
    this.port = port;
    this.projectId = projectId;
    this.controller = null;
    this.server = null;
    this.clients = new Map();
    this.nextClientId = 1;
    this.projectStats = null;
  }

  async start() {
    console.log(`🚀 Inizializzazione progetto: ${this.projectName}`);
    
    // Inizializza controller Visum per questo progetto
    this.controller = PersistentVisumController.getInstance();
    this.controller.setDefaultProject(this.projectPath);
    
    const result = await this.controller.startPersistentVisumProcess();
    
    if (!result.success) {
      throw new Error(`Errore caricamento progetto: ${result.message}`);
    }
    
    this.projectStats = {
      nodes: result.nodes,
      links: result.links,
      zones: result.zones
    };
    
    console.log(`✅ Progetto caricato:`);
    console.log(`   📊 ${result.nodes} nodi, ${result.links} link, ${result.zones} zone`);
    
    // Crea server TCP dedicato per questo progetto
    this.server = createServer((socket) => {
      const clientId = this.nextClientId++;
      this.clients.set(clientId, {
        socket,
        connectTime: Date.now(),
        requests: 0
      });
      
      console.log(`🔌 Client ${clientId} connesso al progetto ${this.projectName}`);
      
      // Messaggio di benvenuto specifico del progetto
      this.sendToClient(socket, {
        type: 'project_welcome',
        clientId: clientId,
        projectId: this.projectId,
        projectName: this.projectName,
        projectPath: this.projectPath,
        network: this.projectStats,
        message: `Connesso al progetto ${this.projectName}`
      });
      
      // Buffer per messaggi incompleti
      let buffer = '';
      
      socket.on('data', async (data) => {
        try {
          buffer += data.toString();
          
          let newlineIndex;
          while ((newlineIndex = buffer.indexOf('\\n')) !== -1) {
            const messageStr = buffer.slice(0, newlineIndex).trim();
            buffer = buffer.slice(newlineIndex + 1);
            
            if (messageStr) {
              const message = JSON.parse(messageStr);
              console.log(`📨 ${this.projectName} <- Client ${clientId}: ${message.type}`);
              
              // Incrementa contatore richieste
              this.clients.get(clientId).requests++;
              
              await this.handleClientMessage(clientId, socket, message);
            }
          }
        } catch (error) {
          console.error(`❌ Errore parsing messaggio Client ${clientId}:`, error.message);
          this.sendToClient(socket, {
            type: 'error',
            message: `Formato messaggio non valido: ${error.message}`
          });
        }
      });
      
      socket.on('close', () => {
        const clientInfo = this.clients.get(clientId);
        const duration = Date.now() - clientInfo.connectTime;
        console.log(`🔌 Client ${clientId} disconnesso dal progetto ${this.projectName}`);
        console.log(`   ⏱️ Durata: ${Math.round(duration/1000)}s | Richieste: ${clientInfo.requests}`);
        this.clients.delete(clientId);
      });
      
      socket.on('error', (error) => {
        console.error(`❌ Errore Client ${clientId}:`, error.message);
        this.clients.delete(clientId);
      });
    });
    
    // Avvia server TCP
    this.server.listen(this.port, 'localhost', () => {
      console.log(`🌐 Server progetto ${this.projectName} in ascolto su porta ${this.port}`);
      console.log(`🔗 Client possono connettersi a localhost:${this.port}`);
      console.log('\\n🟢 SERVER PRONTO PER CLIENT TCP!');
    });
    
    // Gestione shutdown
    process.on('SIGINT', () => {
      this.shutdown('SIGINT ricevuto');
    });
    
    process.on('SIGTERM', () => {
      this.shutdown('SIGTERM ricevuto');
    });
  }
  
  sendToClient(socket, message) {
    const jsonStr = JSON.stringify(message);
    const data = jsonStr + '\\n';
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
            projectId: this.projectId,
            timestamp: Date.now()
          });
          break;
          
        case 'project_info':
          console.log(`ℹ️ Info progetto richieste da Client ${clientId}`);
          this.sendToClient(socket, {
            type: 'project_info_result',
            requestId: message.requestId,
            projectInfo: {
              projectId: this.projectId,
              projectName: this.projectName,
              projectPath: this.projectPath,
              network: this.projectStats,
              serverPort: this.port,
              activeClients: this.clients.size
            }
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
            projectId: this.projectId,
            success: queryResult.success,
            result: queryResult.result,
            error: queryResult.error,
            responseTimeMs: responseTime,
            executionTimeMs: queryResult.executionTimeMs
          });
          
          console.log(`⚡ Query Client ${clientId} completata in ${responseTime}ms`);
          break;
          
        case 'save_project':
          console.log(`💾 Salvataggio progetto richiesto da Client ${clientId}`);
          
          const saveCode = message.saveAs ? 
            `visum.SaveVersionAs(r"${message.saveAs}")` : 
            `visum.SaveVersion()`;
            
          const saveResult = await this.controller.executeCustomCode(
            saveCode,
            'Save Project'
          );
          
          this.sendToClient(socket, {
            type: 'save_result',
            requestId: message.requestId,
            projectId: this.projectId,
            success: saveResult.success,
            message: saveResult.success ? 'Progetto salvato' : 'Errore salvataggio',
            error: saveResult.error,
            savedAs: message.saveAs
          });
          
          console.log(`💾 Salvataggio progetto: ${saveResult.success ? '✅' : '❌'}`);
          break;
          
        case 'shutdown':
          console.log(`🔴 Shutdown richiesto da Client ${clientId}`);
          this.sendToClient(socket, {
            type: 'shutdown_ack',
            requestId: message.requestId,
            message: 'Server in shutdown'
          });
          
          setTimeout(() => {
            this.shutdown('Richiesto da client');
          }, 1000);
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
  
  shutdown(reason) {
    console.log(`\\n🛑 Shutdown server progetto ${this.projectName}: ${reason}`);
    
    // Notifica client connessi
    for (const [clientId, clientInfo] of this.clients) {
      this.sendToClient(clientInfo.socket, {
        type: 'server_shutdown',
        message: 'Server in shutdown',
        reason: reason
      });
    }
    
    // Chiudi server
    if (this.server) {
      this.server.close(() => {
        console.log(`✅ Server progetto ${this.projectName} chiuso`);
        process.exit(0);
      });
    } else {
      process.exit(0);
    }
  }
}

// Avvia server progetto
const server = new ProjectTcpServer(projectPath, port, projectId);
server.start().catch((error) => {
  console.error('❌ Errore avvio server progetto:', error.message);
  process.exit(1);
});