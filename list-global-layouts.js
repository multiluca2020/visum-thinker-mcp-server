// List all global layouts available in a Visum project
import { createTCPClient } from './build/tcp-client.js';

async function listGlobalLayouts() {
    const projectId = '100625_Versione_base_v0_3_sub_ok_priv_10176442';
    
    try {
        const client = await createTCPClient(projectId);
        
        console.log('📋 Listing Global Layouts...\n');
        
        // Access GlobalLayouts collection via IProject
        const code = `
const layouts = Visum.Net.Project.GlobalLayouts;
const count = layouts.Count;
const attributes = ['No', 'Name', 'GlobalLayoutFile', 'GlobalLayoutFileVersionNo'];

const data = layouts.GetMultipleAttributes(attributes);

return {
    count: count,
    layouts: data
};
`;
        
        const result = await client.execute(code);
        
        console.log(`Found ${result.count} global layout(s):\n`);
        
        if (result.layouts && result.layouts.length > 0) {
            result.layouts.forEach((layout, idx) => {
                console.log(`${idx + 1}. Layout No: ${layout[0]}`);
                console.log(`   Name: ${layout[1]}`);
                console.log(`   File: ${layout[2] || '(not associated)'}`);
                console.log(`   Version: ${layout[3] || 'N/A'}`);
                console.log('');
            });
        } else {
            console.log('No global layouts found in this project.');
        }
        
    } catch (error) {
        console.error('❌ Error:', error.message);
        if (error.visumError) {
            console.error('Visum Error:', error.visumError);
        }
    }
}

listGlobalLayouts();
