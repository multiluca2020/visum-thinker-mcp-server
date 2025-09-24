// GUIDA EXPORT MANUALE VISUM - ANALISI APPROFONDITA RETE
// Istruzioni step-by-step per estrarre tutti i dati della rete

import { writeFileSync } from 'fs';

console.log("📋 GUIDA EXPORT MANUALE VISUM CAMPOLEONE");
console.log("═".repeat(50));
console.log("🎯 Istruzioni per analisi approfondita della rete");
console.log("═".repeat(50));

function generateExportGuide() {
  const guide = `
🚄 GUIDA EXPORT DATI RETE CAMPOLEONE
=====================================

🎯 OBIETTIVO: Estrarre dati dettagliati della rete per analisi approfondita
- Nodi e loro attributi (coordinate, tipo, connessioni)
- Archi/Link e loro attributi (lunghezza, velocità, capacità, tipo)
- Tipi di arco e relative caratteristiche
- Velocità a flusso nullo (V0)
- Funzioni di costo volume-capacità
- Zone e matrici O-D

📂 DIRECTORY TEMPORANEA CREATA: C:\\temp\\visum_analysis_20250805_184029

🔧 PROCEDURA STEP-BY-STEP:
==========================

PASSO 1: Preparazione
---------------------
✅ Visum è già aperto con il progetto Campoleone
✅ Directory temporanea creata
✅ Progetto contiene rete di 186.9 MB (rete complessa)

PASSO 2: Export Nodi
--------------------
1. In Visum: Menù "Network" → "Export" → "Text files..."
2. Seleziona "Nodes" nella lista degli oggetti
3. Clicca "Attributes..." per selezionare attributi:
   • No (numero nodo)
   • XCoord, YCoord (coordinate)
   • NodeType (tipo nodo)
   • ConnectedNodes (nodi connessi)
   • Name (nome se presente)
4. File di destinazione: C:\\temp\\visum_analysis_20250805_184029\\nodes.csv
5. Formato: "Delimited" con header
6. Clicca "OK" per esportare

PASSO 3: Export Link/Archi
--------------------------
1. In Visum: Menù "Network" → "Export" → "Text files..."
2. Seleziona "Links" nella lista degli oggetti
3. Clicca "Attributes..." per selezionare attributi:
   • No (numero link)
   • FromNodeNo, ToNodeNo (nodi origine/destinazione)
   • Length (lunghezza in metri)
   • TypeNo (numero tipo link)
   • V0_PrT (velocità a flusso nullo trasporto privato)
   • VCap_PrT (capacità volume trasporto privato)
   • tCur_PrT (tempo corrente)
   • VolCap (rapporto volume/capacità)
   • Name (nome se presente)
4. File di destinazione: C:\\temp\\visum_analysis_20250805_184029\\links.csv
5. Formato: "Delimited" con header
6. Clicca "OK" per esportare

PASSO 4: Export Tipi di Link
----------------------------
1. In Visum: Menù "Network" → "Export" → "Text files..."
2. Seleziona "Link types" nella lista degli oggetti
3. Clicca "Attributes..." per selezionare attributi:
   • No (numero tipo)
   • Name (nome tipo)
   • VMax (velocità massima)
   • DefaultV0_PrT (velocità default a flusso nullo)
   • DefaultVolCap_PrT (capacità default)
   • VolCapFormula (formula volume-capacità)
4. File di destinazione: C:\\temp\\visum_analysis_20250805_184029\\link_types.csv
5. Formato: "Delimited" con header
6. Clicca "OK" per esportare

PASSO 5: Export Zone
--------------------
1. In Visum: Menù "Network" → "Export" → "Text files..."
2. Seleziona "Zones" nella lista degli oggetti
3. Clicca "Attributes..." per selezionare attributi:
   • No (numero zona)
   • Name (nome zona)
   • XCoord, YCoord (coordinate centroide)
   • MainZone (zona principale)
4. File di destinazione: C:\\temp\\visum_analysis_20250805_184029\\zones.csv
5. Formato: "Delimited" con header
6. Clicca "OK" per esportare

PASSO 6: Export Funzioni Volume-Capacità
----------------------------------------
1. In Visum: Menù "Network" → "Export" → "Text files..."
2. Seleziona "Vol-cap functions" nella lista degli oggetti
3. Clicca "Attributes..." per selezionare attributi:
   • No (numero formula)
   • Name (nome formula)
   • Formula (testo della formula)
   • Description (descrizione)
4. File di destinazione: C:\\temp\\visum_analysis_20250805_184029\\volcap_formulas.csv
5. Formato: "Delimited" con header
6. Clicca "OK" per esportare

PASSO 7: Export Matrici (se presenti)
-------------------------------------
1. In Visum: Menù "Network" → "Export" → "Matrices..."
2. Seleziona le matrici di domanda disponibili
3. File di destinazione: C:\\temp\\visum_analysis_20250805_184029\\matrices.csv
4. Formato: "Delimited" con row/column headers
5. Clicca "OK" per esportare

🔍 ANALISI POST-EXPORT:
========================

Dopo aver completato l'export, i file conterranno:

📊 nodes.csv:
- Elenco completo di tutti i nodi della rete
- Coordinate geografiche per mappatura
- Tipi di nodo (intersezioni, fermata, ecc.)

🔗 links.csv:
- Elenco completo di tutti gli archi/link
- Lunghezze, velocità, capacità per ogni link
- Tipologie di strada/ferrovia
- Parametri per calcolo tempi di percorrenza

🏷️ link_types.csv:
- Definizioni dei tipi di link
- Velocità massime per categoria
- Formule di costo associate

🌍 zones.csv:
- Zone di traffico per matrici O-D
- Centroidi e loro posizioni

💰 volcap_formulas.csv:
- Funzioni matematiche di impedenza
- Relazioni velocità-flusso
- Parametri BPR o altre formule

📈 ANALISI DETTAGLIATA POSSIBILE:
=================================

Con questi dati potrai analizzare:

1. TOPOLOGIA RETE:
   - Connettività nodi-archi
   - Densità della rete
   - Lunghezza media degli archi

2. CARATTERISTICHE PRESTAZIONALI:
   - Distribuzione velocità per tipo strada
   - Capacità totale della rete
   - Colli di bottiglia potenziali

3. ANALISI SPAZIALE:
   - Mappa della rete con coordinate
   - Distribuzione geografica delle zone
   - Accessibilità territoriale

4. FUNZIONI DI COSTO:
   - Curve velocità-flusso
   - Parametri di congestione
   - Modelli di ritardo

🎯 PROSSIMI PASSI:
==================

1. Segui la procedura step-by-step sopra
2. Verifica che tutti i file CSV siano stati creati
3. Apri i file per controllo qualità dati
4. Usa Excel/Python/R per analisi statistica
5. Crea visualizzazioni della rete

💡 NOTE IMPORTANTI:
===================

- Il progetto Campoleone è una rete complessa (186.9 MB)
- Aspettati migliaia di nodi e link
- I file CSV potrebbero essere di grandi dimensioni
- Controlla che tutti gli attributi siano inclusi
- Salva una copia di backup dei file esportati

🚀 BUONA ANALISI!
=================
`;

  return guide;
}

