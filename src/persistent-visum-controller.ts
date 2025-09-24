// Visum Controller with Persistent VisumPy Instance
// SOLUZIONE: Istanza VisumPy globale persistente per performance ottimale

import { spawn } from "child_process";
import * as fs from "fs";
import * as path from "path";

export class PersistentVisumController {
  private static instance: PersistentVisumController;
  private pythonPath: string;
  private tempDir: string;
  private defaultProject: string;
  
  // Persistent Python process for VisumPy instance
  private persistentProcess: any = null;
  private isInstanceActive: boolean = false;
  private lastActivityTime: number = 0;
  
  private constructor() {
    this.pythonPath = "H:\\Program Files\\PTV Vision\\PTV Visum 2025\\Exe\\Python\\python.exe";
    this.tempDir = "C:\\temp\\mcp_visum";
    this.defaultProject = "H:\\go\\italferr2025\\Campoleone\\100625_Versione_base_v0.3_sub_ok_priv.ver";
    
    // Ensure temp directory exists
    if (!fs.existsSync(this.tempDir)) {
      fs.mkdirSync(this.tempDir, { recursive: true });
    }
  }
  
  public static getInstance(): PersistentVisumController {
    if (!PersistentVisumController.instance) {
      PersistentVisumController.instance = new PersistentVisumController();
    }
    return PersistentVisumController.instance;
  }
  
