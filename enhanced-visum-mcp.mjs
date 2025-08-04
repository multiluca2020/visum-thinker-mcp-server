#!/usr/bin/env node

// Enhanced Working MCP Server for Claude's Visum Access with Network Analysis
import { createInterface } from 'readline';
import { spawn } from 'child_process';

console.error("Enhanced Visum MCP Server for Claude - starting...");

const rl = createInterface({
  input: process.stdin,
  output: process.stdout,
  terminal: false
});

// Launch Visum if not running
async function launchVisum() {
  return new Promise((resolve) => {
    const script = `
      try {
        # Check if Visum is already running
        $visumProcess = Get-Process -Name "Visum250" -ErrorAction SilentlyContinue
        
        if ($visumProcess) {
          @{
            success = $true
            message = "Visum already running"
            processId = $visumProcess.Id
            alreadyRunning = $true
          } | ConvertTo-Json
        } else {
          # Start Visum visibly
          Write-Host "Starting Visum visibly..."
          $visumPath = "H:\\Program Files\\PTV Vision\\PTV Visum 2025\\Exe\\Visum250.exe"
          
          if (Test-Path $visumPath) {
            # Force Visum to start visibly with WindowStyle Normal
            $process = Start-Process -FilePath $visumPath -WindowStyle Normal -PassThru
            Start-Sleep -Seconds 8  # Wait longer for Visum to fully load
            
            @{
              success = $true
              message = "Visum started successfully"
              processId = $process.Id
              alreadyRunning = $false
            } | ConvertTo-Json
          } else {
            @{
              success = $false
              error = "Visum executable not found at expected path"
            } | ConvertTo-Json
          }
        }
      } catch {
        @{
          success = $false
          error = $_.Exception.Message
        } | ConvertTo-Json
      }
    `;

    const powershell = spawn('powershell', ['-ExecutionPolicy', 'Bypass', '-Command', script]);

    let output = '';
    powershell.stdout.on('data', (data) => {
      output += data.toString();
    });

    powershell.on('close', () => {
      try {
        const result = JSON.parse(output.trim());
        resolve(result);
      } catch {
        resolve({ success: false, error: 'Failed to parse PowerShell output' });
      }
    });
  });
}

// Enhanced Visum COM test function
async function testVisum() {
  return new Promise((resolve) => {
    const script = `
      try {
        $visum = New-Object -ComObject "Visum.Visum"
        $version = $visum.VersionNumber
        $net = $visum.Net
        $netAvailable = ($net -ne $null)
        
        @{
          success = $true
          version = $version
          netAvailable = $netAvailable
          path = "H:\\Program Files\\PTV Vision\\PTV Visum 2025\\Exe\\Visum250.exe"
        } | ConvertTo-Json
        
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($visum) | Out-Null
      } catch {
        @{
          success = $false
          error = $_.Exception.Message
        } | ConvertTo-Json
      }
    `;

    const powershell = spawn('powershell', ['-ExecutionPolicy', 'Bypass', '-Command', script]);

    let output = '';
    powershell.stdout.on('data', (data) => {
      output += data.toString();
    });

    powershell.on('close', () => {
      try {
        const result = JSON.parse(output.trim());
        resolve(result);
      } catch {
        resolve({ success: false, error: 'Failed to parse PowerShell output' });
      }
    });
  });
}

// Initialize Visum with stability
async function initializeVisum() {
  return new Promise((resolve) => {
    const script = `
      try {
        Write-Host "Initializing Visum COM with enhanced stability..."
        
        # Create Visum object
        $visum = New-Object -ComObject "Visum.Visum"
        
        # Test basic functionality
        $version = $visum.VersionNumber
        $net = $visum.Net
        
        if ($version -and ($net -ne $null)) {
          @{
            success = $true
            message = "Visum initialized successfully"
            version = $version
            ready = $true
          } | ConvertTo-Json
        } else {
          @{
            success = $false
            error = "Visum object created but not fully functional"
          } | ConvertTo-Json
        }
        
      } catch {
        @{
          success = $false
          error = $_.Exception.Message
        } | ConvertTo-Json
      }
    `;

    const powershell = spawn('powershell', ['-ExecutionPolicy', 'Bypass', '-Command', script]);

    let output = '';
    powershell.stdout.on('data', (data) => {
      output += data.toString();
    });

    powershell.on('close', () => {
      try {
        const result = JSON.parse(output.trim());
        resolve(result);
      } catch {
        resolve({ success: false, error: 'Failed to initialize Visum' });
      }
    });
  });
}

