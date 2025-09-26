// Project-Specific Persistent Instance Manager
// Gestisce istanze persistenti dedicate per ogni progetto Visum

import { PersistentVisumController } from "./persistent-visum-controller.js";

interface ProjectConfig {
  name: string;
  projectPath: string;
  description: string;
  autoStart?: boolean;
}

interface ProjectInstance {
  config: ProjectConfig;
  controller: PersistentVisumController;
  isActive: boolean;
  startTime?: number;
  lastUsed?: number;
  stats?: {
    nodes: number;
    links: number;
    zones: number;
  };
}

export class ProjectInstanceManager {
  private static instance: ProjectInstanceManager;
  private projectInstances: Map<string, ProjectInstance> = new Map();

  // Configurazioni progetti predefinite
  private readonly PROJECT_CONFIGS: { [key: string]: ProjectConfig } = {
    campoleone: {
      name: "Campoleone",
      projectPath: "H:\\go\\italferr2025\\Campoleone\\100625_Versione_base_v0.3_sub_ok_priv.ver",
      description: "Progetto Campoleone - Rete ferroviaria principale",
      autoStart: true
    },
    // Aggiungi altri progetti qui
    testProject: {
      name: "Test Project", 
      projectPath: "H:\\path\\to\\test\\project.ver",
      description: "Progetto di test per sviluppo",
      autoStart: false
    }
  };

  private constructor() {
    console.error("🏗️ Project Instance Manager initialized");
  }

  public static getInstance(): ProjectInstanceManager {
    if (!ProjectInstanceManager.instance) {
      ProjectInstanceManager.instance = new ProjectInstanceManager();
    }
    return ProjectInstanceManager.instance;
  }

  /**
   * Avvia istanza persistente per progetto specifico
   */
  public async startProjectInstance(projectId: string): Promise<{
    success: boolean;
    message: string;
    stats?: any;
  }> {
    console.error(`🚀 Starting persistent instance for project: ${projectId}`);

    const config = this.PROJECT_CONFIGS[projectId];
    if (!config) {
      return {
        success: false,
        message: `Unknown project ID: ${projectId}. Available: ${Object.keys(this.PROJECT_CONFIGS).join(', ')}`
      };
    }

    // Verifica se l'istanza è già attiva
    if (this.projectInstances.has(projectId)) {
      const existing = this.projectInstances.get(projectId)!;
      if (existing.isActive) {
        return {
          success: true,
          message: `Project ${config.name} instance already running`,
          stats: existing.stats
        };
      }
    }

    try {
      const startTime = Date.now();
      
      // Crea controller personalizzato per questo progetto
      const controller = new PersistentVisumController(config.projectPath);
      
      const result = await controller.startPersistentVisumProcess();
      
      if (result.success) {
        const projectInstance: ProjectInstance = {
          config,
          controller,
          isActive: true,
          startTime,
          lastUsed: Date.now(),
          stats: {
            nodes: result.nodes || 0,
            links: result.links || 0,
            zones: result.zones || 0
          }
        };

        this.projectInstances.set(projectId, projectInstance);

        console.error(`✅ Project ${config.name} instance started successfully`);
        console.error(`   📊 Network: ${result.nodes} nodes, ${result.links} links, ${result.zones} zones`);
        console.error(`   ⏱️ Startup time: ${Date.now() - startTime}ms`);

        return {
          success: true,
          message: `Persistent instance for ${config.name} started successfully`,
          stats: projectInstance.stats
        };
      } else {
        return {
          success: false,
          message: `Failed to start ${config.name}: ${result.message}`
        };
      }
    } catch (error) {
      return {
        success: false,
        message: `Error starting ${config.name}: ${error instanceof Error ? error.message : String(error)}`
      };
    }
  }

  /**
   * Esegue analisi complessa su istanza progetto specifica
   */
  public async executeProjectAnalysis(projectId: string, analysisCode: string, description?: string): Promise<{
    success: boolean;
    result?: any;
    error?: string;
    executionTimeMs?: number;
    projectInfo?: any;
  }> {
    const instance = this.projectInstances.get(projectId);
    
    if (!instance || !instance.isActive) {
      // Prova ad avviare l'istanza automaticamente
      console.error(`⚠️ Instance for ${projectId} not active, starting automatically...`);
      const startResult = await this.startProjectInstance(projectId);
      
      if (!startResult.success) {
        return {
          success: false,
          error: `Instance not available and auto-start failed: ${startResult.message}`
        };
      }

      // Riprendi l'istanza appena avviata
      const newInstance = this.projectInstances.get(projectId)!;
      return this.executeOnInstance(newInstance, analysisCode, description);
    }

    return this.executeOnInstance(instance, analysisCode, description);
  }

