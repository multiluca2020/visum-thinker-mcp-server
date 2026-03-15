#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Network Capacity Optimization via Bounded Least Squares
========================================================
Ottimizza le capacita' dei LinkType Visum minimizzando l'errore tra
tempi congestionati modello (shortest path su TCur) e tempi osservati.

APPROCCIO MATEMATICO:
    Dopo l'assegnazione Visum, ogni arco ha un TCur (tempo congestionato).
    Per un percorso OD, il tempo di viaggio congestionato e':
        T_od = sum_k ( D_od_k / v_cur_k )
    dove:
        D_od_k = lunghezza totale di archi di tipo k sul percorso od
        v_cur_k = velocita' congestionata del tipo k = length / TCur

    Sostituendo beta_k = 1/v_cur_k (lentezza congestionata):
        T_od = D_od @ beta   (LINEARE in beta!)

    Problema di ottimizzazione:
        min ||D @ beta - T_obs||^2
        s.t.  beta_lb <= beta_k <= beta_ub

    Ipotesi di linearita':
        delta_capacity / capacity ~ delta_v_cur / v_cur
    Quindi la variazione di velocita' congestionata si traduce
    in una variazione proporzionale di capacita'.

    Conversione v_cur_opt -> C_index (0-9):
        ratio = v_cur_opt / v_cur_corrente
        cap_pct_target = (ratio - 1) * 100 + cap_pct_corrente
        C_index = argmin |CAP_PCT[i] - cap_pct_target|

UTILIZZO:
    python optimize_capacity.py config.json

CONFIG.JSON:
    {
        "network_dir": "H:/data/network_shp",
        "observed_times_csv": "H:/data/observed_od_times.csv",
        "output_dir": "H:/data/capacity_results",
        "od_col_orig": "from_O",
        "od_col_dest": "to_D",
        "od_col_time": "observed_time",
        "tcur_field": "TCUR_PRT",
        "vol_field": "VOLVEHPRT",
        "cap_field": "CAPPRT",
        "vc_threshold": 0.6,
        "n_iterations": 5,
        "convergence_threshold": 0.005
    }
"""

import sys
import json
import traceback
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")


# =============================================================================
# COSTANTI
# =============================================================================

DEFAULT_CONFIG = {
    "network_dir": None,
    "file_prefix": None,
    "observed_times_csv": None,
    "output_dir": None,
    "od_col_orig": "from_O",
    "od_col_dest": "to_D",
    "od_col_time": "observed_time",
    # Colonne shapefile
    "tcur_field": "TCUR_PRT",
    "vol_field": "VOLVEHPRT",
    "cap_field": "CAPPRT",
    "v0prt_field": "V0PRT",
    "length_field": "LENGTH",
    "linktype_field": "TYPENO",
    "fromnodeno_field": "FROMNODENO",
    "tonodeno_field": "TONODENO",
    # Ottimizzazione
    "vc_threshold": 0.6,            # solo archi con v/c > soglia
    "speed_delta_pct": 25.0,        # max variazione % velocita' congestionata
    "n_iterations": 5,
    "convergence_threshold": 0.005,
    "slope_target_min": 0.9,
    "slope_target_max": 1.1,
    "r2_target": 0.9,
    "fix_connector_t0": True,
    "sample_od_pairs": None,
    "random_seed": 42,
}

# Mapping C_index -> percentuale capacita'
CAP_PCT = {0: -25, 1: -20, 2: -15, 3: -10, 4: -5,
           5: 0, 6: 5, 7: 10, 8: 15, 9: 20}

# Alias colonne shapefile
COLUMN_ALIASES = {
    "V0PRT":       ["V0PRT", "V0_PRT", "V0", "SPEED", "V0PRT_C"],
    "LENGTH":      ["LENGTH", "LEN", "LENGTH_M", "DIST"],
    "TYPENO":      ["TYPENO", "TYPENUMBER", "LINKTYPE", "TYPE"],
    "FROMNODENO":  ["FROMNODENO", "FROMNODE", "FROM_NODE", "FROM"],
    "TONODENO":    ["TONODENO", "TONODE", "TO_NODE", "TO"],
    "ZONENO":      ["ZONENO", "ZONE", "CENTROID", "NO"],
    "NODENO":      ["NODENO", "NODE", "KNOTENNO", "NO"],
    "TCUR_PRT":    ["TCUR_PRT", "TCUR_PRTSYS", "TCUR_PRTSYS(C)", "TCUR",
                    "TCURPRTSYS", "T_CUR", "TCUR_C",
                    "TCUR_PRT~", "TCUR_PR~"],
    "VOLVEHPRT":   ["VOLVEHPRT", "VOLVEHPRT(AP)", "VOLVEH", "VOL",
                    "VOLUME", "VOLVEHPRT_AP",
                    "VOLVEHPR~", "VOLVEHPR"],
    "CAPPRT":      ["CAPPRT", "CAP_PRT", "CAPACITY", "CAP"],
}

OD_COL_ALIASES = {
    "origin":      ["origin", "orig", "from", "o", "from_O", "from_o",
                    "zona_o", "zona_orig"],
    "destination": ["destination", "dest", "to", "d", "to_D", "to_d",
                    "zona_d", "zona_dest"],
    "time_m":      ["time_m", "time_min", "time", "observed_time",
                    "t_min", "tmin", "travel_time", "tempo_min", "tempo"],
}


# =============================================================================
# UTILITY
# =============================================================================

def find_column(df, field_key, aliases_dict=None):
    """Cerca una colonna nel DataFrame con alias case-insensitive.
    Gestisce anche nomi troncati dal formato shapefile DBF (max 10 char, ~N suffix).
    """
    cols_upper = {c.upper(): c for c in df.columns}
    candidates = (aliases_dict or COLUMN_ALIASES).get(field_key.upper(), [field_key])
    for candidate in candidates:
        clean = candidate.upper().replace("(", "").replace(")", "").replace(" ", "")
        # Match esatto
        if clean in cols_upper:
            return cols_upper[clean]
        # Substring: candidato contenuto nel nome colonna o viceversa
        # (gestisce troncamento shapefile: TCUR_PRTSYS vs TCUR_PR~1)
        for cu, co in cols_upper.items():
            cu_base = cu.split("~")[0]  # rimuovi ~N suffix
            if clean in cu or cu_base in clean:
                return co
    return None


def load_shapefile_as_dataframe(filepath, description=""):
    """Carica uno shapefile come DataFrame (prova geopandas, poi pyshp)."""
    filepath = Path(filepath)
    if not filepath.exists():
        print("  [!] {} non trovato: {}".format(description, filepath))
        return None

    try:
        import geopandas as gpd
        df = gpd.read_file(str(filepath))
        print("  {} caricato: {} righe (geopandas)".format(description, len(df)))
        return df
    except Exception:
        pass

    try:
        import shapefile
        sf = shapefile.Reader(str(filepath))
        fields = [f[0] for f in sf.fields[1:]]
        records = [r.record for r in sf.shapeRecords()]
        df = pd.DataFrame(records, columns=fields)
        print("  {} caricato: {} righe (pyshp)".format(description, len(df)))
        return df
    except Exception as e:
        print("  [!] Errore caricamento {}: {}".format(description, e))
        return None


def parse_visum_value(val):
    """Estrai valore numerico da stringa Visum (es. '50km/h' -> 50.0)."""
    import re
    if isinstance(val, (int, float)):
        return float(val)
    if val is None or str(val).strip() == "":
        return 0.0
    m = re.match(r'^([\d.]+)', str(val).strip())
    return float(m.group(1)) if m else 0.0


def length_to_meters(val):
    """Converti lunghezza Visum in metri."""
    import re
    if isinstance(val, (int, float)):
        v = float(val)
        return v * 1000.0 if v < 100 else v  # < 100 -> probabilmente km
    s = str(val).strip()
    m = re.match(r'^([\d.]+)\s*(km|m)?', s, re.IGNORECASE)
    if m:
        num = float(m.group(1))
        unit = (m.group(2) or "").lower()
        return num * 1000.0 if unit == "km" else num
    return 0.0


def speed_to_kmh(val):
    """Converti velocita' Visum in km/h."""
    return parse_visum_value(val)


def tcur_to_minutes(val):
    """Converti TCur Visum in minuti. Visum esporta in secondi di default."""
    v = parse_visum_value(val)
    # Se il valore e' > 300, probabilmente e' in secondi
    if v > 300:
        return v / 60.0
    return v


