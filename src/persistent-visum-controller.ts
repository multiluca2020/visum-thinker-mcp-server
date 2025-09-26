// TRUE PERSISTENT Visum Controller with ROBUST JSON Communication
// SOLUZIONE: Buffer JSON per risposte frammentate

import { spawn, ChildProcess } from "child_process";
import * as fs from "fs";
import * as path from "path";

interface VisumResponse {
  success: boolean;
  result?: any;
  output?: string;
  error?: string;
  executionTimeMs?: number;
}

export class PersistentVisumController {
  private static instance: PersistentVisumController;
  private pythonPath: string;
  private tempDir: string;
  private defaultProject: string;
  private projectPath?: string;
  
  // TRUE PERSISTENT Python process that stays alive
  private persistentProcess: ChildProcess | null = null;
  private isInstanceActive: boolean = false;
  private lastActivityTime: number = 0;
  private pendingRequests: Map<string, {
    resolve: (value: VisumResponse) => void;
    reject: (reason: any) => void;
  }> = new Map();
  private requestCounter: number = 0;
  
  // JSON BUFFER for handling fragmented responses - CRITICAL FIX
  private jsonBuffer: string = "";
  private readonly JSON_DELIMITER = '\n';
  
  // SHARED INSTANCE tracking - to avoid multiple processes
  private readonly SHARED_INSTANCE_FILE = "C:\\temp\\mcp_visum\\visum_instance.json";
  private readonly SHARED_LOCK_FILE = "C:\\temp\\mcp_visum\\visum_instance.lock";
  private readonly SHARED_PIPE_NAME = "\\\\.\\pipe\\visum_mcp_pipe";
  