  private async executeOnInstance(instance: ProjectInstance, analysisCode: string, description?: string): Promise<{
    success: boolean;
    result?: any;
    error?: string;
    executionTimeMs?: number;
    projectInfo?: any;
  }> {
    try {
      instance.lastUsed = Date.now();
      
      const result = await instance.controller.executeCustomCode(analysisCode, description);
      
      return {
        success: result.success,
        result: result.result,
        error: result.error,
        executionTimeMs: result.executionTimeMs,
        projectInfo: {
          projectName: instance.config.name,
          projectId: instance.config.name.toLowerCase(),
          stats: instance.stats
        }
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : String(error)
      };
    }
  }

  /**
   * Get status di tutte le istanze attive
   */
  public getInstancesStatus(): { [projectId: string]: any } {
    const status: { [projectId: string]: any } = {};
    
    for (const [projectId, instance] of this.projectInstances) {
      status[projectId] = {
        name: instance.config.name,
        description: instance.config.description,
        isActive: instance.isActive,
        startTime: instance.startTime,
        lastUsed: instance.lastUsed,
        uptime: instance.startTime ? Date.now() - instance.startTime : 0,
        stats: instance.stats
      };
    }
    
    return status;
  }

  /**
   * Health check per istanza specifica
   */
  public async checkProjectHealth(projectId: string): Promise<{
    success: boolean;
    health?: any;
    error?: string;
  }> {
    const instance = this.projectInstances.get(projectId);
    
    if (!instance || !instance.isActive) {
      return {
        success: false,
        error: `Project instance ${projectId} not active`
      };
    }

    try {
      const healthResult = await instance.controller.checkInstanceHealth();
      
      return {
        success: healthResult.success,
        health: {
          ...healthResult.result,
          projectName: instance.config.name,
          uptime: Date.now() - (instance.startTime || Date.now()),
          lastUsed: instance.lastUsed
        },
        error: healthResult.error
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : String(error)
      };
    }
  }

  /**
   * Shutdown istanza progetto specifica
   */
  public async shutdownProjectInstance(projectId: string): Promise<{
    success: boolean;
    message: string;
  }> {
    const instance = this.projectInstances.get(projectId);
    
    if (!instance) {
      return {
        success: false,
        message: `Project instance ${projectId} not found`
      };
    }

    try {
      await instance.controller.shutdown();
      instance.isActive = false;
      this.projectInstances.delete(projectId);
      
      console.error(`🔚 Project ${instance.config.name} instance shutdown completed`);
      
      return {
        success: true,
        message: `Project ${instance.config.name} instance shutdown successfully`
      };
    } catch (error) {
      return {
        success: false,
        message: `Error shutting down ${instance.config.name}: ${error instanceof Error ? error.message : String(error)}`
      };
    }
  }

  /**
   * Shutdown tutte le istanze
   */
  public async shutdownAllInstances(): Promise<void> {
    console.error("🔚 Shutting down all project instances...");
    
    const shutdownPromises = Array.from(this.projectInstances.keys()).map(
      projectId => this.shutdownProjectInstance(projectId)
    );
    
    await Promise.all(shutdownPromises);
    
    console.error("✅ All project instances shutdown completed");
  }

  /**
   * Auto-start istanze configurate per l'avvio automatico
   */
  public async autoStartInstances(): Promise<void> {
    console.error("🚀 Auto-starting configured project instances...");
    
    for (const [projectId, config] of Object.entries(this.PROJECT_CONFIGS)) {
      if (config.autoStart) {
        console.error(`⚡ Auto-starting ${config.name}...`);
        const result = await this.startProjectInstance(projectId);
        
        if (result.success) {
          console.error(`✅ ${config.name} auto-started successfully`);
        } else {
          console.error(`❌ Failed to auto-start ${config.name}: ${result.message}`);
        }
      }
    }
  }
}