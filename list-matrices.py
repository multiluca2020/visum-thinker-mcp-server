"""
Lista tutte le matrici nel progetto Visum per trovare dove sono i risultati skim
Da eseguire dalla console Visum (usa variabile Visum già disponibile)
"""

# Usa istanza Visum dalla console
visum = Visum

print("\n" + "=" * 70)
print("MATRICI NEL PROGETTO VISUM")
print("=" * 70)

matrices = visum.Net.Matrices.GetAll

print("\nTrovate {} matrici:".format(len(matrices)))
print("\n{:<6} {:<20} {:<20} {:<15}".format("No", "Name", "Code", "Valori > 0"))
print("-" * 70)

for matrix in matrices:
    no = matrix.AttValue("No")
    name = matrix.AttValue("Name")
    code = matrix.AttValue("Code")
    
    # Conta valori > 0
    non_zero = 0
    zones = visum.Net.Zones.GetAll
    zone_numbers = [z.AttValue("No") for z in zones]
    
    # Sample: controlla solo prime 100 coppie per velocità
    sample_size = min(100, len(zone_numbers) ** 2)
    checked = 0
    for orig in zone_numbers[:10]:
        for dest in zone_numbers[:10]:
            try:
                val = matrix.GetValue(orig, dest)
                if val > 0:
                    non_zero += 1
                checked += 1
                if checked >= sample_size:
                    break
            except:
                pass
        if checked >= sample_size:
            break
    
    pct = 100.0 * non_zero / checked if checked > 0 else 0
    
    print("{:<6} {:<20} {:<20} {:>5}/{:<5} ({:.0f}%)".format(
        no, name[:20], code[:20], non_zero, checked, pct))

print("\n" + "=" * 70)
print("\nCerca matrici con Code tipo 'T0PRT', 'TCUR', o simili")
print("Queste contengono i risultati dell'operazione skim!")
