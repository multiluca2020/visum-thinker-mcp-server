# VELOCISSIMO - Usa iteratore invece di GetAll
# Copia/incolla nella console Python di Visum

# Prendi primo link usando iteratore (NO GetAll!)
for link1 in Visum.Net.Links:
    break

attrs = ["VOLPRT", "VolVehPrT", "VolPersPrT", "VolCapRatioPrT(AP)", "V0PRT"]

for attr in attrs:
    try:
        val = link1.AttValue(attr)
        print(f"{attr}: ESISTE (val={val})")
    except Exception as e:
        print(f"{attr}: NON ESISTE - {str(e)[:50]}")
