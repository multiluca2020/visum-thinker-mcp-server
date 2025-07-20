// Visum COM API Integration for MCP Server
import { spawn } from "child_process";
import * as fs from "fs";
import * as path from "path";

interface VisumConfig {
  knownInstallations: Array<{
    path: string;
    version: string;
    lastVerified: string;
  }>;
  preferredPath?: string;
  lastUpdated: string;
}

// Visum integration class using PowerShell COM
export class VisumController {
  private visumPaths = [
    'C:\\Program Files\\PTV Vision\\PTV Visum 2024\\Exe\\Visum240.exe',
    'C:\\Program Files\\PTV Vision\\PTV Visum 2023\\Exe\\Visum230.exe', 
    'C:\\Program Files\\PTV Vision\\PTV Visum 2022\\Exe\\Visum220.exe',
    'C:\\Program Files\\PTV Vision\\PTV Visum 2021\\Exe\\Visum210.exe',
    'C:\\Program Files\\PTV Vision\\PTV Visum 2025\\Exe\\Visum250.exe',
    'C:\\Program Files (x86)\\PTV Vision\\PTV Visum 2024\\Exe\\Visum240.exe',
    'C:\\Program Files (x86)\\PTV Vision\\PTV Visum 2023\\Exe\\Visum230.exe',
    'C:\\Program Files (x86)\\PTV Vision\\PTV Visum 2022\\Exe\\Visum220.exe',
    'C:\\Program Files (x86)\\PTV Vision\\PTV Visum 2021\\Exe\\Visum210.exe'
  ];

  private configPath = path.join(process.cwd(), 'visum-config.json');
  private currentModel: string | null = null;
  private visumInstance: any = null;
  private comAvailable: boolean | null = null;
  private demoMode: boolean = false; // Enable demo mode when Visum is not available
  private customVisumPath: string | null = null; // Store custom Visum path

  // Load configuration from file
  private loadConfig(): VisumConfig {
    try {
      if (fs.existsSync(this.configPath)) {
        const configData = fs.readFileSync(this.configPath, 'utf8');
        const config = JSON.parse(configData) as VisumConfig;
        
        // Verify stored installations are still valid
        config.knownInstallations = config.knownInstallations.filter(install => {
          return fs.existsSync(install.path);
        });
        
        return config;
      }
    } catch (error) {
      console.error('Error loading Visum config:', error);
    }
    
    return {
      knownInstallations: [],
      lastUpdated: new Date().toISOString()
    };
  }

  // Save configuration to file
  private saveConfig(config: VisumConfig): void {
    try {
      config.lastUpdated = new Date().toISOString();
      fs.writeFileSync(this.configPath, JSON.stringify(config, null, 2), 'utf8');
    } catch (error) {
      console.error('Error saving Visum config:', error);
    }
  }

  // Add a new installation to the known list
  private addKnownInstallation(path: string, version: string): void {
    const config = this.loadConfig();
    
    // Check if installation already exists
    const existingIndex = config.knownInstallations.findIndex(install => install.path === path);
    
    if (existingIndex >= 0) {
      // Update existing installation
      config.knownInstallations[existingIndex] = {
        path,
        version,
        lastVerified: new Date().toISOString()
      };
    } else {
      // Add new installation
      config.knownInstallations.push({
        path,
        version,
        lastVerified: new Date().toISOString()
      });
    }

    // Set as preferred if it's the first one or if no preferred exists
    if (!config.preferredPath || config.knownInstallations.length === 1) {
      config.preferredPath = path;
    }

    this.saveConfig(config);
  }

  // Get all known installations, prioritizing preferred path
  private getKnownInstallations(): Array<{path: string, version: string}> {
    const config = this.loadConfig();
    const installations = config.knownInstallations.map(install => ({
      path: install.path,
      version: install.version
    }));

    // Sort to put preferred path first
    if (config.preferredPath) {
      installations.sort((a, b) => {
        if (a.path === config.preferredPath) return -1;
        if (b.path === config.preferredPath) return 1;
        return 0;
      });
    }

    return installations;
  }

