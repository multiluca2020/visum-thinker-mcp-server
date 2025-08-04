// Test diretto statistiche connettività con PowerShell
import { spawn } from 'child_process';

console.log("📊 ANALISI CONNETTIVITÀ DIRETTA - RETE CAMPOLEONE");
console.log("═".repeat(60));

async funct    console.log("\n🤖 Claude: \"Analisi di connettività completata!\"");
    console.log("🤖 Claude: \"La rete ha " + conn.level.toLowerCase() + " connettività con " + basic.nodes.toLocaleString() + " nodi.\"");n getConnectivityStats() {
  console.log("🔍 Ottengo statistiche dettagliate di connettività...");
  
  const projectPath = "H:\\go\\italferr2025\\Campoleone\\100625_Versione_base_v0.3_sub_ok_priv.ver";
  
  const script = `
    try {
      Write-Host "Analizzando connettività rete Campoleone..."
      
      # Create Visum COM object and load project
      $visum = New-Object -ComObject "Visum.Visum"
      $visum.LoadVersion("${projectPath}")
      
      Write-Host "Progetto caricato, analizzando rete..."
      
      # Get network object
      $net = $visum.Net
      
      # Basic network statistics
      $nodeCount = try { $net.Nodes.Count } catch { 0 }
      $linkCount = try { $net.Links.Count } catch { 0 }
      $zoneCount = try { $net.Zones.Count } catch { 0 }
      
      Write-Host "Nodi: $nodeCount"
      Write-Host "Link: $linkCount"
      Write-Host "Zone: $zoneCount"
      
      # Public transport statistics
      $lineCount = try { $net.Lines.Count } catch { 0 }
      $stopCount = try { $net.StopPoints.Count } catch { 0 }
      $timeProfileCount = try { $net.TimeProfiles.Count } catch { 0 }
      $vehicleJourneyCount = try { $net.VehicleJourneys.Count } catch { 0 }
      
      Write-Host "Linee: $lineCount"
      Write-Host "Fermate: $stopCount"
      Write-Host "Profili temporali: $timeProfileCount"
      Write-Host "Corse veicoli: $vehicleJourneyCount"
      
      # Calculate connectivity metrics
      $avgLinksPerNode = if ($nodeCount -gt 0) { [math]::Round(($linkCount * 2.0) / $nodeCount, 2) } else { 0 }
      $connectivityRatio = if ($nodeCount -gt 0) { [math]::Round($linkCount / $nodeCount, 2) } else { 0 }
      $networkDensity = if ($nodeCount -gt 1) { [math]::Round(($linkCount / (($nodeCount * ($nodeCount - 1)) / 2)) * 100, 6) } else { 0 }
      
      Write-Host "Connettività calcolata:"
      Write-Host "  - Media link per nodo: $avgLinksPerNode"
      Write-Host "  - Rapporto connettività: $connectivityRatio"
      Write-Host "  - Densità rete: $networkDensity%"
      
      # Determine connectivity level
      $connectivityLevel = if ($avgLinksPerNode -gt 3) { "Alta" } 
                          elseif ($avgLinksPerNode -gt 2) { "Media" } 
                          else { "Bassa" }
      
      # Get network file info
      $networkFile = try { $visum.VersionFile } catch { "Unknown" }
      
      @{
        success = $true
        projectPath = "${projectPath}"
        networkFile = $networkFile
        basicStats = @{
          nodes = $nodeCount
          links = $linkCount
          zones = $zoneCount
        }
        publicTransport = @{
          lines = $lineCount
          stops = $stopCount
          timeProfiles = $timeProfileCount
          vehicleJourneys = $vehicleJourneyCount
        }
        connectivity = @{
          avgLinksPerNode = $avgLinksPerNode
          connectivityRatio = $connectivityRatio
          networkDensity = $networkDensity
          level = $connectivityLevel
        }
        analysisDate = (Get-Date).ToString()
      } | ConvertTo-Json -Depth 4
      
      # Clean up
      [System.Runtime.InteropServices.Marshal]::ReleaseComObject($visum) | Out-Null
      
    } catch {
      Write-Host "Errore: $($_.Exception.Message)"
      @{
        success = $false
        error = $_.Exception.Message
      } | ConvertTo-Json
    }
  `;

  const powershell = spawn('powershell', ['-ExecutionPolicy', 'Bypass', '-Command', script]);

  let output = '';
  let allOutput = '';
  
  powershell.stdout.on('data', (data) => {
    const text = data.toString();
    allOutput += text;
    
    // Cerca JSON
    if (text.includes('{')) {
      output += text;
    }
    
    // Mostra progress
    if (text.includes('Nodi:') || text.includes('Link:') || text.includes('Zone:')) {
      console.log("📊", text.trim());
    } else if (text.includes('Linee:') || text.includes('Fermate:')) {
      console.log("🚌", text.trim());
    } else if (text.includes('Media link') || text.includes('Rapporto') || text.includes('Densità')) {
      console.log("🔗", text.trim());
    } else if (text.trim() && !text.includes('{') && !text.includes('}')) {
      console.log("📡", text.trim());
    }
  });

  return new Promise((resolve) => {
    powershell.on('close', (code) => {
      console.log(`\n🏁 PowerShell chiuso con codice: ${code}`);
      
      try {
        // Cerca JSON nell'output
        const jsonStart = allOutput.indexOf('{');
        if (jsonStart !== -1) {
          const jsonStr = allOutput.substring(jsonStart);
          const endBrace = jsonStr.lastIndexOf('}');
          if (endBrace !== -1) {
            const cleanJson = jsonStr.substring(0, endBrace + 1);
            const result = JSON.parse(cleanJson);
            resolve(result);
            return;
          }
        }
        resolve({ success: false, error: 'No valid JSON found' });
      } catch (error) {
        console.log("⚠️ JSON parse error:", error.message);
        resolve({ success: false, error: error.message, rawOutput: allOutput });
      }
    });
    
    setTimeout(() => {
      powershell.kill();
      resolve({ success: false, error: 'Timeout dopo 60 secondi' });
    }, 60000);
  });
}

