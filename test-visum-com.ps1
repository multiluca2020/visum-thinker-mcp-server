try {
    Write-Host "Testing Visum COM access..."
    
    # Try to create COM object
    $visum = New-Object -ComObject "Visum.Visum"
    Write-Host "✅ COM object created successfully"
    
    # Try to get version
    $version = $visum.VersionNumber
    Write-Host "✅ Version: $version"
    
    # Try to access network
    $net = $visum.Net
    if ($net -ne $null) {
        Write-Host "✅ Network object accessible"
    } else {
        Write-Host "⚠️ Network object is null"
    }
    
    # Clean up
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($visum) | Out-Null
    Write-Host "✅ COM object released"
    
} catch {
    Write-Host "❌ Visum COM Error Details:"
    Write-Host "Message: $($_.Exception.Message)"
    Write-Host "HResult: $($_.Exception.HResult)"
    Write-Host "Source: $($_.Exception.Source)"
    Write-Host "StackTrace: $($_.Exception.StackTrace)"
}