  // Check if Visum is installed (enhanced version with custom path support)
  async isVisumAvailable(customPath?: string): Promise<{ 
    available: boolean; 
    path?: string; 
    version?: string; 
    comRegistered?: boolean;
    installations?: Array<{path: string, version: string}>;
    error?: string;
    suggestCustomPath?: boolean;
  }> {
    try {
      // Start with known installations from config
      const installations: Array<{path: string, version: string}> = [];
      const knownInstallations = this.getKnownInstallations();
      
      // Check known installations first (they're sorted with preferred first)
      for (const known of knownInstallations) {
        if (fs.existsSync(known.path)) {
          installations.push(known);
        }
      }
      
      // If custom path is provided, validate and prioritize it
      if (customPath) {
        console.error(`Checking custom Visum path: ${customPath}`);
        if (await this.validateVisumPath(customPath)) {
          const version = this.extractVersionFromPath(customPath);
          const customInstallation = { path: customPath, version };
          
          // Remove if it already exists in the list
          const existingIndex = installations.findIndex(inst => inst.path === customPath);
          if (existingIndex >= 0) {
            installations.splice(existingIndex, 1);
          }
          
          // Add to front of list
          installations.unshift(customInstallation);
          this.customVisumPath = customPath; // Store for later use
          
          // Save this as a known installation
          this.addKnownInstallation(customPath, version);
          
          console.error(`✅ Valid Visum installation found at: ${customPath}`);
        } else {
          return {
            available: false,
            comRegistered: (await this.checkComRegistration()).registered,
            error: `Invalid Visum installation at custom path: ${customPath}. Please check the path and ensure it points to a Visum executable.`,
            suggestCustomPath: false
          };
        }
      }
      
      // Check standard paths for new installations
      for (const visumPath of this.visumPaths) {
        if (fs.existsSync(visumPath)) {
          const version = this.extractVersionFromPath(visumPath);
          if (!installations.some(i => i.path === visumPath)) {
            installations.push({ path: visumPath, version });
            // Save this as a new known installation
            this.addKnownInstallation(visumPath, version);
          }
        }
      }

      // Check for custom installations in PTV Vision folders
      const basePaths = [
        'C:\\Program Files\\PTV Vision',
        'C:\\Program Files (x86)\\PTV Vision'
      ];

      for (const basePath of basePaths) {
        if (fs.existsSync(basePath)) {
          try {
            const dirs = fs.readdirSync(basePath, { withFileTypes: true });
            for (const dir of dirs) {
              if (dir.isDirectory() && dir.name.includes('Visum')) {
                const exePath = path.join(basePath, dir.name, 'Exe');
                if (fs.existsSync(exePath)) {
                  const exeFiles = fs.readdirSync(exePath).filter(f => f.startsWith('Visum') && f.endsWith('.exe'));
                  for (const exeFile of exeFiles) {
                    const fullPath = path.join(exePath, exeFile);
                    const version = this.extractVersionFromPath(fullPath) || dir.name;
                    if (!installations.some(i => i.path === fullPath)) {
                      installations.push({ path: fullPath, version });
                      // Save this as a new known installation
                      this.addKnownInstallation(fullPath, version);
                    }
                  }
                }
              }
            }
          } catch (scanError) {
            // Continue if we can't scan a directory
          }
        }
      }

      // Check COM registration
      const comCheck = await this.checkComRegistration();
      
      if (installations.length > 0) {
        // Sort installations by preference (custom path first, then newest versions)
        installations.sort((a, b) => {
          if (a.path === this.customVisumPath) return -1;
          if (b.path === this.customVisumPath) return 1;
          return b.version.localeCompare(a.version);
        });

        return { 
          available: true, 
          path: installations[0].path, 
          version: installations[0].version,
          comRegistered: comCheck.registered,
          installations,
          error: comCheck.registered ? undefined : 'COM objects not registered - you may need to run Visum as Administrator once to register COM components',
          suggestCustomPath: false
        };
      } else {
        return { 
          available: false,
          comRegistered: comCheck.registered,
          error: 'No Visum installations found in standard directories',
          suggestCustomPath: true // Suggest user to provide custom path
        };
      }
    } catch (error) {
      return {
        available: false,
        comRegistered: false,
        error: `Error checking Visum availability: ${error instanceof Error ? error.message : String(error)}`,
        suggestCustomPath: true
      };
    }
  }

  private extractVersionFromPath(path: string): string {
    const match = path.match(/Visum(\d{3})/);
    if (match) {
      const year = 2000 + parseInt(match[1].substring(0, 2));
      return `${year}`;
    }
    return 'Unknown';
  }