  /**
   * Initialize persistent VisumPy instance
   * Creates global instance that stays alive for fast subsequent access
   */
  public async initializePersistentInstance(): Promise<{
    success: boolean;
    message: string;
    nodes?: number;
    links?: number;
    zones?: number;
  }> {
    if (this.isInstanceActive) {
      return { success: true, message: "Persistent instance already active" };
    }
    
    const initCode = `
import sys
import os
import json
import time
import traceback

# Setup VisumPy paths
visum_path = r"H:\\Program Files\\PTV Vision\\PTV Visum 2025\\Exe"
python_path = os.path.join(visum_path, "Python")

if visum_path not in sys.path:
    sys.path.insert(0, visum_path)
if python_path not in sys.path:
    sys.path.insert(0, python_path)

# Global VisumPy instance - SOLUZIONE CHIAVE
GLOBAL_VISUM_INSTANCE = None
GLOBAL_PROJECT_LOADED = None

def initialize_visum():
    global GLOBAL_VISUM_INSTANCE, GLOBAL_PROJECT_LOADED
    
    try:
        import VisumPy.helpers as vh
        
        print("Creating persistent VisumPy instance...")
        GLOBAL_VISUM_INSTANCE = vh.CreateVisum(250)
        
        # Load default project
        project_path = r"${this.defaultProject}"
        print(f"Loading project: {project_path}")
        GLOBAL_VISUM_INSTANCE.LoadVersion(project_path)
        GLOBAL_PROJECT_LOADED = project_path
        
        # Get network info
        nodes = GLOBAL_VISUM_INSTANCE.Net.Nodes.Count
        links = GLOBAL_VISUM_INSTANCE.Net.Links.Count
        zones = GLOBAL_VISUM_INSTANCE.Net.Zones.Count
        
        result = {
            "success": True,
            "message": "Persistent VisumPy instance initialized",
            "nodes": nodes,
            "links": links,
            "zones": zones,
            "timestamp": time.time()
        }
        
        print(f"SUCCESS: {result}")
        
        # Save instance info
        with open(r"${this.tempDir}\\persistent_visum_init.json", 'w') as f:
            json.dump(result, f, indent=2)
            
        return result
        
    except Exception as e:
        error_result = {
            "success": False,
            "message": f"Failed to initialize VisumPy: {str(e)}",
            "error": traceback.format_exc(),
            "timestamp": time.time()
        }
        
        print(f"ERROR: {error_result}")
        
        with open(r"${this.tempDir}\\persistent_visum_error.json", 'w') as f:
            json.dump(error_result, f, indent=2)
            
        return error_result

# Initialize and keep instance alive
if __name__ == "__main__":
    result = initialize_visum()
    
    # Keep process alive for persistent instance
    if result["success"]:
        print("Persistent VisumPy instance ready. Keeping alive...")
        
        # Stay alive and respond to commands
        while True:
            try:
                # Check for commands in temp directory
                command_file = r"${this.tempDir}\\visum_command.json"
                
                if os.path.exists(command_file):
                    print("Processing command...")
                    
                    with open(command_file, 'r') as f:
                        command = json.load(f)
                    
                    # Execute command using global instance
                    if GLOBAL_VISUM_INSTANCE:
                        command_result = execute_visum_command(command)
                        
                        # Save result
                        result_file = r"${this.tempDir}\\visum_result.json"
                        with open(result_file, 'w') as f:
                            json.dump(command_result, f, indent=2)
                    
                    # Remove command file
                    os.remove(command_file)
                
                time.sleep(0.1)  # Small delay to prevent CPU spinning
                
            except KeyboardInterrupt:
                print("Shutting down persistent VisumPy instance...")
                break
            except Exception as e:
                print(f"Error in persistent loop: {e}")
                time.sleep(1)
    
    print("Persistent VisumPy instance terminated.")

def execute_visum_command(command):
    """Execute command using global VisumPy instance"""
    global GLOBAL_VISUM_INSTANCE
    
    try:
        command_type = command.get("type", "unknown")
        
        if command_type == "network_stats":
            return {
                "success": True,
                "nodes": GLOBAL_VISUM_INSTANCE.Net.Nodes.Count,
                "links": GLOBAL_VISUM_INSTANCE.Net.Links.Count,
                "zones": GLOBAL_VISUM_INSTANCE.Net.Zones.Count,
                "timestamp": time.time()
            }
        elif command_type == "node_analysis":
            nodes = GLOBAL_VISUM_INSTANCE.Net.Nodes
            if nodes.Count > 0:
                sample_nodes = nodes.GetMultiAttValues('No')[:10]
                return {
                    "success": True,
                    "sample_nodes": sample_nodes,
                    "total_nodes": nodes.Count,
                    "timestamp": time.time()
                }
        elif command_type == "custom_python":
            # Execute custom Python code with Visum instance available
            code = command.get("code", "")
            local_vars = {"visum": GLOBAL_VISUM_INSTANCE}
            exec(code, globals(), local_vars)
            
            return {
                "success": True,
                "message": "Custom code executed",
                "timestamp": time.time()
            }
        else:
            return {
                "success": False,
                "message": f"Unknown command type: {command_type}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "message": f"Command execution failed: {str(e)}",
            "error": traceback.format_exc(),
            "timestamp": time.time()
        }
`;
    
    try {
      const result = await this.runPython(initCode);
      
      if (result.success) {
        // Check for initialization result
        const resultFile = path.join(this.tempDir, "persistent_visum_init.json");
        
        if (fs.existsSync(resultFile)) {
          const initResult = JSON.parse(fs.readFileSync(resultFile, 'utf-8'));
          
          if (initResult.success) {
            this.isInstanceActive = true;
            this.lastActivityTime = Date.now();
            
            return {
              success: true,
              message: "Persistent VisumPy instance initialized successfully",
              nodes: initResult.nodes,
              links: initResult.links,
              zones: initResult.zones
            };
          }
        }
      }
      
      return {
        success: false,
        message: `Failed to initialize persistent instance: ${result.error || result.output}`
      };
      
    } catch (error) {
      return {
        success: false,
        message: `Initialization error: ${error instanceof Error ? error.message : String(error)}`
      };
    }
  }
  