# =============================================================================
# CARICAMENTO RETE
# =============================================================================

def load_visum_network(network_dir, file_prefix=None, config=None):
    """Carica shapefile rete Visum (link, node, centroid, connector)."""
    net_path = Path(network_dir)
    config = config or {}

    def find_shp(pattern):
        found = list(net_path.glob(pattern))
        return found[0] if found else None

    if file_prefix:
        link_shp = net_path / "{}_link.shp".format(file_prefix)
        node_shp = net_path / "{}_node.shp".format(file_prefix)
        cent_shp = net_path / "{}_zone_centroid.shp".format(file_prefix)
        conn_shp = net_path / "{}_connector.shp".format(file_prefix)
    else:
        link_shp = find_shp("*_link.shp") or find_shp("*link*.shp")
        node_shp = find_shp("*_node.shp") or find_shp("*node*.shp")
        cent_shp = find_shp("*_zone_centroid.shp") or find_shp("*centroid*.shp") or find_shp("*zone*.shp")
        conn_shp = find_shp("*_connector.shp") or find_shp("*connector*.shp")

    links_df = load_shapefile_as_dataframe(link_shp, "Link") if link_shp else None
    nodes_df = load_shapefile_as_dataframe(node_shp, "Node") if node_shp else None
    centroids_df = load_shapefile_as_dataframe(cent_shp, "Centroid") if cent_shp else None
    connectors_df = load_shapefile_as_dataframe(conn_shp, "Connector") if conn_shp else None

    if links_df is None:
        print("[ERR] Shapefile link non trovato in {}".format(network_dir))
        sys.exit(1)

    return links_df, nodes_df, centroids_df, connectors_df


# =============================================================================
# GRAFO NETWORKX (con TCur come peso)
# =============================================================================

def build_graph(links_df, connectors_df, centroids_df, config):
    """
    Costruisce grafo NetworkX dalla rete Visum con TCur come peso.

    Attributi arco:
        tcur      : tempo congestionato (MINUTI)
        t0        : tempo a flusso nullo (MINUTI)
        length    : lunghezza (METRI)
        v0prt     : velocita' a flusso nullo (km/h)
        vcur      : velocita' congestionata (km/h) = length / tcur * 60/1000
        linktype  : numero tipo link
        vol       : volume veicolare
        cap       : capacita'
        vc_ratio  : volume / capacita'
        is_connector : bool
    """
    import networkx as nx

    G = nx.DiGraph()

    # Colonne
    tcur_col = find_column(links_df, config.get("tcur_field", "TCUR_PRT"))
    vol_col  = find_column(links_df, config.get("vol_field", "VOLVEHPRT"))
    cap_col  = find_column(links_df, config.get("cap_field", "CAPPRT"))
    v0_col   = find_column(links_df, config.get("v0prt_field", "V0PRT"))
    len_col  = find_column(links_df, config.get("length_field", "LENGTH"))
    type_col = find_column(links_df, config.get("linktype_field", "TYPENO"))
    from_col = find_column(links_df, config.get("fromnodeno_field", "FROMNODENO"))
    to_col   = find_column(links_df, config.get("tonodeno_field", "TONODENO"))

    print("\n  Colonne link:")
    for name, col in [("TCur", tcur_col), ("Vol", vol_col), ("Cap", cap_col),
                      ("V0PrT", v0_col), ("Length", len_col), ("Type", type_col),
                      ("From", from_col), ("To", to_col)]:
        print("    {} = {}".format(name, col))

    if tcur_col is None:
        print("[ERR] Colonna TCur non trovata! Colonne: {}".format(list(links_df.columns)))
        sys.exit(1)

    link_count = 0
    skipped = 0

    for _, row in links_df.iterrows():
        try:
            fn = int(row[from_col]) if from_col else None
            tn = int(row[to_col])   if to_col   else None
            if fn is None or tn is None:
                skipped += 1
                continue

            length = length_to_meters(row[len_col]) if len_col else 0.0
            v0     = speed_to_kmh(row[v0_col])      if v0_col  else 50.0
            lt     = int(row[type_col])              if type_col else 0
            tcur   = tcur_to_minutes(row[tcur_col])  if tcur_col else 0.0
            vol    = parse_visum_value(row[vol_col])  if vol_col else 0.0
            cap    = parse_visum_value(row[cap_col])  if cap_col else 1.0

            # T0 calcolato
            if v0 > 0 and length > 0:
                t0 = (length / 1000.0 / v0) * 60.0
            else:
                t0 = 0.001

            # TCur: usa valore esportato; se 0, usa T0
            if tcur <= 0:
                tcur = t0

            # Velocita' congestionata
            vcur = (length / 1000.0) / (tcur / 60.0) if tcur > 0 and length > 0 else v0

            # v/c ratio
            vc_ratio = vol / cap if cap > 0 else 0.0

            G.add_edge(fn, tn,
                       tcur=tcur,
                       t0=t0,
                       length=length,
                       v0prt=v0,
                       vcur=vcur,
                       linktype=lt,
                       vol=vol,
                       cap=cap,
                       vc_ratio=vc_ratio,
                       is_connector=False)
            link_count += 1
        except (TypeError, ValueError, KeyError):
            skipped += 1
            continue

    print("  Archi rete aggiunti: {}  (saltati: {})".format(link_count, skipped))

    # Connettori
    connector_count = 0
    if connectors_df is not None:
        zone_col = find_column(connectors_df, "ZONENO")
        node_col = find_column(connectors_df, "NODENO")

        if zone_col and node_col:
            for _, row in connectors_df.iterrows():
                try:
                    zone_id = int(row[zone_col])
                    node_id = int(row[node_col])

                    # TCur connettore: prova a leggere, altrimenti 0
                    t0_c = 0.0
                    v0_conn_col = find_column(connectors_df, config.get("v0prt_field", "V0PRT"))
                    len_conn_col = find_column(connectors_df, config.get("length_field", "LENGTH"))
                    if v0_conn_col and len_conn_col:
                        len_c = length_to_meters(row[len_conn_col])
                        v0_c = speed_to_kmh(row[v0_conn_col])
                        t0_c = (len_c / 1000.0 / max(v0_c, 1.0)) * 60.0 if v0_c > 0 else 0.0

                    centroid_node = -zone_id
                    G.add_edge(centroid_node, node_id,
                               tcur=max(t0_c, 0.0), t0=max(t0_c, 0.0),
                               length=0.0, linktype=-1, vol=0.0, cap=0.0,
                               vc_ratio=0.0, vcur=0.0, v0prt=0.0,
                               is_connector=True)
                    G.add_edge(node_id, centroid_node,
                               tcur=max(t0_c, 0.0), t0=max(t0_c, 0.0),
                               length=0.0, linktype=-1, vol=0.0, cap=0.0,
                               vc_ratio=0.0, vcur=0.0, v0prt=0.0,
                               is_connector=True)
                    connector_count += 1
                except (TypeError, ValueError, KeyError):
                    continue

    print("  Connettori aggiunti: {} zone ({} archi)".format(
        connector_count, connector_count * 2))
    print("\n  Grafo finale: {} nodi, {} archi".format(
        G.number_of_nodes(), G.number_of_edges()))

    return G


# =============================================================================
# CENTROIDI
# =============================================================================

def get_centroid_ids(centroids_df, connectors_df=None):
    """Ricava la lista di ID zone/centroidi."""
    centroid_ids = []
    if centroids_df is not None:
        id_col = (find_column(centroids_df, "ZONENO")
                  or next((c for c in centroids_df.columns
                           if c.upper() in ["NO", "ZONENO"]), None)
                  or centroids_df.columns[0])
        centroid_ids = sorted(centroids_df[id_col].dropna().astype(int).tolist())
    elif connectors_df is not None:
        zone_col = find_column(connectors_df, "ZONENO")
        if zone_col:
            centroid_ids = sorted(
                connectors_df[zone_col].dropna().astype(int).unique().tolist())
    return centroid_ids


# =============================================================================
# SHORTEST PATH
# =============================================================================