  // Validate if a given path is a valid Visum installation
  private async validateVisumPath(customPath: string): Promise<boolean> {
    try {
      // Check if the path exists
      if (!fs.existsSync(customPath)) {
        return false;
      }

      // Check if it's a file and ends with .exe
      const stats = fs.statSync(customPath);
      if (!stats.isFile() || !customPath.toLowerCase().endsWith('.exe')) {
        return false;
      }

      // Check if the filename contains "Visum"
      const filename = path.basename(customPath).toLowerCase();
      if (!filename.includes('visum')) {
        return false;
      }

      // Try to get file version information (optional - just log if fails)
      try {
        const fileSize = stats.size;
        console.error(`Visum executable found: ${customPath} (${(fileSize / 1024 / 1024).toFixed(2)} MB)`);
      } catch (versionError) {
        // Continue validation even if version check fails
      }

      return true;
    } catch (error) {
      console.error(`Error validating Visum path: ${error instanceof Error ? error.message : String(error)}`);
      return false;
    }
  }

  // Check COM registration
  private async checkComRegistration(): Promise<{ registered: boolean; error?: string }> {
    const script = `
      try {
        # Try to find Visum COM objects in registry
        $comObjects = Get-WmiObject -Class Win32_ClassicCOMClass -ErrorAction SilentlyContinue | Where-Object { 
          $_.ProgId -like "*Visum*" -or $_.LocalServer32 -like "*Visum*" 
        }
        
        if ($comObjects) {
          $result = @{
            "registered" = $true
            "objects" = @()
          }
          
          foreach ($obj in $comObjects) {
            $result.objects += @{
              "progId" = $obj.ProgId
              "server" = $obj.LocalServer32
            }
          }
          
          $result | ConvertTo-Json -Depth 3
        } else {
          @{"registered" = $false} | ConvertTo-Json
        }
        
      } catch {
        @{"registered" = $false; "error" = $_.Exception.Message} | ConvertTo-Json
      }
    `;

    try {
      const result = await this.executePowerShellCommand(script);
      if (result.success) {
        if (typeof result.result === 'string') {
          const parsed = JSON.parse(result.result);
          return { registered: parsed.registered || false, error: parsed.error };
        }
        return { registered: result.result?.registered || false };
      } else {
        return { registered: false, error: result.error };
      }
    } catch (error) {
      return { registered: false, error: error instanceof Error ? error.message : String(error) };
    }
  }

  // Execute PowerShell COM commands to control Visum
  async executePowerShellCommand(script: string): Promise<{ success: boolean; result?: any; error?: string }> {
    return new Promise((resolve) => {
      const powershell = spawn('powershell', [
        '-Command', 
        '-', // Read from stdin
      ], {
        stdio: ['pipe', 'pipe', 'pipe']
      });

      let output = '';
      let errorOutput = '';

      powershell.stdout.on('data', (data) => {
        output += data.toString();
      });

      powershell.stderr.on('data', (data) => {
        errorOutput += data.toString();
      });

      powershell.on('close', (code) => {
        if (code === 0) {
          try {
            // Try to parse JSON output if possible
            let result = output.trim();
            if (result.startsWith('{') || result.startsWith('[')) {
              result = JSON.parse(result);
            }
            resolve({ success: true, result });
          } catch {
            resolve({ success: true, result: output.trim() });
          }
        } else {
          resolve({ 
            success: false, 
            error: errorOutput || `PowerShell exited with code ${code}` 
          });
        }
      });

      // Send the PowerShell script
      powershell.stdin.write(script);
      powershell.stdin.end();
    });
  }