  /**
   * Execute command using persistent VisumPy instance
   */
  public async executeVisumCommand(commandType: string, parameters: any = {}): Promise<{
    success: boolean;
    data?: any;
    message?: string;
    error?: string;
  }> {
    if (!this.isInstanceActive) {
      // Try to initialize if not active
      const initResult = await this.initializePersistentInstance();
      if (!initResult.success) {
        return {
          success: false,
          message: "Persistent instance not available and initialization failed"
        };
      }
    }
    
    try {
      // Create command file
      const command = {
        type: commandType,
        parameters,
        timestamp: Date.now()
      };
      
      const commandFile = path.join(this.tempDir, "visum_command.json");
      const resultFile = path.join(this.tempDir, "visum_result.json");
      
      // Remove old result file
      if (fs.existsSync(resultFile)) {
        fs.unlinkSync(resultFile);
      }
      
      // Write command
      fs.writeFileSync(commandFile, JSON.stringify(command, null, 2));
      
      // Wait for result (max 10 seconds)
      const maxWaitTime = 10000;
      const startTime = Date.now();
      
      while (!fs.existsSync(resultFile) && (Date.now() - startTime) < maxWaitTime) {
        await new Promise(resolve => setTimeout(resolve, 100));
      }
      
      if (!fs.existsSync(resultFile)) {
        return {
          success: false,
          message: "Command timeout - no response from persistent instance"
        };
      }
      
      // Read result
      const result = JSON.parse(fs.readFileSync(resultFile, 'utf-8'));
      
      // Cleanup
      if (fs.existsSync(resultFile)) {
        fs.unlinkSync(resultFile);
      }
      
      this.lastActivityTime = Date.now();
      
      return {
        success: result.success,
        data: result,
        message: result.message
      };
      
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : String(error),
        message: "Command execution failed"
      };
    }
  }
  
  /**
   * Get network statistics using persistent instance
   */
  public async getNetworkStats(): Promise<{
    success: boolean;
    nodes?: number;
    links?: number;
    zones?: number;
    message?: string;
  }> {
    const result = await this.executeVisumCommand("network_stats");
    
    if (result.success && result.data) {
      return {
        success: true,
        nodes: result.data.nodes,
        links: result.data.links,
        zones: result.data.zones
      };
    }
    
    return {
      success: false,
      message: result.message || "Failed to get network statistics"
    };
  }
  
  /**
   * Analyze nodes using persistent instance
   */
  public async analyzeNodes(): Promise<{
    success: boolean;
    sampleNodes?: any[];
    totalNodes?: number;
    message?: string;
  }> {
    const result = await this.executeVisumCommand("node_analysis");
    
    if (result.success && result.data) {
      return {
        success: true,
        sampleNodes: result.data.sample_nodes,
        totalNodes: result.data.total_nodes
      };
    }
    
    return {
      success: false,
      message: result.message || "Failed to analyze nodes"
    };
  }
  
  /**
   * Execute custom Python code with Visum instance
   */
  public async executeCustomPython(code: string): Promise<{
    success: boolean;
    message?: string;
    error?: string;
  }> {
    const result = await this.executeVisumCommand("custom_python", { code });
    
    return {
      success: result.success,
      message: result.message,
      error: result.error
    };
  }
  
  /**
   * Check if persistent instance is still active
   */
  public async checkInstanceHealth(): Promise<{
    active: boolean;
    lastActivity: number;
    uptime: number;
  }> {
    const statsResult = await this.getNetworkStats();
    const currentTime = Date.now();
    
    if (statsResult.success) {
      this.lastActivityTime = currentTime;
      
      return {
        active: true,
        lastActivity: this.lastActivityTime,
        uptime: currentTime - this.lastActivityTime
      };
    }
    
    return {
      active: false,
      lastActivity: this.lastActivityTime,
      uptime: 0
    };
  }
  
  /**
   * Utility method to run Python code
   */
  private async runPython(code: string): Promise<{
    success: boolean;
    output: string;
    error?: string;
    exitCode: number;
  }> {
    return new Promise((resolve) => {
      const tempFile = path.join(this.tempDir, `visum_${Date.now()}.py`);
      
      try {
        fs.writeFileSync(tempFile, code);
        
        const process = spawn('powershell.exe', [
          '-Command',
          `& "${this.pythonPath}" "${tempFile}"`
        ]);
        
        let output = '';
        let errorOutput = '';
        
        process.stdout.on('data', (data) => {
          output += data.toString();
        });
        
        process.stderr.on('data', (data) => {
          errorOutput += data.toString();
        });
        
        process.on('close', (code) => {
          try {
            if (fs.existsSync(tempFile)) {
              fs.unlinkSync(tempFile);
            }
          } catch (e) {
            // Ignore cleanup errors
          }
          
          resolve({
            success: code === 0 && !errorOutput,
            output: output.trim(),
            error: errorOutput.trim() || undefined,
            exitCode: code || 0
          });
        });
        
      } catch (error) {
        resolve({
          success: false,
          output: '',
          error: error instanceof Error ? error.message : String(error),
          exitCode: -1
        });
      }
    });
  }
}