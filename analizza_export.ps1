
# Script PowerShell per analisi dei file esportati
# Da eseguire dopo l'export manuale

$exportDir = "C:\temp\visum_analysis_20250805_184029"

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
