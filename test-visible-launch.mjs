// Test diretto del lancio Visum visibile
import { spawn } from 'child_process';

console.log("🚀 TEST LANCIO VISUM VISIBILE");
console.log("═".repeat(35));

async function testVisibleLaunch() {
  console.log("🧪 Eseguo il comando PowerShell per lanciare Visum visibile...\n");
  
  const script = `
    try {
      # Check if Visum is already running
      $visumProcess = Get-Process -Name "Visum250" -ErrorAction SilentlyContinue
      
      if ($visumProcess) {
        Write-Host "Visum già in esecuzione, terminando prima..."
        $visumProcess | Stop-Process -Force
        Start-Sleep -Seconds 2
      }
      
      # Start Visum visibly
      Write-Host "Starting Visum visibly..."
      $visumPath = "H:\\Program Files\\PTV Vision\\PTV Visum 2025\\Exe\\Visum250.exe"
      
      if (Test-Path $visumPath) {
        # Launch Visum with the specific project file
        $projectFile = "H:\\go\\italferr2025\\Campoleone\\100625_Versione_base_v0.3_sub_ok_priv.ver"
        
        if (Test-Path $projectFile) {
          Write-Host "Launching Visum with project: $projectFile"
          $process = Start-Process -FilePath $visumPath -ArgumentList $projectFile -WindowStyle Normal -PassThru
          Write-Host "Process started with ID: $($process.Id)"
          Write-Host "Project loaded: $projectFile"
        } else {
          Write-Host "Launching Visum without project (file not found)"
          $process = Start-Process -FilePath $visumPath -WindowStyle Normal -PassThru
          Write-Host "Process started with ID: $($process.Id)"
        }
        
        Start-Sleep -Seconds 5  # Wait longer for project loading
        
        @{
          success = $true
          message = "Visum started visibly with project"
          processId = $process.Id
          windowStyle = "Normal"
          visible = $true
          projectLoaded = $(Test-Path $projectFile)
        } | ConvertTo-Json
      } else {
        @{
          success = $false
          error = "Visum executable not found at expected path"
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
          console.log("✅ Risultato:", result);
          resolve(result);
        } else {
          console.log("❌ Nessun JSON trovato nell'output");
          resolve({ success: false, error: 'No JSON found' });
        }
      } catch (e) {
        console.log("❌ Errore parsing JSON:", e.message);
        resolve({ success: false, error: 'JSON parse error' });
      }
    });
    
    setTimeout(() => {
      powershell.kill();
      resolve({ success: false, error: 'Timeout' });
    }, 15000);
  });
}

async function verifyVisum() {
  console.log("\n🔍 Verifica che Visum sia effettivamente lanciato...");
  
  const checkScript = `
    # Check process
    $process = Get-Process -Name "Visum250" -ErrorAction SilentlyContinue
    if ($process) {
      Write-Host "Process found: $($process.ProcessName) ID:$($process.Id)"
      Write-Host "Main Window: $($process.MainWindowTitle)"
      
      # Try to connect via COM to get actual network stats
      try {
        Write-Host "Attempting COM connection..."
        $visum = [System.Runtime.InteropServices.Marshal]::GetActiveObject("Visum.Visum")
        
        if ($visum -and $visum.Net) {
          $nodeCount = $visum.Net.Nodes.Count
          $linkCount = $visum.Net.Links.Count
          $zoneCount = $visum.Net.Zones.Count
          
          Write-Host "✅ Network Statistics:"
          Write-Host "  Nodes: $nodeCount"
          Write-Host "  Links: $linkCount" 
          Write-Host "  Zones: $zoneCount"
          
          @{
            processFound = $true
            processId = $process.Id
            mainWindow = $process.MainWindowTitle
            comConnected = $true
            networkStats = @{
              nodes = $nodeCount
              links = $linkCount
              zones = $zoneCount
            }
          } | ConvertTo-Json -Depth 3
        } else {
          Write-Host "❌ COM connected but no network data"
          @{
            processFound = $true
            processId = $process.Id
            mainWindow = $process.MainWindowTitle
            comConnected = $false
            error = "No network data available"
          } | ConvertTo-Json
        }
      } catch {
        Write-Host "❌ COM connection failed: $($_.Exception.Message)"
        @{
          processFound = $true
          processId = $process.Id
          mainWindow = $process.MainWindowTitle
          comConnected = $false
          comError = $_.Exception.Message
        } | ConvertTo-Json
      }
    } else {
      Write-Host "❌ No Visum process found"
      @{ processFound = $false } | ConvertTo-Json
    }
  `;
  
  const powershell = spawn('powershell', ['-ExecutionPolicy', 'Bypass', '-Command', checkScript]);
  
  let output = '';
  powershell.stdout.on('data', (data) => {
    const text = data.toString();
    output += text;
    console.log("📤", text.trim());
  });
  
  return new Promise((resolve) => {
    powershell.on('close', () => {
      try {
        const jsonStart = output.indexOf('{');
        if (jsonStart !== -1) {
          const jsonStr = output.substring(jsonStart);
          const result = JSON.parse(jsonStr);
          console.log("✅ Risultato verifica:", result);
          resolve(result);
        } else {
          console.log("❌ Nessun JSON trovato nell'output");
          resolve(null);
        }
      } catch (e) {
        console.log("⚠️ Errore parsing JSON:", e.message);
        resolve(null);
      }
    });
  });
}

async function runTest() {
  const result = await testVisibleLaunch();
  
  console.log("\n⏳ Attendo che Visum si carichi completamente...");
  await new Promise(r => setTimeout(r, 5000));
  
  await verifyVisum();
  
  console.log("\n" + "═".repeat(35));
  console.log("📊 RISULTATO FINALE");
  console.log("═".repeat(35));
  
  if (result.success) {
    console.log("🎉 ✅ SUCCESSO!");
    console.log(`   Process ID: ${result.processId}`);
    console.log(`   Visibile: ${result.visible}`);
    console.log(`   Window Style: ${result.windowStyle}`);
    console.log("\n📱 Ora Visum dovrebbe essere visibile sullo schermo!");
  } else {
    console.log("❌ FALLIMENTO");
    console.log(`   Errore: ${result.error}`);
  }
}

runTest().catch(console.error);
