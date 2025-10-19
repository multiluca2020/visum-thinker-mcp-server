const { spawn } = require('child_process');
const readline = require('readline');

// Start MCP server
const server = spawn('node', ['build/index.js'], {
  cwd: 'H:\\visum-thinker-mcp-server'
});

const rl = readline.createInterface({
  input: server.stdout,
  output: process.stdout,
  terminal: false
});

// Log stderr
server.stderr.on('data', (data) => {
  console.error(`[SERVER LOG] ${data.toString()}`);
});

// Wait for server to be ready
setTimeout(() => {
  console.log('\n=== SENDING REQUEST ===\n');
  
  const request = {
    method: "tools/call",
    params: {
      name: "project_export_visible_tables",
      arguments: {
        projectId: "S000009result_1278407893",
        layoutFile: "tabelle_report.lay"
      }
    },
    jsonrpc: "2.0",
    id: 1
  };
  
  server.stdin.write(JSON.stringify(request) + '\n');
  
}, 3000);

// Handle response
rl.on('line', (line) => {
  console.log('\n=== RESPONSE ===\n');
  try {
    const response = JSON.parse(line);
    console.log(JSON.stringify(response, null, 2));
    server.kill();
    process.exit(0);
  } catch (e) {
    console.log('Non-JSON:', line);
  }
});

// Timeout
setTimeout(() => {
  console.log('TIMEOUT');
  server.kill();
  process.exit(1);
}, 30000);
