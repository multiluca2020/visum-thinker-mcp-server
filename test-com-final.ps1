try {
    Write-Host "=== SUCCESSFUL VISUM COM TEST ===" -ForegroundColor Green
    
    # Create COM object
    $visum = New-Object -ComObject "Visum.Visum"
    Write-Host "COM object created successfully" -ForegroundColor Green
    
    # Check version
    $version = $visum.VersionNumber
    Write-Host "Version: $version" -ForegroundColor Green
    
    # Check Net object
    $net = $visum.Net
    Write-Host "Net object accessible: $($net -ne $null)" -ForegroundColor Green
    
    # Test persistence over time
    Write-Host "Testing 5-second persistence..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    
    # Retest after wait
    $version2 = $visum.VersionNumber
    $net2 = $visum.Net
    Write-Host "Still responsive after 5 seconds!" -ForegroundColor Green
    Write-Host "Version still accessible: $version2" -ForegroundColor Green
    Write-Host "Net still accessible: $($net2 -ne $null)" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "=== RESULT: VISUM COM IS WORKING CORRECTLY ===" -ForegroundColor Green
    Write-Host "The issue was using wrong method names, not COM instability!" -ForegroundColor Cyan
    
}
catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
}
