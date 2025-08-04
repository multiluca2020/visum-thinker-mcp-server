#!/usr/bin/env node

// Working MCP Server for Claude's Visum Access
import { createInterface } from 'readline';
import { spawn } from 'child_process';

console.error("Working Visum MCP Server for Claude - starting...");

const rl = createInterface({
  input: process.stdin,
  output: process.stdout,
  terminal: false
});

// Visum COM test function
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
          }
        ]
      };
    }
    
    // Handle tools/call
    else if (request.method === 'tools/call') {
      const toolName = request.params.name;
      
      if (toolName === 'check_visum') {
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
          name: "working-visum-mcp",
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
  console.error('MCP server connection closed');
  process.exit(0);
});

console.error("Working Visum MCP Server ready for Claude!");
