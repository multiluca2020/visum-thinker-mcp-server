"""
export_typeno_to_visum.py
=========================
Legge links_remapped.csv (output dell'ottimizzazione) e produce un file .att
importabile in Visum per aggiornare il TYPENO degli archi ottimizzati.

Uso:
    python export_typeno_to_visum.py [links_remapped.csv] [output.att]

oppure modifica i percorsi DEFAULT_ qui sotto e lancia senza argomenti.

Il file .att usa il separatore punto-e-virgola e la codifica ANSI (Visum default).
Formato:
    $LINK:NO;TYPENO
    1;2095
    2;2095
    ...

Il join da (FROMNODENO,TONODENO) a NO viene fatto tramite netexport_link.shp.
"""

import sys
import pandas as pd
from pathlib import Path

# ---- Percorsi di default (modifica qui se necessario) ----
DEFAULT_REMAPPED  = r"H:\go\network_builder\outputs\speed_optimization_arc\links_remapped.csv"
DEFAULT_LINK_SHP  = r"H:\go\network_builder\inputs\net_export\netexport_link.shp"
DEFAULT_OUTPUT    = r"H:\go\network_builder\outputs\speed_optimization_arc\typeno_update.att"

def main():
    remapped_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(DEFAULT_REMAPPED)
    output_path   = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(DEFAULT_OUTPUT)
    link_shp      = Path(DEFAULT_LINK_SHP)

    print("=" * 60)
    print("EXPORT TYPENO -> Visum .att")
    print("=" * 60)
    print(f"  Remapped CSV: {remapped_path}")
    print(f"  Link SHP:     {link_shp}")
    print(f"  Output ATT:   {output_path}")

    # 1. Carica links_remapped.csv
    remap = pd.read_csv(remapped_path, dtype={"FROMNODENO": int, "TONODENO": int,
                                               "TYPENO_ORIG": int, "TYPENO_NEW": int})
    print(f"\n  Archi nel CSV: {len(remap):,}  "
          f"(di cui CHANGED={remap['CHANGED'].sum():,})")

    # Tieni solo gli archi con tipo cambiato (opzionale: rimuovi il filtro
    # per aggiornare TUTTI gli archi, inclusi quelli invariati)
    remap_changed = remap[remap["CHANGED"] == 1].copy()
    print(f"  Archi con tipo modificato: {len(remap_changed):,}")

    # 2. Carica il link shapefile per il join (as DataFrame, no geometria necessaria)
    try:
        import geopandas as gpd
        links = gpd.read_file(link_shp)[["NO", "FROMNODENO", "TONODENO"]]
    except ImportError:
        # Fallback: legge il DBF direttamente
        import dbfread
        tbl = dbfread.DBF(str(link_shp).replace(".shp", ".dbf"))
        links = pd.DataFrame(iter(tbl))[["NO", "FROMNODENO", "TONODENO"]]

    links = links.astype({"NO": int, "FROMNODENO": int, "TONODENO": int})
    print(f"\n  Archi nel SHP: {len(links):,}")

    # 3. Join: (FROMNODENO, TONODENO) → NO
    merged = remap_changed.merge(
        links[["NO", "FROMNODENO", "TONODENO"]],
        on=["FROMNODENO", "TONODENO"],
        how="left"
    )

    no_match = merged["NO"].isna().sum()
    if no_match > 0:
        print(f"  [!] {no_match} archi senza corrispondenza in SHP (non esportati)")

    result = merged.dropna(subset=["NO"])[["NO", "TYPENO_NEW"]].copy()
    result["NO"] = result["NO"].astype(int)
    result = result.sort_values("NO")

    print(f"  Archi da aggiornare in Visum: {len(result):,}")

    # 4. Distribuzione tipi nuovi
    dist = result["TYPENO_NEW"].value_counts().sort_index()
    print(f"\n  Distribuzione TYPENO_NEW:")
    for typeno, cnt in dist.items():
        print(f"    Type {int(typeno):5d}: {cnt:6d} archi")

    # 5. Scrivi il file .att
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="ansi", errors="replace") as f:
        f.write("$VISION\n")
        f.write("$VERSION:VERSNR;FILETYPE;LANGUAGE;UNIT\n")
        f.write("10.000;ATT;ENG;KM\n")
        f.write("\n")
        f.write("$LINK:NO;TYPENO\n")
        for _, row in result.iterrows():
            f.write(f"{int(row['NO'])};{int(row['TYPENO_NEW'])}\n")

    print(f"\n  [OK] File .att scritto: {output_path}")
    print(f"       {len(result):,} righe  (header escluso)")
    print(f"\nImport in Visum:")
    print(f"  File → Importa dati attributi → seleziona {output_path.name}")
    print(f"  Opzione: 'Sovrascrivi attributi esistenti'")

if __name__ == "__main__":
    main()
