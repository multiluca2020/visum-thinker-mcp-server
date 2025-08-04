#!/usr/bin/env node

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

// Create minimal MCP server for testing
const server = new McpServer({
  name: "test-visum-server",
  version: "1.0.0",
}, {
  capabilities: {
    resources: {},
    tools: {},
  },
});

// Add a simple test tool
server.tool(
  "test_tool",
  "Simple test tool to verify MCP communication",
  {
    message: z.string().optional().describe("Optional test message"),
  },
  async ({ message }) => {
    return {
      content: [
        {
          type: "text",
          text: `✅ MCP Server Response: ${message || 'Hello from test tool!'}\nServer is working correctly.`
        }
      ]
    };
  }
);

// Add the check_visum tool in minimal form
server.tool(
  "check_visum",
  "Check if Visum is available",
  {},
  async () => {
    try {
      // Simple direct test
      const { spawn } = await import('child_process');
      
      return new Promise((resolve) => {
        const powershell = spawn('powershell', [
          '-ExecutionPolicy', 'Bypass',
          '-Command',
          'try { $v = New-Object -ComObject "Visum.Visum"; $ver = $v.VersionNumber; "SUCCESS:$ver" } catch { "ERROR:$($_.Exception.Message)" }'
        ]);

        let output = '';
        powershell.stdout.on('data', (data) => {
          output += data.toString();
        });

        powershell.on('close', () => {
          const result = output.trim();
          if (result.startsWith('SUCCESS:')) {
            const version = result.replace('SUCCESS:', '');
            resolve({
              content: [
                {
                  type: "text",
                  text: `✅ **Visum Available**\n\nVersion: ${version}\nCOM interface is working correctly!\n\n*Ready for transportation analysis.*`
                }
              ]
            });
          } else {
            resolve({
              content: [
                {
                  type: "text",
                  text: `❌ **Visum Not Available**\n\nError: ${result.replace('ERROR:', '')}\n\n*Check Visum installation and COM registration.*`
                }
              ]
            });
          }
        });
      });
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `❌ **Error testing Visum:**\n\n${error instanceof Error ? error.message : String(error)}`
          }
        ]
      };
    }
  }
);

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Test Visum MCP Server running on stdio");
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
