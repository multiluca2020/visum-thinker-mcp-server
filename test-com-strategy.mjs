// Strategia: Lancia Visum vuoto per COM, poi carica progetto via LoadVersion
import { spawn } from 'child_process';

console.log("🚀 STRATEGIA COM: Visum vuoto + LoadVersion");
console.log("═".repeat(50));

async function launchVisumForCom() {
  console.log("🔧 Passo 1: Lancio Visum vuoto per abilitare COM...");
  
  const script = `
    try {
      # Launch Visum without any project (clean start)
      $visumPath = "H:\\Program Files\\PTV Vision\\PTV Visum 2025\\Exe\\Visum250.exe"
      
      if (Test-Path $visumPath) {
        Write-Host "Launching Visum without project..."
        $process = Start-Process -FilePath $visumPath -WindowStyle Normal -PassThru
        Write-Host "Visum started with PID: $($process.Id)"
        
        # Wait for Visum to fully initialize
        Start-Sleep -Seconds 8
        
        @{
          success = $true
          processId = $process.Id
          message = "Visum launched without project"
        } | ConvertTo-Json
      } else {
        @{
          success = $false
          error = "Visum executable not found"
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
    const text = data.toString();
    output += text;
    console.log("📡", text.trim());
  });

  return new Promise((resolve) => {
    powershell.on('close', (code) => {
      try {
        const lines = output.split('\n');
        for (const line of lines) {
          if (line.trim().startsWith('{')) {
            const result = JSON.parse(line.trim());
            resolve(result);
            return;
          }
        }
        resolve({ success: false, error: 'No JSON found' });
      } catch (error) {
        resolve({ success: false, error: error.message });
      }
    });
  });
}

async function testComAndLoadProject() {
  console.log("🔧 Passo 2: Test COM e caricamento progetto...");
  
  const projectPath = "H:\\go\\italferr2025\\Campoleone\\100625_Versione_base_v0.3_sub_ok_priv.ver";
  
  const script = `
    try {
      Write-Host "Testing COM connection and loading project..."
      
      # Try to connect to Visum via COM
      try {
        $visum = [System.Runtime.InteropServices.Marshal]::GetActiveObject("Visum.Visum")
        Write-Host "✅ Connected to Visum via GetActiveObject!"
        
        # Load the project
        Write-Host "Loading project: ${projectPath}"
        $visum.LoadVersion("${projectPath}")
        Write-Host "✅ Project loaded successfully!"
        
        # Get network statistics
        $net = $visum.Net
        $nodeCount = try { $net.Nodes.Count } catch { 0 }
        $linkCount = try { $net.Links.Count } catch { 0 }
        $zoneCount = try { $net.Zones.Count } catch { 0 }
        
        Write-Host "📊 Network stats: Nodes=$nodeCount, Links=$linkCount, Zones=$zoneCount"
        
        @{
          success = $true
          comConnection = "GetActiveObject"
          projectLoaded = $true
          projectPath = "${projectPath}"
          networkStats = @{
            nodes = $nodeCount
            links = $linkCount
            zones = $zoneCount
          }
        } | ConvertTo-Json -Depth 3
        
      } catch {
        Write-Host "❌ GetActiveObject failed: $($_.Exception.Message)"
        
        # Try New-Object as fallback
        try {
          Write-Host "Trying New-Object fallback..."
          $visum = New-Object -ComObject "Visum.Visum"
          Write-Host "⚠️ Created new Visum instance"
          
          @{
            success = $true
            comConnection = "New-Object"
            projectLoaded = $false
            warning = "Created new instance instead of using existing"
          } | ConvertTo-Json
          
        } catch {
          @{
            success = $false
            error = "Both COM methods failed"
            details = $_.Exception.Message
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
    const text = data.toString();
    output += text;
    console.log("📡", text.trim());
  });

  return new Promise((resolve) => {
    powershell.on('close', (code) => {
      try {
        const lines = output.split('\n');
        for (const line of lines) {
          if (line.trim().startsWith('{')) {
            const result = JSON.parse(line.trim());
            resolve(result);
            return;
          }
        }
        resolve({ success: false, error: 'No JSON found' });
      } catch (error) {
        resolve({ success: false, error: error.message });
      }
    });
  });
}

async function runComStrategy() {
  console.log("🎯 Strategia: Visum vuoto → COM → LoadVersion\n");
  
  // Passo 1: Lancia Visum vuoto
  const launchResult = await launchVisumForCom();
  
  if (!launchResult.success) {
    console.log("❌ Fallimento nel lancio Visum:", launchResult.error);
    return;
  }
  
  console.log("✅ Visum lanciato, PID:", launchResult.processId);
  
  // Attesa aggiuntiva per stabilizzare COM
  console.log("⏳ Attendo che COM si stabilizzi...");
  await new Promise(r => setTimeout(r, 5000));
  
  // Passo 2: Test COM e caricamento progetto
  const comResult = await testComAndLoadProject();
  
  console.log("\n" + "═".repeat(50));
  console.log("🏁 RISULTATI STRATEGIA COM");
  console.log("═".repeat(50));
  
  console.log(JSON.stringify(comResult, null, 2));
  
  if (comResult.success) {
    console.log("\n✅ SUCCESSO!");
    console.log(`🔗 Connessione COM: ${comResult.comConnection}`);
    
    if (comResult.projectLoaded) {
      console.log("📁 Progetto caricato correttamente!");
      console.log("📊 Statistiche network:");
      const stats = comResult.networkStats;
      console.log(`   Nodi: ${stats.nodes}`);
      console.log(`   Link: ${stats.links}`);
      console.log(`   Zone: ${stats.zones}`);
      
      console.log("\n🎉 PERFETTO! Ora l'MCP server dovrebbe funzionare!");
    } else {
      console.log("⚠️ COM funziona ma progetto non caricato");
    }
  } else {
    console.log("\n❌ FALLIMENTO!");
    console.log(`Errore: ${comResult.error}`);
  }
}

runComStrategy().catch(console.error);
