#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Network Speed Optimization via Bounded Least Squares
=====================================================
Ottimizza le velocita dei LinkType Visum minimizzando l'errore tra
tempi di percorrenza da modello (shortest path) e tempi osservati.

APPROCCIO MATEMATICO:
    Per un percorso fisso od, il tempo di viaggio e:
        T_od = sum_k ( D_od_k / v_k )
    dove D_od_k = lunghezza totale di archi di tipo k sul percorso od.

    Sostituendo beta_k = 1/v_k (la "lentezza" o slowness):
        T_od = D_od ? beta   (LINEARE in beta!)

    Problema di ottimizzazione:
        min ||D @ beta - T_obs||?
        s.t.  1/v_max <= beta_k <= 1/v_min

    Solvibile con scipy.optimize.lsq_linear (BVLS):
        - Ottimo globale garantito (problema convesso)
        - Molto piu veloce di minimize() con Jacobiano
        - I bounds prevengono velocita non realistiche

    Iterazione con re-routing (tipo Frank-Wolfe):
        1. Calcola percorsi con velocita correnti
        2. Costruisce matrice D
        3. Risolve sistema lineare -> nuove velocita
        4. Aggiorna T0 nel grafo
        5. Ripeti fino a convergenza

UTILIZZO:
    python optimize_link_speeds.py config.json

COLONNE SHAPEFILE VISUM (default export):
    wkt_geom  FROMNODENO  TONODENO  TYPENO  TSYSSET  LENGTH    NUMLANES  CAPPRT  V0PRT    ...
    [geom]    1           2         60      CAR,HGV  0.041km   2         2200    50km/h   ...

    NOTA: T0_PRTSYS non viene esportato di default; il script calcola:
        T0 = (LENGTH_km / V0PRT_kmh) * 60  [minuti]

CONFIG.JSON:
    {
        "network_dir": "H:/data/network_shp",
        "observed_times_csv": "H:/data/observed_od_times.csv",
        "output_dir": "H:/data/optimization_results",
        "od_col_orig": "origin",
        "od_col_dest": "destination",
        "od_col_time": "time_m",
        "v0prt_field": "V0PRT",
        "length_field": "LENGTH",
        "linktype_field": "TYPENO",
        "speed_min_kmh": 10.0,
        "speed_max_kmh": 150.0,
        "n_iterations": 10,
        "convergence_threshold": 0.005,
        "fix_connector_t0": true,
        "sample_od_pairs": null
    }
