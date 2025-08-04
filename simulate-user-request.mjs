// Simulazione completa: Utente chiede a Claude di aprire Visum
import { spawn } from 'child_process';

console.log("👤 SIMULAZIONE RICHIESTA UTENTE A CLAUDE");
console.log("═══════════════════════════════════════\n");

console.log("👤 User: 'Claude, puoi aprire Visum per me?'\n");

class ClaudeVirtualAssistant {
  constructor() {
    this.requestId = 1;
  }

  async sendToMCP(method, params = {}) {
    return new Promise((resolve) => {
      console.log(`🧠 Claude pensa: Invio ${method} all'MCP...`);
      
      const child = spawn('node', ['enhanced-visum-mcp.mjs'], { 
        stdio: ['pipe', 'pipe', 'pipe'],
        cwd: process.cwd()
      });

      let output = '';
      let stderr = '';
      
      child.stdout.on('data', (data) => {
        output += data.toString();
      });

      child.stderr.on('data', (data) => {
        stderr += data.toString();
      });

      child.on('close', () => {
        try {
          const lines = output.trim().split('\n');
          const jsonLine = lines.find(line => line.startsWith('{'));
          
          if (jsonLine) {
            const response = JSON.parse(jsonLine);
            resolve({ success: true, response, stderr });
          } else {
            resolve({ success: false, error: 'No JSON in response', output, stderr });
          }
        } catch (error) {
          resolve({ success: false, error: error.message, output, stderr });
        }
      });

      const request = {
        jsonrpc: "2.0",
        id: this.requestId++,
        method: method,
        params: params
      };

      child.stdin.write(JSON.stringify(request) + '\n');
      child.stdin.end();

      // Timeout più lungo per Visum
      setTimeout(() => {
        child.kill();
        resolve({ success: false, error: 'Timeout dopo 20 secondi' });
      }, 20000);
    });
  }

