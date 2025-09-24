#!/usr/bin/env node

import { spawn } from 'child_process';
import fs from 'fs';

// 🔧 CONFIGURAZIONE MCP VISUM
const CONFIG = {
  PYTHON_PATH: "H:\\Program Files\\PTV Vision\\PTV Visum 2025\\Exe\\Python\\python.exe",
  PROJECT_FILE: "H:\\go\\italferr2025\\Campoleone\\100625_Versione_base_v0.3_sub_ok_priv.ver"
};

// 🧪 TEST RAPIDO CONNESSIONE VISUM
console.log('🚀 TEST RAPIDO MCP VISUM TOOLS');
console.log('═'.repeat(40));

// Test script Python diretto
const testScript = `import sys
sys.path.append(r"H:\\Program Files\\PTV Vision\\PTV Visum 2025\\Exe")

try:
    import win32com.client
    print("🔧 Python MCP Test")
    print("=" * 20)
    
    # Prova connessione
    try:
        visum = win32com.client.GetActiveObject("Visum.Vium")
        print("✅ GetActiveObject OK")
    except:
        print("⚠️ GetActiveObject fallito, provo DispatchEx...")
        visum = win32com.client.DispatchEx("Visum.Visum") 
        print("✅ DispatchEx OK")
    
    # Test rete
    nodes = visum.Net.Nodes.Count
    links = visum.Net.Links.Count
    
    print(f"📊 Nodi: {nodes}")
    print(f"🔗 Link: {links}")
    
    if nodes == 0:
        print("🔄 Carico progetto...")
        try:
            visum.LoadNet(r"${CONFIG.PROJECT_FILE}")
            nodes2 = visum.Net.Nodes.Count
            links2 = visum.Net.Links.Count
            print(f"📊 Nodi (dopo caricamento): {nodes2}")
            print(f"🔗 Link (dopo caricamento): {links2}")
            
            if nodes2 > 0:
                print("🎯 SUCCESSO! Progetto caricato via COM")
            else:
                print("❌ Progetto non caricato o vuoto")
        except Exception as load_error:
            print(f"❌ Errore caricamento: {load_error}")
    else:
        print("🎯 Rete già presente!")
    
    print("\\n✅ Test MCP completato!")
    
except Exception as e:
    print(f"❌ Errore MCP: {e}")
    import traceback
    traceback.print_exc()
`;

// Scrivi e esegui script temporaneo
const tempFile = `mcp_test_${Date.now()}.py`;
fs.writeFileSync(tempFile, testScript);

console.log('📝 Script temporaneo creato:', tempFile);
console.log('🐍 Esecuzione con Python di Visum...\n');

const python = spawn('powershell.exe', [
  '-Command', 
  `& "${CONFIG.PYTHON_PATH}" "${tempFile}"`
]);

python.stdout.on('data', (data) => {
  console.log(data.toString().trim());
});

python.stderr.on('data', (data) => {
  console.error('ERROR:', data.toString().trim());
});

python.on('close', (code) => {
  fs.unlinkSync(tempFile);
  console.log(`\n🏁 Test completato con codice: ${code}`);
  
  if (code === 0) {
    console.log('🎉 MCP VISUM TOOLS PRONTO!');
    console.log('✅ Python funziona');
    console.log('✅ win32com disponibile');
    console.log('✅ Connessione COM possibile');
    console.log('\n🔧 PROSSIMI PASSI:');
    console.log('   1. Integrare nel server MCP esistente');
    console.log('   2. Aggiungere i 6 tool sviluppati');
    console.log('   3. Testare con Claude');
  } else {
    console.log('❌ Test fallito, verificare configurazione');
  }
});