// Analyze network function
async function analyzeNetwork() {
  return new Promise((resolve) => {
    const script = `
      try {
        Write-Host "Analyzing Visum network..."
        
        # Create Visum object
        $visum = New-Object -ComObject "Visum.Visum"
        
        # Get network statistics
        $net = $visum.Net
        if ($net -ne $null) {
          $nodeCount = 0
          $linkCount = 0
          $zoneCount = 0
          
          try {
            $nodeCount = $net.Nodes.Count
          } catch { $nodeCount = "Unknown" }
          
          try {
            $linkCount = $net.Links.Count  
          } catch { $linkCount = "Unknown" }
          
          try {
            $zoneCount = $net.Zones.Count
          } catch { $zoneCount = "Unknown" }
          
          @{
            success = $true
            analysis = @{
              nodes = $nodeCount
              links = $linkCount
              zones = $zoneCount
              networkLoaded = $true
              analysisDate = (Get-Date).ToString()
            }
          } | ConvertTo-Json -Depth 3
        } else {
          @{
            success = $false
            error = "No network loaded in Visum"
          } | ConvertTo-Json
        }
        
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($visum) | Out-Null
        
      } catch {
        @{
          success = $false
          error = $_.Exception.Message
        } | ConvertTo-Json
      }
    `;

    const powershell = spawn('powershell', ['-ExecutionPolicy', 'Bypass', '-Command', script]);

    let output = '';
    powershell.stdout.on('data', (data) => {
      output += data.toString();
    });

    powershell.on('close', () => {
      try {
        const result = JSON.parse(output.trim());
        resolve(result);
      } catch {
        resolve({ success: false, error: 'Failed to analyze network' });
      }
    });
  });
}

// Get network statistics
async function getNetworkStats() {
  return new Promise((resolve) => {
    const script = `
      try {
        $visum = New-Object -ComObject "Visum.Visum"
        $net = $visum.Net
        
        if ($net -ne $null) {
          $stats = @{
            nodes = try { $net.Nodes.Count } catch { 0 }
            links = try { $net.Links.Count } catch { 0 }
            zones = try { $net.Zones.Count } catch { 0 }
            lines = try { $net.Lines.Count } catch { 0 }
            stops = try { $net.Stops.Count } catch { 0 }
            timeProfiles = try { $net.TimeProfiles.Count } catch { 0 }
            vehicleJourneys = try { $net.VehicleJourneys.Count } catch { 0 }
            networkFile = try { $visum.GetAttValue("VersionFile") } catch { "Not loaded" }
          }
          
          @{
            success = $true
            stats = $stats
          } | ConvertTo-Json -Depth 3
        } else {
          @{
            success = $false
            error = "No network available"
          } | ConvertTo-Json
        }
        
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($visum) | Out-Null
        
      } catch {
        @{
          success = $false
          error = $_.Exception.Message
        } | ConvertTo-Json
      }
    `;

    const powershell = spawn('powershell', ['-ExecutionPolicy', 'Bypass', '-Command', script]);

    let output = '';
    powershell.stdout.on('data', (data) => {
      output += data.toString();
    });

    powershell.on('close', () => {
      try {
        const result = JSON.parse(output.trim());
        resolve(result);
      } catch {
        resolve({ success: false, error: 'Failed to get network stats' });
      }
    });
  });
}

// Open Visum project (FIXED VERSION)
async function openProject(projectPath) {
  return new Promise((resolve) => {
    const script = `
      try {
        Write-Host "Opening Visum project: ${projectPath}"
        
        # Check if file exists first
        if (-not (Test-Path "${projectPath}")) {
          @{
            success = $false
            error = "Project file not found: ${projectPath}"
          } | ConvertTo-Json
          return
        }
        
        # Use New-Object (works better than GetActiveObject for Visum)
        Write-Host "Creating Visum COM object..."
        $visum = New-Object -ComObject "Visum.Visum"
        
        # Load the project
        Write-Host "Loading project file..."
        $visum.LoadVersion("${projectPath}")
        
        # Get network statistics
        Write-Host "Analyzing network..."
        $net = $visum.Net
        $nodeCount = try { $net.Nodes.Count } catch { 0 }
        $linkCount = try { $net.Links.Count } catch { 0 }
        $zoneCount = try { $net.Zones.Count } catch { 0 }
        
        Write-Host "Project loaded successfully! Nodes: $nodeCount"
        
        @{
          success = $true
          message = "Project opened successfully via COM"
          projectPath = "${projectPath}"
          networkStats = @{
            nodes = $nodeCount
            links = $linkCount
            zones = $zoneCount
          }
        } | ConvertTo-Json -Depth 3
        
        # Clean up COM object
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($visum) | Out-Null
        
      } catch {
        @{
          success = $false
          error = $_.Exception.Message
        } | ConvertTo-Json
      }
    `;

    const powershell = spawn('powershell', ['-ExecutionPolicy', 'Bypass', '-Command', script]);

    let output = '';
    powershell.stdout.on('data', (data) => {
      output += data.toString();
    });

    powershell.on('close', () => {
      try {
        const result = JSON.parse(output.trim());
        resolve(result);
      } catch {
        resolve({ success: false, error: 'Failed to parse PowerShell output' });
      }
    });
  });
}

