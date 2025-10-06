import net from 'net';

// Script semplificato - analisi solo demand segments
const pythonCode = `
import sys

# Analisi semplificata demand segments
print("Analisi demand segments...", file=sys.stderr)

try:
    ds_container = visum.Net.DemandSegments
    all_segments = ds_container.GetAll
    
    segments_data = []
    for ds in all_segments:
        seg_code = ds.AttValue("CODE")
        seg_name = ds.AttValue("NAME") if ds.AttValue("NAME") else ""
        
        # Prova a ottenere il mode
        seg_mode = "N/A"
        try:
            seg_mode = ds.AttValue("MODECODE")
        except:
            try:
                seg_mode = ds.AttValue("TSYSCODE")
            except:
                pass
        
        segments_data.append({
            "code": seg_code,
            "name": seg_name,
            "mode": str(seg_mode)
        })
        
        print(f"  Segment: {seg_code} | Mode: {seg_mode}", file=sys.stderr)
    
    result = {
        "status": "ok",
        "segments": segments_data,
        "total": len(segments_data)
    }
    
except Exception as e:
    result = {
        "status": "error",
        "error": str(e)
    }
`;

const client = new net.Socket();
let welcomeReceived = false;

console.log('🔍 ANALISI DEMAND SEGMENTS SEMPLIFICATA');
console.log('='.repeat(60));

client.connect(7902, '::1', () => {
    console.log('✅ Connesso sulla porta 7902\n');
});

client.on('data', (data) => {
    const response = JSON.parse(data.toString());
    
    if (!welcomeReceived && response.type === 'project_welcome') {
        welcomeReceived = true;
        
        const request = {
            type: 'query',
            requestId: Date.now(),
            description: 'Analisi demand segments',
            code: pythonCode
        };
        client.write(JSON.stringify(request) + '\n');
    } else {
        console.log('\n📊 RISULTATO:\n');
        
        if (response.success && response.result.status === 'ok') {
            const segments = response.result.segments;
            console.log(`Trovati ${segments.length} demand segments:\n`);
            
            segments.forEach((seg, i) => {
                console.log(`${i+1}. CODE: "${seg.code}" | Nome: ${seg.name} | Mode: ${seg.mode}`);
            });
            
            // Filtra solo quelli con mode "C"
            const cSegments = segments.filter(s => s.mode === 'C');
            console.log(`\n✅ Demand segments con MODE "C": ${cSegments.length}`);
            cSegments.forEach(seg => {
                console.log(`   • ${seg.code} - ${seg.name}`);
            });
            
        } else {
            console.log('❌ Errore:', response.error || response.result?.error);
        }
        
        console.log(`\n⏱️ Tempo: ${response.executionTimeMs}ms`);
        client.destroy();
    }
});

client.on('close', () => console.log('\n🔌 Chiuso'));
client.on('error', (err) => console.error('❌', err.message));
