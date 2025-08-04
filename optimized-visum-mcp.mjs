#!/usr/bin/env node

// Enhanced Visum MCP Server - Optimized Version with Extended Timeouts
import { spawn } from 'child_process';

function logToStderr(message) {
  console.error(`[${new Date().toISOString()}] ${message}`);
}

logToStderr("Enhanced Visum MCP Server for Claude - OPTIMIZED VERSION starting...");

// Robust PowerShell execution with extended timeouts
async function executeEnhancedPowerShell(script, timeoutMs = 30000) {
  return new Promise((resolve, reject) => {
    logToStderr(`🔄 Executing PowerShell with ${timeoutMs}ms timeout...`);
    
    const powershell = spawn('powershell', ['-ExecutionPolicy', 'Bypass', '-Command', script]);
    
    let output = '';
    let stderr = '';
    
    powershell.stdout.on('data', (data) => {
      const chunk = data.toString();
      output += chunk;
      logToStderr(`📥 PS Output chunk: ${chunk.substring(0, 100)}...`);
    });
    
    powershell.stderr.on('data', (data) => {
      stderr += data.toString();
    });
    
    // Extended timeout
    const timeout = setTimeout(() => {
      logToStderr(`⏱️  PowerShell timeout after ${timeoutMs}ms - terminating`);
      powershell.kill('SIGKILL');
      reject(new Error(`PowerShell timeout after ${timeoutMs}ms`));
    }, timeoutMs);
    
    powershell.on('close', (code) => {
      clearTimeout(timeout);
      logToStderr(`🏁 PowerShell closed with code ${code}, output: ${output.length} chars`);
      
      if (code === 0) {
        try {
          const jsonMatch = output.match(/\{[\s\S]*\}/);
          if (jsonMatch) {
            const result = JSON.parse(jsonMatch[0]);
            logToStderr(`✅ Parsed JSON successfully`);
            resolve(result);
          } else {
            logToStderr(`⚠️  No JSON found, returning raw output`);
            resolve({ success: true, output: output.trim() });
          }
        } catch (e) {
          logToStderr(`❌ JSON parse error: ${e.message}`);
          resolve({ success: false, error: `JSON parse failed: ${e.message}` });
        }
      } else {
        logToStderr(`❌ PowerShell failed with code ${code}`);
        reject(new Error(`PowerShell failed: code ${code}, stderr: ${stderr}`));
      }
    });
    
    powershell.on('error', (err) => {
      clearTimeout(timeout);
      logToStderr(`❌ PowerShell spawn error: ${err.message}`);
      reject(err);
    });
  });
}

// Fast Visum status check
async function getVisumStatus() {
  const script = `
    try {
      $process = Get-Process -Name "Visum250" -ErrorAction SilentlyContinue
      if ($process) {
        @{
          success = $true
          running = $true
          processId = $process.Id
          startTime = $process.StartTime.ToString()
        } | ConvertTo-Json -Compress
      } else {
        @{
          success = $true
          running = $false
          message = "Visum not running"
        } | ConvertTo-Json -Compress
      }
    } catch {
      @{
        success = $false
        error = $_.Exception.Message
      } | ConvertTo-Json -Compress
    }
  `;
  
  return await executeEnhancedPowerShell(script, 10000); // 10 seconds timeout
}

// Quick Visum COM check
async function checkVisum() {
  const script = `
    try {
      $visum = New-Object -ComObject "Visum.Visum"
      $version = $visum.VersionNumber
      
      @{
        success = $true
        available = $true
        version = $version
        comReady = $true
      } | ConvertTo-Json -Compress
      
      try { [System.Runtime.InteropServices.Marshal]::ReleaseComObject($visum) } catch {}
    } catch {
      @{
        success = $false
        available = $false
        error = $_.Exception.Message
      } | ConvertTo-Json -Compress
    }
  `;
  
  return await executeEnhancedPowerShell(script, 15000); // 15 seconds timeout
}

// Initialize Visum
async function initializeVisum() {
  const script = `
    try {
      $visum = New-Object -ComObject "Visum.Visum"
      $version = $visum.VersionNumber
      $net = $visum.Net
      
      @{
        success = $true
        initialized = $true
        version = $version
        netAvailable = ($net -ne $null)
      } | ConvertTo-Json -Compress
      
      try { [System.Runtime.InteropServices.Marshal]::ReleaseComObject($visum) } catch {}
    } catch {
      @{
        success = $false
        error = $_.Exception.Message
      } | ConvertTo-Json -Compress
    }
  `;
  
  return await executeEnhancedPowerShell(script, 20000); // 20 seconds timeout
}

// Launch Visum visibly
async function launchVisum() {
  const script = `
    try {
      $visumPath = "H:\\Program Files\\PTV Vision\\PTV Visum 2025\\Exe\\Visum250.exe"
      
      if (-not (Test-Path $visumPath)) {
        @{
          success = $false
          error = "Visum executable not found"
        } | ConvertTo-Json -Compress
        return
      }
      
      $existing = Get-Process -Name "Visum250" -ErrorAction SilentlyContinue
      if ($existing) {
        @{
          success = $true
          message = "Visum already running"
          processId = $existing.Id
        } | ConvertTo-Json -Compress
        return
      }
      
      $process = Start-Process -FilePath $visumPath -WindowStyle Normal -PassThru
      Start-Sleep -Seconds 5
      
      @{
        success = $true
        launched = $true
        processId = $process.Id
        visible = $true
      } | ConvertTo-Json -Compress
    } catch {
      @{
        success = $false
        error = $_.Exception.Message
      } | ConvertTo-Json -Compress
    }
  `;
  
  return await executeEnhancedPowerShell(script, 25000); // 25 seconds timeout
}

