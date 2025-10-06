import net from 'net';

const pythonCode = `
import sys

print("RICERCA TRANSPORT SYSTEMS DI TIPO PrT E RELATIVI DEMAND SEGMENTS", file=sys.stderr)
print("=" * 80, file=sys.stderr)

prt_tsys_list = []
segments_by_tsys = {}

try:
    # STEP 1: Trova tutti i Transport Systems di tipo PrT
    all_tsys = visum.Net.TSystems.GetAll
    print(f"\\nSTEP 1: Analisi {len(all_tsys)} Transport Systems...\\n", file=sys.stderr)
    
    for tsys in all_tsys:
        code = tsys.AttValue("CODE")
        name = str(tsys.AttValue("NAME")) if tsys.AttValue("NAME") else ""
        
        # Controlla se è di tipo PrT
        try:
            tsys_type = tsys.AttValue("TSYSTYPE")
        except:
            tsys_type = "N/A"
        
        try:
            tsys_prttype = tsys.AttValue("PRTTYPE")
        except:
            tsys_prttype = "N/A"
            
        try:
            is_prt = tsys.AttValue("ISPRT")
        except:
            is_prt = "N/A"
        
        print(f"  {code:10} - Type:{tsys_type:10} PrtType:{tsys_prttype:10} IsPrt:{is_prt}", file=sys.stderr)
        
        # Se è PrT, aggiungilo alla lista
        if is_prt == True or str(is_prt) == "1" or "PRT" in str(tsys_type).upper():
            prt_tsys_list.append({
                "code": code,
                "name": "",
                "type": str(tsys_type),
                "isPrt": str(is_prt)
            })
            segments_by_tsys[code] = []
    
    print(f"\\nTrovati {len(prt_tsys_list)} Transport Systems di tipo PrT:", file=sys.stderr)
    for tsys in prt_tsys_list:
        print(f"  - {tsys['code']}", file=sys.stderr)
    
    # STEP 2: Trova tutti i demand segments e associali ai TSys PrT
    print(f"\\n{'=' * 80}", file=sys.stderr)
    print("STEP 2: Ricerca demand segments per TSys PrT...\\n", file=sys.stderr)
    
    all_segments = visum.Net.DemandSegments.GetAll
    print(f"Totale demand segments: {len(all_segments)}\\n", file=sys.stderr)
    
    for seg in all_segments:
        code = seg.AttValue("CODE")
        
        # Prova diversi modi per ottenere il TSys
        tsys_code = None
        
        # Metodo 1: via attributo TSYSCODE
        try:
            tsys_code = seg.AttValue("TSYSCODE")
            if tsys_code == "N/A" or not tsys_code:
                tsys_code = None
        except:
            pass
        
        # Metodo 2: via proprietà TSys
        if not tsys_code:
            try:
                tsys_obj = seg.TSys
                tsys_code = tsys_obj.AttValue("CODE")
            except:
                pass
        
        # Metodo 3: via GetAttribute
        if not tsys_code:
            try:
                tsys_code = seg.GetAttribute("TSysCode")
            except:
                pass
        
        # Se il segment appartiene a un TSys PrT, aggiungilo
        if tsys_code and tsys_code in segments_by_tsys:
            segments_by_tsys[tsys_code].append(code)
            print(f"  ✓ {code} → TSys {tsys_code}", file=sys.stderr)
    
    # STEP 3: Genera DSEGSET
    print(f"\\n{'=' * 80}", file=sys.stderr)
    print("STEP 3: Risultati finali\\n", file=sys.stderr)
    
    all_prt_segments = []
    for tsys_code, seg_list in segments_by_tsys.items():
        print(f"  TSys '{tsys_code}': {len(seg_list)} segments", file=sys.stderr)
        all_prt_segments.extend(seg_list)
    
    dsegset_value = ",".join(all_prt_segments)
    
    print(f"\\n{'=' * 80}", file=sys.stderr)
    print(f"✅ TOTALE SEGMENTS PrT: {len(all_prt_segments)}", file=sys.stderr)
    print(f"\\nDSEGSET VALUE:\\n{dsegset_value}", file=sys.stderr)
    
except Exception as e:
    print(f"❌ Errore: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    prt_tsys_list = []
    segments_by_tsys = {}
    all_prt_segments = []
    dsegset_value = ""

result = {
    "status": "ok",
    "prt_tsys": prt_tsys_list,
    "segments_by_tsys": segments_by_tsys,
    "all_segments": all_prt_segments,
    "dsegset": dsegset_value,
    "total": len(all_prt_segments)
}
`;

const client = new net.Socket();
let welcomeReceived = false;

console.log('🔍 RICERCA TSys PrT E RELATIVI DEMAND SEGMENTS');
console.log('='.repeat(60));

client.connect(7905, '::1', () => {
    console.log('✅ Connesso\n');
});

client.on('data', (data) => {
    const response = JSON.parse(data.toString());
    
    if (!welcomeReceived && response.type === 'project_welcome') {
        welcomeReceived = true;
        const request = {
            type: 'query',
            requestId: Date.now(),
            description: 'Trova TSys PrT e segments',
            code: pythonCode
        };
        client.write(JSON.stringify(request) + '\n');
    } else {
        if (response.success && response.result.status === 'ok') {
            const res = response.result;
            
            console.log('\n📊 TRANSPORT SYSTEMS DI TIPO PrT:');
            console.log('='.repeat(60));
            res.prt_tsys.forEach(tsys => {
                console.log(`  ${tsys.code}: ${tsys.name} (Type: ${tsys.type}, IsPrt: ${tsys.isPrt})`);
            });
            
            console.log('\n📋 DEMAND SEGMENTS PER TSys:');
            console.log('='.repeat(60));
            for (const [tsysCode, segments] of Object.entries(res.segments_by_tsys)) {
                console.log(`\n  TSys "${tsysCode}": ${segments.length} segments`);
                if (segments.length > 0) {
                    segments.slice(0, 10).forEach(seg => console.log(`    - ${seg}`));
                    if (segments.length > 10) {
                        console.log(`    ... e altri ${segments.length - 10} segments`);
                    }
                }
            }
            
            console.log('\n' + '='.repeat(60));
            console.log(`✅ TOTALE SEGMENTS PrT: ${res.total}`);
            
            if (res.total > 0) {
                console.log('\n📝 VALORE DSEGSET:');
                console.log('='.repeat(60));
                console.log(res.dsegset);
            }
        } else {
            console.log('❌', response.error || response.result?.error);
        }
        console.log(`\n⏱️ ${response.executionTimeMs}ms`);
        client.destroy();
    }
});

client.on('close', () => console.log('\n🔌 Chiuso'));
client.on('error', (err) => console.error('❌', err.message));
