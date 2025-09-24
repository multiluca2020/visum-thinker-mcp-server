
# Python script che gira in Visum
# Accesso diretto ai dati tramite COM interno

import json
import time

# Questo script gira DENTRO Visum, quindi COM funziona
visum = Visum.GetInstance()  # API interna Visum

# Estrai dati rete
data = {
    "timestamp": time.time(),
    "nodes": visum.Net.Nodes.Count,
    "links": visum.Net.Links.Count,
    "zones": visum.Net.Zones.Count,
    "project_modified": True  # Sempre aggiornato
}

# Sample link data
links_data = []
link_set = visum.Net.Links
attrs = link_set.GetMultipleAttributes(['No', 'Length', 'NumLanes'])
for i, (no, length, lanes) in enumerate(attrs[:10]):  # Prime 10
    links_data.append({
        "no": no,
        "length": length, 
        "lanes": lanes
    })

data["sample_links"] = links_data

# Export JSON per MCP
output_file = r"H:\visum-thinker-mcp-server\visum_data.json"
with open(output_file, 'w') as f:
    json.dump(data, f, indent=2)

# Segnala completamento
with open(r"H:\visum-thinker-mcp-server\export_ready.flag", 'w') as f:
    f.write("READY")
    
print("Data exported to MCP successfully!")