// Basic network analysis
async function analyzeNetwork() {
  const script = `
    try {
      $visum = New-Object -ComObject "Visum.Visum"
      $net = $visum.Net
      
      if ($net -eq $null) {
        @{
          success = $false
          error = "No network loaded"
        } | ConvertTo-Json -Compress
        return
      }
      
      $zones = $net.Zones.Count
      $nodes = $net.Nodes.Count
      $links = $net.Links.Count
      
      @{
        success = $true
        zones = $zones
        nodes = $nodes
        links = $links
        networkLoaded = $true
      } | ConvertTo-Json -Compress
      
      try { [System.Runtime.InteropServices.Marshal]::ReleaseComObject($visum) } catch {}
    } catch {
      @{
        success = $false
        error = $_.Exception.Message
      } | ConvertTo-Json -Compress
    }
  `;
  
  return await executeEnhancedPowerShell(script, 15000); // 15 seconds timeout
}

// Get network statistics
async function getNetworkStats() {
  return await analyzeNetwork(); // Same implementation for now
}

// Tool handlers
const tools = {
  'get_visum_status': getVisumStatus,
  'check_visum': checkVisum,
  'initialize_visum': initializeVisum,
  'launch_visum': launchVisum,
  'analyze_network': analyzeNetwork,
  'get_network_stats': getNetworkStats
};

// MCP Protocol handlers
async function listTools() {
  return {
    tools: [
      {
        name: "get_visum_status",
        description: "Get the current status of Visum process",
        inputSchema: {
          type: "object",
          properties: {}
        }
      },
      {
        name: "check_visum",
        description: "Check if Visum COM interface is available",
        inputSchema: {
          type: "object", 
          properties: {}
        }
      },
      {
        name: "initialize_visum",
        description: "Initialize Visum COM interface",
        inputSchema: {
          type: "object",
          properties: {}
        }
      },
      {
        name: "launch_visum",
        description: "Launch Visum application visibly",
        inputSchema: {
          type: "object",
          properties: {}
        }
      },
      {
        name: "analyze_network",
        description: "Analyze the current Visum network",
        inputSchema: {
          type: "object",
          properties: {}
        }
      },
      {
        name: "get_network_stats",
        description: "Get statistics about the current network",
        inputSchema: {
          type: "object",
          properties: {}
        }
      }
    ]
  };
}

async function callTool(name, args) {
  logToStderr(`🛠️  Calling tool: ${name} with args: ${JSON.stringify(args)}`);
  
  if (!(name in tools)) {
    throw new Error(`Unknown tool: ${name}`);
  }
  
  try {
    const result = await tools[name](args);
    logToStderr(`✅ Tool ${name} completed successfully`);
    return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
  } catch (error) {
    logToStderr(`❌ Tool ${name} failed: ${error.message}`);
    throw error;
  }
}

// Message processing
async function processMessage(message) {
  try {
    const request = JSON.parse(message);
    logToStderr(`📨 Processing request: ${request.method}`);
    
    let response;
    
    switch (request.method) {
      case 'initialize':
        response = {
          jsonrpc: "2.0",
          id: request.id,
          result: {
            protocolVersion: "2024-11-05",
            capabilities: { tools: {} },
            serverInfo: { name: "Enhanced Visum MCP", version: "1.0" }
          }
        };
        break;
        
      case 'tools/list':
        const toolsList = await listTools();
        response = {
          jsonrpc: "2.0",
          id: request.id,
          result: toolsList
        };
        break;
        
      case 'tools/call':
        const result = await callTool(request.params.name, request.params.arguments);
        response = {
          jsonrpc: "2.0",
          id: request.id,
          result: result
        };
        break;
        
      default:
        response = {
          jsonrpc: "2.0",
          id: request.id,
          error: { code: -32601, message: `Method not found: ${request.method}` }
        };
    }
    
    const responseStr = JSON.stringify(response);
    logToStderr(`📤 Sending response: ${responseStr.substring(0, 200)}...`);
    console.log(responseStr);
    
  } catch (error) {
    logToStderr(`❌ Error processing message: ${error.message}`);
    const errorResponse = {
      jsonrpc: "2.0",
      id: null,
      error: { code: -32603, message: error.message }
    };
    console.log(JSON.stringify(errorResponse));
  }
}

// Main server loop
process.stdin.setEncoding('utf8');
process.stdin.on('data', (data) => {
  const lines = data.trim().split('\n');
  for (const line of lines) {
    if (line.trim()) {
      logToStderr(`📨 Received: ${line.substring(0, 100)}...`);
      processMessage(line.trim());
    }
  }
});

logToStderr("Enhanced Visum MCP Server ready for Claude with EXTENDED TIMEOUTS and optimized performance!");