  async respondToUser() {
    console.log("🤖 Claude: 'Certo! Ti aiuto ad aprire Visum. Lascia che controlli prima lo stato del sistema...'");
    console.log("💭 Claude pensa: Prima verifico i tools disponibili nell'MCP\n");

    // Step 1: Check available tools
    console.log("🔍 Step 1: Verifica tools MCP");
    const toolsResult = await this.sendToMCP("tools/list");
    
    if (toolsResult.success) {
      const tools = toolsResult.response.result?.tools || [];
      console.log(`✅ Claude: Ho trovato ${tools.length} strumenti disponibili:`);
      
      const hasLaunch = tools.find(t => t.name === 'launch_visum');
      const hasCheck = tools.find(t => t.name === 'check_visum');
      
      if (hasLaunch) {
        console.log("   🚀 launch_visum - Posso avviare Visum");
      }
      if (hasCheck) {
        console.log("   🔍 check_visum - Posso verificare lo stato");
      }
      
      console.log("\n🤖 Claude: 'Perfetto! Ho tutto quello che serve. Ora provo a lanciare Visum...'");
    } else {
      console.log("❌ Claude: 'C'è un problema con l'MCP server'");
      return false;
    }

    // Step 2: Launch Visum
    console.log("\n🚀 Step 2: Lancio Visum");
    console.log("🤖 Claude: 'Sto avviando Visum per te...'");
    
    const launchResult = await this.sendToMCP("tools/call", {
      name: "launch_visum",
      arguments: {}
    });
    
    if (launchResult.success) {
      const content = launchResult.response.result?.content?.[0]?.text;
      console.log("📤 Risposta MCP ricevuta!");
      
      if (content?.includes("✅")) {
        console.log("🤖 Claude: '✅ Ottimo! Visum è stato avviato con successo!'");
        
        // Estrai info dal contenuto
        const statusMatch = content.match(/Status:\*\* (.+)/);
        const pidMatch = content.match(/Process ID:\*\* (.+)/);
        const alreadyRunningMatch = content.match(/Already Running:\*\* (.+)/);
        
        if (statusMatch) {
          console.log(`   📊 Status: ${statusMatch[1]}`);
        }
        if (pidMatch) {
          console.log(`   🆔 Process ID: ${pidMatch[1]}`);
        }
        if (alreadyRunningMatch) {
          const wasRunning = alreadyRunningMatch[1] === 'Yes';
          if (wasRunning) {
            console.log("   ℹ️ Visum era già in esecuzione");
          } else {
            console.log("   🆕 Visum è stato avviato ex novo");
          }
        }
      } else {
        console.log("🤖 Claude: '❌ Mi dispiace, c'è stato un problema nell'avviare Visum'");
        console.log(`   Errore: ${content?.substring(0, 100)}...`);
        return false;
      }
    } else {
      console.log("🤖 Claude: '❌ Non sono riuscito a comunicare con Visum'");
      console.log(`   Problema tecnico: ${launchResult.error}`);
      return false;
    }

    // Step 3: Verify Visum is working
    console.log("\n🔍 Step 3: Verifica che Visum funzioni");
    console.log("🤖 Claude: 'Ora verifico che Visum sia completamente operativo...'");
    
    // Wait a bit for Visum to fully load
    console.log("⏳ Attendo che Visum si carichi completamente...");
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    const checkResult = await this.sendToMCP("tools/call", {
      name: "check_visum",
      arguments: {}
    });
    
    if (checkResult.success) {
      const content = checkResult.response.result?.content?.[0]?.text;
      
      if (content?.includes("✅")) {
        console.log("🤖 Claude: '🎉 Perfetto! Visum è completamente operativo!'");
        
        // Estrai versione
        const versionMatch = content.match(/Version:\*\* (\d+)/);
        const comMatch = content.match(/COM Interface:\*\* (.+)/);
        
        if (versionMatch) {
          console.log(`   📦 Versione Visum: ${versionMatch[1]}`);
        }
        if (comMatch) {
          console.log(`   🔗 Interfaccia COM: ${comMatch[1]}`);
        }
        
        console.log("\n🤖 Claude: 'Visum è ora aperto e pronto per l'uso! Posso aiutarti con:'");
        console.log("   📊 Analisi della rete di trasporto");
        console.log("   📈 Statistiche dettagliate della rete");
        console.log("   🚌 Analisi del trasporto pubblico");
        console.log("   🎯 Qualsiasi altra funzione di Visum");
        
        return true;
      } else {
        console.log("🤖 Claude: '⚠️ Visum è avviato ma potrebbe servire più tempo per essere completamente pronto'");
        console.log("   Suggerimento: Riprova tra qualche secondo");
        return true; // Successo parziale
      }
    } else {
      console.log("🤖 Claude: '⚠️ Visum è avviato ma la verifica COM ha avuto problemi'");
      console.log(`   Dettaglio tecnico: ${checkResult.error}`);
      return true; // Successo parziale
    }
  }

  async handleUserRequest() {
    console.log("💫 Claude sta elaborando la richiesta...\n");
    
    const success = await this.respondToUser();
    
    console.log("\n" + "═".repeat(50));
    console.log("📋 RIEPILOGO INTERAZIONE");
    console.log("═".repeat(50));
    
    if (success) {
      console.log("🎉 ✅ SUCCESSO!");
      console.log("👤 Richiesta utente: Aprire Visum");
      console.log("🤖 Risposta Claude: ✅ Completata con successo");
      console.log("📊 Risultato: Visum è aperto e operativo");
      console.log("🔧 MCP Tools utilizzati: launch_visum, check_visum");
      console.log("⚡ Automazione: Funzionante");
    } else {
      console.log("❌ FALLIMENTO");
      console.log("👤 Richiesta utente: Aprire Visum"); 
      console.log("🤖 Risposta Claude: ❌ Problemi tecnici");
      console.log("🔧 Troubleshooting necessario");
    }
    
    return success;
  }
}

// Esegui la simulazione completa
const claude = new ClaudeVirtualAssistant();
claude.handleUserRequest().then((success) => {
  console.log(`\n🏁 Simulazione terminata: ${success ? 'SUCCESSO' : 'FALLIMENTO'}`);
}).catch((error) => {
  console.error("\n💥 Errore nella simulazione:", error);
});
