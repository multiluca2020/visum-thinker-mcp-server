// PROJECT SERVER MANAGER - Gestisce server TCP dedicati per ogni progetto Visum
import { spawn } from 'child_process';
import { writeFileSync, readFileSync, existsSync, unlinkSync } from 'fs';
import { join, basename } from 'path';
import { createServer } from 'net';

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
    const serverScript = join(process.cwd(), 'project-tcp-server.mjs');
    
    console.log(`🚀 Avvio server per progetto: ${basename(projectPath)}`);
    console.log(`📡 Porta TCP: ${port}`);
    
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
      }, 120000); // 2 minuti timeout

      serverProcess.stdout.on('data', (data) => {
        const output = data.toString();
        console.log(`📊 Server ${projectId}:`, output.trim());
        
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
        console.error(`❌ Server ${projectId} error:`, data.toString().trim());
      });

      serverProcess.on('exit', (code) => {
        console.log(`🔴 Server ${projectId} terminato con codice ${code}`);
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

    console.log(`🔴 Chiusura progetto: ${serverInfo.projectName}`);

    try {
      // Salva se richiesto
      if (save) {
        console.log('💾 Salvataggio progetto...');
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
      const client = require('net').createConnection(serverInfo.port, 'localhost');
      
      client.on('connect', () => {
        const message = JSON.stringify({ ...command, requestId: Date.now() });
        client.write(message + '\n');
      });

      client.on('data', (data: any) => {
        try {
          const response = JSON.parse(data.toString().trim());
          client.end();
          resolve(response);
        } catch (error) {
          client.end();
          reject(new Error('Errore parsing risposta server'));
        }
      });

      client.on('error', (error: any) => {
        reject(error);
      });

      setTimeout(() => {
        client.end();
        reject(new Error('Timeout comando server'));
      }, 30000);
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
    console.log('🔴 Chiusura tutti i server progetti...');
    
    const promises = [];
    for (const projectId of this.activeServers.keys()) {
      promises.push(this.closeProject(projectId, false));
    }
    
    await Promise.all(promises);
    
    // Pulisci registry
    if (existsSync(this.registryFile)) {
      unlinkSync(this.registryFile);
    }
    
    console.log('✅ Tutti i server progetti chiusi');
  }
}