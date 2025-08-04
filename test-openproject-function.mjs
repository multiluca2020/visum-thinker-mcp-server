// Test diretto della funzione openProject
import { spawn } from 'child_process';

console.log("🔧 TEST DIRETTO: funzione openProject");
console.log("═".repeat(50));

const projectPath = "H:\\go\\italferr2025\\Campoleone\\100625_Versione_base_v0.3_sub_ok_priv.ver";

async function openProject(projectPath) {
  return new Promise((resolve) => {
    const script = `
      try {
        Write-Host "Opening Visum project: ${projectPath}"
        
        # Create Visum object
        $visum = New-Object -ComObject "Visum.Visum"
        
        # Check if file exists
        if (Test-Path "${projectPath}") {
          # Open the project
          $visum.LoadVersion("${projectPath}")
          
          # Get basic project info
          $net = $visum.Net
          $nodeCount = try { $net.Nodes.Count } catch { 0 }
          $linkCount = try { $net.Links.Count } catch { 0 }
          $zoneCount = try { $net.Zones.Count } catch { 0 }
          
          @{
            success = $true
            message = "Project opened successfully"
            projectPath = "${projectPath}"
            networkStats = @{
              nodes = $nodeCount
              links = $linkCount
              zones = $zoneCount
            }
          } | ConvertTo-Json -Depth 3
        } else {
          @{
            success = $false
            error = "Project file not found: ${projectPath}"
          } | ConvertTo-Json
        }
        
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($visum) | Out-Null
        
      } catch {
        @{
          success = $false
          error = $_.Exception.Message
        } | ConvertTo-Json
      }
    `;

    console.log("📤 Eseguo PowerShell script...");
    
    const powershell = spawn('powershell', ['-ExecutionPolicy', 'Bypass', '-Command', script]);

    let output = '';
    let errorOutput = '';
    
    powershell.stdout.on('data', (data) => {
      const text = data.toString();
      output += text;
      console.log("📡 PS STDOUT:", text.trim());
    });
    
    powershell.stderr.on('data', (data) => {
      const text = data.toString();
      errorOutput += text;
      console.log("📡 PS STDERR:", text.trim());
    });

    powershell.on('close', (code) => {
      console.log(`\n🏁 PowerShell chiuso con codice: ${code}`);
      console.log(`📊 Output length: ${output.length}`);
      console.log(`📊 Error length: ${errorOutput.length}`);
      
      if (output.trim()) {
        try {
          const result = JSON.parse(output.trim());
          console.log("✅ JSON parsato con successo!");
          resolve(result);
        } catch (parseError) {
          console.log("❌ Errore parsing JSON:", parseError.message);
          console.log("Raw output:", output);
          resolve({ success: false, error: 'Failed to parse PowerShell output', rawOutput: output });
        }
      } else {
        console.log("❌ Nessun output da PowerShell");
        resolve({ success: false, error: 'No PowerShell output', errorOutput });
      }
    });
    
    // Timeout per il PowerShell
    setTimeout(() => {
      console.log("⏰ Timeout PowerShell - termino processo");
      powershell.kill('SIGTERM');
      resolve({ success: false, error: 'PowerShell timeout after 30 seconds' });
    }, 30000);
  });
}

async function testOpenProject() {
  console.log(`📁 Testing with: ${projectPath}`);
  
  const result = await openProject(projectPath);
  
  console.log("\n" + "═".repeat(50));
  console.log("🏁 RISULTATO:");
  console.log("═".repeat(50));
  
  console.log(JSON.stringify(result, null, 2));
  
  if (result.success) {
    console.log("\n✅ SUCCESSO!");
    console.log("📊 Statistiche network:");
    if (result.networkStats) {
      console.log(`   Nodi: ${result.networkStats.nodes}`);
      console.log(`   Link: ${result.networkStats.links}`);
      console.log(`   Zone: ${result.networkStats.zones}`);
    }
  } else {
    console.log("\n❌ FALLIMENTO!");
    console.log(`   Errore: ${result.error}`);
  }
}

testOpenProject().catch(console.error);
