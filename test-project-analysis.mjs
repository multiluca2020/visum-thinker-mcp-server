// Test analisi progetto Visum già caricato
import { spawn } from 'child_process';

console.log("🔍 ANALISI PROGETTO VISUM CARICATO");
console.log("═".repeat(40));

async function analyzeLoadedProject() {
  console.log("📊 Analizzando il progetto Campoleone già caricato...\n");
  
  const script = `
    try {
      # Check if Visum is running
      $visumProcess = Get-Process -Name "Visum250" -ErrorAction SilentlyContinue
      
      if (!$visumProcess) {
        Write-Host "❌ Visum non è in esecuzione"
        @{ success = $false; error = "Visum not running" } | ConvertTo-Json
        exit
      }
      
      Write-Host "✅ Visum processo trovato: ID $($visumProcess.Id)"
      Write-Host "📝 Finestra: $($visumProcess.MainWindowTitle)"
      Write-Host ""
      
      # Method 1: Try New-Object approach (create new instance and try to connect)
      Write-Host "🔄 Metodo 1: Creazione nuova istanza COM..."
      try {
        $visum = New-Object -ComObject "Visum.Visum"
        Write-Host "✅ Oggetto COM creato"
        
        # Try to connect to existing session
        $visum.LoadVersion("2024")  # Try different version
        Write-Host "✅ Versione caricata"
        
        # Check if we have network data
        if ($visum.Net) {
          $nodeCount = $visum.Net.Nodes.Count
          $linkCount = $visum.Net.Links.Count
          $zoneCount = $visum.Net.Zones.Count
          
          Write-Host "📊 Network trovata!"
          Write-Host "   Nodi: $nodeCount"
          Write-Host "   Link: $linkCount"
          Write-Host "   Zone: $zoneCount"
          
          if ($nodeCount -gt 0) {
            @{
              success = $true
              method = "New-Object"
              networkStats = @{
                nodes = $nodeCount
                links = $linkCount
                zones = $zoneCount
              }
              message = "Network data found via New-Object"
            } | ConvertTo-Json -Depth 3
            exit
          }
        }
        
        Write-Host "⚠️ Network vuota con New-Object"
      } catch {
        Write-Host "❌ New-Object fallito: $($_.Exception.Message)"
      }
      
      # Method 2: Try file-based analysis
      Write-Host ""
      Write-Host "🔄 Metodo 2: Analisi diretta file progetto..."
      
      $projectFile = "H:\\go\\italferr2025\\Campoleone\\100625_Versione_base_v0.3_sub_ok_priv.ver"
      
      if (Test-Path $projectFile) {
        $fileInfo = Get-Item $projectFile
        Write-Host "✅ File progetto trovato:"
        Write-Host "   Path: $projectFile"
        Write-Host "   Size: $([math]::Round($fileInfo.Length / 1MB, 2)) MB"
        Write-Host "   Modified: $($fileInfo.LastWriteTime)"
        
        # Try to read some basic info from the file
        $fileSize = $fileInfo.Length
        
        @{
          success = $true
          method = "File-based"
          projectFile = $projectFile
          fileSize = $fileSize
          fileSizeMB = [math]::Round($fileSize / 1MB, 2)
          lastModified = $fileInfo.LastWriteTime.ToString()
          visumRunning = $true
          processId = $visumProcess.Id
          windowTitle = $visumProcess.MainWindowTitle
          message = "Project file analyzed, Visum process confirmed"
        } | ConvertTo-Json -Depth 3
      } else {
        Write-Host "❌ File progetto non trovato: $projectFile"
        
        @{
          success = $false
          error = "Project file not found"
          processId = $visumProcess.Id
          windowTitle = $visumProcess.MainWindowTitle
        } | ConvertTo-Json
      }
      
    } catch {
      Write-Host "❌ Errore generale: $($_.Exception.Message)"
      @{
        success = $false
        error = $_.Exception.Message
      } | ConvertTo-Json
    }
  `;

  const powershell = spawn('powershell', ['-ExecutionPolicy', 'Bypass', '-Command', script]);

  let output = '';
  let stderr = '';
  
  powershell.stdout.on('data', (data) => {
    const text = data.toString();
    output += text;
    console.log("📤", text.trim());
  });

  powershell.stderr.on('data', (data) => {
    const text = data.toString();
    stderr += text;
    console.log("⚠️", text.trim());
  });

  return new Promise((resolve) => {
    powershell.on('close', (code) => {
      console.log(`\n🏁 PowerShell chiuso con codice: ${code}`);
      
      try {
        const jsonStart = output.indexOf('{');
        if (jsonStart !== -1) {
          const jsonStr = output.substring(jsonStart);
          const result = JSON.parse(jsonStr);
          console.log("✅ Risultato analisi:", result);
          resolve(result);
        } else {
          console.log("❌ Nessun JSON trovato nell'output");
          resolve({ success: false, error: 'No JSON found' });
        }
      } catch (e) {
        console.log("❌ Errore parsing JSON:", e.message);
        console.log("Raw output:", output);
        resolve({ success: false, error: 'JSON parse error' });
      }
    });
    
    setTimeout(() => {
      powershell.kill();
      resolve({ success: false, error: 'Timeout' });
    }, 20000);
  });
}

async function suggestSolutions() {
  console.log("\n💡 SOLUZIONI ALTERNATIVE");
  console.log("═".repeat(25));
  
  console.log("🔧 Opzioni per analisi network:");
  console.log("   1. ✅ File-based: Analisi diretta file .ver");
  console.log("   2. 🔄 Script Python: Usare VisumPy se disponibile");
  console.log("   3. 🖥️  Manual: Interfaccia Visum per export dati");
  console.log("   4. 📋 Registry: Controllare COM registration");
  console.log("   5. 🚀 Alternative: Usare file di export CSV/XML");
  
  console.log("\n🎯 RACCOMANDAZIONE:");
  console.log("   Dato che Visum è visibile e il progetto è caricato,");
  console.log("   possiamo usare l'interfaccia Visum per esportare");
  console.log("   i dati di rete in formato analizzabile.");
}

async function runAnalysis() {
  const result = await analyzeLoadedProject();
  
  console.log("\n" + "═".repeat(40));
  console.log("📊 RISULTATO ANALISI");
  console.log("═".repeat(40));
  
  if (result.success) {
    console.log("🎉 ✅ ANALISI COMPLETATA!");
    console.log(`   Metodo: ${result.method}`);
    
    if (result.networkStats) {
      console.log("📊 Statistiche Network:");
      console.log(`   • Nodi: ${result.networkStats.nodes}`);
      console.log(`   • Link: ${result.networkStats.links}`);
      console.log(`   • Zone: ${result.networkStats.zones}`);
    }
    
    if (result.projectFile) {
      console.log("📁 File Progetto:");
      console.log(`   • Path: ${result.projectFile}`);
      console.log(`   • Size: ${result.fileSizeMB} MB`);
      console.log(`   • Modified: ${result.lastModified}`);
    }
    
    console.log("🖥️  Visum Status:");
    console.log(`   • Process ID: ${result.processId}`);
    console.log(`   • Window: ${result.windowTitle || 'In caricamento...'}`);
    
  } else {
    console.log("❌ ANALISI FALLITA");
    console.log(`   Errore: ${result.error}`);
  }
  
  await suggestSolutions();
}

runAnalysis().catch(console.error);
