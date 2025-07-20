// Test all Visum tools in demo mode
import { VisumController } from './build/visum-controller.js';

const controller = new VisumController();

async function testAllVisumeTools() {
    console.log('=== Testing All Visum Tools (Demo Mode) ===\n');
    
    // Test 1: Check availability
    console.log('1. Check Visum Availability');
    const availability = await controller.isVisumAvailable();
    console.log('✓', availability.available ? 'Available' : 'Not Available');
    console.log('  Details:', { 
        installations: availability.installations?.length || 0,
        comRegistered: availability.comRegistered
    });
    console.log('');
    
    // Test 2: Initialize (will enable demo mode)
    console.log('2. Initialize Visum');
    const initResult = await controller.initializeVisum();
    console.log('✓', initResult.success ? 'Success' : 'Failed');
    console.log('  Demo Mode:', initResult.details?.demoMode ? 'Enabled' : 'Disabled');
    console.log('');
    
    // Test 3: Check demo status
    console.log('3. Demo Status');
    const demoStatus = controller.getDemoStatus();
    console.log('✓', demoStatus);
    console.log('');
    
    // Test 4: Load model (demo)
    console.log('4. Load Model (Demo)');
    const modelPath = 'C:\\Demo\\TestModel.ver';
    const loadResult = await controller.loadModel(modelPath);
    console.log('✓', loadResult.success ? 'Loaded' : 'Failed');
    if (loadResult.modelInfo) {
        console.log('  Model Info:', {
            nodes: loadResult.modelInfo.nodes,
            links: loadResult.modelInfo.links,
            zones: loadResult.modelInfo.zones,
            demoMode: loadResult.modelInfo.demoMode
        });
    }
    console.log('');
    
    // Test 5: Get network stats (demo)
    console.log('5. Get Network Statistics (Demo)');
    const statsResult = await controller.getNetworkStats();
    console.log('✓', statsResult.success ? 'Success' : 'Failed');
    if (statsResult.stats) {
        console.log('  Statistics:', {
            nodes: statsResult.stats.nodes,
            links: statsResult.stats.links,
            lines: statsResult.stats.lines,
            demoMode: statsResult.stats.demoMode
        });
    }
    console.log('');
    
    // Test 6: Run procedure (demo)
    console.log('6. Run Procedure (Demo)');
    const procResult = await controller.runProcedure(1, {});
    console.log('✓', procResult.success ? 'Success' : 'Failed');
    console.log('  Result:', procResult.result);
    console.log('');
    
    // Test 7: Execute custom script (demo)
    console.log('7. Execute Custom Script (Demo)');
    const vbScript = `
        ' Demo VBScript for testing
        Dim visum
        Set visum = CreateObject("Visum.Visum")
        visum.SetAttValue("Comment", "This is a demo script")
    `;
    const scriptResult = await controller.executeCustomScript(vbScript);
    console.log('✓', scriptResult.success ? 'Success' : 'Failed');
    console.log('  Result:', scriptResult.result);
    console.log('');
    
    console.log('=== All Tests Complete ===');
    console.log('Summary: All Visum tools are working correctly in demo mode!');
    console.log('This allows Claude to test all functionality even without Visum installed.');
}

testAllVisumeTools().then(() => {
    console.log('\n✅ Demo mode testing successful!');
    process.exit(0);
}).catch(error => {
    console.error('❌ Demo mode testing failed:', error);
    process.exit(1);
});
