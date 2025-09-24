#!/usr/bin/env node

// 🤖 EMULATORE CLAUDE - Test MCP Visum Tools
import { spawn } from 'child_process';
import readline from 'readline';

console.log('🤖 EMULATORE CLAUDE PER TEST MCP VISUM');
console.log('═'.repeat(50));
console.log('💬 Scrivi i comandi come se fossi Claude');
console.log('🔧 I tool Visum verranno testati direttamente via MCP');
console.log('❌ Premi CTRL+C per uscire');
console.log('═'.repeat(50));

class ClaudeEmulator {
  constructor() {
    this.mcpServer = null;
    this.requestId = 1;
    this.rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
      prompt: '🤖 Claude> '
    });
    
    this.commands = new Map([
      ['check-visum', { tool: 'check_visum', args: {} }],
      ['status-visum', { tool: 'get_visum_status', args: {} }],
      ['launch-visum', { tool: 'visum_launch', requiresArgs: true, argPrompt: 'Percorso progetto (.ver):' }],
      ['analyze-network', { tool: 'visum_network_analysis', requiresArgs: true, argPrompt: 'Tipo analisi (basic/detailed/topology/performance):' }],
      ['export-network', { tool: 'visum_export_network', requiresArgs: true, argPrompt: 'Elementi da esportare (nodes,links,zones):' }],
      ['connectivity-stats', { tool: 'visum_connectivity_stats', args: {} }],
      ['python-script', { tool: 'visum_python_analysis', requiresArgs: true, argPrompt: 'Script Python:' }],
      ['val-script', { tool: 'visum_val_script', requiresArgs: true, argPrompt: 'Script VAL:' }]
    ]);
  }
  
  async startMCPServer() {
    console.log('\n🚀 Avvio server MCP...');
    
    this.mcpServer = spawn('node', ['build/index.js'], {
      stdio: ['pipe', 'pipe', 'pipe'],
      cwd: process.cwd()
    });
    
    this.mcpServer.stderr.on('data', (data) => {
      const message = data.toString().trim();
      if (message.includes('running')) {
        console.log('✅', message);
        this.initializeMCP();
      }
    });
    
    this.mcpServer.stdout.on('data', (data) => {
      const output = data.toString().trim();
      if (output) {
        try {
          const response = JSON.parse(output);
          this.handleMCPResponse(response);
        } catch (e) {
          console.log('📨 Raw output:', output);
        }
      }
    });
    
    this.mcpServer.on('error', (error) => {
      console.error('❌ Errore server MCP:', error.message);
    });
  }
  
  async initializeMCP() {
    console.log('🔧 Inizializzazione MCP...');
    
    const initRequest = {
      jsonrpc: "2.0",
      id: this.requestId++,
      method: "initialize", 
      params: {
        protocolVersion: "2024-11-05",
        capabilities: {},
        clientInfo: { name: "claude-emulator", version: "1.0.0" }
      }
    };
    
    this.sendMCPRequest(initRequest);
    
    setTimeout(() => {
      console.log('\n✅ Claude Emulator pronto!');
      this.showHelp();
      this.rl.prompt();
    }, 1000);
  }
  
  sendMCPRequest(request) {
    if (this.mcpServer && this.mcpServer.stdin.writable) {
      this.mcpServer.stdin.write(JSON.stringify(request) + '\n');
    }
  }
  
  handleMCPResponse(response) {
    console.log('\n📨 RISPOSTA MCP:');
    console.log('═'.repeat(20));
    
    if (response.result && response.result.content) {
      // Risposta tool
      response.result.content.forEach(content => {
        if (content.type === 'text') {
          console.log(content.text);
        }
      });
    } else if (response.result && response.result.tools) {
      // Lista tool
      console.log(`🛠️  ${response.result.tools.length} tool disponibili`);
      const visumTools = response.result.tools.filter(t => t.name.startsWith('visum_'));
      console.log(`🔧 ${visumTools.length} tool Visum trovati`);
    } else if (response.error) {
      // Errore
      console.log('❌ ERRORE:', response.error.message);
      if (response.error.data) {
        console.log('📋 Dettagli:', response.error.data);
      }
    } else {
      // Altra risposta
      console.log('📋 Risposta:', JSON.stringify(response, null, 2));
    }
    
    console.log('═'.repeat(20));
    this.rl.prompt();
  }
  
  showHelp() {
    console.log('\n📋 COMANDI DISPONIBILI:');
    console.log('═'.repeat(25));
    console.log('🔧 check-visum          - Verifica installazione Visum');
    console.log('📊 status-visum         - Status connessione Visum');
    console.log('🚀 launch-visum         - Lancia Visum con progetto');
    console.log('📈 analyze-network      - Analisi rete dettagliata');
    console.log('📤 export-network       - Export elementi rete');
    console.log('📊 connectivity-stats   - Statistiche connettività');
    console.log('🐍 python-script        - Esegui script Python');
    console.log('📜 val-script           - Esegui script VAL');
    console.log('❓ help                 - Mostra questo aiuto');
    console.log('🚪 exit                 - Esci dall\'emulatore');
  }
  
  async handleCommand(input) {
    const command = input.trim().toLowerCase();
    
    if (command === 'help' || command === '?') {
      this.showHelp();
      return;
    }
    
    if (command === 'exit' || command === 'quit') {
      console.log('👋 Chiusura emulatore Claude...');
      if (this.mcpServer) {
        this.mcpServer.kill();
      }
      process.exit(0);
    }
    
    if (this.commands.has(command)) {
      const cmd = this.commands.get(command);
      await this.executeToolCommand(cmd, command);
    } else {
      console.log(`❌ Comando non riconosciuto: ${command}`);
      console.log('💡 Usa "help" per vedere i comandi disponibili');
    }
  }
  
  async executeToolCommand(cmd, commandName) {
    console.log(`\n🔧 Esecuzione: ${cmd.tool}`);
    
    let args = cmd.args || {};
    
    // Se servono argomenti, chiedili
    if (cmd.requiresArgs) {
      args = await this.getCommandArgs(cmd, commandName);
    }
    
    const toolRequest = {
      jsonrpc: "2.0",
      id: this.requestId++,
      method: "tools/call",
      params: {
        name: cmd.tool,
        arguments: args
      }
    };
    
    console.log('📤 Invio richiesta MCP...');
    this.sendMCPRequest(toolRequest);
  }
  
  async getCommandArgs(cmd, commandName) {
    return new Promise((resolve) => {
      if (commandName === 'launch-visum') {
        this.rl.question('📁 Percorso progetto Visum (.ver): ', (projectPath) => {
          resolve({ 
            projectPath: projectPath.trim(),
            visible: true 
          });
        });
      } else if (commandName === 'analyze-network') {
        this.rl.question('📊 Tipo analisi (basic/detailed/topology/performance): ', (analysisType) => {
          resolve({ 
            analysisType: analysisType.trim() || 'detailed',
            exportPath: 'C:\\temp\\mcp_analysis'
          });
        });
      } else if (commandName === 'export-network') {
        this.rl.question('📤 Elementi (nodes,links,zones): ', (elements) => {
          const elementList = elements.trim().split(',').map(e => e.trim()).filter(e => e);
          resolve({ 
            elements: elementList.length > 0 ? elementList : ['nodes', 'links'],
            outputDir: 'C:\\temp\\mcp_export',
            method: 'python'
          });
        });
      } else if (commandName === 'python-script') {
        console.log('🐍 Scrivi script Python (termina con una riga vuota):');
        let script = '';
        const collectScript = () => {
          this.rl.question('>>> ', (line) => {
            if (line.trim() === '') {
              resolve({ script });
            } else {
              script += line + '\\n';
              collectScript();
            }
          });
        };
        collectScript();
      } else if (commandName === 'val-script') {
        this.rl.question('📜 Script VAL: ', (script) => {
          resolve({ script: script.trim() });
        });
      } else {
        resolve({});
      }
    });
  }
  
  start() {
    this.startMCPServer();
    
    this.rl.on('line', (input) => {
      this.handleCommand(input);
    });
    
    this.rl.on('close', () => {
      console.log('\\n👋 Arrivederci!');
      if (this.mcpServer) {
        this.mcpServer.kill();
      }
      process.exit(0);
    });
  }
}

// Avvia emulatore
console.log('🎯 Avvio Claude Emulator per test Visum...');
const emulator = new ClaudeEmulator();
emulator.start();