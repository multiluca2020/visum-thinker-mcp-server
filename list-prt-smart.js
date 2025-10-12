/**
 * Script intelligente che legge la porta dal registry
 * e elenca i modi PRT e demand segments
 */

import net from 'net';
import fs from 'fs';

// Leggi la porta dal registry
const registry = JSON.parse(fs.readFileSync('project-servers-registry.json', 'utf8'));
const servers = Object.values(registry.servers);

if (servers.length === 0) {
    console.log('❌ Nessun server Visum attivo trovato nel registry');
    console.log('💡 Devi prima aprire il progetto con:');
    console.log('   echo \'{"method":"tools/call","params":{"name":"project_open","arguments":{"projectPath":"H:\\\\go\\\\italferr2025\\\\Campoleone\\\\100625_Versione_base_v0.3_sub_ok_priv.ver"}},"jsonrpc":"2.0","id":13}\' | node build/index.js');
    process.exit(1);
}

const server = servers[0];
const PORT = server.port;

console.log(`🔍 Connessione al server Visum sulla porta ${PORT}...`);

const pythonCode = `
import sys

print("=" * 70, file=sys.stderr)
print("  ANALISI MODI PRT E DEMAND SEGMENTS", file=sys.stderr)
print("=" * 70, file=sys.stderr)

try:
    # STEP 1: Trova TSys PRT
    all_tsys = visum.Net.TSystems.GetAll
    prt_tsys = []
    
    print("\\n[STEP 1] Transport Systems di tipo PRT:\\n", file=sys.stderr)
    
    for tsys in all_tsys:
        code = tsys.AttValue("CODE")
        name = tsys.AttValue("NAME")
        tsys_type = tsys.AttValue("TYPE")
        
        if tsys_type == "PRT":
            prt_tsys.append({"code": code, "name": name})
            print(f"  TSys PRT: {code} ({name})", file=sys.stderr)
    
    print(f"\\nTrovati {len(prt_tsys)} TSys PRT", file=sys.stderr)
    
    # STEP 2: Trova Modes associati
    print(f"\\n{'=' * 70}", file=sys.stderr)
    print("[STEP 2] Ricerca Modes associati:\\n", file=sys.stderr)
    
    all_modes = visum.Net.Modes.GetAll
    prt_mode_codes = []
    mode_mapping = {}
    
    for mode in all_modes:
        mode_code = mode.AttValue("CODE")
        mode_name = mode.AttValue("NAME")
        
        for tsys in prt_tsys:
            if mode_name.upper() == tsys["name"].upper():
                prt_mode_codes.append(mode_code)
                mode_mapping[mode_code] = {
                    "mode_name": mode_name,
                    "tsys_code": tsys["code"],
                    "tsys_name": tsys["name"]
                }
                print(f"  Mode '{mode_code}' ({mode_name}) -> TSys {tsys['code']}", file=sys.stderr)
                break
    
    if len(prt_mode_codes) == 0:
        print(f"\\n  Fallback: pattern matching...", file=sys.stderr)
        for tsys in prt_tsys:
            tsys_first = tsys["code"][0]
            for mode in all_modes:
                mode_code = mode.AttValue("CODE")
                if mode_code.upper() == tsys_first.upper():
                    if mode_code not in prt_mode_codes:
                        prt_mode_codes.append(mode_code)
                        mode_mapping[mode_code] = {
                            "mode_name": mode.AttValue("NAME"),
                            "tsys_code": tsys["code"],
                            "tsys_name": tsys["name"]
                        }
                        print(f"  Mode '{mode_code}' -> TSys {tsys['code']} (pattern)", file=sys.stderr)
    
    # STEP 3: Raccogli segments
    print(f"\\n{'=' * 70}", file=sys.stderr)
    print("[STEP 3] Demand Segments per Mode PRT:\\n", file=sys.stderr)
    
    all_segments = visum.Net.DemandSegments.GetAll
    segments_by_mode = {}
    all_prt_segments = []
    
    for seg in all_segments:
        seg_code = seg.AttValue("CODE")
        seg_mode = seg.AttValue("MODE")
        
        if seg_mode in prt_mode_codes:
            if seg_mode not in segments_by_mode:
                segments_by_mode[seg_mode] = []
            segments_by_mode[seg_mode].append(seg_code)
            all_prt_segments.append(seg_code)
    
    for mode_code in sorted(prt_mode_codes):
        segs = segments_by_mode.get(mode_code, [])
        mapping = mode_mapping[mode_code]
        print(f"Mode '{mode_code}' ({mapping['mode_name']}) -> TSys {mapping['tsys_code']}:", file=sys.stderr)
        print(f"  Segments: {len(segs)}", file=sys.stderr)
        for s in segs[:8]:
            print(f"    - {s}", file=sys.stderr)
        if len(segs) > 8:
            print(f"    ... e altri {len(segs) - 8}", file=sys.stderr)
        print(file=sys.stderr)
    
    dsegset_value = ",".join(all_prt_segments)
    
    print(f"{'=' * 70}", file=sys.stderr)
    print(f"TOTALE: {len(all_prt_segments)} demand segments PRT", file=sys.stderr)
    print(f"{'=' * 70}", file=sys.stderr)
    
    result = {
        "status": "ok",
        "prt_tsys": prt_tsys,
        "prt_modes": prt_mode_codes,
        "mode_mapping": mode_mapping,
        "segments_by_mode": segments_by_mode,
        "all_segments": all_prt_segments,
        "dsegset": dsegset_value,
        "total": len(all_prt_segments)
    }
    
except Exception as e:
    print(f"\\nERRORE: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    result = {"status": "error", "error": str(e)}
`;

