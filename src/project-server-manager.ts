// PROJECT SERVER MANAGER - Gestisce server TCP dedicati per ogni progetto Visum
import { spawn } from 'child_process';
import { writeFileSync, readFileSync, existsSync, unlinkSync } from 'fs';
import { join, basename, dirname } from 'path';
import { createServer, createConnection } from 'net';
import { fileURLToPath } from 'url';

// Per supporto ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

export class ProjectServerManager {
  private static instance: ProjectServerManager;
  private activeServers: Map<string, any>;
  private nextPort: number;
  private registryFile: string;

  constructor() {
    this.activeServers = new Map(); // projectId -> serverInfo
    this.nextPort = 7900;
    this.registryFile = 'project-servers-registry.json';
    this.loadRegistry();
  }

  static getInstance() {
    if (!ProjectServerManager.instance) {
      ProjectServerManager.instance = new ProjectServerManager();
    }
    return ProjectServerManager.instance;
  }

  loadRegistry() {
    if (existsSync(this.registryFile)) {
      try {
        const data = JSON.parse(readFileSync(this.registryFile, 'utf8'));
        this.activeServers = new Map(Object.entries(data.servers || {}));
        this.nextPort = data.nextPort || 7900;
      } catch (error: any) {
        console.error('⚠️ Errore caricamento registry:', error.message);
      }
    }
  }

  saveRegistry() {
    const registryData = {
      servers: Object.fromEntries(this.activeServers),
      nextPort: this.nextPort,
      lastUpdate: new Date().toISOString()
    };
    writeFileSync(this.registryFile, JSON.stringify(registryData, null, 2));
  }

  generateProjectId(projectPath: string): string {
    // Genera ID unico basato sul path del progetto
    const projectName = basename(projectPath, '.ver');
    const hash = Math.abs(projectPath.split('').reduce((a: number, b: string) => {
      a = ((a << 5) - a) + b.charCodeAt(0);
      return a & a;
    }, 0));
    return `${projectName}_${hash}`;
  }

  async openProject(projectPath: string): Promise<any> {
    const projectId = this.generateProjectId(projectPath);
    
    // Controlla se il progetto è già aperto
    if (this.activeServers.has(projectId)) {
      const serverInfo = this.activeServers.get(projectId);
      
      // Verifica se il server è ancora attivo
      if (await this.isServerAlive(serverInfo)) {
        return {
          success: true,
          message: 'Progetto già aperto',
          projectId,
          serverInfo: {
            ...serverInfo,
            alreadyOpen: true
          }
        };
      } else {
        // Server morto, rimuovi dal registry
        this.activeServers.delete(projectId);
        this.saveRegistry();
      }
    }

    // Avvia nuovo server per il progetto
    const port = this.nextPort++;
    const serverScript = join(__dirname, '..', 'project-tcp-server.mjs');
    
    console.error(`STARTING: server for project: ${basename(projectPath)}`);
    console.error(`TCP: Porta TCP: ${port}`);
    
    const serverProcess = spawn('node', [serverScript, projectPath, port.toString(), projectId], {
      detached: true,
      stdio: ['ignore', 'pipe', 'pipe']
    });

    const serverInfo = {
      projectId,
      projectPath,
      projectName: basename(projectPath, '.ver'),
      port,
      pid: serverProcess.pid,
      startTime: Date.now(),
      startTimeString: new Date().toLocaleString('it-IT'),
      status: 'starting'
    };

    // Salva nel registry
    this.activeServers.set(projectId, serverInfo);
    this.saveRegistry();

    // Aspetta inizializzazione del server
    return new Promise((resolve) => {
      let initialized = false;
      const timeout = setTimeout(() => {
        if (!initialized) {
          resolve({
            success: false,
            message: 'Timeout inizializzazione server',
            projectId
          });
        }
      }, 300000); // 5 minuti timeout per progetti grandi

      serverProcess.stdout.on('data', (data) => {
        const output = data.toString();
        console.error(`SERVER: ${projectId}:`, output.trim());
        
        if (output.includes('SERVER PRONTO PER CLIENT TCP') && !initialized) {
          initialized = true;
          clearTimeout(timeout);
          
          // Aggiorna status
          serverInfo.status = 'ready';
          this.activeServers.set(projectId, serverInfo);
          this.saveRegistry();
          
          resolve({
            success: true,
            message: `Server progetto avviato su porta ${port}`,
            projectId,
            serverInfo
          });
        }
      });

      serverProcess.stderr.on('data', (data) => {
        const message = data.toString().trim();
        // Distingui tra messaggi informativi e veri errori
        if (message.includes('INIT:') || message.includes('Creating') || message.includes('Starting') || message.includes('Python:')) {
          console.error(`INFO: Server ${projectId}:`, message);
        } else {
          console.error(`ERROR: Server ${projectId} error:`, message);
        }
      });

      serverProcess.on('exit', (code) => {
        console.error(`TERMINATED: Server ${projectId} terminato con codice ${code}`);
        this.activeServers.delete(projectId);
        this.saveRegistry();
      });
    });
  }

