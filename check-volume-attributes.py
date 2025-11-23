"""
Script per verificare attributi volume PrT in Visum
Eseguire questo script direttamente in Visum (Script > Run Script)
"""

import win32com.client

# Connetti a Visum (se già aperto) o usa l'istanza corrente
try:
    visum = Visum
    print("✅ Usando istanza Visum corrente")
except:
    visum = win32com.client.Dispatch("Visum.Visum.250")
    print("✅ Connesso a nuova istanza Visum")

print("\n" + "="*80)
print("VERIFICA ATTRIBUTI VOLUME PrT")
print("="*80)

# 1. Conta archi
links_count = visum.Net.Links.Count
print(f"\n📊 Totale archi nella rete: {links_count:,}")

# 2. Test attributi su primi 10 archi
print("\n🔍 Test attributi sui primi 10 archi:")
print("-" * 80)

all_links = visum.Net.Links.GetAll
test_attributes = [
    "VOLPRT",
    "VolVehPrT", 
    "VolPersPrT",
    "VolPCUPrT",
    "VolCapRatioPrT(AP)",
    "V0PRT"
]

results = {}
for attr in test_attributes:
    results[attr] = {"exists": False, "has_values": False, "sample_values": []}

# Testa su primi 10 archi
for i in range(min(10, len(all_links))):
    link = all_links[i]
    link_key = (link.AttValue("FROMNODENO"), link.AttValue("TONODENO"))
    
    for attr in test_attributes:
        try:
            value = link.AttValue(attr)
            results[attr]["exists"] = True
            results[attr]["sample_values"].append({
                "link": link_key,
                "value": value
            })
            if value > 0:
                results[attr]["has_values"] = True
        except Exception as e:
            if not results[attr].get("error"):
                results[attr]["error"] = str(e)[:100]

# 3. Stampa risultati
print("\n📋 RISULTATI:")
print("=" * 80)

for attr in test_attributes:
    print(f"\n🔹 {attr}:")
    print(f"   Esiste: {'✅ SI' if results[attr]['exists'] else '❌ NO'}")
    
    if results[attr]['exists']:
        print(f"   Ha valori > 0: {'✅ SI' if results[attr]['has_values'] else '❌ NO'}")
        
        # Mostra primi 3 valori
        sample = results[attr]['sample_values'][:3]
        if sample:
            print(f"   Campione valori:")
            for s in sample:
                print(f"      Link {s['link']}: {s['value']}")
    else:
        if results[attr].get('error'):
            print(f"   Errore: {results[attr]['error']}")

# 4. Conta archi con volumi
print("\n" + "="*80)
print("CONTEGGIO ARCHI CON VOLUMI")
print("="*80)

if results["VolCapRatioPrT(AP)"]["exists"]:
    print("\n🔍 Conteggio archi con VolCapRatioPrT(AP) > 0...")
    count_with_vol = 0
    sample_size = min(1000, len(all_links))
    
    for i in range(0, len(all_links), max(1, len(all_links) // sample_size)):
        try:
            link = all_links[i]
            vol = link.AttValue("VolCapRatioPrT(AP)")
            if vol > 0:
                count_with_vol += 1
        except:
            pass
    
    print(f"   Archi campionati: {sample_size:,}")
    print(f"   Archi con volume > 0: {count_with_vol:,}")
    print(f"   Percentuale: {(count_with_vol/sample_size)*100:.1f}%")
else:
    print("\n⚠️  Attributo VolCapRatioPrT(AP) non disponibile")

print("\n" + "="*80)
print("✅ VERIFICA COMPLETATA")
print("="*80)