  // Initialize Visum COM object (enhanced with error handling and demo mode)
  async initializeVisum(): Promise<{ success: boolean; error?: string; details?: any }> {
    // First check if COM is available
    if (this.comAvailable === false) {
      // Enable demo mode for systems without Visum
      this.demoMode = true;
      return { 
        success: true, 
        error: undefined,
        details: {
          success: true,
          message: "Demo mode enabled - Visum COM objects are not available. All operations will be simulated.",
          demoMode: true,
          logDir: process.env.TEMP || 'C:\\temp'
        }
      };
    }

    const script = `
      try {
        # Create temp directory for logs if needed
        $tempDir = $env:TEMP
        $logDir = Join-Path $tempDir "VisumMCP"
        if (-not (Test-Path $logDir)) {
          New-Item -ItemType Directory -Path $logDir -Force | Out-Null
        }
        
        # Set environment variables to avoid log directory issues
        $env:VISUM_LOG_DIR = $logDir
        $env:VISUM_TEMP_DIR = $logDir
        
        Write-Host "Creating Visum COM object..."
        $visum = New-Object -ComObject "Visum.Visum" -ErrorAction Stop
        
        if ($visum) {
          Write-Host "SUCCESS: Visum COM object created"
          
          # Try to set automation mode (may not be available in all versions)
          try {
            $visum.SetAttValue('AppMode', 1)
            Write-Host "Visum set to automation mode"
          } catch {
            Write-Host "Warning: Could not set automation mode (may not be supported): $($_.Exception.Message)"
          }
          
          # Get version info if possible
          try {
            $version = $visum.GetAttValue('VersionStr')
            Write-Host "Visum version: $version"
          } catch {
            Write-Host "Could not retrieve version information"
          }
          
          # Test basic functionality
          try {
            $netCount = 0
            if ($visum.Net) {
              Write-Host "Network object accessible"
            }
            
            @{
              "success" = $true
              "message" = "Visum COM initialized successfully"
              "logDir" = $logDir
              "demoMode" = $false
            } | ConvertTo-Json
            
          } catch {
            Write-Host "Warning: Some network functions may not be available: $($_.Exception.Message)"
            @{
              "success" = $true
              "message" = "Visum COM initialized with limited functionality"
              "warning" = $_.Exception.Message
              "logDir" = $logDir
              "demoMode" = $false
            } | ConvertTo-Json
          }
          
        } else {
          Write-Error "Failed to create Visum COM object"
          exit 1
        }
        
      } catch {
        $errorMsg = $_.Exception.Message
        Write-Error "Failed to create Visum COM object: $errorMsg"
        
        # Provide detailed troubleshooting information
        @{
          "success" = $false
          "error" = $errorMsg
          "troubleshooting" = @(
            "1. Ensure Visum is properly installed",
            "2. Run Visum manually as Administrator at least once",
            "3. Check if Visum COM components are registered",
            "4. Verify Visum license is valid",
            "5. Try restarting Windows after Visum installation"
          )
          "demoMode" = $false
        } | ConvertTo-Json
        
        exit 1
      }
    `;

    const result = await this.executePowerShellCommand(script);
    
    if (!result.success) {
      // Enable demo mode on failure
      this.demoMode = true;
      this.comAvailable = false;
      
      return { 
        success: true, 
        error: undefined,
        details: {
          success: true,
          message: "Demo mode enabled - Visum COM initialization failed. All operations will be simulated.",
          demoMode: true,
          originalError: result.error,
          logDir: process.env.TEMP || 'C:\\temp'
        }
      };
    }
    
    // Cache COM availability result
    this.comAvailable = result.success;
    
    if (result.success && typeof result.result === 'string') {
      try {
        const parsed = JSON.parse(result.result);
        return { 
          success: parsed.success, 
          error: parsed.error, 
          details: parsed 
        };
      } catch {
        return result;
      }
    }
    
    return result;
  }

  // Load a Visum model (enhanced with demo mode)
  async loadModel(modelPath: string): Promise<{ success: boolean; modelInfo?: any; error?: string }> {
    // Demo mode simulation
    if (this.demoMode) {
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate loading time
      
      const demoModelInfo = {
        modelPath: modelPath,
        nodes: 1247,
        links: 3156,
        zones: 89,
        loadedAt: new Date().toString(),
        demoMode: true
      };
      
      this.currentModel = modelPath;
      return { success: true, modelInfo: demoModelInfo };
    }

    if (!fs.existsSync(modelPath)) {
      return { success: false, error: `Model file not found: ${modelPath}` };
    }

    const script = `
      try {
        $visum = New-Object -ComObject "Visum.Visum"
        $visum.LoadVersion("${modelPath.replace(/\\/g, '\\\\')}")
        
        # Get basic model information
        $nodeCount = $visum.Net.Nodes.Count
        $linkCount = $visum.Net.Links.Count
        $zoneCount = $visum.Net.Zones.Count
        
        $modelInfo = @{
          "modelPath" = "${modelPath}"
          "nodes" = $nodeCount
          "links" = $linkCount  
          "zones" = $zoneCount
          "loadedAt" = (Get-Date).ToString()
          "demoMode" = $false
        }
        
        $modelInfo | ConvertTo-Json
        
      } catch {
        Write-Error "Failed to load model: $_"
        exit 1
      }
    `;

    const result = await this.executePowerShellCommand(script);
    if (result.success) {
      this.currentModel = modelPath;
      return { success: true, modelInfo: result.result };
    }
    
    return result;
  }

