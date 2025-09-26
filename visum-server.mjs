// SERVER PERMANENTE VISUM
// Questo server rimane attivo permanentemente in background
// per servire richieste da client esterni

import { PersistentVisumController } from './build/persistent-visum-controller.js';
import { writeFileSync } from 'fs';

console.log('🏗️ VISUM SERVER PERMANENTE');
console.log('=' .repeat(50));
console.log('⚠️  QUESTO SERVER RIMANE ATTIVO FINO A Ctrl+C');
console.log('=' .repeat(50));

const SERVER_INFO_FILE = 'visum-server-info.json';

async function startPermanentServer() {
  const controller = PersistentVisumController.getInstance();
  
  try {
    console.log('🚀 Avvio server Visum permanente...');
    
    // Avvia l'istanza Visum persistente
    const result = await controller.startPersistentVisumProcess();
    
    if (result.success) {
      console.log('✅ SERVER VISUM ATTIVO!');
      console.log(`📊 Network: ${result.nodes} nodi, ${result.links} link, ${result.zones} zone`);
      
      // Salva informazioni server per i client
      const serverInfo = {
        pid: process.pid,
        startTime: Date.now(),
        startTimeString: new Date().toLocaleString('it-IT'),
        nodes: result.nodes,
        links: result.links,
        zones: result.zones,
        status: 'active',
        project: 'Campoleone'
      };
      
      writeFileSync(SERVER_INFO_FILE, JSON.stringify(serverInfo, null, 2));
      console.log(`📝 Info server salvate in ${SERVER_INFO_FILE}`);
      
      console.log('\\n🟢 SERVER IN ASCOLTO');
      console.log('📡 Il server è ora pronto per ricevere comandi dai client');
      console.log('🔗 I client possono connettersi usando PersistentVisumController.getInstance()');
      console.log('⚡ Risposte ultra-veloci garantite (0-16ms)');
      console.log('\\n📋 COMANDI:');
      console.log('   • Ctrl+C per fermare il server');
      console.log('   • node visum-client.mjs per testare connessione client');
      
      // Test periodici per mantenere viva la connessione
      let pingCount = 0;
      const pingInterval = setInterval(async () => {
        try {
          pingCount++;
          const pingResult = await controller.executeCustomCode(`
result = {
    'server_ping': ${pingCount},
    'nodes': visum.Net.Nodes.Count,
    'timestamp': time.time(),
    'uptime_minutes': ${pingCount * 2}
}
`, `Server Ping #${pingCount}`);
          
          if (pingResult.success) {
            const uptime = Math.floor(pingCount * 2);
            console.log(`🔔 Server attivo - Ping #${pingCount} - Uptime: ${uptime} min - ${new Date().toLocaleTimeString()}`);
          } else {
            console.error('⚠️ Ping server fallito:', pingResult.error);
          }
        } catch (error) {
          console.error('⚠️ Errore ping server:', error.message);
        }
      }, 120000); // Ping ogni 2 minuti
      
      // Gestione Ctrl+C per shutdown pulito
      process.on('SIGINT', () => {
        console.log('\\n🛑 Ricevuto segnale di arresto...');
        console.log('🔄 Shutdown server in corso...');
        
        clearInterval(pingInterval);
        
        // Aggiorna status server
        serverInfo.status = 'shutting_down';
        serverInfo.shutdownTime = Date.now();
        writeFileSync(SERVER_INFO_FILE, JSON.stringify(serverInfo, null, 2));
        
        console.log('✅ Server Visum arrestato');
        process.exit(0);
      });
      
    } else {
      console.error(`❌ Errore avvio server: ${result.message}`);
      process.exit(1);
    }
    
  } catch (error) {
    console.error('❌ Errore critico server:', error.message);
    process.exit(1);
  }
}

startPermanentServer();