const client = new net.Socket();
let welcomeReceived = false;

console.log('\n🔍 ANALISI MODI PRT E DEMAND SEGMENTS');
console.log('='.repeat(70));

client.connect(PORT, '::1', () => {
    console.log('✅ Connesso\n');
});

client.on('data', (data) => {
    const response = JSON.parse(data.toString());
    
    if (!welcomeReceived && response.type === 'project_welcome') {
        welcomeReceived = true;
        const request = {
            type: 'query',
            requestId: Date.now(),
            description: 'List PRT segments',
            code: pythonCode
        };
        client.write(JSON.stringify(request) + '\n');
    } else {
        if (response.success) {
            const res = response.result;
            if (res.status === 'ok') {
                console.log('\n📊 TSys PRT:');
                res.prt_tsys.forEach(t => console.log(`  - ${t.code} (${t.name})`));
                
                console.log('\n🔗 MAPPING Mode → TSys:');
                console.log('='.repeat(70));
                for (const [code, map] of Object.entries(res.mode_mapping)) {
                    console.log(`  Mode "${code}" (${map.mode_name}) → TSys ${map.tsys_code}`);
                }
                
                console.log('\n📋 SEGMENTS PER MODE:');
                console.log('='.repeat(70));
                for (const [code, segs] of Object.entries(res.segments_by_mode)) {
                    console.log(`\n${code}: ${segs.length} segments`);
                    segs.slice(0, 10).forEach(s => console.log(`  - ${s}`));
                    if (segs.length > 10) {
                        console.log(`  ... e altri ${segs.length - 10}`);
                    }
                }
                
                console.log('\n' + '='.repeat(70));
                console.log(`✅ TOTALE: ${res.total} segments PRT`);
                console.log('\n📝 DSEGSET COMPLETO:');
                console.log('='.repeat(70));
                console.log(res.dsegset);
            } else {
                console.log(`\n❌ ${res.error}`);
            }
        } else {
            console.log('❌', response.error);
        }
        console.log(`\n⏱️ ${response.executionTimeMs}ms`);
        client.destroy();
    }
});

client.on('close', () => console.log('\n🔌 Chiuso'));
client.on('error', (err) => {
    console.error(`\n❌ Errore: ${err.message}`);
    console.error(`\nIl server sulla porta ${PORT} non risponde.`);
    console.error('Assicurati che il progetto Visum sia aperto.');
});