function createAnalysisScript() {
  const script = `
# Script PowerShell per analisi dei file esportati
# Da eseguire dopo l'export manuale

$exportDir = "C:\\temp\\visum_analysis_20250805_184029"

Write-Host "🔍 ANALISI FILE ESPORTATI VISUM CAMPOLEONE" -ForegroundColor Cyan
Write-Host "=" * 50
Write-Host "Directory: $exportDir" -ForegroundColor Yellow
Write-Host ""

if (Test-Path $exportDir) {
    $csvFiles = Get-ChildItem -Path $exportDir -Filter "*.csv"
    
    if ($csvFiles.Count -gt 0) {
        Write-Host "📊 FILE CSV TROVATI:" -ForegroundColor Green
        
        foreach ($file in $csvFiles) {
            $sizeKB = [math]::Round($file.Length / 1KB, 1)
            $sizeMB = [math]::Round($file.Length / 1MB, 2)
            
            Write-Host ""
            Write-Host "📄 $($file.Name)" -ForegroundColor White
            
            if ($sizeMB -gt 1) {
                Write-Host "   Dimensione: $sizeMB MB" -ForegroundColor Yellow
            } else {
                Write-Host "   Dimensione: $sizeKB KB" -ForegroundColor Yellow
            }
            
            # Analizza contenuto
            try {
                $content = Get-Content $file.FullName -TotalCount 10
                $lineCount = (Get-Content $file.FullName | Measure-Object).Count
                
                Write-Host "   Righe totali: $($lineCount - 1)" -ForegroundColor Cyan
                Write-Host "   Header: $($content[0])" -ForegroundColor Gray
                
                if ($content.Count -gt 1) {
                    Write-Host "   Esempio dati: $($content[1])" -ForegroundColor Gray
                }
                
                # Analisi specifica per tipo file
                switch -Wildcard ($file.Name) {
                    "nodes*" {
                        Write-Host "   → Analisi NODI della rete" -ForegroundColor Green
                        $nodeCount = $lineCount - 1
                        Write-Host "   → Numero nodi: $nodeCount" -ForegroundColor White
                    }
                    "links*" {
                        Write-Host "   → Analisi LINK/ARCHI della rete" -ForegroundColor Green
                        $linkCount = $lineCount - 1
                        Write-Host "   → Numero link: $linkCount" -ForegroundColor White
                        
                        # Calcola densità rete se abbiamo entrambi i file
                        $nodesFile = Get-ChildItem -Path $exportDir -Filter "nodes*.csv" | Select-Object -First 1
                        if ($nodesFile) {
                            $nodeLines = (Get-Content $nodesFile.FullName | Measure-Object).Count
                            $nodeCount = $nodeLines - 1
                            if ($nodeCount -gt 0) {
                                $density = [math]::Round($linkCount / $nodeCount, 2)
                                Write-Host "   → Densità rete: $density link/nodo" -ForegroundColor Magenta
                            }
                        }
                    }
                    "zones*" {
                        Write-Host "   → Analisi ZONE di traffico" -ForegroundColor Green
                        $zoneCount = $lineCount - 1
                        Write-Host "   → Numero zone: $zoneCount" -ForegroundColor White
                    }
                    "link_types*" {
                        Write-Host "   → Analisi TIPI DI LINK" -ForegroundColor Green
                        $typeCount = $lineCount - 1
                        Write-Host "   → Tipi definiti: $typeCount" -ForegroundColor White
                    }
                    "volcap*" {
                        Write-Host "   → Analisi FUNZIONI VOLUME-CAPACITÀ" -ForegroundColor Green
                        $formulaCount = $lineCount - 1
                        Write-Host "   → Formule disponibili: $formulaCount" -ForegroundColor White
                    }
                }
                
            } catch {
                Write-Host "   ❌ Errore lettura file: $($_.Exception.Message)" -ForegroundColor Red
            }
        }
        
        Write-Host ""
        Write-Host "🎯 RIEPILOGO ANALISI:" -ForegroundColor Cyan
        Write-Host "====================="
        Write-Host "✅ File esportati: $($csvFiles.Count)" -ForegroundColor Green
        
        $totalSizeMB = [math]::Round(($csvFiles | Measure-Object Length -Sum).Sum / 1MB, 2)
        Write-Host "📊 Dimensione totale: $totalSizeMB MB" -ForegroundColor Yellow
        
        Write-Host ""
        Write-Host "📋 PROSSIMI PASSI:" -ForegroundColor Cyan
        Write-Host "1. Apri i file CSV in Excel per ispezione visuale"
        Write-Host "2. Usa Python/R per analisi statistica approfondita"
        Write-Host "3. Crea visualizzazioni della topologia di rete"
        Write-Host "4. Analizza distribuzioni velocità e capacità"
        Write-Host "5. Calcola metriche di accessibilità"
        
    } else {
        Write-Host "❌ Nessun file CSV trovato!" -ForegroundColor Red
        Write-Host "💡 Esegui prima l'export manuale seguendo la guida." -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ Directory non trovata: $exportDir" -ForegroundColor Red
    Write-Host "💡 Verifica che l'export sia stato completato." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=" * 50
Write-Host "🚀 ANALISI COMPLETATA!" -ForegroundColor Green
Write-Host "=" * 50
`;

  return script;
}

