import net from 'net';

const pythonCode = `
import sys

print("=" * 80, file=sys.stderr)
print("STEP 1: ANALISI TRANSPORT SYSTEMS (TSys) DI TIPO PRT", file=sys.stderr)
print("=" * 80, file=sys.stderr)

# STEP 1: Trova tutti i Transport Systems di tipo PrT
prt_tsystems = []

try:
    all_tsys = visum.Net.TSystems.GetAll
    print(f"Totale Transport Systems: {len(all_tsys)}", file=sys.stderr)
    
    for tsys in all_tsys:
        tsys_code = tsys.AttValue("CODE")
        tsys_name = tsys.AttValue("NAME") if tsys.AttValue("NAME") else ""
        
        # Verifica il tipo - PrT systems hanno TSYSTYPE = "PrT" o simile
        try:
            tsys_type = tsys.AttValue("TSYSTYPE")
        except:
            tsys_type = "N/A"
        
        # Anche MODE associato
        try:
            tsys_mode = tsys.AttValue("MODECODE")
        except:
            tsys_mode = "N/A"
        
        print(f"  TSys: {tsys_code} | Name: {tsys_name} | Type: {tsys_type} | Mode: {tsys_mode}", file=sys.stderr)
        
        # Considera PrT se type contiene "PrT" o "P" o se è tipo 1
        is_prt = False
        if "PrT" in str(tsys_type) or str(tsys_type) == "P" or str(tsys_type) == "1":
            is_prt = True
        
        if is_prt:
            prt_tsystems.append({
                "code": tsys_code,
                "name": tsys_name,
                "type": str(tsys_type),
                "mode": str(tsys_mode)
            })
            print(f"    -> PRT SYSTEM TROVATO!", file=sys.stderr)
    
    print(f"\\nTotale PrT Transport Systems: {len(prt_tsystems)}", file=sys.stderr)
    
except Exception as e:
    print(f"Errore: {e}", file=sys.stderr)
    prt_tsystems = []

print("\\n" + "=" * 80, file=sys.stderr)
print("STEP 2: DEMAND SEGMENTS PER OGNI TRANSPORT SYSTEM PRT", file=sys.stderr)
print("=" * 80, file=sys.stderr)

# STEP 2: Per ogni TSys PrT, trova i demand segments
tsys_segments_map = {}

try:
    all_segments = visum.Net.DemandSegments.GetAll
    print(f"Totale Demand Segments nel progetto: {len(all_segments)}", file=sys.stderr)
    
    for tsys in prt_tsystems:
        tsys_code = tsys["code"]
        tsys_segments_map[tsys_code] = []
        
        print(f"\\nTSys '{tsys_code}' ({tsys['name']}):", file=sys.stderr)
        
        for seg in all_segments:
            seg_code = seg.AttValue("CODE")
            seg_name = seg.AttValue("NAME") if seg.AttValue("NAME") else ""
            
            # Verifica se appartiene a questo TSys
            try:
                seg_tsys = seg.AttValue("TSYSCODE")
            except:
                seg_tsys = None
            
            if seg_tsys == tsys_code:
                segment_info = {
                    "code": seg_code,
                    "name": seg_name,
                    "tsys": tsys_code
                }
                tsys_segments_map[tsys_code].append(segment_info)
                print(f"  -> Segment: {seg_code} | {seg_name}", file=sys.stderr)
        
        if len(tsys_segments_map[tsys_code]) == 0:
            print(f"  (nessun segment trovato)", file=sys.stderr)
    
except Exception as e:
    print(f"Errore: {e}", file=sys.stderr)

print("\\n" + "=" * 80, file=sys.stderr)

# Costruisci lista completa per assignment
all_prt_segments = []
for tsys_code, segments in tsys_segments_map.items():
    all_prt_segments.extend(segments)

result = {
    "status": "ok",
    "prt_tsystems": prt_tsystems,
    "tsys_segments_map": tsys_segments_map,
    "all_prt_segments": all_prt_segments,
    "summary": {
        "total_prt_tsystems": len(prt_tsystems),
        "total_prt_segments": len(all_prt_segments)
    }
}
`;

const client = new net.Socket();
let welcomeReceived = false;

console.log('🔍 ANALISI PRT TRANSPORT SYSTEMS E DEMAND SEGMENTS');
console.log('='.repeat(80));

client.connect(7905, '::1', () => {
    console.log('✅ Connesso sulla porta 7905\n');
});

client.on('data', (data) => {
    const response = JSON.parse(data.toString());
    
    if (!welcomeReceived && response.type === 'project_welcome') {
        welcomeReceived = true;
        
        const request = {
            type: 'query',
            requestId: Date.now(),
            description: 'Analisi PrT Transport Systems e Demand Segments',
            code: pythonCode
        };
        client.write(JSON.stringify(request) + '\n');
    } else {
        console.log('='.repeat(80));
        console.log('📊 RISULTATO ANALISI\n');
        
        if (response.success && response.result.status === 'ok') {
            const res = response.result;
            
            console.log(`✅ PrT TRANSPORT SYSTEMS: ${res.summary.total_prt_tsystems}\n`);
            
            res.prt_tsystems.forEach((tsys, i) => {
                console.log(`${i+1}. TSys: "${tsys.code}" - ${tsys.name}`);
                console.log(`   Type: ${tsys.type} | Mode: ${tsys.mode}`);
                
                const segments = res.tsys_segments_map[tsys.code] || [];
                console.log(`   Demand Segments: ${segments.length}`);
                
                segments.forEach(seg => {
                    console.log(`     • "${seg.code}" - ${seg.name}`);
                });
                console.log('');
            });
            
            if (res.all_prt_segments.length > 0) {
                const segmentCodes = res.all_prt_segments.map(s => s.code);
                console.log('\n📋 CONFIGURAZIONE PER ASSIGNMENT:');
                console.log('='.repeat(80));
                console.log(`\n✅ Demand Segments PrT da includere: ${segmentCodes.length}`);
                console.log(`   Codici: ${JSON.stringify(segmentCodes)}`);
                console.log(`   Formato Visum (DSEGSET): "${segmentCodes.join(',')}"`);
            } else {
                console.log('\n⚠️ NESSUN DEMAND SEGMENT PRT TROVATO');
            }
            
        } else {
            console.log('❌ Errore:', response.error || response.result?.error);
        }
        
        console.log(`\n⏱️ Tempo analisi: ${response.executionTimeMs}ms`);
        console.log('='.repeat(80));
        client.destroy();
    }
});

client.on('close', () => console.log('\n🔌 Chiuso'));
client.on('error', (err) => console.error('❌', err.message));
