// Test: List Global Layouts from open Visum project
import net from 'net';

const projectId = '100625_Versione_base_v0_3_sub_ok_priv_10176442';
const port = 7914; // porta del server TCP già attivo

function sendCommand(code) {
    return new Promise((resolve, reject) => {
        const client = net.createConnection({ port, host: 'localhost' }, () => {
            console.log('🔗 Connesso al server TCP');
            client.write(JSON.stringify({ code }) + '\n');
        });

        let buffer = '';
        client.on('data', (data) => {
            buffer += data.toString();
            try {
                const response = JSON.parse(buffer);
                client.end();
                resolve(response);
            } catch (e) {
                // Aspetta più dati
            }
        });

        client.on('error', reject);
        client.on('end', () => {
            if (buffer && !buffer.startsWith('{')) {
                reject(new Error('Invalid response: ' + buffer));
            }
        });
    });
}

async function listGlobalLayouts() {
    try {
        console.log('📋 Listing Global Layouts...\n');

        // Codice Python da eseguire
        const pythonCode = `
layouts = Visum.Net.Project.GlobalLayouts
count = layouts.Count

if count == 0:
    result = {"count": 0, "layouts": []}
else:
    # Attributi da leggere
    attrs = ["No", "Name", "GlobalLayoutFile", "GlobalLayoutFileVersionNo"]
    data = layouts.GetMultipleAttributes(attrs)
    
    result = {
        "count": count,
        "layouts": [
            {
                "no": row[0],
                "name": row[1],
                "file": row[2] if row[2] else "(not associated)",
                "version": row[3] if row[3] else "N/A"
            }
            for row in data
        ]
    }

result
`;

        const response = await sendCommand(pythonCode);

        if (response.error) {
            console.error('❌ Error:', response.error);
            return;
        }

        const result = response.result;
        console.log(`✅ Found ${result.count} global layout(s):\n`);

        if (result.count > 0) {
            result.layouts.forEach((layout, idx) => {
                console.log(`${idx + 1}. Layout #${layout.no}`);
                console.log(`   Name: ${layout.name}`);
                console.log(`   File: ${layout.file}`);
                console.log(`   Version: ${layout.version}`);
                console.log('');
            });
        } else {
            console.log('ℹ️  No global layouts in this project.');
        }

    } catch (error) {
        console.error('❌ Error:', error.message);
    }
}

listGlobalLayouts();
