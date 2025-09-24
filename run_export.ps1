
# Script PowerShell per eseguire export automatico
Write-Host "🚀 AVVIO EXPORT AUTOMATICO DATI VISUM"
Write-Host "====================================="

try {
    # Check if Visum is running
    $visum = Get-Process -Name "Visum250" -ErrorAction SilentlyContinue
    if ($visum) {
        Write-Host "✅ Visum trovato (PID: $($visum.Id))"
        
        # Try to run VAL script via COM
        try {
            $visumApp = [System.Runtime.InteropServices.Marshal]::GetActiveObject("Visum.Visum")
            if ($visumApp) {
                Write-Host "🔗 Connessione COM riuscita"
                Write-Host "📋 Esecuzione script VAL..."
                
                $valFile = "campoleone_export.val"
                $visumApp.RunVALScript($valFile)
                
                Write-Host "✅ Export completato!"
                Write-Host "📁 Controlla i file CSV nella directory di lavoro"
            }
        } catch {
            Write-Host "❌ COM fallito: $($_.Exception.Message)"
            Write-Host "💡 Apri manualmente lo script VAL in Visum:"
            Write-Host "   File > Run VAL Script > campoleone_export.val"
        }
    } else {
        Write-Host "❌ Visum non trovato in esecuzione"
    }
} catch {
    Write-Host "❌ Errore: $($_.Exception.Message)"
}

Write-Host ""
Write-Host "📊 ANALISI MANUALE ALTERNATIVA:"
Write-Host "1. In Visum: Network > Export > Text files..."
Write-Host "2. Seleziona tabelle: Nodes, Links, LinkTypes, Zones"
Write-Host "3. Include tutti gli attributi disponibili"
Write-Host "4. Salva come CSV per analisi Excel/Python"
