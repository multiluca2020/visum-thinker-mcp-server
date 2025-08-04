// Test singolo del tool launch_visum
import { spawn } from 'child_process';

console.log("🧪 TEST SINGOLO - Launch Visum Tool\n");

async function testLaunchVisum() {
  console.log("🚀 Test diretto del comando PowerShell per lanciare Visum...");
  
  const script = `
    try {
      # Check if Visum is already running
      $visumProcess = Get-Process -Name "Visum250" -ErrorAction SilentlyContinue
      
      if ($visumProcess) {
        @{
          success = $true
          message = "Visum already running"
          processId = $visumProcess.Id
          alreadyRunning = $true
        } | ConvertTo-Json
      } else {
        # Start Visum
        Write-Host "Starting Visum..."
        $visumPath = "H:\\Program Files\\PTV Vision\\PTV Visum 2025\\Exe\\Visum250.exe"
        
        if (Test-Path $visumPath) {
          $process = Start-Process -FilePath $visumPath -PassThru
          Start-Sleep -Seconds 3  # Reduced wait time
          
          @{
            success = $true
            message = "Visum started successfully"
            processId = $process.Id
            alreadyRunning = $false
          } | ConvertTo-Json
        } else {
          @{
            success = $false
            error = "Visum executable not found at expected path"
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
  let stderr = '';
  
  powershell.stdout.on('data', (data) => {
    const text = data.toString();
    output += text;
    console.log("📤 PowerShell output:", text.trim());
  });

  powershell.stderr.on('data', (data) => {
    const text = data.toString();
    stderr += text;
    console.log("⚠️ PowerShell stderr:", text.trim());
  });

  powershell.on('close', (code) => {
    console.log(`🏁 PowerShell chiuso con codice: ${code}`);
    console.log("📄 Output completo:", output);
    
    try {
      const result = JSON.parse(output.trim());
      console.log("✅ JSON parsato:", result);
      return result;
    } catch (e) {
      console.log("❌ Errore parsing JSON:", e.message);
      console.log("📝 Output raw:", output);
      return { success: false, error: 'JSON parse failed' };
    }
  });

  // Wait for completion
  return new Promise((resolve) => {
    powershell.on('close', () => {
      try {
        const result = JSON.parse(output.trim());
        resolve(result);
      } catch {
        resolve({ success: false, error: 'JSON parse failed', output });
      }
    });
    
    setTimeout(() => {
      powershell.kill();
      resolve({ success: false, error: 'Timeout dopo 20 secondi' });
    }, 20000);
  });
}

async function testViaDirect() {
  console.log("📡 Test via spawn diretto...");
  const result = await testLaunchVisum();
  
  console.log("\n🎯 RISULTATO TEST:");
  if (result.success) {
    console.log("✅ Launch Visum funziona!");
    console.log(`   Status: ${result.message}`);
    console.log(`   Process ID: ${result.processId}`);
    console.log(`   Already running: ${result.alreadyRunning}`);
  } else {
    console.log("❌ Launch Visum fallito:");
    console.log(`   Error: ${result.error}`);
  }
  
  return result;
}

testViaDirect().then(() => {
  console.log("\n✨ Test completato!");
}).catch(console.error);
