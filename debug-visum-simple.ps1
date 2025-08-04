# Visum COM Debugging Script
# This script will help us understand exactly why Visum keeps closing

Write-Host "=== Visum COM Debugging Analysis ===" -ForegroundColor Green

# Step 1: Check Visum installation
Write-Host "`n1. Checking Visum Installation..." -ForegroundColor Yellow
$visumPaths = @(
    'C:\Program Files\PTV Vision\PTV Visum 2025\Exe\Visum250.exe',
    'C:\Program Files\PTV Vision\PTV Visum 2024\Exe\Visum240.exe',
    'C:\Program Files\PTV Vision\PTV Visum 2023\Exe\Visum230.exe',
    'C:\Program Files (x86)\PTV Vision\PTV Visum 2025\Exe\Visum250.exe',
    'C:\Program Files (x86)\PTV Vision\PTV Visum 2024\Exe\Visum240.exe'
)

$foundVisum = $null
foreach ($path in $visumPaths) {
    if (Test-Path $path) {
        Write-Host "   Found: $path" -ForegroundColor Green
        $foundVisum = $path
        break
    } else {
        Write-Host "   Not found: $path" -ForegroundColor Red
    }
}

if (-not $foundVisum) {
    Write-Host "   ERROR: No Visum installation found!" -ForegroundColor Red
    exit 1
}

# Step 2: Check COM registration
Write-Host "`n2. Checking COM Registration..." -ForegroundColor Yellow
try {
    $comObjects = Get-WmiObject -Class Win32_ClassicCOMClass -ErrorAction SilentlyContinue | Where-Object { 
        $_.ProgId -like "*Visum*" -or $_.LocalServer32 -like "*Visum*" 
    }
    
    if ($comObjects) {
        Write-Host "   Visum COM objects found:" -ForegroundColor Green
        foreach ($obj in $comObjects) {
            Write-Host "     ProgId: $($obj.ProgId)" -ForegroundColor Cyan
            Write-Host "     Server: $($obj.LocalServer32)" -ForegroundColor Cyan
        }
    } else {
        Write-Host "   No Visum COM objects registered!" -ForegroundColor Red
        Write-Host "   Try running Visum as Administrator once to register COM" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   Error checking COM registration: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 3: Check running processes
Write-Host "`n3. Checking Running Visum Processes..." -ForegroundColor Yellow
$visumProcesses = Get-Process -Name "Visum*" -ErrorAction SilentlyContinue
if ($visumProcesses) {
    Write-Host "   Found running Visum processes:" -ForegroundColor Orange
    foreach ($proc in $visumProcesses) {
        Write-Host "     PID: $($proc.Id), Name: $($proc.ProcessName)" -ForegroundColor Cyan
    }
    Write-Host "   Killing existing processes..." -ForegroundColor Yellow
    $visumProcesses | Stop-Process -Force -ErrorAction SilentlyContinue
} else {
    Write-Host "   No running Visum processes" -ForegroundColor Green
}

# Step 4: Test basic COM creation
Write-Host "`n4. Testing Basic COM Creation..." -ForegroundColor Yellow
try {
    Write-Host "   Creating COM object..." -ForegroundColor Cyan
    $visum = New-Object -ComObject "Visum.Visum" -ErrorAction Stop
    Write-Host "   COM object created successfully" -ForegroundColor Green
    
    # Immediate test
    Write-Host "   Testing immediate responsiveness..." -ForegroundColor Cyan
    try {
        $version = $visum.GetAttValue('VersionStr')
        Write-Host "   Version retrieved: $version" -ForegroundColor Green
    } catch {
        Write-Host "   Version retrieval failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Network test
    Write-Host "   Testing network object..." -ForegroundColor Cyan
    try {
        $netExists = ($visum.Net -ne $null)
        Write-Host "   Network object accessible: $netExists" -ForegroundColor Green
    } catch {
        Write-Host "   Network object test failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Wait and retest
    Write-Host "   Waiting 3 seconds and retesting..." -ForegroundColor Cyan
    Start-Sleep -Seconds 3
    
    try {
        $version2 = $visum.GetAttValue('VersionStr')
        $net2 = ($visum.Net -ne $null)
        if ($version2 -eq $version -and $net2) {
            Write-Host "   Object survived 3-second test!" -ForegroundColor Green
        } else {
            Write-Host "   Object became unstable after wait" -ForegroundColor Red
        }
    } catch {
        Write-Host "   Object died during wait: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Clean up
    try {
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($visum) | Out-Null
        Write-Host "   COM object released cleanly" -ForegroundColor Green
    } catch {
        Write-Host "   Could not release COM object: $($_.Exception.Message)" -ForegroundColor Orange
    }
    
} catch {
    Write-Host "   COM creation failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   Common causes:" -ForegroundColor Yellow
    Write-Host "     - Visum not properly installed" -ForegroundColor Yellow
    Write-Host "     - License expired or invalid" -ForegroundColor Yellow
    Write-Host "     - COM components not registered" -ForegroundColor Yellow
    Write-Host "     - Insufficient permissions" -ForegroundColor Yellow
}

Write-Host "`n=== Debugging Complete ===" -ForegroundColor Green
Write-Host "Please manually test:" -ForegroundColor White
Write-Host "1. Open Visum from Start Menu" -ForegroundColor Yellow
Write-Host "2. Check if it stays open normally" -ForegroundColor Yellow
Write-Host "3. Check for any license errors" -ForegroundColor Yellow
