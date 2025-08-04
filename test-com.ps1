try {
    Write-Host "Testing Visum COM with H: drive installation..."
    $visum = New-Object -ComObject "Visum.Visum"
    Write-Host "COM object created successfully"
    
    $version = $visum.GetAttValue('VersionStr')
    Write-Host "Version: $version"
    
    Write-Host "Testing persistence (waiting 3 seconds)..."
    Start-Sleep -Seconds 3
    
    $version2 = $visum.GetAttValue('VersionStr')
    Write-Host "Still responsive: $version2"
    
    Write-Host "SUCCESS: Visum COM is working and persistent!"
    
} catch {
    Write-Host "ERROR: $($_.Exception.Message)"
}
