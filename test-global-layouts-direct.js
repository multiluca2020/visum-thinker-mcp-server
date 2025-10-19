// Test diretto: apri progetto S000009result.ver e lista Global Layouts
import { ProjectServerManager } from './build/project-server-manager.js';

const serverManager = ProjectServerManager.getInstance();

async function testGlobalLayouts() {
    try {
        console.log('📂 Apertura progetto S000009result.ver...\n');
        
        // 1. Apri il progetto
        const openResult = await serverManager.openProject('H:\\go\\reports\\Input\\S000009result.ver');
        
        if (!openResult.success) {
            console.error('❌ Errore apertura progetto:', openResult.message);
            return;
        }
        
        console.log('✅ Progetto aperto!');
        console.log(`   Project ID: ${openResult.projectId}`);
        console.log(`   Porta TCP: ${openResult.serverInfo.port}`);
        console.log(`   PID: ${openResult.serverInfo.pid}\n`);
        
        // Aspetta che il server sia completamente pronto
        console.log('⏳ Attendo inizializzazione completa (10 secondi)...\n');
        await new Promise(resolve => setTimeout(resolve, 10000));
        
        // 2. Lista Global Layouts
        console.log('📋 Richiesta lista Global Layouts...\n');
        
        const pythonCode = `
gls = None
result = { 'count': 0, 'layouts': [], 'error': None }
try:
    # Tenta accesso a GlobalLayouts
    try:
        gls = Visum.Net.Project.GlobalLayouts
    except Exception:
        try:
            gls = Visum.Project.GlobalLayouts
        except Exception:
            gls = None

    if gls is None:
        result['error'] = 'GlobalLayouts collection not accessible'
    else:
        count = gls.Count
        if count == 0:
            result['count'] = 0
            result['layouts'] = []
        else:
            attrs = ['No','Name','GlobalLayoutFile','GlobalLayoutFileVersionNo']
            data = gls.GetMultipleAttributes(attrs)
            layouts = []
            # Assume data is columnar: [[no1,no2,...], [name1,name2,...], ...]
            if isinstance(data, (list, tuple)) and len(data) == len(attrs):
                for i in range(count):
                    row = [data[a][i] for a in range(len(attrs))]
                    layouts.append({
                        'no': row[0],
                        'name': row[1],
                        'file': row[2] if row[2] else '(not associated)',
                        'version': row[3] if row[3] else 'N/A',
                        'associated': bool(row[2])
                    })
            result['count'] = len(layouts)
            result['layouts'] = layouts
            assoc = sum(1 for l in layouts if l['associated'])
            result['summary'] = {
                'associated_layouts': assoc,
                'unassociated_layouts': len(layouts) - assoc
            }
except Exception as e:
    result['error'] = str(e)
result
`;

        const response = await serverManager.executeCommand(
            openResult.projectId,
            pythonCode,
            'List Global Layouts'
        );
        
        if (response.type === 'error') {
            console.error('❌ Errore esecuzione:', response.message);
            return;
        }
        
        const result = response.result || {};
        
        if (result.error) {
            console.log(`⚠️  Errore: ${result.error}\n`);
        } else {
            console.log('✅ Global Layouts trovati!\n');
            console.log(`📊 Totale: ${result.count}`);
            if (result.summary) {
                console.log(`   Associati: ${result.summary.associated_layouts}`);
                console.log(`   Non associati: ${result.summary.unassociated_layouts}\n`);
            }
            
            if (result.count > 0) {
                console.log('📋 Lista:\n');
                result.layouts.forEach((layout, idx) => {
                    console.log(`${idx + 1}. Layout #${layout.no}`);
                    console.log(`   Nome: ${layout.name || '(senza nome)'}`);
                    console.log(`   File: ${layout.file}`);
                    console.log(`   Versione: ${layout.version}`);
                    console.log(`   Associato: ${layout.associated ? '✅' : '❌'}\n`);
                });
            } else {
                console.log('ℹ️  Nessun Global Layout nel progetto\n');
            }
        }
        
        // 3. Chiudi il progetto
        console.log('🔚 Chiusura progetto...');
        await serverManager.closeProject(openResult.projectId, false);
        console.log('✅ Test completato!\n');
        
    } catch (error) {
        console.error('❌ Errore:', error.message);
    } finally {
        process.exit(0);
    }
}

testGlobalLayouts();
