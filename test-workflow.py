"""
Test completo del workflow PrT Assignment via MCP
"""
import subprocess
import json
import sys

PROJECT_ID = "100625_Versione_base_v0.3_sub_ok_priv_10176442"

def call_mcp_tool(tool_name, arguments):
    """Chiama un tool MCP usando lo script wrapper"""
    cmd = [
        "node",
        "mcp-quick-call.js",
        tool_name,
        json.dumps(arguments)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    
    # Cerca la risposta JSON nell'output (dopo "📥 Response:")
    lines = result.stdout.split('\n')
    for i, line in enumerate(lines):
        if '📥 Response:' in line or 'Response:' in line:
            # Il JSON inizia dalla riga successiva
            json_text = '\n'.join(lines[i+1:])
            try:
                return json.loads(json_text.strip())
            except:
                pass
        elif line.strip().startswith('{') and '"result"' in line:
            try:
                return json.loads(line)
            except:
                pass
    
    print("❌ No valid response found")
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    return None

def main():
    print("=" * 80)
    print("TEST WORKFLOW COMPLETO: Create PrT Assignment + Configure DSEGSET")
    print("=" * 80)
    print()
    
    # Step 1: Lista segments
    print("📋 Step 1: Lista demand segments disponibili")
    response = call_mcp_tool("visum_list_demand_segments", {
        "projectId": PROJECT_ID
    })
    if response and 'result' in response:
        print("✅ Segments elencati con successo")
        print()
    else:
        print("❌ Errore listing segments")
        return 1
    
    # Step 2: Crea procedura
    print("🎯 Step 2: Crea nuova procedura PrT Assignment")
    response = call_mcp_tool("visum_create_procedure", {
        "projectId": PROJECT_ID,
        "procedureType": "PrT_Assignment"
    })
    
    if not response or 'result' not in response:
        print("❌ Errore creazione procedura")
        return 1
    
    # Estrai la posizione effettiva dalla risposta
    content = response['result']['content'][0]['text']
    
    # Parse della posizione dalla risposta
    import re
    match = re.search(r'\*\*Posizione Effettiva:\*\* (\d+)', content)
    if not match:
        print("❌ Non riesco a trovare la posizione nella risposta")
        print(content)
        return 1
    
    procedure_position = int(match.group(1))
    print(f"✅ Procedura creata alla posizione {procedure_position}")
    print()
    
    # Step 3: Configura DSEGSET
    print(f"⚙️ Step 3: Configura DSEGSET con segments 1-10 sulla posizione {procedure_position}")
    response = call_mcp_tool("visum_configure_dsegset", {
        "projectId": PROJECT_ID,
        "procedurePosition": procedure_position,
        "segmentNumbers": "1-10"
    })
    
    if response and 'result' in response:
        content = response['result']['content'][0]['text']
        match = re.search(r'\*\*Segments configurati:\*\* (\d+)', content)
        if match:
            segment_count = int(match.group(1))
            print(f"✅ DSEGSET configurato con {segment_count} segments")
        else:
            print("✅ DSEGSET configurato")
        print()
    else:
        print("❌ Errore configurazione DSEGSET")
        return 1
    
    # Step 4: Test con filtro modo
    print(f"⚙️ Step 4: Test filtro modo - configura solo modo H sulla posizione {procedure_position}")
    response = call_mcp_tool("visum_configure_dsegset", {
        "projectId": PROJECT_ID,
        "procedurePosition": procedure_position,
        "filterMode": "H"
    })
    
    if response and 'result' in response:
        content = response['result']['content'][0]['text']
        match = re.search(r'\*\*Segments configurati:\*\* (\d+)', content)
        if match:
            segment_count = int(match.group(1))
            print(f"✅ DSEGSET riconfigurato con {segment_count} segments modo H")
        print()
    else:
        print("❌ Errore riconfigurazione DSEGSET")
        return 1
    
    print("=" * 80)
    print("🎉 WORKFLOW COMPLETO TESTATO CON SUCCESSO!")
    print("=" * 80)
    print()
    print(f"✅ Posizione procedura creata: {procedure_position}")
    print("✅ Tutti i formati di input testati:")
    print("   • Notazione numerica (1-10)")
    print("   • Filtro per modo (H)")
    print()
    print(f"💡 Vai in Visum → Procedures → Operations → Posizione {procedure_position}")
    print("   per vedere la procedura configurata!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