"""

import sys
import json
import traceback
import warnings
from pathlib import Path
from itertools import islice

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")


# =============================================================================
# COSTANTI E DEFAULT
# =============================================================================

DEFAULT_CONFIG = {
    "network_dir": None,            # Cartella con gli shapefile *_link.shp, *_node.shp, ecc.
    "file_prefix": None,            # Prefisso file (es. "roma") -> roma_link.shp. None=autodetect
    "observed_times_csv": None,     # CSV con tempi osservati (origin, destination, time_min)
    "output_dir": None,             # Cartella output
    "od_col_orig": "origin",        # Nome colonna origine nel CSV
    "od_col_dest": "destination",   # Nome colonna destinazione nel CSV
    "od_col_time": "time_m",       # Nome colonna tempi osservati (in MINUTI)
    # - Colonne shapefile
    "v0prt_field": "V0PRT",         # Campo velocita libera (es. "50km/h") -- T0 calcolato da V0PRT+LENGTH
    "length_field": "LENGTH",       # Campo lunghezza (es. "0.041km" -- unit suffix gestita automaticamente)
    "linktype_field": "TYPENO",     # Campo numero tipo link
    "fromnodeno_field": "FROMNODENO",
    "tonodeno_field": "TONODENO",
    # - Ottimizzazione
    "optimization_mode": "per_type",  # "per_type" | "per_arc"
    "speed_min_kmh": 10.0,
    "speed_max_kmh": 150.0,
    "speed_delta_kmh": 10.0,         # per_type: max variazione per tipo (km/h)
    "speed_class_gap_kmh": 1.0,      # per_type: gap minimo tra classi
    "speed_delta_arc_kmh": 20.0,     # per_arc:  max variazione per arco (km/h)
    "max_active_arcs":   500,       # per_arc:  top archi per sub-cycle (piccolo -> bvls dense rapido)
    "od_error_frac":     None,      # per_arc:  frazione OD peggiori per sub-cycle (None=auto: 30/20/10%)
    "n_sub_cycles":      3,         # per_arc:  sub-cicli per iterazione (ri-selezione OD senza Dijkstra)
    "n_iterations":      10,        # Max iterazioni ottimizzazione (outer loop con Dijkstra)
    "convergence_threshold": 0.005, # Soglia convergenza legacy (frazione archi riassegnati)
    "slope_target_min":  0.9,       # Convergenza: slope minimo accettabile (default 0.9)
    "slope_target_max":  1.1,       # Convergenza: slope massimo accettabile (default 1.1)
    "r2_target":         0.9,       # Convergenza: R2(origin) minimo accettabile (default 0.9)
    "fix_connector_t0": True,       # True = connettori NON ottimizzati (T0 fisso)
    "sample_od_pairs": None,        # None = tutte le coppie OD; int = campione casuale
    "random_seed": 42,
}

# Nomi alternativi per le colonne (case-insensitive lookup)
COLUMN_ALIASES = {
    "V0PRT":       ["V0PRT", "V0_PRT", "V0", "SPEED", "FREESPEED", "VMAX", "SPEED_KMH",
                    "V0PRT_C", "V0PRTSYS", "V0_PRTSYS", "FREFL_CAR"],
    "T0_PRTSYS":   ["T0_PRTSYS", "T0PRT", "T0", "T0_CAR", "TRAVELTIME", "T0_C", "T0PRTSYS",
                    "T0_PRTSYS(C)", "TT0", "TIME0"],
    "LENGTH":      ["LENGTH", "LEN", "LENGTH_M", "DIST", "DISTANCE", "LAENGE", "LUNGHEZZA"],
    "TYPENO":      ["TYPENO", "TYPENUMBER", "LINKTYPE", "TYPE", "LTYPENUMBER", "TYPE_NO",
                    "LINKTYPENO"],
    "FROMNODENO":  ["FROMNODENO", "FROMNODE", "FROM_NODE", "FROM", "VONKNOTENNO"],
    "TONODENO":    ["TONODENO", "TONODE", "TO_NODE", "TO", "NACHKNOTENNO"],
    "ZONENO":      ["ZONENO", "ZONE", "CENTROID", "BEZIRKNO", "NO"],
    "NODENO":      ["NODENO", "NODE", "KNOTENNO", "NO"],
}


# Alias per colonne del CSV tempi osservati (auto-detection)
OD_COL_ALIASES = {
    "origin":      ["origin", "orig", "from", "o", "zona_o", "zona_orig", "from_zone"],
    "destination": ["destination", "dest", "to", "d", "zona_d", "zona_dest", "to_zone"],
    "time_m":      ["time_m", "time_min", "time", "t_min", "tmin", "travel_time",
                    "traveltime", "time_minutes", "tempo_min", "tempo", "tt"],
}

def find_column(df, field_key, aliases_dict=None):
    """Cerca una colonna nel DataFrame usando il dizionario di alias (case-insensitive)."""
    cols_upper = {c.upper(): c for c in df.columns}
    candidates = (aliases_dict or COLUMN_ALIASES).get(field_key.upper(), [field_key])
    for candidate in candidates:
        clean = candidate.upper().replace("(", "").replace(")", "").replace(" ", "")
        # Cerca esatta
        if clean in cols_upper:
            return cols_upper[clean]
        # Cerca parziale
        for col_up, col_orig in cols_upper.items():
            if clean in col_up:
                return col_orig
    return None


def load_shapefile_as_dataframe(filepath, description=""):
    """Carica uno shapefile come DataFrame pandas (senza dipendenza da geopandas completo)."""
    try:
        import geopandas as gpd
        gdf = gpd.read_file(filepath)
        print(f"  [OK] {description}: {len(gdf)} record, colonne: {list(gdf.columns)}")
        # Converti a DataFrame normale con coordinate centroide per la geometria
        df = pd.DataFrame(gdf.drop(columns=["geometry"], errors="ignore"))
        # Aggiungi coordinate X/Y se geometria disponibile
        if hasattr(gdf, "geometry") and gdf.geometry is not None:
            try:
                df["_X"] = gdf.geometry.centroid.x
                df["_Y"] = gdf.geometry.centroid.y
            except Exception:
                pass
        return df
    except ImportError:
        # Fallback con shapefile via pyshp
        try:
            import shapefile
            sf = shapefile.Reader(filepath)
            fields = [f[0] for f in sf.fields[1:]]
            records = [r.record for r in sf.shapeRecords()]
            df = pd.DataFrame(records, columns=fields)
            print(f"  [OK] {description}: {len(df)} record (via pyshp)")
            return df
        except Exception as e2:
            raise ImportError(f"Impossibile caricare {filepath}: installa geopandas o pyshp.\n{e2}")


def load_visum_network(network_dir, file_prefix=None, config=None):
    """
    Carica la rete Visum da shapefile esportati.

    Ritorna:
        links_df, nodes_df, centroids_df, connectors_df (DataFrame pandas)
    """
    if config is None:
        config = {}

    network_path = Path(network_dir)
    if not network_path.exists():
        raise FileNotFoundError(f"Cartella rete non trovata: {network_dir}")

    def find_shp(pattern):
        files = list(network_path.glob(pattern))
        return files[0] if files else None

    # Auto-detect prefisso
    if file_prefix:
        link_file      = network_path / f"{file_prefix}_link.shp"
        node_file      = network_path / f"{file_prefix}_node.shp"
        centroid_file  = network_path / f"{file_prefix}_zone_centroid.shp"
        connector_file = network_path / f"{file_prefix}_connector.shp"
    else:
        link_file      = find_shp("*_link.shp") or find_shp("*link*.shp")
        node_file      = find_shp("*_node.shp") or find_shp("*node*.shp")
        centroid_file  = find_shp("*_zone_centroid.shp") or find_shp("*centroid*.shp") \
                         or find_shp("*zone*.shp")
        connector_file = find_shp("*_connector.shp") or find_shp("*connector*.shp")

    print(f"\nFile shapefile trovati in {network_path}:")
    for label, f in [("Link", link_file), ("Node", node_file),
                     ("Centroide", centroid_file), ("Connettore", connector_file)]:
        print(f"  {label}: {Path(f).name if f else '-- NON TROVATO --'}")

    if not link_file or not Path(link_file).exists():
        raise FileNotFoundError(f"File _link.shp non trovato in {network_dir}")

    links_df      = load_shapefile_as_dataframe(link_file,      "Link")
    nodes_df      = load_shapefile_as_dataframe(node_file,      "Node")      if node_file      and Path(node_file).exists()      else None
    centroids_df  = load_shapefile_as_dataframe(centroid_file,  "Centroide") if centroid_file  and Path(centroid_file).exists()  else None
    connectors_df = load_shapefile_as_dataframe(connector_file, "Connettore")if connector_file and Path(connector_file).exists() else None

    return links_df, nodes_df, centroids_df, connectors_df


# =============================================================================
# PARSING VALORI VISUM CON UNITA
# =============================================================================

def parse_visum_value(val):
    """
    Parsa un valore Visum che puo contenere un'unita di misura.
    Ritorna (float_value, unit_str).

    Esempi:
        "50km/h"  -> (50.0, "km/h")
        "0.041km" -> (0.041, "km")
        "1500m"   -> (1500.0, "m")
        "2200"    -> (2200.0, "")
        50        -> (50.0, "")
    """
    import re
    if val is None:
        return 0.0, ""
    if isinstance(val, (int, float)):
        return float(val), ""
    s = str(val).strip()
    m = re.match(r'^([+-]?[\d]*\.?[\d]+(?:[eE][+-]?\d+)?)\s*([a-zA-Z/]*)\s*$', s)
    if m:
        try:
            return float(m.group(1)), m.group(2).lower().strip()
        except ValueError:
            pass
    try:
        return float(s), ""
    except ValueError:
        return 0.0, ""


def length_to_meters(val):
    """
    Converte un valore di lunghezza Visum in METRI.
    Gestisce automaticamente suffissi: "0.041km" -> 41.0, "1500m" -> 1500.0.
    Senza unita assume gia in km (unita interna Visum).
    """
    v, unit = parse_visum_value(val)
    if unit in ("km", "kilometer", "kilometres", "kilometre", ""):
        # Visum esporta di default in km; senza unita e probabile sia km
        return v * 1000.0
    elif unit in ("m", "meter", "metres", "metre"):
        return v
    else:
        # fallback: se il valore sembra essere gia in metri (es. >100) lascialo
        return v * 1000.0 if v < 100 else v


def speed_to_kmh(val):
    """
    Converte un valore di velocita Visum in km/h.
    Gestisce: "50km/h" -> 50.0, "31mph" -> 49.9, "50" -> 50.0.
    """
    v, unit = parse_visum_value(val)
    if unit in ("mph",):
        return v * 1.60934
    if unit in ("m/s", "ms"):
        return v * 3.6
    return v  # km/h e il default Visum


# =============================================================================
# COSTRUZIONE GRAFO NETWORKX
# =============================================================================

def build_graph(links_df, connectors_df, centroids_df, config):
    """
    Costruisce un grafo networkx.DiGraph dalla rete Visum.

    Nodi centroide: -zone_no  (negativi per non collidere con nodi rete)
    Nodi rete:       node_no  (positivi)

    Attributi degli archi:
        t0        : tempo di percorrenza (MINUTI), calcolato da V0PRT + LENGTH
        length    : lunghezza (METRI)
        v0prt     : velocita libera (km/h), dal campo V0PRT shapefile
        linktype  : numero tipo link (int)
        is_connector: bool

    NOTA: T0_PRTSYS non viene esportato di default da Visum.
          Il T0 viene calcolato come: (LENGTH_km / V0PRT_kmh) * 60 [minuti]
    """
    import networkx as nx

    G = nx.DiGraph()

    # --------------- NOMI COLONNE LINKS ---------------
    v0prt_col = find_column(links_df, config.get("v0prt_field", "V0PRT"))
    len_col   = find_column(links_df, config.get("length_field", "LENGTH"))
    type_col  = find_column(links_df, config.get("linktype_field", "TYPENO"))
    from_col  = find_column(links_df, config.get("fromnodeno_field", "FROMNODENO"))
    to_col    = find_column(links_df, config.get("tonodeno_field", "TONODENO"))

    missing = [(name, key) for name, key in [
        ("V0PRT", v0prt_col), ("Length", len_col), ("LinkType", type_col),
        ("FromNode", from_col), ("ToNode", to_col)
    ] if key is None]
    if missing:
        print(f"  [!] Colonne non trovate (verifica i nomi nei shapefile): {missing}")
        print(f"  Colonne disponibili: {list(links_df.columns)}")

    print(f"\n  Colonne link: V0PRT={v0prt_col}, Length={len_col}, Type={type_col}, "
          f"From={from_col}, To={to_col}")
    print(f"  T0 calcolato da: (LENGTH_km / V0PRT_kmh) x 60  [minuti]")

    # Mostra esempi di parsing dalla prima riga valida
    sample_row = links_df.iloc[0] if len(links_df) > 0 else None
    if sample_row is not None:
        s_len = sample_row[len_col] if len_col else "?"
        s_v0  = sample_row[v0prt_col] if v0prt_col else "?"
        s_len_m = length_to_meters(s_len) if len_col else 0.0
        s_v0_kmh = speed_to_kmh(s_v0) if v0prt_col else 0.0
        s_t0 = (s_len_m / 1000.0 / max(s_v0_kmh, 0.001)) * 60.0 if s_v0_kmh > 0 else 0.0
        print(f"  Esempio prima riga: LENGTH={s_len!r} -> {s_len_m:.1f}m, "
              f"V0PRT={s_v0!r} -> {s_v0_kmh:.1f}km/h, T0_calc={s_t0:.4f}min")

    # --------------- AGGIUNGI ARCHI RETE ---------------
    link_count = 0
    skipped = 0
    for _, row in links_df.iterrows():
        try:
            fn = int(row[from_col]) if from_col else None
            tn = int(row[to_col])   if to_col   else None
            if fn is None or tn is None:
                skipped += 1
                continue

            length = length_to_meters(row[len_col])  if len_col   else 0.0
            v0     = speed_to_kmh(row[v0prt_col])    if v0prt_col else 50.0
            lt     = int(row[type_col])               if type_col  else 0

            # T0 = (length_km / v0_kmh) * 60 min
            if v0 > 0 and length > 0:
                t0 = (length / 1000.0 / v0) * 60.0
            elif length > 0:
                t0 = (length / 1000.0 / 50.0) * 60.0  # fallback 50 km/h
            else:
                t0 = 0.001  # evita T0=0 (loop infinito in Dijkstra)

            G.add_edge(fn, tn,
                       t0=t0,
                       length=length,
                       v0prt=v0,
                       linktype=lt,
                       is_connector=False)
            link_count += 1
        except (TypeError, ValueError, KeyError):
            skipped += 1
            continue

    print(f"  Archi rete aggiunti: {link_count}  (saltati: {skipped})")

    # --------------- AGGIUNGI CONNETTORI ---------------
    connector_count = 0
    if connectors_df is not None:
        zone_col = find_column(connectors_df, "ZONENO")
        node_col = find_column(connectors_df, "NODENO")
        # Connettori: cerca T0_PRTSYS diretto (a volte esportato), poi fallback a V0PRT+LENGTH
        t0_conn_col = find_column(connectors_df, "T0_PRTSYS")

        if zone_col is None:
            zone_col = next((c for c in connectors_df.columns
                             if "ZONE" in c.upper() or "BEZIRK" in c.upper()), None)
        if node_col is None:
            node_col = next((c for c in connectors_df.columns
                             if "NODE" in c.upper() or "KNOTEN" in c.upper()), None)

        if zone_col and node_col:
            for _, row in connectors_df.iterrows():
                try:
                    zone_id = int(row[zone_col])
                    node_id = int(row[node_col])
                    # Connettori: prova a leggere T0 direttamente se presente,
                    # altrimenti calcola da V0PRT+LENGTH (o usa 0.0 se assenti)
                    if t0_conn_col and pd.notna(row.get(t0_conn_col, None)):
                        t0_c = float(row[t0_conn_col]) / 60.0  # secondi -> minuti
                    else:
                        # Prova V0PRT + LENGTH per il connettore
                        v0_conn_col  = find_column(connectors_df, config.get("v0prt_field", "V0PRT"))
                        len_conn_col = find_column(connectors_df, config.get("length_field", "LENGTH"))
                        if v0_conn_col and len_conn_col:
                            len_c = length_to_meters(row[len_conn_col])
                            v0_c  = speed_to_kmh(row[v0_conn_col])
                            t0_c  = (len_c / 1000.0 / max(v0_c, 1.0)) * 60.0 if v0_c > 0 else 0.0
                        else:
                            t0_c = 0.0

                    centroid_node = -zone_id  # nodo centroide (negativo)

                    # Connettori bidirezionali
                    G.add_edge(centroid_node, node_id,
                               t0=max(t0_c, 0.0), length=0.0,
                               linktype=-1, is_connector=True)
                    G.add_edge(node_id, centroid_node,
                               t0=max(t0_c, 0.0), length=0.0,
                               linktype=-1, is_connector=True)
                    connector_count += 1
                except (TypeError, ValueError, KeyError):
                    continue
        else:
            print(f"  [!] Connettori: colonne ZONENO/NODENO non trovate. "
                  f"Colonne disponibili: {list(connectors_df.columns)}")

    print(f"  Connettori aggiunti: {connector_count} zone ({connector_count*2} archi)")
    print(f"\n  Grafo finale: {G.number_of_nodes()} nodi, {G.number_of_edges()} archi")

    return G


# =============================================================================
# CALCOLO SHORTEST PATH (SKIM O/D)
# =============================================================================

def get_centroid_ids(centroids_df, connectors_df=None):
    """Ricava la lista di ID zone/centroidi."""
    centroid_ids = []

    if centroids_df is not None:
        id_col = (find_column(centroids_df, "ZONENO")
                  or next((c for c in centroids_df.columns
                            if c.upper() in ["NO", "ZONENO", "BEZIRKNO"]), None)
                  or centroids_df.columns[0])
        centroid_ids = sorted(centroids_df[id_col].dropna().astype(int).tolist())

    elif connectors_df is not None:
        zone_col = find_column(connectors_df, "ZONENO")
        if zone_col:
            centroid_ids = sorted(connectors_df[zone_col].dropna().astype(int).unique().tolist())

    return centroid_ids


def compute_od_skims(G, centroid_ids, weight="t0", verbose=True,
                     od_filter=None):
    """
    Calcola shortest path da ogni centroide a tutti gli altri.

    Args:
        od_filter : set di tuple (orig_zone, dest_zone) da calcolare.
                    Se None -> calcola tutte le coppie (comportamento precedente).
                    Se fornito -> Dijkstra solo per le origini presenti nel filtro,
                    e memorizza solo i percorsi verso le destinazioni richieste.
                    Riduce drasticamente tempo e memoria su reti grandi.

    Ritorna:
        od_times  : dict {(orig_zone, dest_zone): tempo_minuti}
        od_paths  : dict {(orig_zone, dest_zone): [nodi_percorso]}
    """
    import networkx as nx

    n = len(centroid_ids)
    centroid_nodes = [-z for z in centroid_ids]

    # Verifica quali centroidi sono effettivamente nel grafo
    valid_centroids = [(z, -z) for z in centroid_ids if -z in G]
    if len(valid_centroids) < len(centroid_ids):
        print("  [!] {} centroidi non trovati nel grafo "
              "(mancano connettori?)".format(len(centroid_ids) - len(valid_centroids)))

    # Se od_filter e' fornito, calcola solo le origini necessarie
    if od_filter is not None:
        needed_origins = {o for o, d in od_filter}
        needed_by_origin = {}
        for o, d in od_filter:
            needed_by_origin.setdefault(o, set()).add(d)
        origins_to_run = [(z, -z) for z, _ in valid_centroids if z in needed_origins]
        dest_lookup    = {z: -z for z, _ in valid_centroids}
        mode_label     = "filtrato ({} origini, {} coppie)".format(
            len(origins_to_run), len(od_filter))
    else:
        origins_to_run  = valid_centroids
        needed_by_origin = None
        dest_lookup      = {z: -z for z, _ in valid_centroids}
        n_valid = len(valid_centroids)
        mode_label = "{} origini x {} dest = {:,} coppie".format(
            n_valid, n_valid, n_valid * (n_valid - 1))

    od_times = {}
    od_paths = {}
    n_run = len(origins_to_run)

    if verbose:
        print("\n  Calcolo shortest path: {}".format(mode_label))

    for i, (zone_id, centroid_node) in enumerate(origins_to_run):
        if verbose and i % max(1, n_run // 10) == 0:
            print("  Origine {}/{} (zona {})...".format(i + 1, n_run, zone_id))

        try:
            lengths, paths = nx.single_source_dijkstra(G, centroid_node, weight=weight)
        except Exception:
            continue

        # Destinazioni da salvare per questa origine
        dest_zones = needed_by_origin[zone_id] if needed_by_origin else \
                     [z for z, _ in valid_centroids if z != zone_id]

        for dest_zone in dest_zones:
            dest_node = dest_lookup.get(dest_zone)
            if dest_node is None:
                continue
            if dest_node in lengths and lengths[dest_node] < 1e9:
                od_times[(zone_id, dest_zone)] = lengths[dest_node]
                od_paths[(zone_id, dest_zone)] = paths[dest_node]

    if verbose:
        print("  Coppie OD con percorso valido: {:,}".format(len(od_times)))

    return od_times, od_paths


# =============================================================================
# MATRICE COMPOSIZIONE LINKTYPE
# =============================================================================

def build_composition_matrix(G, od_paths_subset, linktype_list):
    """
    Costruisce la matrice D (n_od x n_linktypes):
        D[i, k] = lunghezza totale (m) di archi di tipo k nel percorso OD i

    Nota: connettori (linktype=-1) sono esclusi automaticamente.

    Ritorna:
        D        : np.ndarray (n_od x n_linktypes)
        od_order : lista di coppie (orig, dest) nell'ordine delle righe
    """
    type_index = {lt: j for j, lt in enumerate(linktype_list)}
    od_order   = list(od_paths_subset.keys())
    n_od       = len(od_order)
    n_types    = len(linktype_list)

    D = np.zeros((n_od, n_types), dtype=np.float64)

    for i, od_key in enumerate(od_order):
        path = od_paths_subset[od_key]
        for u, v in zip(path[:-1], path[1:]):
            if not G.has_edge(u, v):
                continue
            edge = G[u][v]
            lt     = edge.get("linktype", -1)
            length = edge.get("length", 0.0)
            if lt in type_index and length > 0:
                D[i, type_index[lt]] += length

    return D, od_order


# =============================================================================
# OTTIMIZZAZIONE: BOUNDED LEAST SQUARES (lsq_linear)
# =============================================================================

def compute_metrics(T_pred_min, T_obs):
    """
    Calcola metriche di confronto tra tempi modello e osservati.
    R2 e slope sono per regressione PASSANTE PER L'ORIGINE (no intercetta):
        T_model = slope * T_obs
        R2 = 1 - SS_res / SS_tot   dove SS_tot = sum(T_obs^2)  (non varianza!)
        slope = sum(T_pred * T_obs) / sum(T_obs^2)
    """
    residuals = T_pred_min - T_obs
    SS_res = float(np.sum(residuals ** 2))
    SS_tot = float(np.sum(T_obs ** 2))          # passante per origine
    r2     = 1.0 - SS_res / max(SS_tot, 1e-12)
    slope  = float(np.sum(T_pred_min * T_obs) / max(SS_tot, 1e-12))
    rmse   = float(np.sqrt(np.mean(residuals ** 2)))
    mae    = float(np.mean(np.abs(residuals)))
    mape   = float(np.mean(np.abs(residuals / (T_obs + 1e-3))) * 100)
    return {
        "rmse": rmse, "mae": mae, "r2": r2, "slope": slope, "mape": mape,
        "residuals": residuals.tolist(),
    }


def compute_speed_bounds(linktype_list, initial_speeds,
                         delta_v=10.0, v_min=10.0, v_max=150.0, gap=1.0):
    """
    Calcola i bounds di velocita per ogni LinkType:
      - Ogni tipo puo variare al massimo +-delta_v km/h dalla sua velocita iniziale
      - Il gap minimo tra classi adiacenti (ordinate per velocita) e' preservato
        (nessuna classe puo "scavalcare" un'altra)
      - Garantisce sempre lb < ub (minimo MIN_WIDTH km/h di ampiezza)

    Ritorna:
        speed_bounds : dict {linktype: (lb_kmh, ub_kmh)}
    """
    MIN_WIDTH = 0.5   # km/h: ampiezza minima assoluta del range per ogni tipo

    # Ordina per velocita iniziale crescente
    sorted_lt = sorted(linktype_list, key=lambda lt: initial_speeds.get(lt, 50.0))
    n = len(sorted_lt)

    lb = np.array([max(initial_speeds.get(lt, 50.0) - delta_v, v_min) for lt in sorted_lt],
                  dtype=float)
    ub = np.array([min(initial_speeds.get(lt, 50.0) + delta_v, v_max) for lt in sorted_lt],
                  dtype=float)

    # Garanzia iniziale: ub >= lb + MIN_WIDTH
    for i in range(n):
        if ub[i] < lb[i] + MIN_WIDTH:
            mid = (lb[i] + ub[i]) / 2.0
            lb[i] = max(mid - MIN_WIDTH / 2.0, v_min)
            ub[i] = lb[i] + MIN_WIDTH

    # Applica vincolo di non-sovrapposizione: ub[k] < lb[k+1] (con gap)
    for k in range(n - 1):
        if ub[k] >= lb[k + 1] - gap:
            v_k   = initial_speeds.get(sorted_lt[k],     50.0)
            v_k1  = initial_speeds.get(sorted_lt[k + 1], 50.0)
            mid   = (v_k + v_k1) / 2.0
            # Taglia solo quanto necessario per aprire il gap
            new_ub_k   = min(ub[k],     mid - gap / 2.0)
            new_lb_k1  = max(lb[k + 1], mid + gap / 2.0)
            # Applica solo se non crea lb >= ub
            if new_ub_k > lb[k] + MIN_WIDTH:
                ub[k] = new_ub_k
            if new_lb_k1 < ub[k + 1] - MIN_WIDTH:
                lb[k + 1] = new_lb_k1

    # Passata finale: assicura lb + MIN_WIDTH <= ub per ogni tipo
    for i in range(n):
        if ub[i] < lb[i] + MIN_WIDTH:
            # Apri il range simmetricamente attorno alla velocita iniziale
            v0 = initial_speeds.get(sorted_lt[i], 50.0)
            lb[i] = max(v0 - MIN_WIDTH / 2.0, v_min)
            ub[i] = max(lb[i] + MIN_WIDTH,
                        min(v0 + MIN_WIDTH / 2.0, v_max))
            lb[i] = ub[i] - MIN_WIDTH  # riallinea

    return {lt: (float(lb[i]), float(ub[i])) for i, lt in enumerate(sorted_lt)}


def optimize_speeds_lsq(D, T_obs, linktype_list,
                        v_min=10.0, v_max=150.0,
                        initial_speeds=None,
                        speed_bounds=None):
    """
    Risolve il problema di ottimizzazione velocita con scipy.optimize.lsq_linear.

    Modello lineare (beta_k = 1/speed_k in h/km):
        T_od [min] = sum_k  D_od_k [km] *  beta_k [h/km] * 60
        -> T_od/60 = D_km @ beta   -> risolvi lsq_linear

    Bounds:
      Se speed_bounds fornito: usa bounds per-tipo {lt: (lb_kmh, ub_kmh)}
      Altrimenti: bounds globali [v_min, v_max]

    R2 e slope calcolati per regressione PASSANTE PER L'ORIGINE.
    """
    from scipy.optimize import lsq_linear

    n_od, n_types = D.shape
    D_km     = D / 1000.0
    T_obs_h  = T_obs / 60.0

    # Bounds per-tipo o globali
    if speed_bounds:
        lb = np.array([1.0 / max(speed_bounds.get(lt, (v_min, v_max))[1], 0.01)
                       for lt in linktype_list])
        ub = np.array([1.0 / max(speed_bounds.get(lt, (v_min, v_max))[0], 0.01)
                       for lt in linktype_list])
    else:
        lb = np.full(n_types, 1.0 / v_max)
        ub = np.full(n_types, 1.0 / v_min)

    # Rimuovi LinkType non usati (colonne all-zero)
    col_norms = np.linalg.norm(D_km, axis=0)
    active    = col_norms > 1e-6
    inactive_types = [linktype_list[j] for j in range(n_types) if not active[j]]
    if inactive_types:
        print("  [i] LinkType non presenti nei percorsi: {}".format(inactive_types))

    D_active  = D_km[:, active]
    lb_active = lb[active]
    ub_active = ub[active]

    # Sicurezza: garantisce lb < ub in modo STRETTO (richiesto da scipy lsq_linear)
    EPS_BETA = 1e-6   # differenza minima in spazio beta
    bad = lb_active >= ub_active - EPS_BETA
    if np.any(bad):
        n_bad = int(np.sum(bad))
        print("  [!] {} tipo/i con bounds degenerati (lb~=ub) -> margine forzato".format(n_bad))
        # Apri verso il basso: sposta lb
        lb_active = np.where(bad, ub_active - EPS_BETA * 100, lb_active)
        # Se ub era al limite inferiore assoluto, apri verso l'alto: sposta ub
        still_bad = lb_active >= ub_active - EPS_BETA
        ub_active[still_bad] = lb_active[still_bad] + EPS_BETA * 100

    print("\n  lsq_linear: {} coppie OD x {} LinkType attivi".format(n_od, int(np.sum(active))))
    if speed_bounds:
        print("  Bounds per-tipo (+-{:.0f} km/h con ordinamento preservato):".format(
            list(speed_bounds.values())[0][1] - list(speed_bounds.values())[0][0] if speed_bounds else 0))
        for lt in sorted(linktype_list):
            if lt in speed_bounds:
                lo, hi = speed_bounds[lt]
                v_init = initial_speeds.get(lt, 50.0) if initial_speeds else 50.0
                print("    Type {:3d}: [{:.1f}, {:.1f}] km/h  (init={:.1f})".format(
                    lt, lo, hi, v_init))

    result = lsq_linear(
        D_active, T_obs_h,
        bounds=(lb_active, ub_active),
        method="bvls",
        verbose=0,
        max_iter=5000,
    )

    # Ricostruisci vettore beta completo
    beta_full = np.full(n_types, 1.0 / 50.0)
    j = 0
    for i in range(n_types):
        if active[i]:
            beta_full[i] = result.x[j]
            j += 1
        elif initial_speeds:
            lt = linktype_list[i]
            v0 = initial_speeds.get(lt, 50.0)
            beta_full[i] = 1.0 / max(v0, 1.0)

    speeds_opt = {linktype_list[i]: round(1.0 / beta_full[i], 2) for i in range(n_types)}

    # Metriche (R2 e slope passanti per l'origine)
    T_pred_min = D_km @ beta_full * 60.0
    metrics = compute_metrics(T_pred_min, T_obs)

    print("  RMSE: {:.3f} min  |  MAE: {:.3f} min  |  "
          "R2(origin): {:.4f}  |  slope: {:.4f}  |  MAPE: {:.2f}%".format(
              metrics["rmse"], metrics["mae"], metrics["r2"],
              metrics["slope"], metrics["mape"]))

    metrics["n_od"] = n_od
    metrics["n_types_active"] = int(np.sum(active))
    return speeds_opt, metrics


def get_initial_speeds_from_graph(G, linktype_list):
    """
    Ricava le velocita iniziali (km/h per LinkType) dal grafo.
    Priorita:
        1. Media pesata di v0prt (se presente come attributo arco)
        2. Calcolata da length/T0
        3. Default 50 km/h
    """
    type_v0_sum    = {lt: 0.0 for lt in linktype_list}
    type_v0_count  = {lt: 0   for lt in linktype_list}
    type_lengths   = {lt: 0.0 for lt in linktype_list}
    type_times     = {lt: 0.0 for lt in linktype_list}

    for _, _, data in G.edges(data=True):
        lt     = data.get("linktype", -1)
        length = data.get("length", 0.0)
        t0     = data.get("t0", 0.0)
        v0prt  = data.get("v0prt", None)   # dal campo V0PRT shapefile
        if lt not in type_v0_sum:
            continue
        if v0prt is not None and v0prt > 0:
            type_v0_sum[lt]   += v0prt
            type_v0_count[lt] += 1
        if length > 0 and t0 > 0:
            type_lengths[lt] += length
            type_times[lt]   += t0

    speeds = {}
    for lt in linktype_list:
        if type_v0_count[lt] > 0:
            # Media aritmetica di V0PRT (velocita di progetto del LinkType)
            speeds[lt] = round(type_v0_sum[lt] / type_v0_count[lt], 2)
        elif type_times[lt] > 0:
            # Fallback: v = (length_m / 1000) / (t0_min / 60)  [km/h]
            speeds[lt] = round((type_lengths[lt] / 1000.0) / (type_times[lt] / 60.0), 2)
        else:
            speeds[lt] = 50.0

    return speeds


# =============================================================================
# AGGIORNAMENTO T0 NEL GRAFO
# =============================================================================

def update_graph_t0(G, speeds_dict, fix_connectors=True):
    """
    Aggiorna i tempi T0 (minuti) nel grafo in base alle nuove velocita (km/h).
        T0 [min] = (length [m] / 1000 / speed [km/h]) * 60
    Connettori (linktype=-1) sono ignorati se fix_connectors=True.
    """
    updated = 0
    for u, v, data in G.edges(data=True):
        lt     = data.get("linktype", -1)
        length = data.get("length", 0.0)
        is_con = data.get("is_connector", False)

        if fix_connectors and is_con:
            continue
        if lt < 0 or lt not in speeds_dict:
            continue
        if length <= 0:
            continue

        new_speed = speeds_dict[lt]
        data["t0"] = (length / 1000.0 / new_speed) * 60.0
        updated += 1

    return updated


# =============================================================================
# PER-ARC MODE: matrice composizione e funzioni specifiche
# =============================================================================

def build_composition_matrix_per_arc(G, od_paths_subset, max_arcs=None,
                                      exclude_arcs=None):
    """
    Costruisce la matrice sparsa D (n_od x n_archi_attivi):
        D[i, j] = lunghezza in metri dell'arco j nel percorso OD i

    Esclude automaticamente i connettori.
    Se exclude_arcs e' fornito (set di tuple (u,v)), quegli archi vengono saltati.
    Se max_arcs e' specificato, mantiene solo i max_arcs archi con piu'
    km totali percorsi (i piu' importanti per l'ottimizzazione).

    Ritorna:
        D_sparse     : scipy.sparse.csr_matrix  (n_od x n_archi)
        arc_list     : lista di tuple (u, v) nell'ordine delle colonne
        od_order     : lista di coppie OD nell'ordine delle righe
        arc_coverage : {(u,v): km_totali} per tutti gli archi candidati
    """
    from scipy.sparse import lil_matrix, csr_matrix

    _excl = exclude_arcs or set()

    # Raccoglie tutti gli archi (non connettori, non esclusi) presenti in almeno un percorso
    arc_set = set()
    for path in od_paths_subset.values():
        for u, v in zip(path[:-1], path[1:]):
            if (u, v) in _excl:
                continue
            if G.has_edge(u, v) and not G[u][v].get("is_connector", False):
                arc_set.add((u, v))

    # Calcola copertura (km totali) per tutti gli archi candidati
    arc_coverage = {}
    for path in od_paths_subset.values():
        for u, v in zip(path[:-1], path[1:]):
            if (u, v) in arc_set:
                length = G[u][v].get("length", 0.0) if G.has_edge(u, v) else 0.0
                arc_coverage[(u, v)] = arc_coverage.get((u, v), 0.0) + length

    # Se richiesto, tieni solo i max_arcs piu' coperti (maggior volume totale)
    if max_arcs and len(arc_set) > max_arcs:
        top_arcs = sorted(arc_coverage, key=lambda a: arc_coverage[a], reverse=True)[:max_arcs]
        arc_set = set(top_arcs)
        print("  [i] Archi limitati ai top {} piu' percorsi (su {} candidati)".format(
            max_arcs, len(arc_coverage)))

    arc_list  = sorted(arc_set)
    arc_index = {arc: j for j, arc in enumerate(arc_list)}
    od_order  = list(od_paths_subset.keys())
    n_od      = len(od_order)
    n_arcs    = len(arc_list)

    D = lil_matrix((n_od, n_arcs), dtype=np.float64)
    for i, od_key in enumerate(od_order):
        path = od_paths_subset[od_key]
        for u, v in zip(path[:-1], path[1:]):
            if not G.has_edge(u, v):
                continue
            edge = G[u][v]
            if edge.get("is_connector", False):
                continue
            length = edge.get("length", 0.0)
            if length > 0 and (u, v) in arc_index:
                D[i, arc_index[(u, v)]] += length

    return csr_matrix(D), arc_list, od_order, arc_coverage


def optimize_speeds_per_arc(D_sparse, T_obs, arc_list, arc_initial_speeds,
                            delta_v=20.0, v_min=10.0, v_max=150.0):
    """
    Ottimizzazione per-arco:
        T_od [min] = sum_j  D_j [km] * beta_j [h/km] * 60
        beta_j = 1 / v_j

    Bounds per arco: +- delta_v km/h dalla velocita iniziale dell'arco.

    Strategia solvente:
      - Matrice densa (n_od * n_arcs <= DENSE_LIMIT): converti e usa bvls (piu' veloce)
      - Matrice sparsa grande: usa trf con lsmr (solver iterativo, veloce su sparso)
    """
    from scipy.optimize import lsq_linear
    from scipy.sparse import issparse

    DENSE_LIMIT = 4_000_000   # celle: se n_od*n_arcs <= 4M usa dense+bvls

    n_od, n_arcs = D_sparse.shape
    D_km    = D_sparse / 1000.0
    T_obs_h = T_obs / 60.0

    # Bounds per arco in spazio beta (beta = 1/v)
    EPS = 1e-6
    lb = np.array([
        1.0 / min(arc_initial_speeds.get(arc, 50.0) + delta_v, v_max)
        for arc in arc_list
    ], dtype=np.float64)
    ub = np.array([
        1.0 / max(arc_initial_speeds.get(arc, 50.0) - delta_v, v_min)
        for arc in arc_list
    ], dtype=np.float64)

    # Garanzia lb < ub stretto
    bad = lb >= ub - EPS
    if np.any(bad):
        lb[bad] = np.maximum(ub[bad] - EPS * 100, 0.0)
        still_bad = lb >= ub - EPS
        ub[still_bad] = lb[still_bad] + EPS * 100

    # Scelta solver
    use_dense = (n_od * n_arcs <= DENSE_LIMIT)
    if use_dense:
        D_solve = np.array(D_km.todense()) if issparse(D_km) else D_km
        method  = "bvls"
        lsq_solver = None
        max_iter = 5000
    else:
        D_solve = D_km   # sparsa
        method  = "trf"
        lsq_solver = "lsmr"   # solver iterativo: veloce su matrici sparse grandi
        max_iter = 500    # trf converge in poche iterazioni esterne

    sparse_mb = D_km.data.nbytes / 1e6 if issparse(D_km) else D_km.nbytes / 1e6
    print("  lsq_linear per-arco: {} OD x {} archi  "
          "({:.1f} MB sparso)  solver={}/{}".format(
              n_od, n_arcs, sparse_mb, method,
              lsq_solver if lsq_solver else "default"))

    kwargs = dict(bounds=(lb, ub), method=method, verbose=0, max_iter=max_iter)
    if lsq_solver:
        kwargs["lsq_solver"] = lsq_solver

    result = lsq_linear(D_solve, T_obs_h, **kwargs)

    beta = result.x
    speeds_opt = {arc: round(1.0 / max(beta[j], 1e-8), 2)
                  for j, arc in enumerate(arc_list)}

    # Metriche
    if issparse(D_km):
        T_pred_h = np.array(D_km.dot(beta)).flatten()
    else:
        T_pred_h = D_km @ beta
    T_pred_min = T_pred_h * 60.0
    metrics = compute_metrics(T_pred_min, T_obs)
    metrics["n_od"]          = n_od
    metrics["n_arcs_active"] = n_arcs

    print("  RMSE: {:.3f} min  |  MAE: {:.3f} min  |  "
          "R2(origin): {:.4f}  |  slope: {:.4f}  |  MAPE: {:.2f}%".format(
              metrics["rmse"], metrics["mae"], metrics["r2"],
              metrics["slope"], metrics["mape"]))
    return speeds_opt, metrics


def snap_arc_to_type(v_opt, v_orig, type_speeds, delta_v=20.0):
    """
    Trova il tipo ammissibile la cui velocita e' piu' vicina a v_opt.
    Ammissibile = |v_type - v_orig| <= delta_v.
    """
    admissible = {lt: v for lt, v in type_speeds.items()
                  if abs(v - v_orig) <= delta_v}
    if not admissible:
        admissible = type_speeds  # fallback: tutti i tipi
    best_lt = min(admissible, key=lambda lt: abs(admissible[lt] - v_opt))
    return best_lt, type_speeds[best_lt]


def update_graph_types(G, arc_assignments, type_speeds, fix_connectors=True):
    """
    Aggiorna linktype e T0 di ogni arco in base al tipo assegnato.
        arc_assignments : {(u, v): new_linktype}
        type_speeds     : {linktype: speed_kmh}
    """
    updated = 0
    for (u, v), new_lt in arc_assignments.items():
        if not G.has_edge(u, v):
            continue
        data = G[u][v]
        if fix_connectors and data.get("is_connector", False):
            continue
        length    = data.get("length", 0.0)
        new_speed = type_speeds.get(new_lt, 50.0)
        data["linktype"] = new_lt
        data["v0prt"]    = new_speed
        if length > 0:
            data["t0"] = (length / 1000.0 / new_speed) * 60.0
        updated += 1
    return updated


def update_graph_arc_speeds(G, arc_opt_speeds, fix_connectors=True):
    """
    Applica velocita' continue ottimali direttamente al T0 di ogni arco,
    SENZA cambiare il linktype. Usato durante i sub-cycles per evitare la
    perdita di informazione dovuta allo snap al tipo piu' vicino.
        arc_opt_speeds : {(u, v): speed_kmh}  velocita' continua ottimale
    """
    updated = 0
    for (u, v), v_new in arc_opt_speeds.items():
        if not G.has_edge(u, v):
            continue
        data = G[u][v]
        if fix_connectors and data.get("is_connector", False):
            continue
        length = data.get("length", 0.0)
        if length > 0 and v_new > 0:
            data["v0prt"] = v_new
            data["t0"]    = (length / 1000.0 / v_new) * 60.0
            updated += 1
    return updated


def recompute_od_times_from_paths(G, od_paths):
    """
    Ricalcola i tempi OD sommando G[u][v]['t0'] lungo i percorsi gia' noti.
    Nessun Dijkstra: O(n_od * lunghezza_media_percorso). Usato dopo aggiornamento
    velocita' per aggiornare gli errori senza dover rifare shortest path.
    """
    od_times = {}
    for od, path in od_paths.items():
        t = 0.0
        for u, v in zip(path[:-1], path[1:]):
            if G.has_edge(u, v):
                t += G[u][v].get("t0", 0.0)
        od_times[od] = t
    return od_times


def run_iterative_optimization_per_arc(G, centroid_ids, T_obs_dict, linktype_list, config):
    """
    Ottimizzazione iterativa con re-routing per singolo arco.

    Per ogni iterazione:
      1. Calcola percorsi minimi con T0 corrente
      2. Costruisce matrice sparsa D (n_OD x n_archi_attivi)
      3. BVLS con bounds +-delta_v per arco -> velocita continua ottimale v*
      4. Snap: ogni arco -> tipo piu' vicino con |v_tipo - v_orig| <= delta_v
      5. Aggiorna grafo (linktype + T0)
      6. Ripete fino a convergenza (% archi riassegnati < soglia)

    Ritorna:
        best_arc_assignments : {(u,v): linktype}
        type_speeds          : {linktype: speed_kmh}  (velocita originali tipi)
        history              : lista dict per iterazione
    """
    import sys as _sys

    n_iter      = config.get("n_iterations", 10)
    conv_thresh = config.get("convergence_threshold", 0.005)
    v_min       = config.get("speed_min_kmh", 10.0)
    v_max       = config.get("speed_max_kmh", 150.0)
    delta_v     = config.get("speed_delta_arc_kmh", 20.0)
    fix_conn    = config.get("fix_connector_t0", True)
    max_arcs    = config.get("max_active_arcs", 500)
    od_frac_cfg = config.get("od_error_frac", None)   # non usato, ignorato
    slope_min   = config.get("slope_target_min", 0.9)
    slope_max   = config.get("slope_target_max", 1.1)
    r2_target   = config.get("r2_target", 0.9)

    od_pairs    = list(T_obs_dict.keys())
    type_speeds = get_initial_speeds_from_graph(G, linktype_list)

    # Velocita iniziali per singolo arco (da V0PRT o dal tipo)
    arc_initial_speeds = {}
    for u, v, data in G.edges(data=True):
        if data.get("is_connector", False):
            continue
        lt = data.get("linktype", -1)
        if lt < 0:
            continue
        v0 = data.get("v0prt", None)
        arc_initial_speeds[(u, v)] = float(v0) if v0 else type_speeds.get(lt, 50.0)

    best_arc_assignments = {
        (u, v): data.get("linktype", -1)
        for u, v, data in G.edges(data=True)
        if not data.get("is_connector", False) and data.get("linktype", -1) >= 0
    }

    history = []
    od_filter = set(od_pairs)

    print("\n" + "=" * 70)
    print("OTTIMIZZAZIONE PER ARCO - archi disgiunti tra iterazioni")
    print("=" * 70)
    print("  delta_v arco:   +- {:.1f} km/h".format(delta_v))
    print("  max archi/iter: {}".format(max_arcs))
    print("  n_iterations:   {}".format(n_iter))
    print("  Archi ottimizzabili: {}".format(len(arc_initial_speeds)))
    print("\nVelocita tipi:")
    for lt in sorted(linktype_list):
        print("  Type {:3d}: {:.1f} km/h".format(lt, type_speeds.get(lt, 50.0)))

    # ------------------------------------------------------------------ #
    # ERRORE INIZIALE                                                      #
    # ------------------------------------------------------------------ #
    print("\n" + "-" * 50)
    print("ERRORE INIZIALE (V0PRT originale)")
    print("-" * 50)
    _sys.stdout.flush()

    od_times, od_paths = compute_od_skims(
        G, centroid_ids, verbose=True, od_filter=od_filter)

    valid_ods_all = [(od, T_obs_dict[od]) for od in od_pairs if od in od_paths]
    if not valid_ods_all:
        print("  [!] Nessuna coppia OD valida - uscita")
        return best_arc_assignments, type_speeds, history

    # Errori iniziali
    od_errors = {od: abs(od_times[od] - T_obs_dict[od]) for od, _ in valid_ods_all}
    T_obs_arr0  = np.array([t for _, t in valid_ods_all])
    T_pred_arr0 = np.array([od_times[od] for od, _ in valid_ods_all])
    m0 = compute_metrics(T_pred_arr0, T_obs_arr0)
    print("  Coppie OD valide: {} / {}".format(len(valid_ods_all), len(od_pairs)))
    print("  RMSE: {:.3f} min  |  MAE: {:.3f} min  |  "
          "R2(origin): {:.4f}  |  slope: {:.4f}  |  MAPE: {:.2f}%".format(
              m0["rmse"], m0["mae"], m0["r2"], m0["slope"], m0["mape"]))
    history.append({"iteration": 0, "sub_cycle": 0, "label": "initial",
                    "n_od_used": len(valid_ods_all),
                    "max_rel_change_pct": 0.0,
                    "metrics": m0,
                    "_T_obs_arr": T_obs_arr0,
                    "_T_pred_arr": T_pred_arr0})

    print("  OD validi per BVLS: {}".format(len(valid_ods_all)))

    # Archi gia' ottimizzati nelle iterazioni precedenti (persistente)
    already_optimized = set()

    # ------------------------------------------------------------------ #
    # LOOP PRINCIPALE                                                      #
    # ------------------------------------------------------------------ #
    for iteration in range(1, n_iter + 1):
        print("\n" + "=" * 60)
        print("ITERAZIONE {} / {}".format(iteration, n_iter))
        print("=" * 60)
        _sys.stdout.flush()

        # -------------------------------------------------------------- #
        # BVLS su top max_arcs piu' percorsi, esclusi quelli gia'         #
        # ottimizzati nelle iterazioni precedenti.                        #
        # -------------------------------------------------------------- #
        if not od_paths:
            print("  [!] Nessun percorso disponibile - skip iterazione")
            continue

        full_paths = {od: od_paths[od] for od in od_pairs if od in od_paths}
        if not full_paths:
            print("  [!] Nessun percorso valido - skip iterazione")
            continue

        print("  Archi gia' ottimizzati (esclusi): {}".format(len(already_optimized)))

        D_iter, arc_list_iter, od_order_iter, _ = build_composition_matrix_per_arc(
            G, full_paths,
            max_arcs=max_arcs,
            exclude_arcs=already_optimized)

        if len(arc_list_iter) == 0:
            print("  [!] Nessun arco rimasto da ottimizzare - stop.")
            break

        T_obs_iter_bvls = np.array([T_obs_dict[od] for od in od_order_iter])
        print("  BVLS: {} OD x {} archi".format(len(od_order_iter), len(arc_list_iter)))
        _sys.stdout.flush()

        arc_opt_speeds, _ = optimize_speeds_per_arc(
            D_iter, T_obs_iter_bvls, arc_list_iter, arc_initial_speeds,
            delta_v=delta_v, v_min=v_min, v_max=v_max)

        update_graph_arc_speeds(G, arc_opt_speeds, fix_connectors=fix_conn)

        # Registra archi ottimizzati in questo giro
        already_optimized.update(arc_list_iter)

        total_arcs_touched = len(arc_list_iter)
        total_reassigned = sum(
            1 for arc in arc_list_iter
            if abs(arc_opt_speeds.get(arc, arc_initial_speeds.get(arc, 50.0))
                   - arc_initial_speeds.get(arc, 50.0)) > 0.5)
        print("  Archi modificati (>0.5 km/h): {} / {}".format(
            total_reassigned, total_arcs_touched))

        # Metrica veloce (percorsi fissi, senza Dijkstra)
        od_times_fast_all = recompute_od_times_from_paths(G, od_paths)
        valid_fast = [(od, T_obs_dict[od]) for od in od_pairs
                      if od in od_times_fast_all and od in od_paths]
        if valid_fast:
            T_obs_fast  = np.array([t for _, t in valid_fast])
            T_pred_fast = np.array([od_times_fast_all[od] for od, _ in valid_fast])
            m_fast = compute_metrics(T_pred_fast, T_obs_fast)
            print("  Metrica FAST (percorsi fissi): RMSE={:.3f}  slope={:.4f}  R2={:.4f}".format(
                m_fast["rmse"], m_fast["slope"], m_fast["r2"]))
        _sys.stdout.flush()

        # ---- Fine sub-cycles: Dijkstra completo per rotta ----
        _sys.stdout.flush()
        print("  Ricalcolo percorsi (Dijkstra completo)...")
        od_times, od_paths = compute_od_skims(
            G, centroid_ids, verbose=True, od_filter=od_filter)

        valid_ods_all = [(od, T_obs_dict[od]) for od in od_pairs if od in od_paths]
        if not valid_ods_all:
            print("  [!] Nessuna coppia OD valida - uscita anticipata")
            break

        T_obs_iter  = np.array([t for _, t in valid_ods_all])
        T_pred_iter = np.array([od_times[od] for od, _ in valid_ods_all])
        m_iter = compute_metrics(T_pred_iter, T_obs_iter)
        od_errors = {od: abs(od_times[od] - T_obs_dict[od]) for od, _ in valid_ods_all}

        # Snap finale per aggiornare best_arc_assignments (solo per report)
        for u, v, data in G.edges(data=True):
            if data.get("is_connector", False):
                continue
            v_cur  = data.get("v0prt", None)
            v_orig = arc_initial_speeds.get((u, v), None)
            if v_cur is not None and v_orig is not None:
                new_lt, _ = snap_arc_to_type(v_cur, v_orig, type_speeds, delta_v)
                best_arc_assignments[(u, v)] = new_lt

        print("  RMSE: {:.3f} min  |  MAE: {:.3f} min  |  "
              "R2(origin): {:.4f}  |  slope: {:.4f}  |  MAPE: {:.2f}%".format(
                  m_iter["rmse"], m_iter["mae"], m_iter["r2"],
                  m_iter["slope"], m_iter["mape"]))
        print("  Archi modificati: {} / {}  |  Totale ottimizzati: {}".format(
            total_reassigned, total_arcs_touched, len(already_optimized)))

        history.append({
            "iteration": iteration,
            "n_od_used": len(valid_ods_all),
            "arcs_this_iter": total_arcs_touched,
            "arcs_modified": total_reassigned,
            "arcs_optimized_total": len(already_optimized),
            "max_rel_change_pct": round(total_reassigned / max(total_arcs_touched, 1) * 100, 3),
            "metrics": m_iter,
            "_T_obs_arr": T_obs_iter,
            "_T_pred_arr": T_pred_iter,
        })

        # Convergenza su slope e R2
        slope_ok = slope_min <= m_iter["slope"] <= slope_max
        r2_ok    = m_iter["r2"] >= r2_target
        if slope_ok and r2_ok:
            print("  [OK] CONVERGENZA: slope={:.4f} in [{:.2f},{:.2f}]  R2={:.4f} >= {:.2f}".format(
                m_iter["slope"], slope_min, slope_max, m_iter["r2"], r2_target))
            break
        else:
            missing = []
            if not slope_ok:
                missing.append("slope={:.4f} fuori [{:.2f},{:.2f}]".format(
                    m_iter["slope"], slope_min, slope_max))
            if not r2_ok:
                missing.append("R2={:.4f} < {:.2f}".format(m_iter["r2"], r2_target))
            print("  [..] Non convergito: {}".format(" | ".join(missing)))

    return best_arc_assignments, type_speeds, history


# =============================================================================
# OTTIMIZZAZIONE ITERATIVA (con re-routing)
# =============================================================================

def run_iterative_optimization(G, centroid_ids, T_obs_dict, linktype_list,
                                config):
    """
    Ottimizzazione iterativa con re-routing (tipo Frank-Wolfe).
    Bounds di velocita: +-delta_v km/h dall'iniziale, ordinamento classi preservato.
    """
    n_iter      = config.get("n_iterations", 10)
    conv_thresh = config.get("convergence_threshold", 0.005)
    v_min       = config.get("speed_min_kmh", 10.0)
    v_max       = config.get("speed_max_kmh", 150.0)
    delta_v     = config.get("speed_delta_kmh", 10.0)   # max variazione per tipo
    gap         = config.get("speed_class_gap_kmh", 1.0) # gap minimo tra classi
    fix_conn    = config.get("fix_connector_t0", True)
    slope_min   = config.get("slope_target_min", 0.9)
    slope_max   = config.get("slope_target_max", 1.1)
    r2_target   = config.get("r2_target", 0.9)

    od_pairs = list(T_obs_dict.keys())

    initial_speeds = get_initial_speeds_from_graph(G, linktype_list)

    # Calcola bounds per-tipo (fissi per tutta l'ottimizzazione)
    speed_bounds = compute_speed_bounds(
        linktype_list, initial_speeds,
        delta_v=delta_v, v_min=v_min, v_max=v_max, gap=gap
    )

    current_speeds = dict(initial_speeds)  # copia
    history = []

    print("\n" + "=" * 70)
    print("OTTIMIZZAZIONE ITERATIVA VELOCITA LINKTYPE")
    print("=" * 70)
    print("\nParametri:")
    print("  delta_v max:  +- {:.1f} km/h per classe".format(delta_v))
    print("  gap min:       {:.1f} km/h tra classi adiacenti".format(gap))
    print("  n_iterazioni:  {}".format(n_iter))
    print("\nVelocita iniziali e bounds:")
    for lt in sorted(linktype_list):
        v  = initial_speeds.get(lt, 50.0)
        lo, hi = speed_bounds.get(lt, (v_min, v_max))
        print("  Type {:3d}: {:.1f} km/h  bounds=[{:.1f}, {:.1f}]".format(lt, v, lo, hi))

    # ---- ERRORE INIZIALE (prima di qualsiasi modifica) ----
    print("\n" + "-" * 50)
    print("ERRORE INIZIALE (con V0PRT originale)")
    print("-" * 50)
    od_filter = set(od_pairs)
    import sys as _sys; _sys.stdout.flush()
    od_times_init, od_paths_init = compute_od_skims(
        G, centroid_ids, verbose=True, od_filter=od_filter)
    valid_init = [(od, T_obs_dict[od]) for od in od_pairs if od in od_paths_init]
    if valid_init:
        T_obs_arr  = np.array([t for _, t in valid_init])
        T_pred_arr = np.array([od_times_init[od] for od, _ in valid_init])
        m0 = compute_metrics(T_pred_arr, T_obs_arr)
        print("  Coppie OD valide: {} / {}".format(len(valid_init), len(od_pairs)))
        print("  RMSE: {:.3f} min  |  MAE: {:.3f} min  |  "
              "R2(origin): {:.4f}  |  slope: {:.4f}  |  MAPE: {:.2f}%".format(
                  m0["rmse"], m0["mae"], m0["r2"], m0["slope"], m0["mape"]))
        history.append({"iteration": 0, "label": "initial",
                        "n_od_used": len(valid_init),
                        "max_rel_change_pct": 0.0,
                        "speeds": {str(lt): v for lt, v in initial_speeds.items()},
                        "metrics": m0,
                        # Usati per scatter plot; non serializzati in JSON
                        "_T_obs_arr":  T_obs_arr,
                        "_T_pred_arr": T_pred_arr})
    else:
        print("  [!] Nessuna coppia OD valida per calcolo errore iniziale")

    for iteration in range(1, n_iter + 1):
        print("\n" + "=" * 40)
        print("ITERAZIONE {} / {}".format(iteration, n_iter))
        print("=" * 40)
        _sys.stdout.flush()

        # Step 1: Shortest path
        od_times, od_paths = compute_od_skims(
            G, centroid_ids, verbose=True, od_filter=od_filter)

        # Step 2: Filtra coppie OD valide
        valid_ods = [(od, T_obs_dict[od]) for od in od_pairs if od in od_paths]
        if not valid_ods:
            print("  ERRORE: Nessuna coppia OD valida!")
            break

        od_paths_filt = {od: od_paths[od] for od, _ in valid_ods}
        T_obs_filt    = np.array([t for _, t in valid_ods])

        if len(valid_ods) < len(od_pairs):
            print("  [!] Coppie OD usate: {} / {}".format(len(valid_ods), len(od_pairs)))

        # Step 3: Matrice composizione
        D, od_order = build_composition_matrix(G, od_paths_filt, linktype_list)

        d_per_type = D.sum(axis=0)
        print("\n  Lunghezze percorse per LinkType:")
        for j, lt in enumerate(linktype_list):
            pct = d_per_type[j] / max(d_per_type.sum(), 1) * 100
            print("    Type {:3d}: {:.1f} km  ({:.1f}%)".format(
                lt, d_per_type[j] / 1000, pct))

        # Step 4: Ottimizzazione con bounds per-tipo
        new_speeds, metrics = optimize_speeds_lsq(
            D, T_obs_filt, linktype_list, v_min, v_max,
            initial_speeds=initial_speeds,
            speed_bounds=speed_bounds,
        )

        # Step 5: Log variazioni (con segno corretto)
        print("\n  Velocita aggiornate:")
        max_rel_change = 0.0
        for lt in sorted(new_speeds.keys()):
            v_old    = current_speeds.get(lt, 50.0)
            v_new    = new_speeds[lt]
            delta    = v_new - v_old
            rel_pct  = delta / max(v_old, 1.0) * 100.0
            abs_rel  = abs(rel_pct)
            max_rel_change = max(max_rel_change, abs_rel / 100.0)
            flag = " <-" if abs_rel > 1.0 else ""
            lo, hi = speed_bounds.get(lt, (v_min, v_max))
            print("    Type {:3d}: {:6.1f} -> {:6.1f} km/h  ({:+.1f}%)  "
                  "bounds=[{:.1f},{:.1f}]{}".format(
                      lt, v_old, v_new, rel_pct, lo, hi, flag))

        history.append({
            "iteration": iteration,
            "n_od_used": len(valid_ods),
            "max_rel_change_pct": round(max_rel_change * 100, 3),
            "speeds": {str(lt): v for lt, v in new_speeds.items()},
            "metrics": metrics,
        })

        # Step 6: Aggiorna grafo
        n_updated = update_graph_t0(G, new_speeds, fix_connectors=fix_conn)
        print("  Grafo aggiornato: {} archi T0 modificati".format(n_updated))

        current_speeds = new_speeds

        print("\n  Max variazione rel: {:.3f}%  (soglia: {:.2f}%)".format(
            max_rel_change * 100, conv_thresh * 100))

        slope_ok = slope_min <= metrics["slope"] <= slope_max
        r2_ok    = metrics["r2"] >= r2_target
        if slope_ok and r2_ok:
            print("  [OK] CONVERGENZA: slope={:.4f} in [{:.2f},{:.2f}]  R2={:.4f} >= {:.2f}".format(
                metrics["slope"], slope_min, slope_max, metrics["r2"], r2_target))
            break
        else:
            missing = []
            if not slope_ok:
                missing.append("slope={:.4f} fuori [{:.2f},{:.2f}]".format(
                    metrics["slope"], slope_min, slope_max))
            if not r2_ok:
                missing.append("R2={:.4f} < {:.2f}".format(metrics["r2"], r2_target))
            print("  [..] Non convergito: {}".format(" | ".join(missing)))

    return current_speeds, history


# =============================================================================
# OUTPUT E REPORT
# =============================================================================

def compute_final_skims(G, centroid_ids, best_speeds, linktype_list):
    """Calcola skim finale con velocita ottimizzate e composizione percorsi."""
    od_times, od_paths = compute_od_skims(G, centroid_ids, verbose=True)

    D, od_order = build_composition_matrix(G, od_paths, linktype_list)

    rows = []
    for i, (orig, dest) in enumerate(od_order):
        row = {"origin": orig, "destination": dest,
               "time_model_min": round(od_times.get((orig, dest), np.nan), 4)}
        d_total = D[i].sum()
        for j, lt in enumerate(linktype_list):
            row[f"length_type_{lt}_m"]  = round(D[i, j], 1)
            row[f"pct_type_{lt}"]       = round(D[i, j] / max(d_total, 1) * 100, 2)
        rows.append(row)

    return pd.DataFrame(rows)


# =============================================================================
# STATISTICHE PER LINKTYPE E REMAPPING
# =============================================================================

def compute_linktype_stats(G, linktype_list, initial_speeds, best_speeds):
    """
    Calcola statistiche per LinkType: n_archi, lunghezza totale, V0PRT medio,
    velocita iniziale, velocita ottimizzata, variazione percentuale.

    Ritorna:
        DataFrame con colonne:
            linktype | n_links | total_length_km | v0prt_mean_kmh |
            speed_initial_kmh | speed_optimized_kmh | delta_pct
    """
    from collections import defaultdict
    stats = defaultdict(lambda: {"n": 0, "length": 0.0, "v0_sum": 0.0, "v0_count": 0})

    for _, _, data in G.edges(data=True):
        lt = data.get("linktype", -1)
        if lt < 0 or data.get("is_connector", False):
            continue
        s = stats[lt]
        s["n"]      += 1
        s["length"] += data.get("length", 0.0)
        v0 = data.get("v0prt", None)
        if v0 and v0 > 0:
            s["v0_sum"]   += v0
            s["v0_count"] += 1

    rows = []
    for lt in sorted(linktype_list):
        s      = stats[lt]
        v0_m   = s["v0_sum"] / s["v0_count"] if s["v0_count"] > 0 else None
        v_init = initial_speeds.get(lt, 50.0)
        v_opt  = best_speeds.get(lt, v_init)
        delta  = (v_opt - v_init) / max(v_init, 1.0) * 100.0
        rows.append({
            "linktype":            lt,
            "n_links":             s["n"],
            "total_length_km":     round(s["length"] / 1000.0, 2),
            "v0prt_mean_kmh":      round(v0_m, 2) if v0_m else "",
            "speed_initial_kmh":   round(v_init, 2),
            "speed_optimized_kmh": round(v_opt, 2),
            "delta_pct":           round(delta, 2),
        })
    return pd.DataFrame(rows)


def remap_links_by_optimized_speed(links_df, best_speeds,
                                    v0prt_field="V0PRT", linktype_field="TYPENO",
                                    fromnodeno_field="FROMNODENO",
                                    tonodeno_field="TONODENO"):
    """
    Riassegna il LinkType di ogni arco al tipo la cui velocita ottimizzata
    e piu vicina al V0PRT dell'arco.

    Logica:
        new_type = argmin_k |V0PRT_link - speed_opt[k]|

    Ritorna:
        DataFrame con colonne:
            FROMNODENO | TONODENO | V0PRT_kmh | TYPENO_ORIG |
            TYPENO_OPT | SPEED_OPT_kmh | SPEED_DELTA_kmh | CHANGED
    """
    v0prt_col = find_column(links_df, v0prt_field)
    type_col  = find_column(links_df, linktype_field)
    from_col  = find_column(links_df, fromnodeno_field)
    to_col    = find_column(links_df, tonodeno_field)

    if not best_speeds:
        print("  [!] best_speeds vuoto -- remapping non eseguito")
        return pd.DataFrame()

    # Vettori ordinati per velocita (minima -> massima)
    sorted_items = sorted(best_speeds.items(), key=lambda x: x[1])
    lt_arr = np.array([lt for lt, _ in sorted_items], dtype=int)
    v_arr  = np.array([v  for _, v  in sorted_items], dtype=float)

    records = []
    changed = 0
    for _, row in links_df.iterrows():
        v0     = speed_to_kmh(row[v0prt_col]) if v0prt_col else 50.0
        lt_old = int(row[type_col]) if type_col else 0
        fn     = int(row[from_col]) if from_col else None
        tn     = int(row[to_col])   if to_col   else None

        idx    = int(np.argmin(np.abs(v_arr - v0)))
        lt_new = int(lt_arr[idx])
        v_opt  = float(v_arr[idx])

        rec = {
            "FROMNODENO":     fn,
            "TONODENO":       tn,
            "V0PRT_kmh":      round(v0, 2),
            "TYPENO_ORIG":    lt_old,
            "TYPENO_OPT":     lt_new,
            "SPEED_OPT_kmh":  round(v_opt, 2),
            "SPEED_DELTA_kmh": round(v_opt - v0, 2),
            "CHANGED":        int(lt_new != lt_old),
        }
        records.append(rec)
        if lt_new != lt_old:
            changed += 1

    remap_df = pd.DataFrame(records)
    pct = changed / max(len(records), 1) * 100
    print(f"  Archi riassegnati: {changed} / {len(records)}  ({pct:.1f}%)")

    # Riepilogo per tipo
    if not remap_df.empty and "TYPENO_ORIG" in remap_df.columns:
        print(f"  Distribuzione nuovi LinkType:")
        for lt_new, cnt in remap_df["TYPENO_OPT"].value_counts().sort_index().items():
            print(f"    Type {lt_new:3d}: {cnt:6d} archi  "
                  f"(speed_opt={best_speeds.get(lt_new, 0):.1f} km/h)")
    return remap_df


def save_scatter_plots(output_dir, history, skim_df, T_obs_dict):
    """
    Genera scatter T_obs vs T_modello all'inizio e alla fine dell'ottimizzazione.
    Tre pannelli: [Iniziale] [Finale] [Sovrapposto con entrambe le nuvole].
    Retta di regressione passante per l'origine su entrambi i pannelli.
    Salvato come scatter_model_vs_obs.png nella cartella output.
    """
    try:
        import matplotlib
        matplotlib.use("Agg")          # no GUI / no display
        import matplotlib.pyplot as plt
    except ImportError:
        print("  [!] matplotlib non disponibile - scatter plot saltato")
        return None

    out_path = Path(output_dir)

    # ---- Dati INIZIALI (iteration 0) ------------------------------------
    T_obs_init = T_pred_init = m_init = None
    if history and history[0].get("iteration") == 0:
        h0 = history[0]
        t_o = h0.get("_T_obs_arr")
        t_p = h0.get("_T_pred_arr")
        if t_o is not None and len(t_o) > 0:
            T_obs_init  = np.asarray(t_o)
            T_pred_init = np.asarray(t_p)
            m_init      = h0["metrics"]

    # ---- Dati FINALI (da skim_df + T_obs_dict) --------------------------
    T_obs_final = T_pred_final = m_final = None
    if skim_df is not None and T_obs_dict:
        rows = []
        for _, row in skim_df.iterrows():
            key   = (int(row["origin"]), int(row["destination"]))
            t_obs = T_obs_dict.get(key)
            t_mod = row["time_model_min"]
            if t_obs is not None and not np.isnan(t_mod):
                rows.append((float(t_obs), float(t_mod)))
        if rows:
            T_obs_final  = np.array([r[0] for r in rows])
            T_pred_final = np.array([r[1] for r in rows])
            m_final      = history[-1]["metrics"] if history else None

    if T_obs_init is None and T_obs_final is None:
        print("  [!] Nessun dato disponibile per scatter plot")
        return None

    # ---- Asse comune (basato su 99° percentile) -------------------------
    all_vals = []
    for arr in [T_obs_init, T_pred_init, T_obs_final, T_pred_final]:
        if arr is not None:
            all_vals.extend(arr.tolist())
    ax_max = float(np.percentile(all_vals, 99)) * 1.05

    # ---- Funzioni di disegno --------------------------------------------
    BLUE   = "#1E88E5"
    GREEN  = "#43A047"
    DBLUE  = "#0D47A1"
    DGREEN = "#1B5E20"

    def _metrics_text(m):
        return ("R\u00b2(origin)={:.4f}\n"
                "slope     ={:.4f}\n"
                "RMSE={:.2f} min\n"
                "MAE ={:.2f} min\n"
                "MAPE={:.1f}%\n"
                "n={}").format(
            m["r2"], m["slope"], m["rmse"], m["mae"],
            m["mape"], m.get("n_od", len(T_obs_final) if T_obs_final is not None else 0))

    def _draw_panel(ax, T_obs, T_pred, m, title, dot_col, line_col):
        ax.scatter(T_obs, T_pred, s=7, alpha=0.30, color=dot_col, rasterized=True)
        # 1:1 perfetto
        ax.plot([0, ax_max], [0, ax_max], "k--", lw=1.5, label="1:1 perfetto", zorder=5)
        # Regressione per l'origine
        slope = m["slope"]
        x_r   = np.array([0, ax_max])
        ax.plot(x_r, slope * x_r, "-", color=line_col, lw=2.2,
                label="regressione (slope={:.3f})".format(slope))
        # Box metriche
        ax.text(0.97, 0.04, _metrics_text(m),
                transform=ax.transAxes, fontsize=8.5,
                va="bottom", ha="right", family="monospace",
                bbox=dict(boxstyle="round,pad=0.45",
                          facecolor="white", edgecolor="#cccccc", alpha=0.90))
        ax.set_xlim(0, ax_max)
        ax.set_ylim(0, ax_max)
        ax.set_xlabel("T osservato [min]", fontsize=10)
        ax.set_ylabel("T modello [min]",   fontsize=10)
        ax.set_title(title, fontsize=11, fontweight="bold")
        ax.legend(fontsize=8.5, loc="upper left")
        ax.set_aspect("equal", adjustable="box")
        ax.grid(True, lw=0.5, alpha=0.45)

    # ---- Layout figura --------------------------------------------------
    has_both = (T_obs_init is not None and T_obs_final is not None)
    n_cols   = 3 if has_both else (1 if T_obs_init is not None or T_obs_final is not None else 0)
    if n_cols == 0:
        return None

    fig, axes = plt.subplots(1, n_cols, figsize=(6.8 * n_cols, 7.0),
                             squeeze=False)
    axes = axes[0]

    col = 0
    if T_obs_init is not None:
        _draw_panel(axes[col], T_obs_init, T_pred_init, m_init,
                    "INIZIALE\n(V0PRT originali)", BLUE, DBLUE)
        col += 1

    if T_obs_final is not None:
        last_iter = history[-1].get("iteration", "?") if history else "?"
        _draw_panel(axes[col], T_obs_final, T_pred_final, m_final,
                    "FINALE\n(iterazione {})".format(last_iter), GREEN, DGREEN)
        col += 1

    if has_both:
        ax = axes[col]
        ax.scatter(T_obs_init,  T_pred_init,  s=7, alpha=0.20, color=BLUE,  label="iniziale",  rasterized=True)
        ax.scatter(T_obs_final, T_pred_final, s=7, alpha=0.20, color=GREEN, label="finale",    rasterized=True)
        ax.plot([0, ax_max], [0, ax_max], "k--", lw=1.5, label="1:1 perfetto", zorder=5)
        for T_obs, T_pred, m, lc, lbl in [
            (T_obs_init,  T_pred_init,  m_init,  DBLUE,  "reg. inizio"),
            (T_obs_final, T_pred_final, m_final, DGREEN, "reg. fine"),
        ]:
            x_r = np.array([0, ax_max])
            ax.plot(x_r, m["slope"] * x_r, "-", color=lc, lw=2.2,
                    label="{} (slope={:.3f})".format(lbl, m["slope"]))
        # Mini box delta metriche
        dr2   = m_final["r2"]   - m_init["r2"]
        drmse = m_final["rmse"] - m_init["rmse"]
        dmape = m_final["mape"] - m_init["mape"]
        delta_txt = ("Delta inizio->fine:\n"
                     "R\u00b2 {:+.4f}\n"
                     "RMSE {:+.2f} min\n"
                     "MAPE {:+.1f}%").format(dr2, drmse, dmape)
        ax.text(0.97, 0.04, delta_txt,
                transform=ax.transAxes, fontsize=9,
                va="bottom", ha="right", family="monospace",
                bbox=dict(boxstyle="round,pad=0.45",
                          facecolor="#FFFDE7", edgecolor="#F9A825", alpha=0.92))
        ax.set_xlim(0, ax_max)
        ax.set_ylim(0, ax_max)
        ax.set_xlabel("T osservato [min]", fontsize=10)
        ax.set_ylabel("T modello [min]",   fontsize=10)
        ax.set_title("CONFRONTO\n(inizio vs fine)", fontsize=11, fontweight="bold")
        ax.legend(fontsize=8.5, loc="upper left")
        ax.set_aspect("equal", adjustable="box")
        ax.grid(True, lw=0.5, alpha=0.45)

    fig.suptitle(
        "T modello vs T osservato  -  Regressione passante per l'origine",
        fontsize=13, fontweight="bold", y=1.005)
    fig.tight_layout()

    scatter_file = out_path / "scatter_model_vs_obs.png"
    fig.savefig(scatter_file, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("  [OK] Scatter plot: {}".format(scatter_file))
    return str(scatter_file)


def save_arc_assignments(output_dir, arc_assignments, type_speeds,
                         arc_initial_speeds, G):
    """
    Salva i CSV specifici del per-arc mode:
      arc_assignments.csv     : per ogni arco ottimizzato: from, to, old_type, new_type, v_orig, v_new
      type_changes_summary.csv: conteggio riassegnazioni per tipo (da -> a)
    """
    out_path = Path(output_dir)

    # 1. arc_assignments.csv
    rows = []
    type_change_counts = {}   # {(old_lt, new_lt): count}
    for (u, v), new_lt in arc_assignments.items():
        v_orig = arc_initial_speeds.get((u, v), 50.0)
        # old type was the initial graph type; now graph has been updated -> use initial_speeds lookup
        # We store old_type from what arc_initial_speeds implies (type with closest speed)
        old_lt_g = G[u][v].get("linktype", -1) if G.has_edge(u, v) else -1
        # old type = current graph type (already updated) -- we need pre-update, passed via arc_assignments starting state
        # Use the fact that arc_initial_speeds stores the original v0prt; old_type tracked in run function
        rows.append({
            "from_node":      u,
            "to_node":        v,
            "new_type":       new_lt,
            "v_original_kmh": round(v_orig, 2),
            "v_new_kmh":      round(type_speeds.get(new_lt, 50.0), 2),
        })
        type_change_counts[new_lt] = type_change_counts.get(new_lt, 0) + 1

    arc_df = pd.DataFrame(rows)
    arc_file = out_path / "arc_assignments.csv"
    arc_df.to_csv(arc_file, index=False, sep=";")
    print("  [OK] Assegnazioni archi: {} ({} archi)".format(arc_file, len(arc_df)))

    # 2. type_assignment_counts.csv
    summary_rows = [
        {"type": lt,
         "v_kmh": type_speeds.get(lt, 50.0),
         "n_arcs_assigned": cnt}
        for lt, cnt in sorted(type_change_counts.items())
    ]
    if summary_rows:
        summary_df = pd.DataFrame(summary_rows)
        summary_file = out_path / "type_assignment_counts.csv"
        summary_df.to_csv(summary_file, index=False, sep=";")
        print("  [OK] Conteggio per tipo: {}".format(summary_file))
        print("\n  Distribuzione archi per tipo dopo ottimizzazione:")
        for _, r in summary_df.iterrows():
            print("    Type {:3d} ({:5.1f} km/h): {:,} archi".format(
                int(r["type"]), float(r["v_kmh"]), int(r["n_arcs_assigned"])))

    return str(arc_file)


def save_results(output_dir, best_speeds, history, skim_df, T_obs_dict, config,
                 G=None, initial_speeds=None, links_df=None, linktype_list=None,
                 arc_assignments=None, arc_initial_speeds=None):
    """Salva tutti i risultati nella cartella output."""
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    # 1. Velocita ottimizzate
    speeds_df = pd.DataFrame([
        {"linktype": lt, "speed_kmh_optimized": v}
        for lt, v in sorted(best_speeds.items())
    ])
    speeds_file = out_path / "optimized_speeds.csv"
    speeds_df.to_csv(speeds_file, index=False, sep=";")
    print(f"  [OK] Velocita ottimizzate: {speeds_file}")

    # 2. History iterazioni
    history_rows = []
    for h in history:
        row = {"iteration": h["iteration"],
               "n_od_used": h["n_od_used"],
               "max_rel_change_pct": h["max_rel_change_pct"],
               **{f"rmse": h["metrics"]["rmse"],
                  f"mae": h["metrics"]["mae"],
                  f"r2": h["metrics"]["r2"],
                  f"mape": h["metrics"]["mape"]}}
        # speeds presente solo in per_type mode
        for lt_str, v in h.get("speeds", {}).items():
            row[f"speed_type_{lt_str}"] = v
        history_rows.append(row)
    history_df = pd.DataFrame(history_rows)
    history_file = out_path / "optimization_history.csv"
    history_df.to_csv(history_file, index=False, sep=";")
    print(f"  [OK] History iterazioni: {history_file}")

    # 3. Confronto tempi modello vs osservati
    if skim_df is not None and T_obs_dict:
        skim_df["time_observed_min"] = skim_df.apply(
            lambda r: T_obs_dict.get((int(r["origin"]), int(r["destination"])), np.nan), axis=1
        )
        skim_df["error_min"]   = skim_df["time_model_min"] - skim_df["time_observed_min"]
        skim_df["error_pct"]   = (skim_df["error_min"]
                                  / skim_df["time_observed_min"].replace(0, np.nan) * 100)
        comparison_file = out_path / "od_comparison.csv"
        skim_df.to_csv(comparison_file, index=False, sep=";")
        print(f"  [OK] Confronto OD: {comparison_file}")

    # 4. Statistiche per LinkType con velocita iniziali vs ottimizzate
    if G is not None and initial_speeds is not None and linktype_list:
        stats_df = compute_linktype_stats(G, linktype_list, initial_speeds, best_speeds)
        stats_file = out_path / "linktype_stats.csv"
        stats_df.to_csv(stats_file, index=False, sep=";")
        print(f"  [OK] Statistiche LinkType: {stats_file}")
        print(f"\n  Riepilogo velocita per LinkType:")
        for _, r in stats_df.iterrows():
            arrow = "^" if float(r["delta_pct"]) > 0 else "v" if float(r["delta_pct"]) < 0 else "="
            print(f"    Type {int(r['linktype']):3d}: "
                  f"{r['speed_initial_kmh']:5.1f} -> {r['speed_optimized_kmh']:5.1f} km/h  "
                  f"{arrow}{abs(float(r['delta_pct'])):4.1f}%  "
                  f"({int(r['n_links'])} archi, {r['total_length_km']} km)")

    # 5. Remapping LinkType in base a velocita ottimizzate
    if links_df is not None and best_speeds:
        print(f"\n  Remapping LinkType (V0PRT -> closest optimized speed):")
        remap_df = remap_links_by_optimized_speed(
            links_df, best_speeds,
            v0prt_field=config.get("v0prt_field", "V0PRT"),
            linktype_field=config.get("linktype_field", "TYPENO"),
        )
        if not remap_df.empty:
            remap_file = out_path / "links_remapped.csv"
            remap_df.to_csv(remap_file, index=False, sep=";")
            print(f"  [OK] Remapping archi: {remap_file}")

    # 5b. Per-arc assignments (solo in per-arc mode)
    if arc_assignments is not None and arc_initial_speeds is not None and G is not None:
        save_arc_assignments(output_dir, arc_assignments,
                             best_speeds,   # in per-arc mode best_speeds = type_speeds
                             arc_initial_speeds, G)

    # 6. Scatter plot T_modello vs T_osservato (iniziale e finale)
    save_scatter_plots(output_dir, history, skim_df, T_obs_dict)

    # 7. Report JSON  (i campi _T_obs_arr/_T_pred_arr vengono esclusi)
    def _strip_private(h_entry):
        return {k: v for k, v in h_entry.items() if not k.startswith("_")}

    final_metrics = history[-1]["metrics"] if history else {}
    history_clean = [_strip_private(h) for h in history]
    report = {
        "config": config,
        "optimized_speeds": {str(lt): v for lt, v in sorted(best_speeds.items())},
        "n_iterations": len(history),
        "final_metrics": final_metrics,
        "convergence": len(history) < config.get("n_iterations", 10),
        "history": history_clean,
    }
    report_file = out_path / "optimization_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)
    print(f"  [OK] Report JSON: {report_file}")

    return str(speeds_file)


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 70)
    print("NETWORK SPEED OPTIMIZATION")
    print("Ottimizzazione velocita LinkType via Bounded Least Squares")
    print("=" * 70)

    # -- Carica config
    if len(sys.argv) < 2:
        print("Uso: python optimize_link_speeds.py config.json")
        sys.exit(1)

    config_path = Path(sys.argv[1])
    if not config_path.exists():
        print(f"[ERR] Config non trovato: {config_path}")
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        user_config = json.load(f)

    config = {**DEFAULT_CONFIG, **user_config}

    print(f"\nConfig: {config_path}")
    print(f"  Rete:              {config['network_dir']}")
    print(f"  Tempi osservati:   {config['observed_times_csv']}")
    print(f"  Output:            {config['output_dir']}")

    # -- Verifica input obbligatori
    for key in ["network_dir", "observed_times_csv", "output_dir"]:
        if not config.get(key):
            print(f"[ERR] Config mancante: '{key}'")
            sys.exit(1)

    # -- 1. Carica rete Visum
    print("\n" + "-" * 60)
    print("STEP 1: Caricamento rete Visum")
    print("-" * 60)
    links_df, nodes_df, centroids_df, connectors_df = load_visum_network(
        config["network_dir"],
        file_prefix=config.get("file_prefix"),
        config=config,
    )

    # -- 2. Carica tempi osservati
    print("\n" + "-" * 60)
    print("STEP 2: Caricamento tempi osservati")
    print("-" * 60)
    obs_df = pd.read_csv(
        config["observed_times_csv"],
        sep=None, engine="python", encoding="utf-8-sig"
    )
    print(f"  Righe caricate: {len(obs_df)}, colonne: {list(obs_df.columns)}")

    orig_col = config["od_col_orig"]
    dest_col = config["od_col_dest"]
    time_col = config["od_col_time"]

    # Auto-detection colonne: exact match -> case-insensitive -> alias
    def resolve_col(configured_name, alias_key):
        if configured_name in obs_df.columns:
            return configured_name
        # Case-insensitive exact
        match = next((c for c in obs_df.columns
                      if c.lower() == configured_name.lower()), None)
        if match:
            return match
        # Alias list
        for alias in OD_COL_ALIASES.get(alias_key, []):
            match = next((c for c in obs_df.columns
                          if c.lower() == alias.lower()), None)
            if match:
                print(f"  [i] Colonna '{configured_name}' non trovata -> uso '{match}' (alias)")
                return match
        return None

    orig_col_found = resolve_col(orig_col, "origin")
    dest_col_found = resolve_col(dest_col, "destination")
    time_col_found = resolve_col(time_col, "time_m")

    ok = True
    for name, found in [(orig_col, orig_col_found),
                        (dest_col, dest_col_found),
                        (time_col, time_col_found)]:
        if found is None:
            print(f"[ERR] Colonna '{name}' non trovata. Colonne disponibili: {list(obs_df.columns)}")
            ok = False
    if not ok:
        sys.exit(1)

    orig_col, dest_col, time_col = orig_col_found, dest_col_found, time_col_found
    print(f"  Colonne OD usate: origin={orig_col}, dest={dest_col}, time={time_col}")

    # Campionamento opzionale
    sample = config.get("sample_od_pairs")
    if sample and len(obs_df) > sample:
        obs_df = obs_df.sample(n=sample, random_state=config.get("random_seed", 42))
        print(f"  Campione: {len(obs_df)} coppie OD selezionate casualmente")

    T_obs_dict = {
        (int(row[orig_col]), int(row[dest_col])): float(row[time_col])
        for _, row in obs_df.iterrows()
    }
    print(f"  Coppie OD osservate: {len(T_obs_dict)}")
    obs_arr = np.array(list(T_obs_dict.values()))
    print(f"  Tempi osservati: min={obs_arr.min():.1f}  "
          f"mean={obs_arr.mean():.1f}  max={obs_arr.max():.1f} min")

    # -- 3. Costruisci grafo
    print("\n" + "-" * 60)
    print("STEP 3: Costruzione grafo NetworkX")
    print("-" * 60)
    G = build_graph(links_df, connectors_df, centroids_df, config)

    # -- 4. Ricava centroidi e LinkType
    centroid_ids = get_centroid_ids(centroids_df, connectors_df)
    if not centroid_ids:
        print("[ERR] Nessun centroide trovato!")
        sys.exit(1)
    print(f"\n  Centroidi: {len(centroid_ids)}  "
          f"(min={min(centroid_ids)}, max={max(centroid_ids)})")

    # Ricava LinkType unici dalla rete (escludi connettori -1 e tipo 0)
    linktype_list = sorted({
        data["linktype"]
        for _, _, data in G.edges(data=True)
        if data.get("linktype", -1) >= 0 and not data.get("is_connector", False)
    })
    print(f"  LinkType presenti: {linktype_list}")

    # -- 5. Ottimizzazione iterativa
    print("\n" + "-" * 60)
    print("STEP 4: Ottimizzazione iterativa velocita")
    print("-" * 60)
    initial_speeds = get_initial_speeds_from_graph(G, linktype_list)

    opt_mode       = config.get("optimization_mode", "per_type")
    arc_assignments    = None
    arc_initial_speeds = None

    if opt_mode == "per_arc":
        print("  Modalita: PER ARCO (per-arc)")
        best_arc_assignments, type_speeds, history = run_iterative_optimization_per_arc(
            G, centroid_ids, T_obs_dict, linktype_list, config
        )
        # In per-arc mode, best_speeds = type speeds (invariati)
        best_speeds        = type_speeds
        arc_assignments    = best_arc_assignments
        # Rebuild arc_initial_speeds for save_arc_assignments
        arc_initial_speeds = {}
        for u, v, data in G.edges(data=True):
            if data.get("is_connector", False):
                continue
            lt = data.get("linktype", -1)
            if lt < 0:
                continue
            v0 = data.get("v0prt", None)
            arc_initial_speeds[(u, v)] = float(v0) if v0 else initial_speeds.get(lt, 50.0)
    else:
        print("  Modalita: PER TIPO (per_type)")
        best_speeds, history = run_iterative_optimization(
            G, centroid_ids, T_obs_dict, linktype_list, config
        )

    # -- 6. Skim finale
    print("\n" + "-" * 60)
    print("STEP 5: Calcolo skim finale")
    print("-" * 60)
    skim_df = compute_final_skims(G, centroid_ids, best_speeds, linktype_list)

    # -- 7. Salva risultati
    print("\n" + "-" * 60)
    print("STEP 6: Salvataggio risultati")
    print("-" * 60)
    save_results(config["output_dir"], best_speeds, history, skim_df, T_obs_dict, config,
                 G=G, initial_speeds=initial_speeds,
                 links_df=links_df, linktype_list=linktype_list,
                 arc_assignments=arc_assignments,
                 arc_initial_speeds=arc_initial_speeds)

    print("\n" + "=" * 70)
    print("OTTIMIZZAZIONE COMPLETATA  [mode={}]".format(opt_mode))
    print("=" * 70)
    if history:
        last = history[-1]["metrics"]
        print("  Iterazioni:  {}".format(len(history)))
        print("  RMSE finale: {:.3f} min".format(last["rmse"]))
        print("  MAE finale:  {:.3f} min".format(last["mae"]))
        print("  R2 finale:   {:.4f}".format(last["r2"]))
        print("  MAPE finale: {:.2f}%".format(last["mape"]))
    print("\n  Output: {}".format(config["output_dir"]))
    print("=" * 70)

    flag_file = Path(config["output_dir"]) / "optimization_complete.flag"
    flag_data = {
        "status":           "success",
        "optimization_mode": opt_mode,
        "n_iterations":     len(history),
        "final_metrics":    history[-1]["metrics"] if history else {},
    }
    if opt_mode == "per_arc":
        flag_data["arc_assignments_csv"] = str(Path(config["output_dir"]) / "arc_assignments.csv")
        flag_data["type_assignment_counts_csv"] = str(Path(config["output_dir"]) / "type_assignment_counts.csv")
    else:
        flag_data["optimized_speeds"]  = {str(lt): v for lt, v in sorted(best_speeds.items())}
        flag_data["links_remapped_csv"] = str(Path(config["output_dir"]) / "links_remapped.csv")
        flag_data["linktype_stats_csv"] = str(Path(config["output_dir"]) / "linktype_stats.csv")
    with open(flag_file, "w") as f:
        json.dump(flag_data, f, indent=2)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrotto dall'utente.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERR] ERRORE: {e}")
        traceback.print_exc()
        sys.exit(2)
