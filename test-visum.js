// Test Visum integration separately
import { VisumController } from './build/visum-controller.js';

const controller = new VisumController();

async function testVisum() {
    console.log('=== Testing Visum Integration ===\n');
    
    // Test 1: Check availability
    console.log('1. Checking Visum availability...');
    try {
        const availability = await controller.isVisumAvailable();
        console.log('Result:', availability);
    } catch (error) {
        console.error('Error:', error.message);
    }
    
    console.log('\n2. Testing COM object creation...');
    try {
        const result = await controller.initializeVisum();
        console.log('Result:', result);
    } catch (error) {
        console.error('Error:', error.message);
    }
    
    console.log('\n3. Testing basic PowerShell command...');
    try {
        const result = await controller.executePowerShellCommand(`
            try {
                Write-Output "PowerShell is working"
                Write-Output "Current directory: $(Get-Location)"
                Write-Output "User: $($env:USERNAME)"
                Write-Output "Temp directory: $($env:TEMP)"
            } catch {
                Write-Error "PowerShell test failed: $_"
            }
        `);
        console.log('Result:', result);
    } catch (error) {
        console.error('Error:', error.message);
    }
    
    console.log('\n4. Testing Visum COM registration check...');
    try {
        const result = await controller.executePowerShellCommand(`
            try {
                # Check if Visum COM is registered
                $comObject = Get-WmiObject -Class Win32_ClassicCOMClass | Where-Object { $_.ProgId -like "*Visum*" }
                if ($comObject) {
                    Write-Output "Visum COM objects found:"
                    $comObject | Select-Object ProgId, LocalServer32 | ConvertTo-Json
                } else {
                    Write-Output "No Visum COM objects found in registry"
                }
                
                # Try to find Visum installations
                $visumPaths = @(
                    "C:\\Program Files\\PTV Vision",
                    "C:\\Program Files (x86)\\PTV Vision"
                )
                
                foreach ($basePath in $visumPaths) {
                    if (Test-Path $basePath) {
                        Write-Output "Found PTV Vision at: $basePath"
                        Get-ChildItem $basePath -Directory | ForEach-Object {
                            Write-Output "  - $($_.Name)"
                        }
                    }
                }
            } catch {
                Write-Error "COM check failed: $_"
            }
        `);
        console.log('Result:', result);
    } catch (error) {
        console.error('Error:', error.message);
    }
}

testVisum().then(() => {
    console.log('\n=== Test Complete ===');
    process.exit(0);
}).catch(error => {
    console.error('Test failed:', error);
    process.exit(1);
});
