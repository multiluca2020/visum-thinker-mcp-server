// Test diretto connessione COM con Visum esistente
import { spawn } from 'child_process';

console.log("🔧 TEST CONNESSIONE COM VISUM ESISTENTE");
console.log("═".repeat(50));

async function testComConnection() {
  console.log("🔍 Provo a connettermi all'istanza Visum esistente...");
  
  const script = `
    try {
      Write-Host "Tentativo connessione a Visum esistente..."
      
      # Prova GetActiveObject per connettersi all'istanza esistente
      try {
        $visum = [System.Runtime.InteropServices.Marshal]::GetActiveObject("Visum.Visum")
        Write-Host "✅ Connesso a istanza esistente!"
        
        # Test basic functionality
        $net = $visum.Net
        if ($net -ne $null) {
          Write-Host "✅ Network object ottenuto!"
          
          $nodeCount = try { $net.Nodes.Count } catch { "Error" }
          $linkCount = try { $net.Links.Count } catch { "Error" }
          $zoneCount = try { $net.Zones.Count } catch { "Error" }
          
          Write-Host "📊 Nodi: $nodeCount"
          Write-Host "📊 Link: $linkCount"  
          Write-Host "📊 Zone: $zoneCount"
          
          @{
            success = $true
            connection = "GetActiveObject"
            network = @{
              nodes = $nodeCount
              links = $linkCount
              zones = $zoneCount
              available = $true
            }
          } | ConvertTo-Json -Depth 3
        } else {
          @{
            success = $false
            error = "Network object is null"
            connection = "GetActiveObject"
          } | ConvertTo-Json
        }
      } catch {
        Write-Host "❌ GetActiveObject failed: $($_.Exception.Message)"
        
        # Fallback to New-Object (creates new instance)
        try {
          Write-Host "🔄 Trying New-Object as fallback..."
          $visum = New-Object -ComObject "Visum.Visum"
          Write-Host "⚠️ Created new instance (not ideal)"
          
          @{
            success = $true
            connection = "New-Object"
            warning = "Created new Visum instance"
            network = @{
              nodes = 0
              links = 0
              zones = 0
              available = $false
            }
          } | ConvertTo-Json -Depth 3
        } catch {
          @{
            success = $false
            error = "Both GetActiveObject and New-Object failed"
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
  let errorOutput = '';
  
  powershell.stdout.on('data', (data) => {
    const text = data.toString();
    output += text;
    console.log("📡 PS:", text.trim());
  });
  
  powershell.stderr.on('data', (data) => {
    const text = data.toString();
    errorOutput += text;
    console.log("⚠️ PS Error:", text.trim());
  });

  return new Promise((resolve) => {
    powershell.on('close', (code) => {
      console.log(`\n🏁 PowerShell chiuso con codice: ${code}`);
      
      try {
        // Cerca JSON nell'output
        const lines = output.split('\n');
        for (const line of lines) {
          if (line.trim().startsWith('{')) {
            const result = JSON.parse(line.trim());
            resolve(result);
            return;
          }
        }
        resolve({ success: false, error: 'No JSON found in output' });
      } catch (error) {
        resolve({ success: false, error: `Parse error: ${error.message}`, rawOutput: output });
      }
    });
    
    setTimeout(() => {
      powershell.kill();
      resolve({ success: false, error: 'Timeout' });
    }, 15000);
  });
}

async function runTest() {
  const result = await testComConnection();
  
  console.log("\n" + "═".repeat(50));
  console.log("🏁 RISULTATI TEST COM");
  console.log("═".repeat(50));
  
  console.log(JSON.stringify(result, null, 2));
  
  if (result.success) {
    console.log("\n✅ SUCCESSO!");
    console.log(`🔗 Tipo connessione: ${result.connection}`);
    
    if (result.network) {
      console.log("📊 Statistiche network:");
      console.log(`   Nodi: ${result.network.nodes}`);
      console.log(`   Link: ${result.network.links}`);
      console.log(`   Zone: ${result.network.zones}`);
      console.log(`   Disponibile: ${result.network.available}`);
    }
    
    if (result.warning) {
      console.log(`⚠️ Avviso: ${result.warning}`);
    }
    
    return result.connection === "GetActiveObject";
  } else {
    console.log("\n❌ FALLIMENTO!");
    console.log(`Errore: ${result.error}`);
    return false;
  }
}

runTest().then((success) => {
  console.log(`\n🎯 GetActiveObject funziona: ${success ? 'SÌ' : 'NO'}`);
}).catch(console.error);
