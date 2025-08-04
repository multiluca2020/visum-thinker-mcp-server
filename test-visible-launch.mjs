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
        # Force Visum to start visibly with WindowStyle Normal
        Write-Host "Launching Visum with visible window..."
        $process = Start-Process -FilePath $visumPath -WindowStyle Normal -PassThru
        Write-Host "Process started with ID: $($process.Id)"
        
        Start-Sleep -Seconds 3  # Wait for initial startup
        
        @{
          success = $true
          message = "Visum started visibly"
          processId = $process.Id
          windowStyle = "Normal"
          visible = $true
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
    Get-Process -Name "Visum250" -ErrorAction SilentlyContinue | 
    Select-Object ProcessName, Id, StartTime, MainWindowTitle | 
    ConvertTo-Json
  `;
  
  const powershell = spawn('powershell', ['-ExecutionPolicy', 'Bypass', '-Command', checkScript]);
  
  let output = '';
  powershell.stdout.on('data', (data) => {
    output += data.toString();
  });
  
  return new Promise((resolve) => {
    powershell.on('close', () => {
      try {
        if (output.trim()) {
          const processes = JSON.parse(output.trim());
          console.log("✅ Visum processi trovati:", processes);
          resolve(processes);
        } else {
          console.log("❌ Nessun processo Visum trovato");
          resolve(null);
        }
      } catch (e) {
        console.log("⚠️ Errore verifica:", e.message);
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