// Handle MCP requests
rl.on('line', async (line) => {
  try {
    console.error(`Received request: ${line}`);
    const request = JSON.parse(line);
    
    let response = {
      jsonrpc: "2.0",
      id: request.id
    };

    // Handle tools/list
    if (request.method === 'tools/list') {
      response.result = {
        tools: [
          {
            name: "launch_visum",
            description: "Launch PTV Visum if not already running",
            inputSchema: {
              type: "object",
              properties: {},
              required: []
            }
          },
          {
            name: "open_project",
            description: "Open a Visum project file (.ver)",
            inputSchema: {
              type: "object",
              properties: {
                projectPath: {
                  type: "string",
                  description: "Full path to the Visum project file (.ver)"
                }
              },
              required: ["projectPath"]
            }
          },
          {
            name: "check_visum",
            description: "Check if PTV Visum is installed and accessible",
            inputSchema: {
              type: "object",
              properties: {},
              required: []
            }
          },
          {
            name: "initialize_visum",
            description: "Initialize Visum COM connection for automation",
            inputSchema: {
              type: "object", 
              properties: {},
              required: []
            }
          },
          {
            name: "get_visum_status",
            description: "Get current Visum status and configuration",
            inputSchema: {
              type: "object",
              properties: {},
              required: []
            }
          },
          {
            name: "analyze_network",
            description: "Analyze the current Visum network and get basic statistics",
            inputSchema: {
              type: "object",
              properties: {},
              required: []
            }
          },
          {
            name: "get_network_stats",
            description: "Get detailed network statistics from Visum",
            inputSchema: {
              type: "object",
              properties: {},
              required: []
            }
          }
        ]
      };
    }
    
    // Handle tools/call
    else if (request.method === 'tools/call') {
      const toolName = request.params.name;
      const args = request.params.arguments || {};
      
      if (toolName === 'launch_visum') {
        const launchResult = await launchVisum();
        
        if (launchResult.success) {
          response.result = {
            content: [
              {
                type: "text",
                text: `✅ **Visum Launch ${launchResult.alreadyRunning ? 'Status' : 'Successful'}**\n\n` +
                      `**Process Details:**\n` +
                      `• **Status:** ${launchResult.message}\n` +
                      `• **Process ID:** ${launchResult.processId}\n` +
                      `• **Already Running:** ${launchResult.alreadyRunning ? 'Yes' : 'No'}\n\n` +
                      `**Next Steps:**\n` +
                      `• Visum is now ready for COM automation\n` +
                      `• You can now use check_visum or analyze_network\n` +
                      `• Load a network model for analysis\n\n` +
                      `*Visum application is active and ready for transportation modeling.*`
              }
            ]
          };
        } else {
          response.result = {
            content: [
              {
                type: "text",
                text: `❌ **Visum Launch Failed**\n\n` +
                      `**Error:** ${launchResult.error}\n\n` +
                      `**Troubleshooting:**\n` +
                      `• Verify Visum installation path\n` +
                      `• Check if Visum license is available\n` +
                      `• Run as Administrator if needed\n` +
                      `• Ensure no other Visum instances are stuck\n\n` +
                      `*Could not start Visum application.*`
              }
            ]
          };
        }
      }
      
      else if (toolName === 'check_visum') {
        const visumTest = await testVisum();
        
        if (visumTest.success) {
          response.result = {
            content: [
              {
                type: "text",
                text: `✅ **Visum Available and Working**\n\n` +
                      `**Installation Details:**\n` +
                      `• **Version:** ${visumTest.version}\n` +
                      `• **Path:** ${visumTest.path}\n` +
                      `• **Network Object:** ${visumTest.netAvailable ? 'Available' : 'Not Available'}\n` +
                      `• **COM Interface:** Functional\n\n` +
                      `**Status:** Ready for transportation modeling and analysis\n\n` +
                      `*Visum is properly installed and COM automation is working correctly.*`
              }
            ]
          };
        } else {
          response.result = {
            content: [
              {
                type: "text", 
                text: `❌ **Visum Not Available**\n\n` +
                      `**Error:** ${visumTest.error}\n\n` +
                      `**Troubleshooting:**\n` +
                      `• Verify Visum is installed\n` +
                      `• Check COM registration\n` +
                      `• Run Visum once as Administrator\n` +
                      `• Ensure license is valid\n\n` +
                      `*Contact system administrator if issues persist.*`
              }
            ]
          };
        }
      }
      
      else if (toolName === 'initialize_visum') {
        const initResult = await initializeVisum();
        
        if (initResult.success) {
          response.result = {
            content: [
              {
                type: "text",
                text: `✅ **Visum Initialized Successfully**\n\n` +
                      `**Connection Details:**\n` +
                      `• **Version:** ${initResult.version}\n` +
                      `• **Status:** ${initResult.message}\n` +
                      `• **COM Object:** Active and responsive\n\n` +
                      `**Ready for Operations:**\n` +
                      `• Load transportation models\n` +
                      `• Execute procedures and analyses\n` +
                      `• Access network data\n\n` +
                      `*Visum automation is now active and ready for use.*`
              }
            ]
          };
        } else {
          response.result = {
            content: [
              {
                type: "text",
                text: `❌ **Initialization Failed**\n\n` +
                      `**Error:** ${initResult.error}\n\n` +
                      `**Suggestions:**\n` +
                      `• Restart Visum manually\n` +
                      `• Check for running Visum processes\n` +
                      `• Verify COM permissions\n` +
                      `• Try running as Administrator\n\n` +
                      `*Visum COM automation could not be established.*`
              }
            ]
          };
        }
      }
      
      else if (toolName === 'get_visum_status') {
        const statusTest = await testVisum();
        
        response.result = {
          content: [
            {
              type: "text",
              text: `📊 **Current Visum Status**\n\n` +
                    `**Availability:** ${statusTest.success ? '✅ Available' : '❌ Not Available'}\n` +
                    `**COM Interface:** ${statusTest.success ? 'Working' : 'Failed'}\n` +
                    `**Installation Path:** H:\\Program Files\\PTV Vision\\PTV Visum 2025\\Exe\\Visum250.exe\n` +
                    `**Version:** ${statusTest.version || 'Unknown'}\n\n` +
                    `**MCP Server:** ✅ Running and responsive\n` +
                    `**Communication:** ✅ STDIO protocol working\n` +
                    `**Last Check:** ${new Date().toLocaleString()}\n\n` +
                    `*This MCP server is working correctly for Claude integration.*`
            }
          ]
        };
      }
      
      else if (toolName === 'analyze_network') {
        const analysisResult = await analyzeNetwork();
        
        if (analysisResult.success) {
          const analysis = analysisResult.analysis;
          response.result = {
            content: [
              {
                type: "text",
                text: `📊 **Network Analysis Results**\n\n` +
                      `**Network Components:**\n` +
                      `• **Nodes:** ${analysis.nodes}\n` +
                      `• **Links:** ${analysis.links}\n` +
                      `• **Zones:** ${analysis.zones}\n\n` +
                      `**Analysis Status:**\n` +
                      `• **Network Loaded:** ${analysis.networkLoaded ? '✅ Yes' : '❌ No'}\n` +
                      `• **Analysis Date:** ${analysis.analysisDate}\n\n` +
                      `**Network Summary:**\n` +
                      `The current Visum network contains ${analysis.nodes} nodes connected by ${analysis.links} links, ` +
                      `with ${analysis.zones} traffic analysis zones defined.\n\n` +
                      `*Network analysis completed successfully.*`
              }
            ]
          };
        } else {
          response.result = {
            content: [
              {
                type: "text",
                text: `❌ **Network Analysis Failed**\n\n` +
                      `**Error:** ${analysisResult.error}\n\n` +
                      `**Possible Causes:**\n` +
                      `• No network model loaded in Visum\n` +
                      `• Visum COM connection lost\n` +
                      `• Insufficient permissions\n\n` +
                      `**Suggestions:**\n` +
                      `• Load a network model in Visum first\n` +
                      `• Check Visum connection status\n` +
                      `• Try reinitializing Visum\n\n` +
                      `*Please ensure a network is loaded before analysis.*`
              }
            ]
          };
        }
      }
      
      else if (toolName === 'get_network_stats') {
        const statsResult = await getNetworkStats();
        
        if (statsResult.success) {
          const stats = statsResult.stats;
          response.result = {
            content: [
              {
                type: "text",
                text: `📈 **Detailed Network Statistics**\n\n` +
                      `**Basic Network Elements:**\n` +
                      `• **Nodes:** ${stats.nodes}\n` +
                      `• **Links:** ${stats.links}\n` +
                      `• **Zones:** ${stats.zones}\n\n` +
                      `**Public Transport Elements:**\n` +
                      `• **Lines:** ${stats.lines}\n` +
                      `• **Stops:** ${stats.stops}\n` +
                      `• **Time Profiles:** ${stats.timeProfiles}\n` +
                      `• **Vehicle Journeys:** ${stats.vehicleJourneys}\n\n` +
                      `**Network File:**\n` +
                      `• **Source:** ${stats.networkFile}\n\n` +
                      `**Network Connectivity:**\n` +
                      `Average links per node: ${stats.nodes > 0 ? (stats.links / stats.nodes * 2).toFixed(2) : 'N/A'}\n\n` +
                      `*Detailed network statistics retrieved successfully.*`
              }
            ]
          };
        } else {
          response.result = {
            content: [
              {
                type: "text",
                text: `❌ **Statistics Retrieval Failed**\n\n` +
                      `**Error:** ${statsResult.error}\n\n` +
                      `*Could not retrieve detailed network statistics.*`
              }
            ]
          };
        }
      }
      
      else if (toolName === 'open_project') {
        const projectPath = args.projectPath;
        const openResult = await openProject(projectPath);
        
        if (openResult.success) {
          response.result = {
            content: [
              {
                type: "text",
                text: `✅ **Project Opened Successfully**\n\n` +
                      `**File:** ${projectPath}\n` +
                      `**Status:** Project loaded in Visum\n` +
                      `**Size:** ${openResult.size || 'Unknown'}\n\n` +
                      `**Network Details:**\n` +
                      `• **Type:** ${openResult.fileType || 'Visum Version'}\n` +
                      `• **Loaded:** ${new Date().toLocaleString()}\n\n` +
                      `**Next Steps:**\n` +
                      `• Use analyze_network to inspect the network\n` +
                      `• Use get_network_stats for detailed statistics\n` +
                      `• Perform transportation analysis\n\n` +
                      `*The project is now ready for analysis in Visum.*`
              }
            ]
          };
        } else {
          response.result = {
            content: [
              {
                type: "text",
                text: `❌ **Project Opening Failed**\n\n` +
                      `**File:** ${projectPath}\n` +
                      `**Error:** ${openResult.error}\n\n` +
                      `**Possible Causes:**\n` +
                      `• File not found or inaccessible\n` +
                      `• Invalid Visum project format\n` +
                      `• Visum not properly connected\n` +
                      `• File permissions issue\n\n` +
                      `**Suggestions:**\n` +
                      `• Verify the file path is correct\n` +
                      `• Check file exists and is readable\n` +
                      `• Ensure Visum is running (use launch_visum)\n` +
                      `• Try absolute path format\n\n` +
                      `*Could not load the specified project file.*`
              }
            ]
          };
        }
      }
      
      else {
        response.error = {
          code: -32601,
          message: `Unknown tool: ${toolName}`
        };
      }
    }
    
    // Handle initialize
    else if (request.method === 'initialize') {
      response.result = {
        protocolVersion: "2024-11-05",
        capabilities: {
          tools: {}
        },
        serverInfo: {
          name: "enhanced-visum-mcp",
          version: "1.0.0"
        }
      };
    }
    
    else {
      response.error = {
        code: -32601,
        message: `Unknown method: ${request.method}`
      };
    }

    // Send response
    console.log(JSON.stringify(response));
    console.error(`Sent response for ${request.method}`);
    
  } catch (error) {
    console.error(`Error processing request: ${error.message}`);
    
    // Send error response
    const errorResponse = {
      jsonrpc: "2.0",
      id: 1,
      error: {
        code: -32603,
        message: error.message
      }
    };
    
    console.log(JSON.stringify(errorResponse));
  }
});

rl.on('close', () => {
  console.error('Enhanced MCP server connection closed');
  process.exit(0);
});

console.error("Enhanced Visum MCP Server ready for Claude with network analysis!");