  // Get network statistics (enhanced with demo mode)
  async getNetworkStats(): Promise<{ success: boolean; stats?: any; error?: string }> {
    // Demo mode simulation
    if (this.demoMode) {
      await new Promise(resolve => setTimeout(resolve, 500)); // Simulate processing time
      
      const demoStats = {
        nodes: 1247,
        links: 3156,
        zones: 89,
        lines: 45,
        stops: 234,
        timeProfiles: 12,
        vehicleJourneys: 1678,
        demoMode: true
      };
      
      return { success: true, stats: demoStats };
    }

    const script = `
      try {
        $visum = New-Object -ComObject "Visum.Visum"
        
        if ($visum.Net -eq $null) {
          Write-Error "No network loaded"
          exit 1
        }
        
        $stats = @{
          "nodes" = $visum.Net.Nodes.Count
          "links" = $visum.Net.Links.Count
          "zones" = $visum.Net.Zones.Count
          "lines" = $visum.Net.Lines.Count
          "stops" = $visum.Net.Stops.Count
          "timeProfiles" = $visum.Net.TimeProfiles.Count
          "vehicleJourneys" = $visum.Net.VehicleJourneys.Count
          "demoMode" = $false
        }
        
        $stats | ConvertTo-Json
        
      } catch {
        Write-Error "Failed to get network stats: $_"
        exit 1
      }
    `;

    return await this.executePowerShellCommand(script);
  }

  // Run procedure (enhanced with demo mode)
  async runProcedure(procedureNumber: number, parameters?: Record<string, any>): Promise<{ success: boolean; result?: any; error?: string }> {
    // Demo mode simulation
    if (this.demoMode) {
      await new Promise(resolve => setTimeout(resolve, 2000)); // Simulate procedure execution time
      
      const procedureNames: { [key: number]: string } = {
        1: "Traffic Assignment",
        2: "Public Transport Assignment", 
        3: "Dynamic Traffic Assignment",
        4: "Route Search",
        5: "Network Analysis"
      };
      
      const procedureName = procedureNames[procedureNumber] || `Procedure ${procedureNumber}`;
      
      return { 
        success: true, 
        result: `Demo: ${procedureName} completed successfully (simulated)` 
      };
    }

    const script = `
      try {
        $visum = New-Object -ComObject "Visum.Visum"
        
        Write-Output "Running procedure ${procedureNumber}..."
        $visum.Procedures.Execute(${procedureNumber})
        Write-Output "Procedure ${procedureNumber} completed successfully"
        
      } catch {
        Write-Error "Failed to run procedure ${procedureNumber}: $_"
        exit 1
      }
    `;

    return await this.executePowerShellCommand(script);
  }

  // Execute custom VBScript (enhanced with demo mode)
  async executeCustomScript(vbScript: string): Promise<{ success: boolean; result?: any; error?: string }> {
    // Demo mode simulation
    if (this.demoMode) {
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate script execution time
      
      return { 
        success: true, 
        result: `Demo: Custom VBScript executed successfully (simulated)\nScript length: ${vbScript.length} characters` 
      };
    }

    // Create temporary VBS file
    const tempPath = path.join(process.cwd(), `visum_script_${Date.now()}.vbs`);
    
    try {
      fs.writeFileSync(tempPath, vbScript);

      const script = `
        try {
          $visum = New-Object -ComObject "Visum.Visum"
          $visum.Procedures.ExecuteVBSFile("${tempPath.replace(/\\/g, '\\\\')}")
          Write-Output "Custom script executed successfully"
          
        } catch {
          Write-Error "Failed to execute custom script: $_"
          exit 1
        }
      `;

      const result = await this.executePowerShellCommand(script);
      
      // Cleanup temp file
      if (fs.existsSync(tempPath)) {
        fs.unlinkSync(tempPath);
      }
      
      return result;
      
    } catch (error) {
      // Cleanup temp file on error
      if (fs.existsSync(tempPath)) {
        fs.unlinkSync(tempPath);
      }
      
      return { 
        success: false, 
        error: `Failed to create/execute script: ${error instanceof Error ? error.message : String(error)}` 
      };
    }
  }

  // Get current model info
  getCurrentModel(): string | null {
    return this.currentModel;
  }

  // Check if running in demo mode
  isDemoMode(): boolean {
    return this.demoMode;
  }

  // Get demo status information
  getDemoStatus(): { demoMode: boolean; reason?: string; comAvailable?: boolean } {
    return {
      demoMode: this.demoMode,
      reason: this.demoMode ? 'Visum COM objects not available' : undefined,
      comAvailable: this.comAvailable ?? undefined
    };
  }
}
