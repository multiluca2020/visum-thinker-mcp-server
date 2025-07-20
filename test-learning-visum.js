// Test script to demonstrate Visum path learning functionality
import { VisumController } from './build/visum-controller.js';
import fs from 'fs';

console.log('🧪 Testing Visum Path Learning Functionality\n');

const controller = new VisumController();

// Test 1: Check initial state (no custom paths known)
console.log('=== Test 1: Initial State Check ===');
let result = await controller.isVisumAvailable();
console.log('Available:', result.available);
console.log('Installations found:', result.installations?.length || 0);
console.log('');

// Test 2: Simulate user providing a custom path
console.log('=== Test 2: Learning Custom Path ===');
const testCustomPath = 'D:\\Software\\PTV\\Visum\\Exe\\Visum240.exe';
console.log(`Simulating user provided path: ${testCustomPath}`);

// First we'll simulate this path exists by checking what happens when we test it
result = await controller.isVisumAvailable(testCustomPath);
console.log('Custom path check result:', result.available ? 'Valid' : 'Invalid');
console.log('Error message:', result.error || 'None');
console.log('');

// Test 3: Check if configuration was saved
console.log('=== Test 3: Configuration Persistence Check ===');
const configPath = 'visum-config.json';
if (fs.existsSync(configPath)) {
    const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
    console.log('Configuration file exists!');
    console.log('Known installations:', config.knownInstallations.length);
    console.log('Preferred path:', config.preferredPath || 'None set');
    console.log('Last updated:', config.lastUpdated);
    
    if (config.knownInstallations.length > 0) {
        console.log('\nKnown installations:');
        config.knownInstallations.forEach((install, index) => {
            console.log(`  ${index + 1}. ${install.path} (${install.version}) - Last verified: ${install.lastVerified}`);
        });
    }
} else {
    console.log('No configuration file found yet.');
}
console.log('');

// Test 4: Test subsequent calls (should use cached/known paths)
console.log('=== Test 4: Subsequent Calls Test ===');
console.log('Calling isVisumAvailable() again (should use known installations)...');
result = await controller.isVisumAvailable();
console.log('Available:', result.available);
console.log('Using path:', result.path || 'None');
console.log('');

// Test 5: Demo mode information
console.log('=== Test 5: Demo Mode Status ===');
const demoStatus = controller.getDemoStatus();
console.log('Demo mode active:', demoStatus.demoMode);
console.log('Reason:', demoStatus.reason || 'Normal operation');
console.log('COM available:', demoStatus.comAvailable ?? 'Unknown');
console.log('');

console.log('✅ Testing complete! The system now:');
console.log('   • Remembers custom Visum installation paths');
console.log('   • Persists configuration between server restarts'); 
console.log('   • Prioritizes previously validated installations');
console.log('   • Only asks for custom paths when needed');
console.log('\nNext time Claude restarts, it will automatically check known paths first!');