function main() {
  console.log("📋 Generazione guida e script di analisi...\n");
  
  // Genera la guida completa
  const guide = generateExportGuide();
  writeFileSync('GUIDA_EXPORT_VISUM.txt', guide, 'utf8');
  console.log("✅ Guida creata: GUIDA_EXPORT_VISUM.txt");
  
  // Genera script di analisi
  const analysisScript = createAnalysisScript();
  writeFileSync('analizza_export.ps1', analysisScript, 'utf8');
  console.log("✅ Script analisi creato: analizza_export.ps1");
  
  console.log("\n" + "═".repeat(50));
  console.log("📊 ISTRUZIONI COMPLETE GENERATE!");
  console.log("═".repeat(50));
  
  console.log("\n🎯 COSA FARE ORA:");
  console.log("1. Apri il file: GUIDA_EXPORT_VISUM.txt");
  console.log("2. Segui le istruzioni step-by-step per l'export");
  console.log("3. Dopo l'export, esegui: .\\analizza_export.ps1");
  console.log("4. Analizza i dati esportati");
  
  console.log("\n💡 RISULTATO ATTESO:");
  console.log("- File CSV con tutti i dati della rete Campoleone");
  console.log("- Nodi, archi, velocità, capacità, funzioni di costo");
  console.log("- Dati pronti per analisi approfondita");
  
  console.log("\n🚄 La rete Campoleone (186.9 MB) contiene probabilmente:");
  console.log("- Migliaia di nodi (intersezioni, stazioni)");
  console.log("- Decine di migliaia di archi (strade, binari)");
  console.log("- Centinaia di zone di traffico");
  console.log("- Parametri tecnici dettagliati per modellazione trasporti");
  
  console.log("\n" + "═".repeat(50));
  console.log("🎯 PRONTO PER ANALISI APPROFONDITA RETE!");
  console.log("═".repeat(50));
}

main();