async function runConnectivityAnalysis() {
  console.log("🤖 Claude: \"Eseguirò un'analisi completa di connettività!\"");
  console.log("⏳ Analisi in corso...\n");
  
  const result = await getConnectivityStats();
  
  console.log("\n" + "═".repeat(60));
  console.log("📊 RISULTATI ANALISI CONNETTIVITÀ");
  console.log("═".repeat(60));
  
  if (result.success) {
    console.log("✅ ANALISI COMPLETATA CON SUCCESSO!\n");
    
    const basic = result.basicStats;
    const pt = result.publicTransport;
    const conn = result.connectivity;
    
    console.log("🏗️ **STATISTICHE BASE DELLA RETE:**");
    console.log(`🔗 Nodi: ${basic.nodes.toLocaleString()}`);
    console.log(`🛣️  Collegamenti: ${basic.links.toLocaleString()}`);
    console.log(`🏘️  Zone: ${basic.zones.toLocaleString()}`);
    
    console.log("\n🚌 **TRASPORTO PUBBLICO:**");
    console.log(`🚍 Linee: ${pt.lines.toLocaleString()}`);
    console.log(`🚏 Fermate: ${pt.stops.toLocaleString()}`);
    console.log(`⏰ Profili temporali: ${pt.timeProfiles.toLocaleString()}`);
    console.log(`🚐 Corse veicoli: ${pt.vehicleJourneys.toLocaleString()}`);
    
    console.log("\n📈 **METRICHE DI CONNETTIVITÀ:**");
    console.log(`🔗 Media collegamenti per nodo: ${conn.avgLinksPerNode}`);
    console.log(`📊 Rapporto connettività: ${conn.connectivityRatio}`);
    console.log(`🌐 Densità della rete: ${conn.networkDensity}%`);
    console.log(`⚡ Livello di connettività: ${conn.level}`);
    
    console.log("\n🎯 **VALUTAZIONE CONNETTIVITÀ:**");
    if (conn.level === "Alta") {
      console.log("✅ ECCELLENTE: Rete altamente connessa");
      console.log("• Buona ridondanza dei percorsi");
      console.log("• Robusta contro interruzioni");
      console.log("• Efficiente per il routing");
    } else if (conn.level === "Media") {
      console.log("⚠️ BUONA: Connettività adeguata");
      console.log("• Connettività sufficiente");
      console.log("• Possibili miglioramenti");
    } else {
      console.log("🔴 BASSA: Rete poco connessa");
      console.log("• Vulnerabile a interruzioni");
      console.log("• Limitati percorsi alternativi");
    }
    
    console.log("\n📋 **DETTAGLI TECNICI:**");
    console.log(`📁 File progetto: ${result.networkFile || 'Unknown'}`);
    console.log(`📅 Analizzato: ${result.analysisDate}`);
    
    console.log("\n🤖 Claude: \"Analisi di connettività completata!\"");
    console.log(`🤖 Claude: \"La rete ha ${conn.level.toLowerCase()} connettività con ${basic.nodes.toLocaleString()} nodi.\"");
    
  } else {
    console.log("❌ ANALISI FALLITA");
    console.log(`Errore: ${result.error}`);
    
    if (result.rawOutput) {
      console.log("\n📄 Output grezzo (primi 500 caratteri):");
      console.log(result.rawOutput.substring(0, 500));
    }
  }
  
  console.log("\n🚀 ANALISI CONNETTIVITÀ CAMPOLEONE COMPLETATA!");
}

runConnectivityAnalysis().catch(console.error);