def compute_od_skims(G, centroid_ids, weight="tcur", verbose=True,
                     od_filter=None):
    """Calcola shortest path da ogni centroide usando TCur come peso."""
    import networkx as nx

    centroid_nodes = [-z for z in centroid_ids]
    valid_centroids = [(z, -z) for z in centroid_ids if -z in G]

    if od_filter is not None:
        needed_origins = {o for o, d in od_filter}
        needed_by_origin = {}
        for o, d in od_filter:
            needed_by_origin.setdefault(o, set()).add(d)
        origins_to_run = [(z, -z) for z, _ in valid_centroids if z in needed_origins]
        dest_lookup = {z: -z for z, _ in valid_centroids}
        mode_label = "filtrato ({} origini, {} coppie)".format(
            len(origins_to_run), len(od_filter))
    else:
        origins_to_run = valid_centroids
        needed_by_origin = None
        dest_lookup = {z: -z for z, _ in valid_centroids}
        n_valid = len(valid_centroids)
        mode_label = "{} origini x {} dest".format(n_valid, n_valid)

    od_times = {}
    od_paths = {}
    n_run = len(origins_to_run)

    if verbose:
        print("\n  Shortest path (peso={}): {}".format(weight, mode_label))

    for i, (zone_id, centroid_node) in enumerate(origins_to_run):
        if verbose and i % max(1, n_run // 10) == 0:
            print("  Origine {}/{} (zona {})...".format(i + 1, n_run, zone_id))

        try:
            lengths, paths = nx.single_source_dijkstra(
                G, centroid_node, weight=weight)
        except Exception:
            continue

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
# MATRICE COMPOSIZIONE
# =============================================================================

def build_composition_matrix(G, od_paths_subset, linktype_list):
    """
    Costruisce D (n_od x n_linktypes):
        D[i, k] = lunghezza totale (m) di archi di tipo k nel percorso OD i
    """
    type_index = {lt: j for j, lt in enumerate(linktype_list)}
    od_order = list(od_paths_subset.keys())
    n_od = len(od_order)
    n_types = len(linktype_list)

    D = np.zeros((n_od, n_types), dtype=np.float64)

    for i, od_key in enumerate(od_order):
        path = od_paths_subset[od_key]
        for u, v in zip(path[:-1], path[1:]):
            if not G.has_edge(u, v):
                continue
            edge = G[u][v]
            lt = edge.get("linktype", -1)
            length = edge.get("length", 0.0)
            if lt in type_index and length > 0:
                D[i, type_index[lt]] += length

    return D, od_order


# =============================================================================
# METRICHE
# =============================================================================

def compute_metrics(T_pred_min, T_obs):
    """Metriche: RMSE, MAE, R2 (passante per origine), slope, MAPE."""
    residuals = T_pred_min - T_obs
    SS_res = float(np.sum(residuals ** 2))
    SS_tot = float(np.sum(T_obs ** 2))
    r2     = 1.0 - SS_res / max(SS_tot, 1e-12)
    slope  = float(np.sum(T_pred_min * T_obs) / max(SS_tot, 1e-12))
    rmse   = float(np.sqrt(np.mean(residuals ** 2)))
    mae    = float(np.mean(np.abs(residuals)))
    mape   = float(np.mean(np.abs(residuals / (T_obs + 1e-3))) * 100)
    return {
        "rmse": rmse, "mae": mae, "r2": r2, "slope": slope, "mape": mape,
    }


# =============================================================================
# BOUNDS VELOCITA' CONGESTIONATA
# =============================================================================

def compute_congested_speed_bounds(linktype_list, initial_vcur,
                                    delta_pct=25.0, v_min=5.0, v_max=150.0):
    """
    Bounds per la velocita' congestionata, basati su variazione percentuale.
    Ogni tipo puo' variare +-delta_pct% dalla sua vcur iniziale.
    """
    bounds = {}
    for lt in linktype_list:
        v0 = initial_vcur.get(lt, 30.0)
        lb = max(v0 * (1.0 - delta_pct / 100.0), v_min)
        ub = min(v0 * (1.0 + delta_pct / 100.0), v_max)
        if ub <= lb:
            ub = lb + 0.5
        bounds[lt] = (lb, ub)
    return bounds


# =============================================================================
# OTTIMIZZAZIONE BVLS
# =============================================================================

def optimize_congested_speeds(D, T_obs, linktype_list,
                               initial_vcur=None,
                               speed_bounds=None,
                               v_min=5.0, v_max=150.0):
    """
    Risolve il BVLS per trovare velocita' congestionate ottimali.
    Stessa formulazione di optimize_speeds_lsq ma con vcur al posto di v0.
    """
    from scipy.optimize import lsq_linear

    n_od, n_types = D.shape
    D_km = D / 1000.0
    T_obs_h = T_obs / 60.0

    # Bounds
    if speed_bounds:
        lb = np.array([1.0 / max(speed_bounds.get(lt, (v_min, v_max))[1], 0.01)
                       for lt in linktype_list])
        ub = np.array([1.0 / max(speed_bounds.get(lt, (v_min, v_max))[0], 0.01)
                       for lt in linktype_list])
    else:
        lb = np.full(n_types, 1.0 / v_max)
        ub = np.full(n_types, 1.0 / v_min)

    # Rimuovi colonne all-zero
    col_norms = np.linalg.norm(D_km, axis=0)
    active = col_norms > 1e-6
    inactive_types = [linktype_list[j] for j in range(n_types) if not active[j]]
    if inactive_types:
        print("  [i] LinkType non nei percorsi: {} tipo/i".format(len(inactive_types)))

    D_active = D_km[:, active]
    lb_active = lb[active]
    ub_active = ub[active]

    # Garantisci lb < ub
    EPS_BETA = 1e-6
    bad = lb_active >= ub_active - EPS_BETA
    if np.any(bad):
        lb_active = np.where(bad, ub_active - EPS_BETA * 100, lb_active)
        still_bad = lb_active >= ub_active - EPS_BETA
        ub_active[still_bad] = lb_active[still_bad] + EPS_BETA * 100

    print("\n  BVLS: {} coppie OD x {} LinkType attivi".format(
        n_od, int(np.sum(active))))

    result = lsq_linear(
        D_active, T_obs_h,
        bounds=(lb_active, ub_active),
        method="bvls",
        verbose=0,
        max_iter=5000,
    )

    # Ricostruisci beta completo
    beta_full = np.full(n_types, 1.0 / 30.0)
    j = 0
    for i in range(n_types):
        if active[i]:
            beta_full[i] = result.x[j]
            j += 1
        elif initial_vcur:
            lt = linktype_list[i]
            v0 = initial_vcur.get(lt, 30.0)
            beta_full[i] = 1.0 / max(v0, 1.0)

    vcur_opt = {linktype_list[i]: round(1.0 / beta_full[i], 2)
                for i in range(n_types)}

    # Metriche
    T_pred_min = D_km @ beta_full * 60.0
    metrics = compute_metrics(T_pred_min, T_obs)

    print("  RMSE: {:.3f} min  |  MAE: {:.3f} min  |  "
          "R2(origin): {:.4f}  |  slope: {:.4f}  |  MAPE: {:.2f}%".format(
              metrics["rmse"], metrics["mae"], metrics["r2"],
              metrics["slope"], metrics["mape"]))

    return vcur_opt, metrics


# =============================================================================
# VELOCITA' CONGESTIONATE INIZIALI DAL GRAFO
# =============================================================================

def get_initial_vcur_from_graph(G, linktype_list):
    """Ricava velocita' congestionate medie per LinkType dal grafo."""
    type_vcur_sum = {lt: 0.0 for lt in linktype_list}
    type_vcur_cnt = {lt: 0   for lt in linktype_list}

    for _, _, data in G.edges(data=True):
        lt = data.get("linktype", -1)
        vcur = data.get("vcur", 0.0)
        if lt in type_vcur_sum and vcur > 0:
            type_vcur_sum[lt] += vcur
            type_vcur_cnt[lt] += 1

    vcur = {}
    for lt in linktype_list:
        if type_vcur_cnt[lt] > 0:
            vcur[lt] = round(type_vcur_sum[lt] / type_vcur_cnt[lt], 2)
        else:
            vcur[lt] = 30.0

    return vcur


# =============================================================================
# AGGIORNAMENTO TCur NEL GRAFO
# =============================================================================

def update_graph_tcur(G, vcur_dict, fix_connectors=True):
    """Aggiorna TCur nel grafo: tcur = (length_m / 1000 / vcur_kmh) * 60."""
    updated = 0
    for u, v, data in G.edges(data=True):
        lt = data.get("linktype", -1)
        length = data.get("length", 0.0)
        is_con = data.get("is_connector", False)

        if is_con and fix_connectors:
            continue
        if lt < 0 or length <= 0:
            continue

        new_vcur = vcur_dict.get(lt)
        if new_vcur and new_vcur > 0:
            new_tcur = (length / 1000.0 / new_vcur) * 60.0
            data["tcur"] = new_tcur
            data["vcur"] = new_vcur
            updated += 1

    return updated


# =============================================================================
# CONVERSIONE VCUR OTTIMALE -> CAPACITA' (C_INDEX)
# =============================================================================

def vcur_to_capacity_index(linktype_list, initial_vcur, optimal_vcur,
                            current_c_index=None):
    """
    Converte velocita' congestionate ottimali in C_index (0-9).

    Logica: ratio = v_opt / v_cur -> variazione percentuale necessaria.
    Mappa alla percentuale di capacita' piu' vicina nel range CAP_PCT.

    Args:
        linktype_list: lista link type
        initial_vcur: dict {lt: vcur_corrente_kmh}
        optimal_vcur: dict {lt: vcur_ottimale_kmh}
        current_c_index: dict {base_type: C_index_corrente} (default: tutti 5)

    Returns:
        dict {base_type: new_C_index}
        dict {base_type: {"vcur_init", "vcur_opt", "ratio", "cap_pct_target", "c_index"}}
    """
    if current_c_index is None:
        current_c_index = {}

    cap_pct_values = sorted(CAP_PCT.items(), key=lambda x: x[0])
    results = {}
    details = {}

    for lt in linktype_list:
        v_init = initial_vcur.get(lt, 30.0)
        v_opt = optimal_vcur.get(lt, v_init)

        # Base type
        if lt >= 1000:
            base = lt // 100
        else:
            base = lt

        # Ratio di cambio velocita'
        ratio = v_opt / max(v_init, 0.1)

        # C_index corrente per questo base type
        ci_current = current_c_index.get(base, 5)
        cap_pct_current = CAP_PCT.get(ci_current, 0)

        # Target: capacita' proporzionale al cambio di velocita'
        # Se v_opt e' +10% -> cap deve essere +10%
        cap_pct_target = cap_pct_current + (ratio - 1.0) * 100.0

        # Trova C_index piu' vicino
        best_ci = ci_current
        best_dist = abs(cap_pct_target - CAP_PCT[ci_current])
        for ci, pct in cap_pct_values:
            dist = abs(cap_pct_target - pct)
            if dist < best_dist:
                best_dist = dist
                best_ci = ci

        results[base] = best_ci
        details[base] = {
            "vcur_init": round(v_init, 2),
            "vcur_opt": round(v_opt, 2),
            "ratio": round(ratio, 4),
            "cap_pct_current": cap_pct_current,
            "cap_pct_target": round(cap_pct_target, 1),
            "c_index_old": ci_current,
            "c_index_new": best_ci,
            "cap_pct_new": CAP_PCT[best_ci],
        }

    return results, details


def remap_links_by_optimized_capacity(links_df, optimal_vcur, initial_vcur,
                                       linktype_list, G=None):
    """
    Riassegna il TypeNo di ogni singolo arco in base alla capacita' ottimizzata.

    Per ogni link:
      1. Trova il base_type (BB) e il V_index corrente (S)
      2. Calcola il ratio v_opt / v_init per il suo linktype
      3. Mappa a C_index (0-9) piu' vicino
      4. Nuovo TypeNo = BB * 100 + S * 10 + C_index_new

    Produce DataFrame con FROMNODENO, TONODENO, TYPENO_ORIG, TYPENO_NEW, CHANGED
    identico al formato di remap_links_by_optimized_speed per riuso di
    apply_typeno_remap_to_visum.
    """
    from_col = find_column(links_df, "FROMNODENO")
    to_col = find_column(links_df, "TONODENO")
    type_col = find_column(links_df, "TYPENO")

    if not from_col or not to_col or not type_col:
        print("  [!] Colonne chiave mancanti -- remap non eseguito")
        return pd.DataFrame()

    # Fattori CAP_PCT per lookup veloce
    cap_pct_sorted = sorted(CAP_PCT.items(), key=lambda x: x[0])

    records = []
    changed = 0

    for _, row in links_df.iterrows():
        fn = int(row[from_col])
        tn = int(row[to_col])
        lt_old = int(row[type_col])

        # Decodifica tipo corrente
        if lt_old >= 1000:
            base = lt_old // 100
            v_idx = (lt_old % 100) // 10
            c_idx_old = lt_old % 10
        elif lt_old >= 100:
            base = lt_old // 100
            v_idx = (lt_old % 100) // 10
            c_idx_old = lt_old % 10
        else:
            base = lt_old
            v_idx = 5
            c_idx_old = 5

        # Velocita' ottimizzata per questo linktype
        v_init = initial_vcur.get(lt_old, 30.0)
        v_opt = optimal_vcur.get(lt_old, v_init)

        # Ratio di cambio -> target capacita'
        ratio = v_opt / max(v_init, 0.1)
        cap_pct_current = CAP_PCT.get(c_idx_old, 0)
        cap_pct_target = cap_pct_current + (ratio - 1.0) * 100.0

        # Trova C_index piu' vicino
        best_ci = c_idx_old
        best_dist = abs(cap_pct_target - CAP_PCT.get(c_idx_old, 0))
        for ci, pct in cap_pct_sorted:
            dist = abs(cap_pct_target - pct)
            if dist < best_dist:
                best_dist = dist
                best_ci = ci

        lt_new = base * 100 + v_idx * 10 + best_ci

        rec = {
            "FROMNODENO": fn,
            "TONODENO": tn,
            "TYPENO_ORIG": lt_old,
            "TYPENO_NEW": lt_new,
            "CHANGED": int(lt_new != lt_old),
        }
        records.append(rec)
        if lt_new != lt_old:
            changed += 1

    remap_df = pd.DataFrame(records)
    pct = changed / max(len(records), 1) * 100
    print("  Archi riassegnati: {} / {}  ({:.1f}%)".format(
        changed, len(records), pct))

    if not remap_df.empty:
        print("  Distribuzione nuovi LinkType:")
        for lt_new, cnt in remap_df["TYPENO_NEW"].value_counts().sort_index().items():
            print("    Type {:5d}: {:6d} archi".format(int(lt_new), int(cnt)))

    return remap_df


# =============================================================================
# FILTRO LINK TYPE CONGESTIONATI
# =============================================================================

def filter_congested_types(G, linktype_list, vc_threshold=0.6):
    """
    Filtra link type congestionati: solo quelli con v/c medio > soglia
    e volume significativo.

    Returns:
        active_types: lista link type attivi per ottimizzazione
        type_stats: dict {lt: {avg_vc, total_vol, total_cap, n_links}}
    """
    type_stats = {}
    for _, _, data in G.edges(data=True):
        lt = data.get("linktype", -1)
        if lt < 0 or data.get("is_connector", False):
            continue
        if lt not in {t for t in linktype_list}:
            continue

        vol = data.get("vol", 0.0)
        cap = data.get("cap", 0.0)

        if lt not in type_stats:
            type_stats[lt] = {"total_vol": 0.0, "total_cap": 0.0, "n_links": 0}
        type_stats[lt]["total_vol"] += vol
        type_stats[lt]["total_cap"] += cap
        type_stats[lt]["n_links"] += 1

    for lt in type_stats:
        s = type_stats[lt]
        s["avg_vc"] = s["total_vol"] / max(s["total_cap"], 1.0)

    # Filtra per v/c > soglia e volume > 0
    active_types = sorted([lt for lt, s in type_stats.items()
                           if s["avg_vc"] > vc_threshold and s["total_vol"] > 0])

    # Tutti i tipi con traffico (anche non congestionati) per completezza
    all_with_traffic = sorted([lt for lt, s in type_stats.items()
                               if s["total_vol"] > 0])

    return active_types, all_with_traffic, type_stats


# =============================================================================
# LOOP ITERATIVO
# =============================================================================

def run_iterative_optimization(G, centroid_ids, T_obs_dict, config):
    """
    Ottimizzazione iterativa con re-routing:
    1. Shortest path su TCur
    2. Matrice composizione D
    3. BVLS -> velocita' congestionate ottimali
    4. Aggiorna TCur nel grafo
    5. Ripeti
    """
    n_iter = config.get("n_iterations", 5)
    vc_threshold = config.get("vc_threshold", 0.6)
    delta_pct = config.get("speed_delta_pct", 25.0)
    fix_conn = config.get("fix_connector_t0", True)
    slope_min = config.get("slope_target_min", 0.9)
    slope_max = config.get("slope_target_max", 1.1)
    r2_target = config.get("r2_target", 0.9)

    od_pairs = list(T_obs_dict.keys())
    od_filter = set(od_pairs)

    # Identifica tipi congestionati
    active_types, all_types, type_stats = filter_congested_types(
        G, list({data["linktype"] for _, _, data in G.edges(data=True)
                 if data.get("linktype", -1) >= 0}),
        vc_threshold=vc_threshold)

    # Per il BVLS usiamo TUTTI i tipi con traffico (non solo congestionati)
    # perche' i percorsi passano anche su archi non congestionati
    linktype_list = all_types

    print("\n  Tipi con traffico: {}".format(len(all_types)))
    print("  Tipi congestionati (v/c > {:.2f}): {}".format(
        vc_threshold, len(active_types)))
    print("\n  Statistiche v/c per tipo:")
    for lt in sorted(type_stats.keys()):
        s = type_stats[lt]
        tag = " ** CONGESTIONATO" if lt in active_types else ""
        print("    Type {:5d}: v/c={:.3f}  vol={:.0f}  cap={:.0f}  n={}{}".format(
            lt, s["avg_vc"], s["total_vol"], s["total_cap"], s["n_links"], tag))

    initial_vcur = get_initial_vcur_from_graph(G, linktype_list)

    # Bounds: per tipi congestionati +-delta_pct%, per gli altri +-5% (quasi fissi)
    speed_bounds = {}
    for lt in linktype_list:
        v0 = initial_vcur.get(lt, 30.0)
        if lt in active_types:
            pct = delta_pct
        else:
            pct = 5.0  # quasi fisso
        lb = max(v0 * (1.0 - pct / 100.0), 3.0)
        ub = min(v0 * (1.0 + pct / 100.0), 150.0)
        if ub <= lb:
            ub = lb + 0.5
        speed_bounds[lt] = (lb, ub)

    current_vcur = dict(initial_vcur)
    history = []

    print("\n" + "=" * 70)
    print("OTTIMIZZAZIONE ITERATIVA CAPACITA' (VELOCITA' CONGESTIONATE)")
    print("=" * 70)
    print("\nParametri:")
    print("  Soglia v/c: {:.2f}".format(vc_threshold))
    print("  Delta max: +-{:.0f}% (congestionati), +-5% (altri)".format(delta_pct))
    print("  Iterazioni max: {}".format(n_iter))
    print("\nVelocita' congestionate iniziali e bounds:")
    for lt in sorted(linktype_list):
        v = initial_vcur.get(lt, 30.0)
        lo, hi = speed_bounds.get(lt, (3.0, 150.0))
        tag = " **" if lt in active_types else ""
        print("  Type {:5d}: {:6.1f} km/h  bounds=[{:.1f}, {:.1f}]{}".format(
            lt, v, lo, hi, tag))

    # Errore iniziale
    print("\n" + "-" * 50)
    print("ERRORE INIZIALE (con TCur da assegnazione)")
    print("-" * 50)
    sys.stdout.flush()
    od_times_init, od_paths_init = compute_od_skims(
        G, centroid_ids, weight="tcur", verbose=True, od_filter=od_filter)
    valid_init = [(od, T_obs_dict[od]) for od in od_pairs if od in od_paths_init]
    if valid_init:
        T_obs_arr = np.array([t for _, t in valid_init])
        T_pred_arr = np.array([od_times_init[od] for od, _ in valid_init])
        m0 = compute_metrics(T_pred_arr, T_obs_arr)
        print("  Coppie OD valide: {} / {}".format(len(valid_init), len(od_pairs)))
        print("  RMSE: {:.3f} min  |  MAE: {:.3f} min  |  "
              "R2(origin): {:.4f}  |  slope: {:.4f}  |  MAPE: {:.2f}%".format(
                  m0["rmse"], m0["mae"], m0["r2"], m0["slope"], m0["mape"]))
        history.append({"iteration": 0, "label": "initial",
                        "n_od_used": len(valid_init),
                        "metrics": m0,
                        "max_rel_change_pct": 0.0,
                        "_T_obs_arr": T_obs_arr.tolist(),
                        "_T_pred_arr": T_pred_arr.tolist(),
                        "vcur": {str(lt): v for lt, v in initial_vcur.items()}})

    # Loop
    for iteration in range(1, n_iter + 1):
        print("\n" + "=" * 40)
        print("ITERAZIONE {} / {}".format(iteration, n_iter))
        print("=" * 40)
        sys.stdout.flush()

        # Step 1: Shortest path su TCur
        od_times, od_paths = compute_od_skims(
            G, centroid_ids, weight="tcur", verbose=True, od_filter=od_filter)

        # Step 2: Filtra OD valide
        valid_ods = [(od, T_obs_dict[od]) for od in od_pairs if od in od_paths]
        if not valid_ods:
            print("  ERRORE: Nessuna coppia OD valida!")
            break

        od_paths_filt = {od: od_paths[od] for od, _ in valid_ods}
        T_obs_filt = np.array([t for _, t in valid_ods])

        # Step 3: Matrice composizione
        D, od_order = build_composition_matrix(G, od_paths_filt, linktype_list)

        d_per_type = D.sum(axis=0)
        print("\n  Lunghezze percorse per LinkType (top 10):")
        sorted_idx = np.argsort(d_per_type)[::-1]
        for rank, j in enumerate(sorted_idx[:10]):
            lt = linktype_list[j]
            pct = d_per_type[j] / max(d_per_type.sum(), 1) * 100
            tag = " **" if lt in active_types else ""
            print("    Type {:5d}: {:8.1f} km  ({:5.1f}%){}".format(
                lt, d_per_type[j] / 1000, pct, tag))

        # Step 4: BVLS
        new_vcur, metrics = optimize_congested_speeds(
            D, T_obs_filt, linktype_list,
            initial_vcur=initial_vcur,
            speed_bounds=speed_bounds)

        # Step 5: Log variazioni
        print("\n  Velocita' congestionate aggiornate:")
        for lt in sorted(new_vcur.keys()):
            v_old = current_vcur.get(lt, 30.0)
            v_new = new_vcur[lt]
            delta = v_new - v_old
            rel_pct = delta / max(v_old, 1.0) * 100.0
            tag = " **" if lt in active_types else ""
            if abs(rel_pct) > 0.5:
                print("    Type {:5d}: {:6.1f} -> {:6.1f} km/h  ({:+.1f}%){}".format(
                    lt, v_old, v_new, rel_pct, tag))

        # Calcola T_pred su tutte le coppie per scatter e max_rel_change
        D_km_full = D / 1000.0
        beta_iter = np.array([1.0 / max(new_vcur.get(lt, 30.0), 0.1)
                              for lt in linktype_list])
        T_pred_iter = D_km_full @ beta_iter * 60.0
        T_obs_iter = T_obs_filt

        max_rel_change = 0.0
        for lt in linktype_list:
            v_old = current_vcur.get(lt, 30.0)
            v_new = new_vcur.get(lt, v_old)
            rel = abs(v_new - v_old) / max(v_old, 0.1) * 100
            if rel > max_rel_change:
                max_rel_change = rel

        history.append({
            "iteration": iteration,
            "n_od_used": len(valid_ods),
            "metrics": metrics,
            "max_rel_change_pct": round(max_rel_change, 4),
            "_T_obs_arr": T_obs_iter.tolist(),
            "_T_pred_arr": T_pred_iter.tolist(),
            "vcur": {str(lt): v for lt, v in new_vcur.items()},
        })

        # Step 6: Aggiorna grafo
        n_updated = update_graph_tcur(G, new_vcur, fix_connectors=fix_conn)
        print("  Grafo aggiornato: {} archi TCur modificati".format(n_updated))

        current_vcur = new_vcur

        # Convergenza
        slope_ok = slope_min <= metrics["slope"] <= slope_max
        r2_ok = metrics["r2"] >= r2_target
        if slope_ok and r2_ok:
            print("  [OK] CONVERGENZA: slope={:.4f}  R2={:.4f}".format(
                metrics["slope"], metrics["r2"]))
            break
        else:
            missing = []
            if not slope_ok:
                missing.append("slope={:.4f}".format(metrics["slope"]))
            if not r2_ok:
                missing.append("R2={:.4f}".format(metrics["r2"]))
            print("  [..] Non convergito: {}".format(" | ".join(missing)))

    return current_vcur, initial_vcur, linktype_list, active_types, history


# =============================================================================
# SKIM FINALI
# =============================================================================

def compute_final_skims(G, centroid_ids, optimal_vcur, linktype_list):
    """Calcola skim finale con velocita' congestionate ottimizzate."""
    od_times, od_paths = compute_od_skims(G, centroid_ids, weight="tcur",
                                           verbose=True)
    D, od_order = build_composition_matrix(G, od_paths, linktype_list)

    rows = []
    for i, (orig, dest) in enumerate(od_order):
        row = {"origin": orig, "destination": dest,
               "time_model_min": round(od_times.get((orig, dest), np.nan), 4)}
        d_total = D[i].sum()
        for j, lt in enumerate(linktype_list):
            row["length_type_{}_m".format(lt)] = round(D[i, j], 1)
            row["pct_type_{}".format(lt)] = round(
                D[i, j] / max(d_total, 1) * 100, 2)
        rows.append(row)

    return pd.DataFrame(rows)


# =============================================================================
# STATISTICHE PER LINKTYPE
# =============================================================================

def compute_linktype_stats(G, linktype_list, initial_vcur, optimal_vcur):
    """
    Statistiche per LinkType: n_archi, lunghezza totale, vcur medio,
    velocita' iniziale vs ottimizzata, variazione percentuale.
    """
    from collections import defaultdict
    stats = defaultdict(lambda: {"n": 0, "length": 0.0,
                                 "vcur_sum": 0.0, "vcur_count": 0,
                                 "vol_sum": 0.0, "cap_sum": 0.0})

    for _, _, data in G.edges(data=True):
        lt = data.get("linktype", -1)
        if lt < 0 or data.get("is_connector", False):
            continue
        s = stats[lt]
        s["n"] += 1
        s["length"] += data.get("length", 0.0)
        vcur = data.get("vcur", 0.0)
        if vcur > 0:
            s["vcur_sum"] += vcur
            s["vcur_count"] += 1
        s["vol_sum"] += data.get("vol", 0.0)
        s["cap_sum"] += data.get("cap", 0.0)

    rows = []
    for lt in sorted(linktype_list):
        s = stats[lt]
        vcur_m = (s["vcur_sum"] / s["vcur_count"]
                  if s["vcur_count"] > 0 else None)
        avg_vc = s["vol_sum"] / max(s["cap_sum"], 1.0)
        v_init = initial_vcur.get(lt, 30.0)
        v_opt = optimal_vcur.get(lt, v_init)
        delta = (v_opt - v_init) / max(v_init, 1.0) * 100.0
        rows.append({
            "linktype": lt,
            "n_links": s["n"],
            "total_length_km": round(s["length"] / 1000.0, 2),
            "vcur_mean_kmh": round(vcur_m, 2) if vcur_m else "",
            "avg_vc_ratio": round(avg_vc, 3),
            "vcur_initial_kmh": round(v_init, 2),
            "vcur_optimized_kmh": round(v_opt, 2),
            "delta_pct": round(delta, 2),
        })
    return pd.DataFrame(rows)


# =============================================================================
# SCATTER PLOTS
# =============================================================================

def save_scatter_plots(output_dir, history, skim_df, T_obs_dict,
                       snap_data=None):
    """
    Genera scatter T_obs vs T_modello.
    Pannelli: [Iniziale] [Finale BVLS] [Sovrapposto] + opzionale [Post-snap]
    """
    try:
        import matplotlib
        matplotlib.use("Agg")
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
            T_obs_init = np.asarray(t_o)
            T_pred_init = np.asarray(t_p)
            m_init = h0["metrics"]

    # ---- Dati FINALI (da skim_df + T_obs_dict) --------------------------
    T_obs_final = T_pred_final = m_final = None
    if skim_df is not None and T_obs_dict:
        rows = []
        for _, row in skim_df.iterrows():
            key = (int(row["origin"]), int(row["destination"]))
            t_obs = T_obs_dict.get(key)
            t_mod = row["time_model_min"]
            if t_obs is not None and not np.isnan(t_mod):
                rows.append((float(t_obs), float(t_mod)))
        if rows:
            T_obs_final = np.array([r[0] for r in rows])
            T_pred_final = np.array([r[1] for r in rows])
            m_final = history[-1]["metrics"] if history else None

    # ---- Dati POST-SNAP (capacita' discreta tipo ottimale) ---------------
    T_obs_snap = T_pred_snap = m_snap_plot = None
    if snap_data is not None:
        T_obs_snap, T_pred_snap, m_snap_plot = snap_data

    if T_obs_init is None and T_obs_final is None:
        print("  [!] Nessun dato disponibile per scatter plot")
        return None

    # ---- Asse comune (basato su 99 percentile) -------------------------
    all_vals = []
    for arr in [T_obs_init, T_pred_init, T_obs_final, T_pred_final,
                T_obs_snap, T_pred_snap]:
        if arr is not None:
            all_vals.extend(arr.tolist())
    ax_max = float(np.percentile(all_vals, 99)) * 1.05

    # ---- Colori ---------------------------------------------------------
    BLUE = "#1E88E5"
    GREEN = "#43A047"
    ORANGE = "#FB8C00"
    DBLUE = "#0D47A1"
    DGREEN = "#1B5E20"
    DORANGE = "#E65100"

    def _metrics_text(m):
        n = m.get("n_od", len(T_obs_final) if T_obs_final is not None else 0)
        return ("R\u00b2(origin)={:.4f}\n"
                "slope     ={:.4f}\n"
                "RMSE={:.2f} min\n"
                "MAE ={:.2f} min\n"
                "MAPE={:.1f}%\n"
                "n={}").format(m["r2"], m["slope"], m["rmse"],
                               m["mae"], m["mape"], n)

    def _draw_panel(ax, T_obs, T_pred, m, title, dot_col, line_col):
        ax.scatter(T_obs, T_pred, s=7, alpha=0.30, color=dot_col,
                   rasterized=True)
        ax.plot([0, ax_max], [0, ax_max], "k--", lw=1.5,
                label="1:1 perfetto", zorder=5)
        slope = m["slope"]
        x_r = np.array([0, ax_max])
        ax.plot(x_r, slope * x_r, "-", color=line_col, lw=2.2,
                label="regressione (slope={:.3f})".format(slope))
        ax.text(0.97, 0.04, _metrics_text(m),
                transform=ax.transAxes, fontsize=8.5,
                va="bottom", ha="right", family="monospace",
                bbox=dict(boxstyle="round,pad=0.45",
                          facecolor="white", edgecolor="#cccccc", alpha=0.90))
        ax.set_xlim(0, ax_max)
        ax.set_ylim(0, ax_max)
        ax.set_xlabel("T osservato [min]", fontsize=10)
        ax.set_ylabel("T modello [min]", fontsize=10)
        ax.set_title(title, fontsize=11, fontweight="bold")
        ax.legend(fontsize=8.5, loc="upper left")
        ax.set_aspect("equal", adjustable="box")
        ax.grid(True, lw=0.5, alpha=0.45)

    # ---- Layout figura --------------------------------------------------
    has_both = (T_obs_init is not None and T_obs_final is not None)
    has_snap = (T_obs_snap is not None)
    n_cols = max(1, (1 if T_obs_init is not None else 0)
                 + (1 if T_obs_final is not None else 0)
                 + (1 if has_both else 0)
                 + (1 if has_snap else 0))
    if n_cols == 0:
        return None

    fig, axes = plt.subplots(1, n_cols, figsize=(6.8 * n_cols, 7.0),
                             squeeze=False)
    axes = axes[0]

    col = 0
    if T_obs_init is not None:
        _draw_panel(axes[col], T_obs_init, T_pred_init, m_init,
                    "INIZIALE\n(TCur da assegnazione)", BLUE, DBLUE)
        col += 1

    if T_obs_final is not None:
        last_iter = history[-1].get("iteration", "?") if history else "?"
        _draw_panel(axes[col], T_obs_final, T_pred_final, m_final,
                    "FINALE BVLS\n(iterazione {})".format(last_iter),
                    GREEN, DGREEN)
        col += 1

    if has_both:
        ax = axes[col]
        ax.scatter(T_obs_init, T_pred_init, s=7, alpha=0.20, color=BLUE,
                   label="iniziale", rasterized=True)
        ax.scatter(T_obs_final, T_pred_final, s=7, alpha=0.20, color=GREEN,
                   label="BVLS finale", rasterized=True)
        ax.plot([0, ax_max], [0, ax_max], "k--", lw=1.5,
                label="1:1 perfetto", zorder=5)
        for T_obs, T_pred, m, lc, lbl in [
            (T_obs_init, T_pred_init, m_init, DBLUE, "reg. inizio"),
            (T_obs_final, T_pred_final, m_final, DGREEN, "reg. BVLS"),
        ]:
            x_r = np.array([0, ax_max])
            ax.plot(x_r, m["slope"] * x_r, "-", color=lc, lw=2.2,
                    label="{} (slope={:.3f})".format(lbl, m["slope"]))
        dr2 = m_final["r2"] - m_init["r2"]
        drmse = m_final["rmse"] - m_init["rmse"]
        dmape = m_final["mape"] - m_init["mape"]
        delta_txt = ("Delta inizio->BVLS:\n"
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
        ax.set_ylabel("T modello [min]", fontsize=10)
        ax.set_title("CONFRONTO\n(inizio vs BVLS)", fontsize=11,
                     fontweight="bold")
        ax.legend(fontsize=8.5, loc="upper left")
        ax.set_aspect("equal", adjustable="box")
        ax.grid(True, lw=0.5, alpha=0.45)
        col += 1

    if has_snap:
        _draw_panel(axes[col], T_obs_snap, T_pred_snap, m_snap_plot,
                    "POST-SNAP\n(capacita' tipo ottimale)", ORANGE, DORANGE)
        ax = axes[col]
        refs = []
        if m_init is not None:
            refs.append((m_init, DBLUE, "inizio"))
        if m_final is not None:
            refs.append((m_final, DGREEN, "BVLS"))
        for m_ref, lc, lbl in refs:
            x_r = np.array([0, ax_max])
            ax.plot(x_r, m_ref["slope"] * x_r, "--", color=lc, lw=1.2,
                    alpha=0.55,
                    label="slope {} ={:.3f}".format(lbl, m_ref["slope"]))
        ax.legend(fontsize=7.5, loc="upper left")
        col += 1

    fig.suptitle(
        "T modello vs T osservato  -  Ottimizzazione Capacita'",
        fontsize=13, fontweight="bold", y=1.005)
    fig.tight_layout()

    scatter_file = out_path / "scatter_model_vs_obs.png"
    fig.savefig(scatter_file, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("  [OK] Scatter plot: {}".format(scatter_file))
    return str(scatter_file)


# =============================================================================
# SALVATAGGIO RISULTATI
# =============================================================================

def save_results(output_dir, optimal_vcur, initial_vcur, linktype_list,
                 active_types, history, T_obs_dict, config,
                 capacity_remap=None, capacity_details=None,
                 skim_df=None, G=None):
    """Salva tutti i risultati nella cartella output."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    # 1. Velocita' congestionate ottimizzate
    rows = []
    for lt in sorted(linktype_list):
        v_init = initial_vcur.get(lt, 30.0)
        v_opt = optimal_vcur.get(lt, v_init)
        is_active = lt in active_types
        rows.append({
            "linktype": lt,
            "vcur_initial": round(v_init, 2),
            "vcur_optimized": round(v_opt, 2),
            "delta_pct": round((v_opt - v_init) / max(v_init, 0.1) * 100, 2),
            "congested": int(is_active),
        })
    pd.DataFrame(rows).to_csv(str(out / "optimized_vcur.csv"),
                               index=False, sep=";")
    print("  [OK] Velocita' congestionate: {}".format(out / "optimized_vcur.csv"))

    # 2. Capacity remap
    if capacity_details:
        cap_rows = []
        for base_type, info in sorted(capacity_details.items()):
            cap_rows.append({
                "base_type": base_type,
                "vcur_initial": info["vcur_init"],
                "vcur_optimal": info["vcur_opt"],
                "ratio": info["ratio"],
                "c_index_old": info["c_index_old"],
                "c_index_new": info["c_index_new"],
                "cap_pct_old": info["cap_pct_current"],
                "cap_pct_new": info["cap_pct_new"],
            })
        pd.DataFrame(cap_rows).to_csv(
            str(out / "capacity_remap.csv"), index=False, sep=";")
        print("  [OK] Capacity remap: {}".format(out / "capacity_remap.csv"))

    # 3. Storico iterazioni
    hist_rows = []
    for h in history:
        m = h.get("metrics", {})
        row = {
            "iteration": h.get("iteration", 0),
            "n_od": h.get("n_od_used", 0),
            "max_rel_change_pct": h.get("max_rel_change_pct", 0),
            "rmse": round(m.get("rmse", 0), 4),
            "mae": round(m.get("mae", 0), 4),
            "r2": round(m.get("r2", 0), 4),
            "slope": round(m.get("slope", 0), 4),
            "mape": round(m.get("mape", 0), 2),
        }
        for lt_str, v in h.get("vcur", {}).items():
            row["vcur_type_{}".format(lt_str)] = v
        hist_rows.append(row)
    pd.DataFrame(hist_rows).to_csv(
        str(out / "optimization_history.csv"), index=False, sep=";")
    print("  [OK] History iterazioni: {}".format(out / "optimization_history.csv"))

    # 4. Confronto OD tempi modello vs osservati
    if skim_df is not None and T_obs_dict:
        skim_df["time_observed_min"] = skim_df.apply(
            lambda r: T_obs_dict.get(
                (int(r["origin"]), int(r["destination"])), np.nan), axis=1)
        skim_df["error_min"] = (skim_df["time_model_min"]
                                - skim_df["time_observed_min"])
        skim_df["error_pct"] = (skim_df["error_min"]
                                / skim_df["time_observed_min"].replace(0, np.nan)
                                * 100)
        comparison_file = out / "od_comparison.csv"
        skim_df.to_csv(str(comparison_file), index=False, sep=";")
        print("  [OK] Confronto OD: {}".format(comparison_file))

    # 5. Statistiche per LinkType
    if G is not None and linktype_list:
        stats_df = compute_linktype_stats(G, linktype_list,
                                          initial_vcur, optimal_vcur)
        stats_file = out / "linktype_stats.csv"
        stats_df.to_csv(str(stats_file), index=False, sep=";")
        print("  [OK] Statistiche LinkType: {}".format(stats_file))
        print("\n  Riepilogo velocita' congestionate per LinkType:")
        for _, r in stats_df.iterrows():
            arrow = ("^" if float(r["delta_pct"]) > 0
                     else "v" if float(r["delta_pct"]) < 0 else "=")
            print("    Type {:5d}: "
                  "{:5.1f} -> {:5.1f} km/h  "
                  "{}{:4.1f}%  "
                  "({} archi, {} km, v/c={})".format(
                      int(r["linktype"]),
                      float(r["vcur_initial_kmh"]),
                      float(r["vcur_optimized_kmh"]),
                      arrow, abs(float(r["delta_pct"])),
                      int(r["n_links"]),
                      r["total_length_km"],
                      r["avg_vc_ratio"]))

    # 6. Scatter plot
    save_scatter_plots(output_dir, history, skim_df, T_obs_dict)

    # 7. Report JSON (escludi campi _T_obs_arr/_T_pred_arr)
    def _strip_private(h_entry):
        return {k: v for k, v in h_entry.items() if not k.startswith("_")}

    final_metrics = history[-1]["metrics"] if history else {}
    history_clean = [_strip_private(h) for h in history]
    report = {
        "config": config,
        "optimized_vcur": {str(lt): v
                           for lt, v in sorted(optimal_vcur.items())},
        "n_iterations": len(history),
        "final_metrics": final_metrics,
        "convergence": len(history) < config.get("n_iterations", 5),
        "history": history_clean,
    }
    if capacity_remap:
        report["capacity_remap"] = {str(k): v
                                     for k, v in capacity_remap.items()}
    if capacity_details:
        report["capacity_details"] = {
            str(k): v for k, v in capacity_details.items()}
    report_file = out / "optimization_report.json"
    with open(str(report_file), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)
    print("  [OK] Report JSON: {}".format(report_file))

    # 8. Flag file
    flag_data = {
        "status": "success",
        "n_iterations": len(history),
        "final_metrics": final_metrics,
        "capacity_remap_csv": str(out / "capacity_remap.csv"),
        "links_remapped_csv": str(out / "links_remapped.csv"),
        "optimized_vcur_csv": str(out / "optimized_vcur.csv"),
    }
    if capacity_remap:
        flag_data["capacity_remap"] = {str(k): v
                                        for k, v in capacity_remap.items()}

    with open(str(out / "optimization_complete.flag"), "w") as f:
        json.dump(flag_data, f, indent=2)
    print("  [OK] Flag file: optimization_complete.flag")


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 70)
    print("NETWORK CAPACITY OPTIMIZATION")
    print("Ottimizzazione capacita' LinkType via Bounded Least Squares")
    print("=" * 70)

    # Config
    if len(sys.argv) < 2:
        print("Uso: python optimize_capacity.py config.json")
        sys.exit(1)

    config_path = Path(sys.argv[1])
    if not config_path.exists():
        print("[ERR] Config non trovato: {}".format(config_path))
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        user_config = json.load(f)

    config = {**DEFAULT_CONFIG, **user_config}

    print("\nConfig: {}".format(config_path))
    print("  Rete:            {}".format(config["network_dir"]))
    print("  Tempi osservati: {}".format(config["observed_times_csv"]))
    print("  Output:          {}".format(config["output_dir"]))

    for key in ["network_dir", "observed_times_csv", "output_dir"]:
        if not config.get(key):
            print("[ERR] Config mancante: '{}'".format(key))
            sys.exit(1)

    # 1. Carica rete
    print("\n" + "-" * 60)
    print("STEP 1: Caricamento rete Visum (con TCur)")
    print("-" * 60)
    links_df, nodes_df, centroids_df, connectors_df = load_visum_network(
        config["network_dir"], file_prefix=config.get("file_prefix"), config=config)

    # 2. Tempi osservati
    print("\n" + "-" * 60)
    print("STEP 2: Caricamento tempi osservati")
    print("-" * 60)
    obs_df = pd.read_csv(
        config["observed_times_csv"],
        sep=None, engine="python", encoding="utf-8-sig")
    print("  Righe: {}, colonne: {}".format(len(obs_df), list(obs_df.columns)))

    # Risolvi nomi colonne
    def resolve_col(configured_name, alias_key):
        if configured_name in obs_df.columns:
            return configured_name
        match = next((c for c in obs_df.columns
                      if c.lower() == configured_name.lower()), None)
        if match:
            return match
        for alias in OD_COL_ALIASES.get(alias_key, []):
            match = next((c for c in obs_df.columns
                          if c.lower() == alias.lower()), None)
            if match:
                return match
        return None

    orig_col = resolve_col(config["od_col_orig"], "origin")
    dest_col = resolve_col(config["od_col_dest"], "destination")
    time_col = resolve_col(config["od_col_time"], "time_m")

    for name, found in [(config["od_col_orig"], orig_col),
                        (config["od_col_dest"], dest_col),
                        (config["od_col_time"], time_col)]:
        if found is None:
            print("[ERR] Colonna '{}' non trovata. Disponibili: {}".format(
                name, list(obs_df.columns)))
            sys.exit(1)

    # Campionamento
    sample = config.get("sample_od_pairs")
    if sample and len(obs_df) > sample:
        obs_df = obs_df.sample(n=sample, random_state=config.get("random_seed", 42))

    T_obs_dict = {
        (int(row[orig_col]), int(row[dest_col])): float(row[time_col])
        for _, row in obs_df.iterrows()
    }
    print("  Coppie OD osservate: {}".format(len(T_obs_dict)))
    obs_arr = np.array(list(T_obs_dict.values()))
    print("  Tempi: min={:.1f}  mean={:.1f}  max={:.1f} min".format(
        obs_arr.min(), obs_arr.mean(), obs_arr.max()))

    # 3. Grafo
    print("\n" + "-" * 60)
    print("STEP 3: Costruzione grafo NetworkX (peso=TCur)")
    print("-" * 60)
    G = build_graph(links_df, connectors_df, centroids_df, config)

    # 4. Centroidi
    centroid_ids = get_centroid_ids(centroids_df, connectors_df)
    if not centroid_ids:
        print("[ERR] Nessun centroide!")
        sys.exit(1)
    print("\n  Centroidi: {}".format(len(centroid_ids)))

    # 5. Ottimizzazione
    print("\n" + "-" * 60)
    print("STEP 4: Ottimizzazione iterativa")
    print("-" * 60)

    optimal_vcur, initial_vcur, linktype_list, active_types, history = \
        run_iterative_optimization(G, centroid_ids, T_obs_dict, config)

    # 6. Remap per-link: assegna nuovo TypeNo a ogni singolo arco
    print("\n" + "-" * 60)
    print("STEP 5: Remap capacita' per singolo arco")
    print("-" * 60)

    remap_df = remap_links_by_optimized_capacity(
        links_df, optimal_vcur, initial_vcur, linktype_list, G=G)

    # Salva links_remapped.csv (formato compatibile con apply_typeno_remap_to_visum)
    remap_file = Path(config["output_dir"]) / "links_remapped.csv"
    remap_file.parent.mkdir(parents=True, exist_ok=True)
    remap_df.to_csv(str(remap_file), index=False, sep=";")
    print("  [OK] links_remapped.csv: {}".format(remap_file))

    # Anche capacity_remap per-base-type (per report)
    type_col = find_column(links_df, config.get("linktype_field", "TYPENO"))
    current_c_index = {}
    if type_col:
        for _, row in links_df.iterrows():
            try:
                tn = int(row[type_col])
                if tn >= 1000:
                    base = tn // 100
                    ci = tn % 10
                else:
                    base = tn
                    ci = 5
                current_c_index[base] = ci
            except (ValueError, TypeError):
                pass

    capacity_remap, capacity_details = vcur_to_capacity_index(
        linktype_list, initial_vcur, optimal_vcur, current_c_index)

    print("\nCapacita' ottimali per base type:")
    for base_type in sorted(capacity_details.keys()):
        d = capacity_details[base_type]
        changed_flag = " <-- CAMBIATO" if d["c_index_old"] != d["c_index_new"] else ""
        print("  Base {:3d}: v_cur {:.1f} -> {:.1f} km/h (ratio={:.3f})  "
              "C_index {} -> {} (cap {:+d}% -> {:+d}%){}".format(
                  base_type,
                  d["vcur_init"], d["vcur_opt"], d["ratio"],
                  d["c_index_old"], d["c_index_new"],
                  d["cap_pct_current"], d["cap_pct_new"],
                  changed_flag))

    # 7. Skim finali con vcur ottimizzate
    print("\n" + "-" * 60)
    print("STEP 6: Skim finali con velocita' congestionate ottimizzate")
    print("-" * 60)
    skim_df = compute_final_skims(G, centroid_ids, optimal_vcur, linktype_list)

    # 8. Salva
    print("\n" + "-" * 60)
    print("STEP 7: Salvataggio risultati")
    print("-" * 60)
    save_results(config["output_dir"], optimal_vcur, initial_vcur,
                 linktype_list, active_types, history, T_obs_dict, config,
                 capacity_remap=capacity_remap,
                 capacity_details=capacity_details,
                 skim_df=skim_df, G=G)

    # Riepilogo
    print("\n" + "=" * 70)
    print("OTTIMIZZAZIONE CAPACITA' COMPLETATA")
    print("=" * 70)
    if history:
        last = history[-1]["metrics"]
        print("  Iterazioni:  {}".format(len(history)))
        print("  RMSE finale: {:.3f} min".format(last["rmse"]))
        print("  R2 finale:   {:.4f}".format(last["r2"]))
        print("  slope finale: {:.4f}".format(last["slope"]))
    n_changed = sum(1 for d in capacity_details.values()
                    if d["c_index_old"] != d["c_index_new"])
    print("  Tipi con capacita' modificata: {} / {}".format(
        n_changed, len(capacity_details)))
    print("\n  Output: {}".format(config["output_dir"]))
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrotto dall'utente.")
        sys.exit(1)
    except Exception as e:
        print("\n[ERR] ERRORE: {}".format(e))
        traceback.print_exc()
        sys.exit(2)