  async saveProject(projectId: string, saveAs: string | null = null): Promise<any> {
    const serverInfo = this.activeServers.get(projectId);
    if (!serverInfo) {
      return {
        success: false,
        message: 'Progetto non trovato'
      };
    }

    // Invia comando di salvataggio al server TCP
    return await this.sendCommandToServer(projectId, {
      type: 'save_project',
      saveAs: saveAs
    });
  }

  async closeProject(projectId: string, save: boolean = false): Promise<any> {
    const serverInfo = this.activeServers.get(projectId);
    if (!serverInfo) {
      return {
        success: false,
        message: 'Progetto non trovato'
      };
    }

    console.error(`CLOSING: Chiusura progetto: ${serverInfo.projectName}`);

    try {
      // Salva se richiesto
      if (save) {
        console.error('SAVING: Salvataggio progetto...');
        await this.saveProject(projectId);
      }

      // Invia comando di shutdown al server
      await this.sendCommandToServer(projectId, { type: 'shutdown' });

      // Rimuovi dal registry
      this.activeServers.delete(projectId);
      this.saveRegistry();

      return {
        success: true,
        message: `Progetto ${serverInfo.projectName} chiuso${save ? ' e salvato' : ''}`
      };
    } catch (error) {
      return {
        success: false,
        message: `Errore chiusura progetto: ${(error as Error).message}`
      };
    }
  }

  async executeCommand(projectId: string, code: string, description: string): Promise<any> {
    return await this.sendCommandToServer(projectId, {
      type: 'query',
      code,
      description
    });
  }

  async sendCommandToServer(projectId: string, command: any): Promise<any> {
    const serverInfo = this.activeServers.get(projectId);
    if (!serverInfo) {
      throw new Error('Server progetto non trovato');
    }

    return new Promise((resolve, reject) => {
      const client = createConnection(serverInfo.port, 'localhost');
      let buffer = '';
      
      client.on('connect', () => {
        const message = JSON.stringify({ ...command, requestId: Date.now() });
        client.write(message + '\n');
      });

      client.on('data', (data: any) => {
        buffer += data.toString();
        
        // Dividi per newlines per separare i messaggi
        const messages = buffer.split('\n');
        buffer = messages.pop() || ''; // Mantieni l'ultimo pezzo (potrebbe essere incompleto)
        
        for (const message of messages) {
          if (message.trim()) {
            try {
              // Rimuovi backslash-n letterali che il server TCP Python aggiunge
              const cleanedResponse = message.replace(/\\n$/g, '');
              const response = JSON.parse(cleanedResponse);
              
              // Ignora il messaggio di welcome, aspetta la risposta vera
              if (response.type === 'project_welcome') {
                continue;
              }
              
              // Risposta al comando ricevuta (query_result, save_result, error, etc.)
              if (response.type === 'query_result' || response.type === 'save_result' || 
                  response.type === 'error' || response.type === 'shutdown_ack' ||
                  response.result !== undefined) {
                client.end();
                resolve(response);
                return;
              }
            } catch (error) {
              // Ignora messaggi malformati, continua ad aspettare
              console.error('WARN: Messaggio TCP non parsabile:', message);
            }
          }
        }
      });

      client.on('error', (error: any) => {
        reject(error);
      });

      setTimeout(() => {
        client.end();
        reject(new Error('Timeout comando server'));
      }, 300000); // 5 minuti timeout per operazioni pesanti su reti grandi
    });
  }

  async isServerAlive(serverInfo: any): Promise<boolean> {
    try {
      process.kill(serverInfo.pid, 0);
      return true;
    } catch {
      return false;
    }
  }

  getActiveProjects() {
    const projects = [];
    for (const [projectId, serverInfo] of this.activeServers) {
      projects.push({
        projectId,
        projectName: serverInfo.projectName,
        projectPath: serverInfo.projectPath,
        port: serverInfo.port,
        pid: serverInfo.pid,
        status: serverInfo.status,
        startTime: serverInfo.startTimeString
      });
    }
    return projects;
  }

  async shutdownAll() {
    console.error('SHUTDOWN: Chiusura tutti i server progetti...');
    
    const promises = [];
    for (const projectId of this.activeServers.keys()) {
      promises.push(this.closeProject(projectId, false));
    }
    
    await Promise.all(promises);
    
    // Pulisci registry
    if (existsSync(this.registryFile)) {
      unlinkSync(this.registryFile);
    }
    
    console.error('SUCCESS: Tutti i server progetti chiusi');
  }
}