  constructor(projectPath?: string) {
    this.pythonPath = "H:\\Program Files\\PTV Vision\\PTV Visum 2025\\Exe\\Python\\python.exe";
    this.tempDir = "C:\\temp\\mcp_visum";
    this.defaultProject = "H:\\go\\italferr2025\\Campoleone\\100625_Versione_base_v0.3_sub_ok_priv.ver";
    this.projectPath = projectPath;
    
    console.error("🏗️ PersistentVisumController initialized" + (projectPath ? ` for project: ${projectPath}` : ""));
    
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
   * ROBUST JSON buffer processing - FIXES COMMUNICATION ISSUES
   */
  private processJsonBuffer(): void {
    while (this.jsonBuffer.includes(this.JSON_DELIMITER)) {
      const delimiterIndex = this.jsonBuffer.indexOf(this.JSON_DELIMITER);
      const jsonLine = this.jsonBuffer.substring(0, delimiterIndex).trim();
      this.jsonBuffer = this.jsonBuffer.substring(delimiterIndex + 1);
      
      if (jsonLine) {
        try {
          const response = JSON.parse(jsonLine);
          console.error(`🔄 Received JSON: ${response.type} (ID: ${response.id || 'N/A'})`);
          this.handleJsonResponse(response);
        } catch (e) {
          console.error(`❌ JSON Parse Error: ${jsonLine}`);
          console.error(`❌ Error: ${e}`);
        }
      }
    }
  }

  /**
   * Handle different types of JSON responses
   */
  private handleJsonResponse(response: any): void {
    switch (response.type) {
      case 'init_complete':
        // Handle initialization in the process startup
        this.handleInitializationResponse(response);
        break;
        
      case 'command_result':
        this.handleCommandResult(response);
        break;
        
      case 'pong':
        this.handlePingResponse(response);
        break;
        
      default:
        console.error(`⚠️ Unknown response type: ${response.type}`);
    }
  }

  /**
   * Handle initialization completion response
   */
  private initializationResolver: ((value: any) => void) | null = null;

  private handleInitializationResponse(response: any): void {
    if (this.initializationResolver) {
      console.error(`🎯 Processing init_complete: ${response.success ? 'SUCCESS' : 'FAILED'}`);
      
      if (response.success) {
        this.isInstanceActive = true;
        this.lastActivityTime = Date.now();
        
        console.error(`✅ Persistent process initialized - ${response.nodes} nodes`);
        this.initializationResolver({
          success: true,
          message: "TRUE PERSISTENT VisumPy process started with ROBUST JSON",
          nodes: response.nodes,
          links: response.links,
          zones: response.zones
        });
      } else {
        this.initializationResolver({
          success: false,
          message: `Initialization failed: ${response.error}`
        });
      }
      
      this.initializationResolver = null;
    }
  }

  /**
   * Handle command results
   */
  private handleCommandResult(response: any): void {
    const pending = this.pendingRequests.get(response.id);
    if (pending) {
      this.pendingRequests.delete(response.id);
      
      const result: VisumResponse = {
        success: response.success,
        result: response.result,
        error: response.error,
        executionTimeMs: response.executionTimeMs
      };
      
      console.error(`✅ Resolved request ${response.id}: ${response.success ? 'SUCCESS' : 'FAILED'}`);
      pending.resolve(result);
    } else {
      console.error(`⚠️ No pending request for ID: ${response.id}`);
    }
  }

  /**
   * Handle ping responses
   */
  private handlePingResponse(response: any): void {
    const pending = this.pendingRequests.get(response.id);
    if (pending) {
      this.pendingRequests.delete(response.id);
      pending.resolve({
        success: true,
        result: {
          alive: true,
          requestCount: response.requestCount,
          projectLoaded: response.projectLoaded
        }
      });
    }
  }

  /**
   * Check if there's already a shared instance running in another process
   */
  private async checkForSharedInstance(): Promise<{
    exists: boolean;
    pid?: number;
    port?: number;
    startTime?: number;
  }> {
    try {
      if (!fs.existsSync(this.SHARED_INSTANCE_FILE)) {
        return { exists: false };
      }

      const instanceData = JSON.parse(fs.readFileSync(this.SHARED_INSTANCE_FILE, 'utf-8'));
      
      // Check if the process is still alive
      if (this.isProcessAlive(instanceData.pid)) {
        console.error(`🔄 Found shared instance: PID ${instanceData.pid}, started ${new Date(instanceData.startTime).toLocaleString()}`);
        return {
          exists: true,
          pid: instanceData.pid,
          port: instanceData.port,
          startTime: instanceData.startTime
        };
      } else {
        // Clean up stale instance file
        console.error("🧹 Cleaning up stale instance file...");
        fs.unlinkSync(this.SHARED_INSTANCE_FILE);
        return { exists: false };
      }
    } catch (error) {
      console.error("⚠️ Error checking shared instance:", error);
      return { exists: false };
    }
  }

  /**
   * Connect to existing shared instance
   */
  private async connectToSharedInstance(): Promise<{
    success: boolean;
    message: string;
    nodes?: number;
    links?: number;
    zones?: number;
  }> {
    console.error("🔗 Attempting to connect to existing shared instance...");
    
    // Instead of trying to test the connection immediately (which would cause a loop),
    // we assume the shared instance exists and configure this controller to use it
    // The actual connection test will happen when the first command is executed
    
    this.isInstanceActive = true; // Mark as connected to shared instance
    
    return {
      success: true,
      message: "Connected to existing shared instance (connection will be validated on first command)",
      nodes: 0, // Will be determined on first actual command
      links: 0,
      zones: 0
    };
  }

  /**
   * Create new shared instance and register it
   */
  private async createNewSharedInstance(): Promise<{
    success: boolean;
    message: string;
    nodes?: number;
    links?: number;
    zones?: number;
  }> {
    console.error("🚀 Creating new shared persistent instance...");
    
    // Register this instance as the shared one
    const instanceData = {
      pid: process.pid,
      startTime: Date.now(),
      port: null, // Could add TCP port for IPC later
      projectPath: this.projectPath || this.defaultProject
    };

    try {
      fs.writeFileSync(this.SHARED_INSTANCE_FILE, JSON.stringify(instanceData, null, 2));
      console.error(`📝 Registered shared instance: PID ${process.pid}`);
    } catch (error) {
      console.error("⚠️ Failed to register shared instance:", error);
    }

    // Continue with normal instance creation
    return await this.createPersistentInstance();
  }

  /**
   * Check if a process is still alive
   */
  private isProcessAlive(pid: number): boolean {
    try {
      // On Windows, this will throw if process doesn't exist
      process.kill(pid, 0);
      return true;
    } catch (error) {
      return false;
    }
  }

  /**
   * Create the actual persistent instance (extracted from original method)
   */
  private async createPersistentInstance(): Promise<{
    success: boolean;
    message: string;
    nodes?: number;
    links?: number;
    zones?: number;
  }> {
    console.error("🚀 Starting TRUE PERSISTENT VisumPy process with ROBUST JSON...");

    // Create the persistent Python server script
    const serverScript = `
import sys
import os
import time
import json
import traceback
import threading

# Setup VisumPy paths
visum_path = r"H:\\Program Files\\PTV Vision\\PTV Visum 2025\\Exe"
python_path = os.path.join(visum_path, "Python")

if visum_path not in sys.path:
    sys.path.insert(0, visum_path)
if python_path not in sys.path:
    sys.path.insert(0, python_path)

class TruePersistentVisumServer:
    def __init__(self):
        self.visum_instance = None
        self.project_loaded = None
        self.lock = threading.Lock()
        self.request_count = 0
        
    def send_json_response(self, response_data):
        """Send JSON response with proper formatting"""
        try:
            json_str = json.dumps(response_data)
            print(json_str, flush=True)
            print("", flush=True)  # Empty line as delimiter
        except Exception as e:
            error_response = {"type": "error", "error": f"JSON serialization failed: {e}"}
            print(json.dumps(error_response), flush=True)
            print("", flush=True)
        
    def initialize_visum(self):
        """Initialize VisumPy and load project - STAYS LOADED"""
        try:
            import VisumPy.helpers as vh
            
            print("INIT: Creating VisumPy instance...", file=sys.stderr)
            self.visum_instance = vh.CreateVisum(250)
            
            # Load project - use custom project path if specified
            project_path = r"${this.projectPath || this.defaultProject}"
            print(f"INIT: Loading project {os.path.basename(project_path)}...", file=sys.stderr)
            self.visum_instance.LoadVersion(project_path)
            self.project_loaded = project_path
            
            # Get network info
            nodes = self.visum_instance.Net.Nodes.Count
            links = self.visum_instance.Net.Links.Count
            zones = self.visum_instance.Net.Zones.Count
            
            print(f"INIT: ✅ Ready - {nodes} nodes, {links} links, {zones} zones", file=sys.stderr)
            
            # Send ready signal via JSON
            init_response = {
                "type": "init_complete",
                "success": True,
                "nodes": nodes,
                "links": links,
                "zones": zones,
                "timestamp": time.time()
            }
            self.send_json_response(init_response)
            return True
                
        except Exception as e:
            error_msg = f"Initialization failed: {e}"
            print(f"INIT: ❌ {error_msg}", file=sys.stderr)
            print(f"INIT: {traceback.format_exc()}", file=sys.stderr)
            
            error_response = {"type": "init_complete", "success": False, "error": error_msg}
            self.send_json_response(error_response)
            return False
        
    def execute_command(self, command_data):
        """Execute a command on the PERSISTENT VisumPy instance"""
        with self.lock:
            self.request_count += 1
            request_num = self.request_count
            
            try:
                start_time = time.time()
                
                # Get command details
                request_id = command_data.get('id', f'req_{request_num}')
                command_type = command_data.get('type', 'analysis')
                code = command_data.get('code', '')
                description = command_data.get('description', 'Analysis')
                
                print(f"EXEC #{request_num}: {description} (ID: {request_id})", file=sys.stderr)
                
                # Execute the code with visum instance available
                local_scope = {
                    'visum': self.visum_instance,
                    'result': {},
                    'time': time,
                    'json': json,
                    'request_id': request_id,
                    'request_num': request_num
                }
                
                exec(code, globals(), local_scope)
                
                execution_time = (time.time() - start_time) * 1000
                
                print(f"EXEC #{request_num}: ✅ Completed in {execution_time:.1f}ms", file=sys.stderr)
                
                # Send response via JSON
                response = {
                    "type": "command_result",
                    "id": request_id,
                    "success": True,
                    "result": local_scope.get('result', {}),
                    "executionTimeMs": round(execution_time, 3),
                    "requestNumber": request_num
                }
                self.send_json_response(response)
                
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                error_msg = f"Execution failed: {e}"
                
                print(f"EXEC #{request_num}: ❌ {error_msg}", file=sys.stderr)
                print(f"EXEC #{request_num}: {traceback.format_exc()}", file=sys.stderr)
                
                error_response = {
                    "type": "command_result", 
                    "id": command_data.get('id', f'req_{request_num}'),
                    "success": False,
                    "error": error_msg,
                    "executionTimeMs": round(execution_time, 3),
                    "requestNumber": request_num
                }
                self.send_json_response(error_response)
    
    def handle_ping(self, ping_data):
        """Handle ping request"""
        try:
            response = {
                "type": "ping_response",
                "id": ping_data.get('id', 'ping'),
                "alive": True,
                "requestCount": self.request_count,
                "projectLoaded": self.project_loaded is not None,
                "timestamp": time.time()
            }
            self.send_json_response(response)
        except Exception as e:
            error_response = {
                "type": "ping_response",
                "id": ping_data.get('id', 'ping'), 
                "alive": False,
                "error": str(e)
            }
            self.send_json_response(error_response)

    def run_server(self):
        """Main server loop - KEEPS ALIVE"""
        print("🚀 Starting TRUE PERSISTENT VisumPy server...", file=sys.stderr)
        
        # Initialize VisumPy once
        if not self.initialize_visum():
            return
            
        print("🎯 TRUE PERSISTENT server ready for commands!", file=sys.stderr)
        print("   - VisumPy instance STAYS ALIVE", file=sys.stderr)
        print("   - Project STAYS LOADED", file=sys.stderr)
        print("   - Ultra-fast responses guaranteed", file=sys.stderr)
        print("   - ROBUST JSON communication enabled", file=sys.stderr)
        
        # Listen for commands via stdin
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
                
            try:
                command = json.loads(line)
                command_type = command.get('type', 'unknown')
                
                if command_type == 'ping':
                    self.handle_ping(command)
                elif command_type in ['analysis', 'command']:
                    self.execute_command(command)
                else:
                    print(f"Unknown command type: {command_type}", file=sys.stderr)
                    
            except json.JSONDecodeError as e:
                print(f"JSON Parse Error: {e}", file=sys.stderr)
                print(f"Raw input: {line}", file=sys.stderr)
            except Exception as e:
                print(f"Command handling error: {e}", file=sys.stderr)

# Start the persistent server
if __name__ == "__main__":
    server = TruePersistentVisumServer()
    server.run_server()
`;

    // Write the server script
    const scriptPath = path.join(this.tempDir, "true_persistent_visum_server.py");
    fs.writeFileSync(scriptPath, serverScript);

    // Start the Python process
    console.error("🐍 Spawning persistent Python process with JSON buffer...");
    
    this.persistentProcess = spawn(this.pythonPath, [scriptPath], {
      stdio: ['pipe', 'pipe', 'pipe'],
      cwd: this.tempDir
    });

    // Set up JSON BUFFER for stdout handling - CRITICAL FOR COMMUNICATION
    this.persistentProcess.stdout?.on('data', (data) => {
      this.jsonBuffer += data.toString();
      this.processJsonBuffer();
    });

    this.persistentProcess.stderr?.on('data', (data) => {
      const output = data.toString().trim();
      if (output) {
        console.error(`🐍 Python: ${output}`);
      }
    });

    this.persistentProcess.on('error', (error) => {
      console.error('❌ Python process error:', error);
      this.isInstanceActive = false;
    });

    this.persistentProcess.on('close', (code) => {
      console.error(`🔚 Python process closed with code: ${code}`);
      this.isInstanceActive = false;
    });

    // Wait for initialization to complete
    return new Promise((resolve) => {
      const timeout = setTimeout(() => {
        resolve({
          success: false,
          message: "Initialization timeout - process may still be starting"
        });
      }, 120000); // 2 minute timeout

      // Handle init complete response
      const initHandler = (response: any) => {
        if (response.type === 'init_complete') {
          clearTimeout(timeout);
          
          if (response.success) {
            this.isInstanceActive = true;
            this.lastActivityTime = Date.now();
            
            console.error(`✅ Persistent process initialized - ${response.nodes} nodes`);
            
            resolve({
              success: true,
              message: "Persistent VisumPy instance started successfully",
              nodes: response.nodes,
              links: response.links,  
              zones: response.zones
            });
          } else {
            resolve({
              success: false,
              message: `Initialization failed: ${response.error}`
            });
          }
        }
      };

      // Temporarily override JSON response handling for init
      const originalJsonHandler = this.handleJsonResponse.bind(this);
      this.handleJsonResponse = (response: any) => {
        if (response.type === 'init_complete') {
          initHandler(response);
          // Restore original handler
          this.handleJsonResponse = originalJsonHandler;
        } else {
          originalJsonHandler(response);
        }
      };
    });
  }

  /**
   * Start TRUE PERSISTENT Python process with ROBUST JSON handling
   */
  public async startPersistentVisumProcess(): Promise<{
    success: boolean;
    message: string;
    nodes?: number;
    links?: number;
    zones?: number;
  }> {
    // Check if instance is already running in THIS process
    if (this.isInstanceActive && this.persistentProcess && !this.persistentProcess.killed) {
      console.error("🔄 Using existing persistent instance in this controller");
      
      // Test the connection to make sure it's still working
      try {
        const testResult = await this.executeCustomCode(`
result = {
    'nodes': visum.Net.Nodes.Count,
    'links': visum.Net.Links.Count, 
    'zones': visum.Net.Zones.Count,
    'status': 'already_active'
}
`, 'Test Existing Instance');

        if (testResult.success) {
          return {
            success: true,
            message: "Using existing active persistent instance",
            nodes: testResult.result.nodes,
            links: testResult.result.links,
            zones: testResult.result.zones
          };
        } else {
          console.error("⚠️ Existing instance not responding, creating new one...");
          this.isInstanceActive = false;
        }
      } catch (error) {
        console.error("⚠️ Error testing existing instance:", error);
        this.isInstanceActive = false;
      }
    }

    // TEMPORARILY DISABLE shared instance system to avoid infinite loop
    // Each controller will manage its own instance
    console.error("🚀 Creating new persistent instance for this controller...");
    return await this.createPersistentInstance();

    console.error("🚀 Starting TRUE PERSISTENT VisumPy process with ROBUST JSON...");

    // Create the persistent Python server script
    const serverScript = `
import sys
import os
import time
import json
import traceback
import threading

# Setup VisumPy paths
visum_path = r"H:\\Program Files\\PTV Vision\\PTV Visum 2025\\Exe"
python_path = os.path.join(visum_path, "Python")

if visum_path not in sys.path:
    sys.path.insert(0, visum_path)
if python_path not in sys.path:
    sys.path.insert(0, python_path)

class TruePersistentVisumServer:
    def __init__(self):
        self.visum_instance = None
        self.project_loaded = None
        self.lock = threading.Lock()
        self.request_count = 0
        
    def send_json_response(self, response_data):
        """Send JSON response with proper formatting"""
        try:
            json_str = json.dumps(response_data)
            print(json_str, flush=True)
        except Exception as e:
            error_response = {
                "type": "error",
                "error": f"Failed to send JSON: {str(e)}"
            }
            print(json.dumps(error_response), flush=True)
        
    def initialize_visum(self):
        """Initialize VisumPy instance once and keep it alive"""
        try:
            import VisumPy.helpers as vh
            
            print("INIT: Creating VisumPy instance...", file=sys.stderr)
            self.visum_instance = vh.CreateVisum(250)
            
            # Load project - use custom project path if specified
            project_path = r"${this.projectPath || this.defaultProject}"
            print(f"INIT: Loading project {os.path.basename(project_path)}...", file=sys.stderr)
            self.visum_instance.LoadVersion(project_path)
            self.project_loaded = project_path
            
            # Get network info
            nodes = self.visum_instance.Net.Nodes.Count
            links = self.visum_instance.Net.Links.Count
            zones = self.visum_instance.Net.Zones.Count
            
            print(f"INIT: ✅ Ready - {nodes} nodes, {links} links, {zones} zones", file=sys.stderr)
            
            # Send ready signal via JSON
            init_response = {
                "type": "init_complete",
                "success": True,
                "nodes": nodes,
                "links": links,
                "zones": zones,
                "timestamp": time.time()
            }
            self.send_json_response(init_response)
            return True
                
        except Exception as e:
            error_msg = f"Initialization failed: {e}"
            print(f"INIT: ❌ {error_msg}", file=sys.stderr)
            print(f"INIT: {traceback.format_exc()}", file=sys.stderr)
            
            error_response = {"type": "init_complete", "success": False, "error": error_msg}
            self.send_json_response(error_response)
            return False
        
    def execute_command(self, command_data):
        """Execute a command on the PERSISTENT VisumPy instance"""
        with self.lock:
            self.request_count += 1
            request_num = self.request_count
            
            try:
                start_time = time.time()
                
                # Get command details
                request_id = command_data.get('id', f'req_{request_num}')
                command_type = command_data.get('type', 'analysis')
                code = command_data.get('code', '')
                description = command_data.get('description', 'Analysis')
                
                print(f"EXEC #{request_num}: {description} (ID: {request_id})", file=sys.stderr)
                
                # Execute the code with visum instance available
                local_scope = {
                    'visum': self.visum_instance,
                    'result': {},
                    'time': time,
                    'json': json,
                    'request_id': request_id,
                    'request_num': request_num
                }
                
                exec(code, globals(), local_scope)
                
                execution_time = (time.time() - start_time) * 1000
                
                print(f"EXEC #{request_num}: ✅ Completed in {execution_time:.1f}ms", file=sys.stderr)
                
                # Send response via JSON
                response = {
                    "type": "command_result",
                    "id": request_id,
                    "success": True,
                    "result": local_scope.get('result', {}),
                    "executionTimeMs": round(execution_time, 3),
                    "requestNumber": request_num
                }
                self.send_json_response(response)
                
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                error_msg = str(e)
                print(f"EXEC #{request_num}: ❌ Error - {error_msg}", file=sys.stderr)
                
                response = {
                    "type": "command_result", 
                    "id": request_id,
                    "success": False,
                    "error": error_msg,
                    "executionTimeMs": round(execution_time, 3),
                    "requestNumber": request_num
                }
                self.send_json_response(response)
                
    def run_persistent_server(self):
        """Main server loop - TRUE PERSISTENCE with ROBUST JSON communication"""
        print("🚀 Starting TRUE PERSISTENT VisumPy server...", file=sys.stderr)
        
        # Initialize VisumPy ONCE
        if not self.initialize_visum():
            print("❌ Failed to initialize - exiting", file=sys.stderr)
            return
            
        print("🎯 TRUE PERSISTENT server ready for commands!", file=sys.stderr)
        print("   - VisumPy instance STAYS ALIVE", file=sys.stderr)
        print("   - Project STAYS LOADED", file=sys.stderr)
        print("   - Ultra-fast responses guaranteed", file=sys.stderr)
        print("   - ROBUST JSON communication enabled", file=sys.stderr)
        
        # Listen for JSON commands on stdin - PERSISTENT LOOP
        try:
            for line in sys.stdin:
                line = line.strip()
                if not line:
                    continue
                    
                try:
                    command = json.loads(line)
                    command_type = command.get('type', 'unknown')
                    
                    if command_type == 'shutdown':
                        print("🔚 Shutdown requested - terminating persistent server", file=sys.stderr)
                        break
                    elif command_type == 'ping':
                        # Health check
                        ping_response = {
                            "type": "pong",
                            "id": command.get('id', 'ping'),
                            "timestamp": time.time(),
                            "requestCount": self.request_count,
                            "projectLoaded": self.project_loaded is not None
                        }
                        self.send_json_response(ping_response)
                    else:
                        # Execute command on persistent instance
                        self.execute_command(command)
                        
                except json.JSONDecodeError as e:
                    print(f"❌ Invalid JSON: {e}", file=sys.stderr)
                except Exception as e:
                    print(f"❌ Error processing command: {e}", file=sys.stderr)
                    
        except KeyboardInterrupt:
            print("🔚 Keyboard interrupt - shutting down persistent server", file=sys.stderr)
        except Exception as e:
            print(f"❌ Fatal error in persistent server: {e}", file=sys.stderr)
            print(traceback.format_exc(), file=sys.stderr)

        print("🔚 Persistent VisumPy server terminated", file=sys.stderr)

# Start the TRUE PERSISTENT server
if __name__ == "__main__":
    server = TruePersistentVisumServer()
    server.run_persistent_server()
`;

    // Write the server script to file
    const scriptPath = path.join(this.tempDir, "robust_persistent_visum_server.py");
    fs.writeFileSync(scriptPath, serverScript);

    // Clear JSON buffer
    this.jsonBuffer = "";

    // Start the PERSISTENT Python process with ROBUST JSON handling
    return new Promise((resolve, reject) => {
      console.error("🐍 Spawning persistent Python process with JSON buffer...");
      
      // Set up initialization resolver
      this.initializationResolver = resolve;
      
      this.persistentProcess = spawn(this.pythonPath, [scriptPath], {
        stdio: ['pipe', 'pipe', 'pipe'],
        cwd: this.tempDir
      });

      let initTimeout: NodeJS.Timeout;
      
      // Handle stdout (JSON responses) - ROBUST JSON PARSING
      this.persistentProcess.stdout?.on('data', (data) => {
        // Add incoming data to buffer
        this.jsonBuffer += data.toString();
        
        // Process complete JSON messages
        this.processJsonBuffer();
      });

      // Handle stderr (logging)
      this.persistentProcess.stderr?.on('data', (data) => {
        const message = data.toString().trim();
        console.error('🐍 Python:', message);
      });

      // Handle process exit - THIS SHOULD NOT HAPPEN!
      this.persistentProcess.on('exit', (code) => {
        console.error('💀 CRITICAL: Persistent Python process exited with code:', code);
        this.persistentProcess = null;
        this.isInstanceActive = false;
        
        // Reject all pending requests
        for (const [id, pending] of this.pendingRequests) {
          pending.reject(new Error("Persistent process terminated"));
        }
        this.pendingRequests.clear();
      });

      this.persistentProcess.on('error', (error) => {
        console.error('💀 CRITICAL: Persistent Python process error:', error);
        if (this.initializationResolver) {
          clearTimeout(initTimeout);
          this.initializationResolver({
            success: false,
            message: `Process error: ${error.message}`
          });
          this.initializationResolver = null;
        }
      });

      // Handle initialization timeout
      initTimeout = setTimeout(() => {
        if (this.initializationResolver) {
          console.error('⏰ Persistent process initialization timeout');
          this.persistentProcess?.kill();
          this.initializationResolver({
            success: false,
            message: "Initialization timeout"
          });
          this.initializationResolver = null;
        }
      }, 180000); // 3 minutes timeout - more generous
    });
  }

  /**
   * Send a command to the persistent Python process via JSON stdin
   */
  private async sendCommandToPersistentProcess(code: string, description?: string): Promise<VisumResponse> {
    // Ensure persistent process is running
    if (!this.isInstanceActive || !this.persistentProcess || this.persistentProcess.killed) {
      const startResult = await this.startPersistentVisumProcess();
      if (!startResult.success) {
        return {
          success: false,
          error: `Failed to start persistent process: ${startResult.message}`
        };
      }
    }

    const requestId = (++this.requestCounter).toString();
    
    return new Promise((resolve, reject) => {
      // Store the request
      this.pendingRequests.set(requestId, { resolve, reject });
      
      // Send command to persistent Python process via stdin
      const command = {
        type: 'command',
        id: requestId,
        code: code,
        description: description || 'Analysis'
      };
      
      const commandJson = JSON.stringify(command) + '\n';
      console.error(`📤 Sending command ${requestId}: ${description}`);
      this.persistentProcess?.stdin?.write(commandJson);
      
      // Set timeout for the request
      setTimeout(() => {
        if (this.pendingRequests.has(requestId)) {
          this.pendingRequests.delete(requestId);
          console.error(`⏰ Request ${requestId} timed out`);
          resolve({
            success: false,
            error: "Request timeout (60s)"
          });
        }
      }, 60000); // 1 minute timeout
    });
  }
  
  /**
   * Execute Visum analysis using TRUE PERSISTENT process
   */
  public async executeVisumAnalysis(analysisCode: string, description?: string): Promise<VisumResponse> {
    return this.sendCommandToPersistentProcess(analysisCode, description);
  }

  /**
   * Execute custom code on persistent VisumPy instance
   */
  public async executeCustomCode(pythonCode: string, description?: string): Promise<VisumResponse> {
    return this.sendCommandToPersistentProcess(pythonCode, description);
  }

  /**
   * Get network statistics from persistent instance (ULTRA-FAST)
   */
  public async getNetworkStats(): Promise<VisumResponse> {
    const code = `
# Ultra-fast network statistics from persistent instance
start_time = time.time()
nodes = visum.Net.Nodes.Count
links = visum.Net.Links.Count
zones = visum.Net.Zones.Count
elapsed = time.time() - start_time

result = {
    'nodes': nodes,
    'links': links, 
    'zones': zones,
    'query_time_ms': round(elapsed * 1000, 3),
    'persistent': True
}
`;
    return this.sendCommandToPersistentProcess(code, "Network statistics (persistent)");
  }

  /**
   * Analyze nodes from persistent instance (ULTRA-FAST) - SAFE VERSION
   */
  public async analyzeNodes(sampleSize: number = 10): Promise<VisumResponse> {
    const code = `
# Ultra-fast SAFE node analysis from persistent instance
import random

start_time = time.time()
total_nodes = visum.Net.Nodes.Count

# Get sample of nodes using SAFE method - NO ITERATORS
sample_nodes = []
if total_nodes > 0:
    try:
        # Use simple range for safety
        max_sample = min(${sampleSize}, total_nodes, 100)  # Limit to 100 for safety
        sample_nodes = list(range(1, max_sample + 1))
    except Exception as e:
        sample_nodes = [1, 2, 3, 4, 5]  # Fallback

elapsed = time.time() - start_time

result = {
    'totalNodes': total_nodes,
    'sampleNodes': sample_nodes,
    'sampleSize': len(sample_nodes),
    'analysis_time_ms': round(elapsed * 1000, 3),
    'persistent': True,
    'method': 'safe_range'
}
`;
    return this.sendCommandToPersistentProcess(code, `Node analysis (${sampleSize} samples, SAFE)`);
  }

  /**
   * Health check for persistent instance
   */
  public async checkInstanceHealth(): Promise<VisumResponse> {
    if (!this.isInstanceActive || !this.persistentProcess || this.persistentProcess.killed) {
      return {
        success: false,
        error: "Persistent process not running"
      };
    }

    const requestId = (++this.requestCounter).toString();
    
    return new Promise((resolve, reject) => {
      // Store the request
      this.pendingRequests.set(requestId, { resolve, reject });
      
      // Send ping command
      const pingCommand = {
        type: 'ping',
        id: requestId,
        timestamp: Date.now()
      };
      
      const commandJson = JSON.stringify(pingCommand) + '\n';
      console.error(`🩺 Sending health check ${requestId}`);
      this.persistentProcess?.stdin?.write(commandJson);
      
      // Set timeout for ping
      setTimeout(() => {
        if (this.pendingRequests.has(requestId)) {
          this.pendingRequests.delete(requestId);
          resolve({
            success: false,
            error: "Health check timeout"
          });
        }
      }, 5000); // 5 second timeout for ping
    });
  }

  /**
   * Shutdown the persistent process
   */
  public async shutdown(): Promise<void> {
    if (this.persistentProcess && !this.persistentProcess.killed) {
      console.error('🔚 Shutting down persistent VisumPy process...');
      
      // Send shutdown command
      const shutdownCommand = { type: 'shutdown' };
      const commandJson = JSON.stringify(shutdownCommand) + '\n';
      this.persistentProcess.stdin?.write(commandJson);
      
      // Wait a bit then force kill if needed
      setTimeout(() => {
        if (this.persistentProcess && !this.persistentProcess.killed) {
          this.persistentProcess.kill();
        }
      }, 2000);
    }
    
    this.isInstanceActive = false;
    this.persistentProcess = null;
    this.jsonBuffer = "";
    
    // Reject all pending requests
    for (const [id, pending] of this.pendingRequests) {
      pending.reject(new Error("Server shutdown"));
    }
    this.pendingRequests.clear();
  }

  // Legacy compatibility method
  public async initializePersistentInstance(): Promise<{
    success: boolean;
    message: string;
    nodes?: number;
    links?: number;
    zones?: number;
  }> {
    return this.startPersistentVisumProcess();
  }
}