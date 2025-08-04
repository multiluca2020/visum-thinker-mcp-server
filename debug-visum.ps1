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
        Write-Host "   ✓ Found: $path" -ForegroundColor Green
        $foundVisum = $path
        break
    } else {
        Write-Host "   ✗ Not found: $path" -ForegroundColor Red
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
        Write-Host "   ✓ Visum COM objects found:" -ForegroundColor Green
        foreach ($obj in $comObjects) {
            Write-Host "     - ProgId: $($obj.ProgId)" -ForegroundColor Cyan
            Write-Host "     - Server: $($obj.LocalServer32)" -ForegroundColor Cyan
        }
    } else {
        Write-Host "   ✗ No Visum COM objects registered!" -ForegroundColor Red
        Write-Host "   → Try running Visum as Administrator once to register COM" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ✗ Error checking COM registration: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 3: Check running processes
Write-Host "`n3. Checking Running Visum Processes..." -ForegroundColor Yellow
$visumProcesses = Get-Process -Name "Visum*" -ErrorAction SilentlyContinue
if ($visumProcesses) {
    Write-Host "   ⚠ Found running Visum processes:" -ForegroundColor Orange
    foreach ($proc in $visumProcesses) {
        Write-Host "     - PID: $($proc.Id), Name: $($proc.ProcessName)" -ForegroundColor Cyan
    }
    Write-Host "   → Killing existing processes..." -ForegroundColor Yellow
    $visumProcesses | Stop-Process -Force -ErrorAction SilentlyContinue
} else {
    Write-Host "   ✓ No running Visum processes" -ForegroundColor Green
}

# Step 4: Test basic COM creation
Write-Host "`n4. Testing Basic COM Creation..." -ForegroundColor Yellow
try {
    Write-Host "   → Creating COM object..." -ForegroundColor Cyan
    $visum = New-Object -ComObject "Visum.Visum" -ErrorAction Stop
    Write-Host "   ✓ COM object created successfully" -ForegroundColor Green
    
    # Immediate test
    Write-Host "   → Testing immediate responsiveness..." -ForegroundColor Cyan
    try {
        $version = $visum.GetAttValue('VersionStr')
        Write-Host "   ✓ Version retrieved: $version" -ForegroundColor Green
    } catch {
        Write-Host "   ✗ Version retrieval failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Network test
    Write-Host "   → Testing network object..." -ForegroundColor Cyan
    try {
        $netExists = ($visum.Net -ne $null)
        Write-Host "   ✓ Network object accessible: $netExists" -ForegroundColor Green
    } catch {
        Write-Host "   ✗ Network object test failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Wait and retest
    Write-Host "   → Waiting 3 seconds and retesting..." -ForegroundColor Cyan
    Start-Sleep -Seconds 3
    
    try {
        $version2 = $visum.GetAttValue('VersionStr')
        $net2 = ($visum.Net -ne $null)
        if ($version2 -eq $version -and $net2) {
            Write-Host "   ✓ Object survived 3-second test!" -ForegroundColor Green
        } else {
            Write-Host "   ✗ Object became unstable after wait" -ForegroundColor Red
        }
    } catch {
        Write-Host "   ✗ Object died during wait: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Clean up
    try {
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($visum) | Out-Null
        Write-Host "   ✓ COM object released cleanly" -ForegroundColor Green
    } catch {
        Write-Host "   ⚠ Could not release COM object: $($_.Exception.Message)" -ForegroundColor Orange
    }
    
} catch {
    Write-Host "   ✗ COM creation failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   → Common causes:" -ForegroundColor Yellow
    Write-Host "     - Visum not properly installed" -ForegroundColor Yellow
    Write-Host "     - License expired or invalid" -ForegroundColor Yellow
    Write-Host "     - COM components not registered" -ForegroundColor Yellow
    Write-Host "     - Insufficient permissions" -ForegroundColor Yellow
}

# Step 5: Check Windows Event Log for Visum errors
Write-Host "`n5. Checking Recent Windows Event Log Errors..." -ForegroundColor Yellow
try {
    $events = Get-WinEvent -FilterHashtable @{LogName='Application'; StartTime=(Get-Date).AddHours(-1)} -ErrorAction SilentlyContinue | 
              Where-Object { $_.LevelDisplayName -eq 'Error' -and ($_.Message -like '*Visum*' -or $_.Message -like '*PTV*') } |
              Select-Object -First 5
    
    if ($events) {
        Write-Host "   ⚠ Found recent Visum-related errors:" -ForegroundColor Orange
        foreach ($event in $events) {
            Write-Host "     - Time: $($event.TimeCreated)" -ForegroundColor Cyan
            Write-Host "     - Source: $($event.ProviderName)" -ForegroundColor Cyan
            Write-Host "     - Message: $($event.Message.Substring(0, [Math]::Min(200, $event.Message.Length)))..." -ForegroundColor Cyan
            Write-Host ""
        }
    } else {
        Write-Host "   ✓ No recent Visum errors in event log" -ForegroundColor Green
    }
} catch {
    Write-Host "   ⚠ Could not check event log: $($_.Exception.Message)" -ForegroundColor Orange
}

# Step 6: Check license
Write-Host "`n6. Testing Manual Visum Launch..." -ForegroundColor Yellow
Write-Host "   → This will help determine if the issue is COM-specific or general" -ForegroundColor Cyan
Write-Host "   → Please manually open Visum from Start Menu and report if it:" -ForegroundColor Cyan
Write-Host "     A) Opens normally and stays open" -ForegroundColor Yellow
Write-Host "     B) Opens but closes immediately" -ForegroundColor Yellow  
Write-Host "     C) Shows license error" -ForegroundColor Yellow
Write-Host "     D) Fails to start completely" -ForegroundColor Yellow

Write-Host "`n=== Debugging Complete ===" -ForegroundColor Green
Write-Host "Please run this script and share the output for analysis." -ForegroundColor White
