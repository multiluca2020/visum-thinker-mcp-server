// Simple Direct Visum Controller - NO server process needed!
// SOLUZIONE FINALE: Approccio diretto con istanza VisumPy mantenuta in memoria

import { spawn } from "child_process";
import * as fs from "fs";
import * as path from "path";

export class SimpleVisumController {
  private static instance: SimpleVisumController;
  private pythonPath: string;
  private tempDir: string;
  private defaultProject: string;
  private isInitialized: boolean = false;
  
  private constructor() {
    this.pythonPath = "H:\\Program Files\\PTV Vision\\PTV Visum 2025\\Exe\\Python\\python.exe";
    this.tempDir = "C:\\temp\\mcp_visum";
    this.defaultProject = "H:\\go\\italferr2025\\Campoleone\\100625_Versione_base_v0.3_sub_ok_priv.ver";
    
    // Ensure temp directory exists
    if (!fs.existsSync(this.tempDir)) {
      fs.mkdirSync(this.tempDir, { recursive: true });
    }
  }
  
  public static getInstance(): SimpleVisumController {
    if (!SimpleVisumController.instance) {
      SimpleVisumController.instance = new SimpleVisumController();
    }
    return SimpleVisumController.instance;
  }
  
  /**
   * Execute Visum analysis with the simple direct approach
   * Creates VisumPy instance once, reuses for all subsequent calls
   */
  public async executeVisumAnalysis(analysisCode: string, description?: string): Promise<{
    success: boolean;
    result?: any;
    output?: string;
    error?: string;
    executionTimeMs?: number;
  }> {
    const startTime = Date.now();
    
    // Create the complete Python script with Direct Manager
    const pythonScript = `
import sys
import os
import time
import json
import traceback

# Setup VisumPy paths
visum_path = r"H:\\Program Files\\PTV Vision\\PTV Visum 2025\\Exe"
python_path = os.path.join(visum_path, "Python")

if visum_path not in sys.path:
    sys.path.insert(0, visum_path)
if python_path not in sys.path:
    sys.path.insert(0, python_path)

# Global instance manager (singleton pattern)
class DirectVisumManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.visum_instance = None
            cls._instance.project_loaded = None
            cls._instance.initialization_time = None
        return cls._instance
        
    def initialize_visum(self):
        """Initialize VisumPy instance once"""
        if self.visum_instance is None:
            try:
                init_start = time.time()
                import VisumPy.helpers as vh
                
                print("Creating VisumPy instance...")
                self.visum_instance = vh.CreateVisum(250)
                
                # Load default project
                project_path = r"${this.defaultProject}"
                print(f"Loading project: {os.path.basename(project_path)}")
                self.visum_instance.LoadVersion(project_path)
                self.project_loaded = project_path
                
                self.initialization_time = time.time() - init_start
                
                nodes = self.visum_instance.Net.Nodes.Count
                print(f"✅ Initialized in {self.initialization_time:.3f}s: {nodes:,} nodes")
                return True
                
            except Exception as e:
                print(f"❌ Initialization failed: {e}")
                traceback.print_exc()
                return False
        else:
            print("✅ Using existing VisumPy instance")
            return True
    
    def execute_analysis(self, analysis_code, description=""):
        """Execute analysis code on the active VisumPy instance"""
        if not self.initialize_visum():
            return {"success": False, "error": "Failed to initialize Visum"}
        
        try:
            exec_start = time.time()
            
            # Create namespace with visum available
            namespace = {
                'visum': self.visum_instance,
                'json': json,
                'time': time,
                'os': os,
                'result': {},  # Where analysis stores results
                'print': print  # Enable printing from analysis code
            }
            
            # Execute the analysis code
            print(f"🔍 Executing: {description}")
            exec(analysis_code, namespace)
            
            exec_time = time.time() - exec_start
            
            # Get results
            analysis_result = namespace.get('result', {})
            
            # Add execution info
            final_result = {
                "success": True,
                "analysis_result": analysis_result,
                "execution_time_ms": round(exec_time * 1000, 3),
                "initialization_time_s": self.initialization_time,
                "description": description,
                "timestamp": time.time()
            }
            
            print(f"✅ Analysis completed in {exec_time*1000:.3f}ms")
            return final_result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": f"Analysis execution failed: {str(e)}",
                "traceback": traceback.format_exc(),
                "description": description
            }
            print(f"❌ Analysis failed: {e}")
            return error_result
    
    def get_instance_info(self):
        """Get current instance information"""
        if self.visum_instance:
            try:
                return {
                    "active": True,
                    "nodes": self.visum_instance.Net.Nodes.Count,
                    "links": self.visum_instance.Net.Links.Count,
                    "zones": self.visum_instance.Net.Zones.Count,
                    "project": self.project_loaded,
                    "initialization_time": self.initialization_time
                }
            except Exception as e:
                return {"active": False, "error": f"Instance not accessible: {e}"}
        return {"active": False, "error": "Instance not created"}

# Execute the analysis
try:
    manager = DirectVisumManager()
    
    # Analysis code to execute
    analysis_code = """${analysisCode}"""
    
    result = manager.execute_analysis(analysis_code, "${description || 'Visum Analysis'}")
    
    # Save result to file for retrieval
    result_file = r"${path.join(this.tempDir, `visum_result_${Date.now()}.json`)}"
    with open(result_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    # Print result for immediate feedback
    print("\\n" + "="*50)
    print("ANALYSIS RESULT:")
    print(json.dumps(result, indent=2))
    print("="*50)
    
    # Also print result file location
    print(f"\\nResult saved to: {result_file}")

except Exception as e:
    error_result = {
        "success": False,
        "error": f"Script execution failed: {str(e)}",
        "traceback": traceback.format_exc()
    }
    
    print("\\n" + "="*50)
    print("SCRIPT ERROR:")
    print(json.dumps(error_result, indent=2))
    print("="*50)
`;

    try {
      const pythonResult = await this.runPython(pythonScript);
      const executionTime = Date.now() - startTime;
      
      // Try to parse result from output
      let analysisResult = null;
      
      if (pythonResult.success && pythonResult.output) {
        // Look for JSON result in output
        const lines = pythonResult.output.split('\n');
        let jsonStart = -1;
        let jsonEnd = -1;
        
        for (let i = 0; i < lines.length; i++) {
          if (lines[i].includes('ANALYSIS RESULT:')) {
            jsonStart = i + 1;
          }
          if (jsonStart >= 0 && lines[i].includes('====================')) {
            jsonEnd = i;
            break;
          }
        }
        
        if (jsonStart >= 0 && jsonEnd >= 0) {
          try {
            const jsonText = lines.slice(jsonStart, jsonEnd).join('\n');
            analysisResult = JSON.parse(jsonText);
          } catch (parseError) {
            // Fallback: try to find result file
            const resultFiles = fs.readdirSync(this.tempDir)
              .filter(f => f.startsWith('visum_result_'))
              .sort()
              .reverse();
            
            if (resultFiles.length > 0) {
              const latestResult = path.join(this.tempDir, resultFiles[0]);
              try {
                analysisResult = JSON.parse(fs.readFileSync(latestResult, 'utf-8'));
                // Cleanup
                fs.unlinkSync(latestResult);
              } catch (fileError) {
                // Could not parse result file
              }
            }
          }
        }
      }
      
      return {
        success: pythonResult.success && (analysisResult?.success !== false),
        result: analysisResult,
        output: pythonResult.output,
        error: pythonResult.error,
        executionTimeMs: executionTime
      };
      
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : String(error),
        executionTimeMs: Date.now() - startTime
      };
    }
  }
  
  /**
   * Get basic network statistics
   */
  public async getNetworkStats(): Promise<{
    success: boolean;
    nodes?: number;
    links?: number;
    zones?: number;
    executionTimeMs?: number;
  }> {
    const analysisCode = `
# Basic network statistics
nodes = visum.Net.Nodes.Count
links = visum.Net.Links.Count
zones = visum.Net.Zones.Count

result['network_stats'] = {
    'nodes': nodes,
    'links': links,
    'zones': zones,
    'timestamp': time.time()
}

print(f"Network: {nodes:,} nodes, {links:,} links, {zones:,} zones")
`;

    const analysisResult = await this.executeVisumAnalysis(analysisCode, "Network Statistics");
    
    if (analysisResult.success && analysisResult.result?.analysis_result?.network_stats) {
      const stats = analysisResult.result.analysis_result.network_stats;
      return {
        success: true,
        nodes: stats.nodes,
        links: stats.links,
        zones: stats.zones,
        executionTimeMs: analysisResult.executionTimeMs
      };
    }
    
    return {
      success: false,
      executionTimeMs: analysisResult.executionTimeMs
    };
  }
  
  /**
   * Analyze network nodes
   */
  public async analyzeNodes(sampleSize: number = 10): Promise<{
    success: boolean;
    totalNodes?: number;
    sampleNodes?: any[];
    executionTimeMs?: number;
  }> {
    const analysisCode = `
# Node analysis
node_container = visum.Net.Nodes
total_nodes = node_container.Count

sample_nodes = []
if total_nodes > 0:
    # Get sample of nodes with their IDs
    try:
        sample_size = min(${sampleSize}, total_nodes)
        node_ids = node_container.GetMultiAttValues('No')[:sample_size]
        sample_nodes = node_ids
    except Exception as e:
        print(f"Warning: Could not get node details: {e}")
        sample_nodes = []

result['node_analysis'] = {
    'total_nodes': total_nodes,
    'sample_nodes': sample_nodes,
    'sample_size': len(sample_nodes)
}

print(f"Analyzed {total_nodes:,} nodes, sampled {len(sample_nodes)}")
`;

    const analysisResult = await this.executeVisumAnalysis(analysisCode, `Node Analysis (sample: ${sampleSize})`);
    
    if (analysisResult.success && analysisResult.result?.analysis_result?.node_analysis) {
      const nodeData = analysisResult.result.analysis_result.node_analysis;
      return {
        success: true,
        totalNodes: nodeData.total_nodes,
        sampleNodes: nodeData.sample_nodes,
        executionTimeMs: analysisResult.executionTimeMs
      };
    }
    
    return {
      success: false,
      executionTimeMs: analysisResult.executionTimeMs
    };
  }
  
  /**
   * Execute custom Python code with Visum instance
   */
  public async executeCustomCode(pythonCode: string, description?: string): Promise<{
    success: boolean;
    result?: any;
    output?: string;
    error?: string;
    executionTimeMs?: number;
  }> {
    return this.executeVisumAnalysis(pythonCode, description || "Custom Analysis");
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
      const tempFile = path.join(this.tempDir, `simple_visum_${Date.now()}.py`);
      
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