try {
    Write-Host "Testing Visum COM interface discovery..."
    $visum = New-Object -ComObject "Visum.Visum"
    Write-Host "COM object created successfully"
    
    # Check available members
    Write-Host "Available members:"
    $visum | Get-Member | Select-Object Name, MemberType | Sort-Object Name | Format-Table
    
    # Test basic properties
    Write-Host "Testing basic properties..."
    
    # Try different common methods
    $methods = @('Version', 'GetVersion', 'VersionString', 'GetVersionString')
    foreach ($method in $methods) {
        try {
            $result = $visum.$method
            Write-Host "SUCCESS: $method = $result"
        } catch {
            Write-Host "FAILED: $method - $($_.Exception.Message)"
        }
    }
    
    # Test Net property
    Write-Host "Testing Net property..."
    try {
        $net = $visum.Net
        if ($net) {
            Write-Host "SUCCESS: Net object accessible"
        } else {
            Write-Host "Net property is null"
        }
    } catch {
        Write-Host "FAILED: Net property - $($_.Exception.Message)"
    }
    
} catch {
    Write-Host "ERROR: $($_.Exception.Message)"
}
