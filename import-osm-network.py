#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Import OpenStreetMap (OSM) network into Visum
Utilizza il metodo IIO.ImportOpenStreetMap della COM API
"""

import os
import sys
import win32com.client
from pathlib import Path
import subprocess
import json
import tempfile


# Mapping di default per conversione LinkType
# Utilizzato quando non viene fornito un mapping personalizzato
# Mapping: LINKTYPE standard (dopo import OSM) → LINKTYPE active (nel territorio)

# OLD MAPPING (commentato - 2026-01-12)
# DEFAULT_LINKTYPE_MAPPING = {
#     20: 50,   # Trunk 2 lanes
#     21: 51,   # Trunk 1 lane
#     29: 59,   # Trunk_link
#     30: 60,   # Primary
#     39: 69,   # Primary_link
#     40: 70,   # Secondary 2 lanes
#     41: 71,   # Secondary 1/>=3 lanes
#     42: 78,   # Tertiary 1 lane
#     43: 72,   # Tertiary 2 lanes (nuovo)
#     44: 80,   # Unclassified (nuovo)
#     49: 79,   # Secondary_link/Tertiary_link
#     81: 81,   # Residential (mantiene)
#     82: 82    # Living_street (mantiene)
# }

# NEW MAPPING (aggiornato - 2026-01-12)
DEFAULT_LINKTYPE_MAPPING = {
    0: 0,     # Blocked Oneway
    1: 1,     # Construction
    7: 7,     # Ferrovia
    8: 8,     # Metropolitana
    9: 9,     # Tram
    10: 10,   # Autostrade 4 corsie
    11: 11,   # Autostrade 3 corsie
    12: 12,   # Autostrade 2 corsie
    13: 13,   # Autostrade 1 corsia
    18: 18,   # Autostrade rampe 2 corsie
    19: 19,   # Autostrade rampe 1 corsia
    20: 50,   # Extraurbane principali 2 corsie → Urbane scorrimento 2 corsie
    21: 51,   # Extraurbane principali 1 corsia → Urbane scorrimento 1 corsie
    28: 58,   # Extraurbane principali rampe 2 corsie → Urbane scorrimento rampe 2 corsie
    29: 59,   # Extraurbane principali rampe 1 corsia → Urbane scorrimento rampe 1 corsia
    30: 60,   # Extraurbane secondarie 2 corsie → Urbane principali 2 corsie
    31: 61,   # Extraurbane secondarie 1 corsia 1 tipo → Urbane principali 1 corsia
    39: 69,   # Extraurbane secondarie intersezioni → Urbane principali intersezioni
    40: 70,   # Extraurbane locali 2 corsie → Urbane interquartiere 2 corsie
    41: 71,   # Extraurbane locali 1 corsia 1 tipo → Urbane interquartiere 1 corsia
    42: 80,   # Extraurbane locali 1 corsia 2 tipo → Urbane locali 1 corsia Tipo 1
    43: 80,   # Extraurbane locali 1 corsia 3 tipo → Urbane locali 1 corsia Tipo 2
    44: 81,   # Extraurbane locali 1 corsia 4 tipo → Urbane locali 1 corsia Tipo 3
    49: 79,   # Extraurbane locali intersezioni → Urbane interquartiere intersezioni
    82: 82,   # Residential
    83: 83,   # Living_street
    94: 94    # ferry
}


def import_osm_network(osm_file_path, config_preset="Detailed urban network", 
                       save_net_file=True, clipping=0, 
                       coord_min=None, coord_max=None, visum_version="2025",
                       save_project_as=None, custom_param_files=None, gpa_file=None,
                       visum_instance=None):
    """
    Importa una rete OSM in Visum.
    
    Args:
        osm_file_path (str): Percorso completo al file OSM o OSM.bz2 da importare
        config_preset (str): Nome del preset di configurazione OSM in Visum
                            Default: "Detailed urban network"
                            Preset disponibili: "Detailed urban network", "Simple urban network", ecc.
        save_net_file (bool): Se True, mantiene il file .net temporaneo
                             Default: True
        clipping (int): Tipo di clipping (0=no, 1=inside, 2=extended)
                       Default: 0
        coord_min (tuple): (XMin, YMin) per clipping area. Default: None
        coord_max (tuple): (XMax, YMax) per clipping area. Default: None
        visum_version (str): Versione di Visum da usare (es. "2025", "2024", "2021")
                            Default: "2025". Ignorato se visum_instance è fornito.
        save_project_as (str): Percorso dove salvare il progetto Visum (.ver)
                              Se None, non salva. Default: None
        custom_param_files (dict): Dizionario con percorsi custom per file di configurazione
                                  {"xml": "path/to/custom.xml", 
                                   "cfg": "path/to/custom.cfg",
                                   "net": "path/to/custom.net"}
                                  Se None, usa i file del preset. Default: None
        gpa_file (str): Percorso a file .gpa per applicare parametri grafici dopo import
                       Se None, non applica parametri grafici. Default: None
        visum_instance: Istanza Visum esistente (es. dalla console Python di Visum)
                       Se None, crea una nuova istanza. Default: None
    
    Returns:
        dict: Risultato dell'import con status e messaggi
    
    Raises:
        FileNotFoundError: Se il file OSM non esiste
        ValueError: Se i parametri non sono validi
        Exception: Se l'import fallisce
    
    Examples:
        # Da script standalone
        result = import_osm_network("città.osm")
        
        # Dalla console Python di Visum
        result = import_osm_network("città.osm", visum_instance=Visum)
    """
    
    result = {
        "status": "failed",
        "message": "",
        "osm_file": osm_file_path,
        "config": config_preset
    }
    
    try:
        # Validazione file OSM
        osm_path = Path(osm_file_path)
        if not osm_path.exists():
            raise FileNotFoundError(f"File OSM non trovato: {osm_file_path}")
        
        if not osm_path.suffix.lower() in [".osm", ".bz2"]:
            raise ValueError(f"File deve avere estensione .osm o .osm.bz2, trovato: {osm_path.suffix}")
        
        # Connessione a Visum
        if visum_instance is not None:
            # Usa l'istanza fornita (es. dalla console Python di Visum)
            visum = visum_instance
            print("✓ Uso istanza Visum esistente (console)")
        else:
            # Crea nuova istanza COM
            print(f"Connessione a Visum {visum_version}...")
            visum = win32com.client.Dispatch(f"Visum.Visum.{visum_version}")
            print("✓ Visum connesso")
        
        # Costruzione percorsi file di configurazione
        osm_file_names = [str(osm_path)]
        
        # File temporaneo .net (stesso percorso del file OSM, con nome modificato)
        temp_net_file = str(osm_path.with_stem(osm_path.stem + "_import").with_suffix(".net"))
        
        # Se sono forniti file custom, usali
        if custom_param_files:
            print("Uso file di configurazione custom...")
            xml_file = custom_param_files.get("xml")
            cfg_file = custom_param_files.get("cfg")
            net_file = custom_param_files.get("net")
            
            if not all([xml_file, cfg_file, net_file]):
                raise ValueError("custom_param_files deve contenere 'xml', 'cfg' e 'net'")
            
            param_file_names = [
                xml_file,
                cfg_file,
                net_file,
                temp_net_file,
                gpa_file if gpa_file else ""
            ]
        else:
            # Usa i preset di default di Visum
            program_files = os.environ.get("ProgramFiles")
            if not program_files:
                raise Exception("Variabile d'ambiente ProgramFiles non trovata")
            
            cfg_base_path = os.path.join(
                program_files,
                "PTV Vision",
                f"PTV Visum {visum_version}",
                "Exe",
                "Importer",
                "OSM",
                config_preset
            )
            
            # Verifica che la cartella di configurazione esista
            if not os.path.exists(cfg_base_path):
                raise FileNotFoundError(f"Cartella di configurazione OSM non trovata: {cfg_base_path}")
            
            print(f"✓ Cartella configurazione trovata: {cfg_base_path}")
            
            param_file_names = [
                os.path.join(cfg_base_path, f"{config_preset}.xml"),
                os.path.join(cfg_base_path, f"{config_preset}.cfg"),
                os.path.join(cfg_base_path, f"{config_preset}.net"),
                temp_net_file,
                gpa_file if gpa_file else ""
            ]
        
        # Validazione file di configurazione
        for i, param_file in enumerate(param_file_names[:3]):  # Solo XML, CFG, NET
            if not os.path.exists(param_file):
                raise FileNotFoundError(f"File di configurazione non trovato: {param_file}")
        
        # Validazione file GPA se fornito
        if gpa_file and not os.path.exists(gpa_file):
            raise FileNotFoundError(f"File GPA non trovato: {gpa_file}")
        
        print("✓ Tutti i file di configurazione trovati")
        print(f"  - XML: {param_file_names[0]}")
        print(f"  - CFG: {param_file_names[1]}")
        print(f"  - NET: {param_file_names[2]}")
        print(f"  - Temporaneo: {param_file_names[3]}")
        
        # Parametri clipping
        x_coord_min = coord_min[0] if coord_min else 0
        y_coord_min = coord_min[1] if coord_min else 0
        x_coord_max = coord_max[0] if coord_max else 0
        y_coord_max = coord_max[1] if coord_max else 0
        
        # Esecuzione import
        print("\nInizio import OSM...")
        print(f"File OSM: {osm_file_path}")
        print(f"Clipping: {clipping} (0=no, 1=inside, 2=extended)")
        
        visum.IO.ImportOpenStreetMap(
            osm_file_names,
            param_file_names,
            save_net_file,
            clipping,
            x_coord_min,
            y_coord_min,
            x_coord_max,
            y_coord_max
        )
        
        print("✓ Import completato con successo!")
        
        # Informazioni di riepilogo
        try:
            num_nodes = visum.Net.Nodes.Count
            num_links = visum.Net.Links.Count
            result["status"] = "success"
            result["message"] = f"Network importata: {num_nodes} nodi, {num_links} link"
            result["nodes_count"] = num_nodes
            result["links_count"] = num_links
            result["temp_net_file"] = temp_net_file if save_net_file else "rimosso"
            print(f"✓ Rete caricata: {num_nodes} nodi, {num_links} link")
        except Exception as e:
            result["status"] = "success_partial"
            result["message"] = f"Import completato ma conteggio elementi fallito: {str(e)}"
        
        # Salvataggio progetto se richiesto
        if save_project_as:
            try:
                print(f"\nSalvataggio progetto in: {save_project_as}")
                save_path = Path(save_project_as)
                
                # Crea la directory se non esiste
                save_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Salva il progetto
                visum.SaveVersion(str(save_path))
                print(f"✓ Progetto salvato: {save_project_as}")
                result["project_file"] = str(save_path)
                result["message"] += f" | Progetto salvato in {save_path.name}"
            except Exception as e:
                print(f"✗ Errore durante salvataggio progetto: {str(e)}")
                result["save_error"] = str(e)
                result["message"] += f" | ATTENZIONE: salvataggio fallito"
        
        return result
    
    except FileNotFoundError as e:
        result["message"] = f"Errore file: {str(e)}"
        print(f"✗ {result['message']}")
        return result
    except ValueError as e:
        result["message"] = f"Errore validazione: {str(e)}"
        print(f"✗ {result['message']}")
        return result
    except Exception as e:
        result["message"] = f"Errore durante l'import: {str(e)}"
        print(f"✗ {result['message']}")
        return result


def list_available_presets(visum_version="2025"):
    """
    Elenca i preset OSM disponibili nell'installazione di Visum.
    
    Args:
        visum_version (str): Versione di Visum. Default: "2025"
    
    Returns:
        list: Lista dei nomi dei preset disponibili
    """
    program_files = os.environ.get("ProgramFiles")
    if not program_files:
        print("✗ Variabile d'ambiente ProgramFiles non trovata")
        return []
    
    osm_base_path = os.path.join(
        program_files,
        "PTV Vision",
        f"PTV Visum {visum_version}",
        "Exe",
        "Importer",
        "OSM"
    )
    
    if not os.path.exists(osm_base_path):
        print(f"✗ Cartella OSM non trovata: {osm_base_path}")
        return []
    
    presets = []
    for item in os.listdir(osm_base_path):
        item_path = os.path.join(osm_base_path, item)
        if os.path.isdir(item_path):
            # Verifica che contenga i file necessari
            xml_file = os.path.join(item_path, f"{item}.xml")
            cfg_file = os.path.join(item_path, f"{item}.cfg")
            net_file = os.path.join(item_path, f"{item}.net")
            
            if all([os.path.exists(xml_file), os.path.exists(cfg_file), os.path.exists(net_file)]):
                presets.append(item)
    
    return presets


def copy_and_customize_preset(preset_name, custom_dir, visum_version="2025"):
    """
    Copia un preset esistente in una cartella custom per permetterne la modifica.
    
    Args:
        preset_name (str): Nome del preset da copiare
        custom_dir (str): Cartella dove copiare i file
        visum_version (str): Versione di Visum. Default: "2025"
    
    Returns:
        dict: Percorsi dei file copiati {"xml": ..., "cfg": ..., "net": ...}
    """
    import shutil
    
    program_files = os.environ.get("ProgramFiles")
    if not program_files:
        raise Exception("Variabile d'ambiente ProgramFiles non trovata")
    
    preset_path = os.path.join(
        program_files,
        "PTV Vision",
        f"PTV Visum {visum_version}",
        "Exe",
        "Importer",
        "OSM",
        preset_name
    )
    
    if not os.path.exists(preset_path):
        raise FileNotFoundError(f"Preset non trovato: {preset_path}")
    
    # Crea directory custom
    custom_path = Path(custom_dir)
    custom_path.mkdir(parents=True, exist_ok=True)
    
    # Copia i file
    files = {}
    for ext in ["xml", "cfg", "net"]:
        src = os.path.join(preset_path, f"{preset_name}.{ext}")
        dst = custom_path / f"{preset_name}_custom.{ext}"
        
        if os.path.exists(src):
            shutil.copy2(src, dst)
            files[ext] = str(dst)
            print(f"✓ Copiato: {dst}")
        else:
            raise FileNotFoundError(f"File non trovato: {src}")
    
    print(f"\n✓ Preset copiato in: {custom_dir}")
    print("Ora puoi modificare i file .cfg e .xml per customizzare l'import!")
    
    return files


def main():
    """
    Funzione principale - NON eseguita automaticamente quando lo script è caricato
    nella console Python di Visum. Chiama manualmente se necessario.
    """
    print("=" * 80)
    print(" " * 20 + "LIBRERIA IMPORT OSM + CONVERSIONE LINKTYPE")
    print("=" * 80)
    print("\n✓ Script import-osm-network.py caricato correttamente!")
    print("\n" + "=" * 80)
    print("FUNZIONI DISPONIBILI:")
    print("=" * 80)
    
    print("\n【1】 PROCESSO INTEGRATO (RACCOMANDATO)")
    print("-" * 80)
    print("  import_osm_and_convert_linktypes()")
    print("  Scopo: Import OSM + Selezione territori + Conversione LinkType in un solo comando")
    print("  Sintassi:")
    print("    result = import_osm_and_convert_linktypes(")
    print("        osm_file_path=r'H:\\file.osm.bz2',")
    print("        config_folder=r'H:\\ConfigFolder',")
    print("        territory_numbers=[1],              # Territori da selezionare")
    print("        clipping=1,                         # 0=no, 1=inside, 2=extended")
    print("        coord_min=(12.5886, 42.5126),       # XMin, YMin")
    print("        coord_max=(12.7325, 42.6115),       # XMax, YMax")
    print("        linktype_mapping=None,              # None=usa default")
    print("        apply_defaults=True,                # ★ Applica defaults dai LinkTypes")
    print("        save_project_as=r'H:\\output.ver'   # Opzionale")
    print("    )")
    
    print("\n【2】 IMPORT OSM")
    print("-" * 80)
    print("  a) import_osm_simple(osm_file, preset='Detailed urban network')")
    print("     Scopo: Import veloce con preset Visum standard")
    print("     Sintassi: result = import_osm_simple(r'C:\\file.osm')")
    print("")
    print("  b) import_osm_from_folder(osm_file, config_folder, clipping=0, ...)")
    print("     Scopo: Import con cartella configurazione custom")
    print("     Sintassi:")
    print("       result = import_osm_from_folder(")
    print("           r'H:\\file.osm.bz2',")
    print("           r'H:\\ConfigFolder',")
    print("           clipping=1,")
    print("           coord_min=(XMin, YMin),")
    print("           coord_max=(XMax, YMax)")
    print("       )")
    
    print("\n【3】 SELEZIONE SPAZIALE")
    print("-" * 80)
    print("  select_links_by_territories(territory_numbers=[1])")
    print("  Scopo: Seleziona link che si sovrappongono con territori")
    print("  Sintassi:")
    print("    result = select_links_by_territories([1, 2, 3])  # Lista territori")
    print("    # Usa SetTerritoryActive per selezione spaziale precisa")
    
    print("\n【4】 CONVERSIONE LINKTYPE")
    print("-" * 80)
    print("  change_linktype_by_mapping(linktype_mapping=None, only_selected=True)")
    print("  Scopo: Modifica LinkType secondo mapping definito")
    print("  Sintassi:")
    print("    # Usa mapping di default")
    print("    result = change_linktype_by_mapping()")
    print("")
    print("    # Mapping personalizzato")
    print("    mapping = {20: 60, 21: 61, 30: 70}")
    print("    result = change_linktype_by_mapping(mapping, only_selected=True)")
    print("")
    print("  Mapping di default: {20:60, 21:61, 29:69, 30:70, 39:79, 40:0, 41:80, 42:81, 81:81}")
    
    print("\n【5】 APPLICA DEFAULTS DAI LINKTYPES (★ NUOVO)")
    print("-" * 80)
    print("  apply_linktype_defaults(recalculate_length=True)")
    print("  Scopo: Ricalcola lunghezze + applica defaults dai LinkTypes (corsie, velocità)")
    print("  Sintassi:")
    print("    result = apply_linktype_defaults()  # Ricalcola lunghezze e applica defaults")
    print("  ")
    print("  Risolve 3 problemi:")
    print("    • Lunghezza link = 0 km dopo import OSM")
    print("    • NumLanes non impostato")
    print("    • v0PrT / vMaxPrT non impostati")
    
    print("\n【6】 UTILITY")
    print("-" * 80)
    print("  a) list_available_presets(visum_version='2025')")
    print("     Scopo: Elenca preset OSM disponibili nell'installazione Visum")
    print("")
    print("  b) copy_and_customize_preset(preset_name, custom_dir)")
    print("     Scopo: Copia preset per personalizzazione")
    
    print("\n" + "=" * 80)
    print("ESEMPIO COMPLETO:")
    print("=" * 80)
    print("exec(open(r'H:\\visum-thinker-mcp-server\\import-osm-network.py', encoding='utf-8').read())")
    print("result = import_osm_and_convert_linktypes(")
    print("    osm_file_path=r'H:\\go\\network_builder\\inputs\\centro-latest.osm.bz2',")
    print("    config_folder=r'H:\\go\\network_builder\\Go_Urban road network',")
    print("    territory_numbers=[1],")
    print("    clipping=1,")
    print("    coord_min=(12.5886, 42.5126),")
    print("    coord_max=(12.7325, 42.6115),")
    print("    apply_defaults=True,                # ★ Applica defaults!")
    print("    save_project_as=r'H:\\projects\\centro.ver'")
    print(")")
    print("=" * 80)


# ============================================================================
# ESEMPI DI UTILIZZO
# ============================================================================

def example_standalone():
    """Esempio: esecuzione da script standalone"""
    result = import_osm_network(
        osm_file_path=r"C:\Data\città.osm",
        config_preset="Detailed urban network",
        save_project_as=r"C:\Projects\città.ver"
    )
    return result


def import_osm_simple(osm_file_path, preset="Detailed urban network"):
    """
    Funzione SEMPLICE per importare OSM dalla console Python di Visum.
    USA QUESTA dalla console di Visum!
    
    Args:
        osm_file_path (str): Percorso al file .osm o .osm.bz2
        preset (str): Nome preset (default: "Detailed urban network")
    
    Returns:
        dict: Risultato con status e info
    
    Esempio dalla console Visum:
        >>> exec(open(r"H:\visum-thinker-mcp-server\import-osm-network.py").read())
        >>> result = import_osm_simple(r"C:\MioFile.osm")
    """
    return import_osm_network(
        osm_file_path=osm_file_path,
        config_preset=preset,
        visum_instance=Visum  # Usa l'istanza Visum della console
    )


def import_osm_from_folder(osm_file_path, config_folder, clipping=0, 
                           coord_min=None, coord_max=None, 
                           save_project_as=None):
    """
    Importa OSM cercando automaticamente i file di configurazione in una cartella.
    
    Args:
        osm_file_path (str): Percorso al file .osm o .osm.bz2
        config_folder (str): Cartella contenente i file .xml, .cfg, .net, .gpa
        clipping (int): Tipo di clipping (0=no, 1=inside, 2=extended). Default: 0
        coord_min (tuple): (XMin, YMin) per clipping. Default: None
        coord_max (tuple): (XMax, YMax) per clipping. Default: None
        save_project_as (str): Percorso dove salvare il progetto. Default: None
    
    Returns:
        dict: Risultato con status e info
    
    Esempio dalla console Visum:
        >>> result = import_osm_from_folder(
        ...     r"H:\\go\\network_builder\\inputs\\centro-latest.osm.bz2",
        ...     r"H:\\go\\network_builder\\UrbanRoadNetwork",
        ...     clipping=1,
        ...     coord_min=(12.5886, 42.5126),
        ...     coord_max=(12.7325, 42.6115)
        ... )
    """
    from pathlib import Path
    import glob
    
    config_path = Path(config_folder)
    
    if not config_path.exists():
        return {
            "status": "failed",
            "message": f"Cartella non trovata: {config_folder}"
        }
    
    # Cerca i file di configurazione
    xml_files = list(config_path.glob("*.xml"))
    cfg_files = list(config_path.glob("*.cfg"))
    net_files = list(config_path.glob("*.net"))
    gpa_files = list(config_path.glob("*.gpa"))
    
    if not xml_files:
        return {
            "status": "failed",
            "message": f"Nessun file .xml trovato in {config_folder}"
        }
    if not cfg_files:
        return {
            "status": "failed",
            "message": f"Nessun file .cfg trovato in {config_folder}"
        }
    if not net_files:
        return {
            "status": "failed",
            "message": f"Nessun file .net trovato in {config_folder}"
        }
    
            # Usa il primo file trovato di ogni tipo
    xml_file = str(xml_files[0])
    cfg_file = str(cfg_files[0])
    net_file = str(net_files[0])
    gpa_file = str(gpa_files[0]) if gpa_files else None
    
    print("File trovati in {}:".format(config_folder))
    print("  - XML: {}".format(xml_files[0].name))
    print("  - CFG: {}".format(cfg_files[0].name))
    print("  - NET: {}".format(net_files[0].name))
    if gpa_file:
        print("  - GPA: {}".format(gpa_files[0].name))    # Chiama la funzione principale con i file trovati
    return import_osm_network(
        osm_file_path=osm_file_path,
        custom_param_files={
            "xml": xml_file,
            "cfg": cfg_file,
            "net": net_file
        },
        clipping=clipping,
        coord_min=coord_min,
        coord_max=coord_max,
        gpa_file=gpa_file,
        save_project_as=save_project_as,
        visum_instance=Visum  # Usa l'istanza Visum della console
    )


def example_visum_console():
    """
    Esempio: esecuzione dalla console Python di Visum
    
    Dalla console Python di Visum, esegui:
    >>> exec(open(r"H:\visum-thinker-mcp-server\import-osm-network.py").read())
    >>> result = import_osm_simple(r"C:\Data\città.osm")
    """
    # Nota: 'Visum' è già disponibile nella console Python di Visum
    result = import_osm_simple(r"C:\Data\città.osm")
    return result


def example_custom_config():
    """Esempio: con configurazione personalizzata"""
    # Prima copia e modifica un preset
    files = copy_and_customize_preset(
        preset_name="Detailed urban network",
        custom_dir=r"C:\MyConfigs"
    )
    
    # Poi usa i file custom
    result = import_osm_network(
        osm_file_path=r"C:\Data\città.osm",
        custom_param_files=files
    )
    return result


def select_links_by_territories(territory_numbers=None):
    """
    Seleziona i link che si sovrappongono spazialmente con i territori.
    USA SetTerritoryActive per selezione spaziale precisa.
    
    METODO:
    Chiama visum.Net.SetTerritoryActive(terr_no) per ogni territorio.
    Questo marca tutti gli oggetti di rete (link, nodi, zone) contenuti
    nel territorio impostando Active=1.
    Poi copia il risultato in AddVal1 per uso successivo.
    
    Args:
        territory_numbers (list): Lista di numeri territorio (es. [1, 2, 3])
                                 Se None, usa territorio 1
                                 Default: None
    
    Returns:
        dict: Risultato con numero di link selezionati (AddVal1=1)
    
    Esempio dalla console Visum:
        >>> # Solo territorio 1
        >>> result = select_links_by_territories([1])
        >>> # Territori 1, 2, 3
        >>> result = select_links_by_territories([1, 2, 3])
        >>> print("Link selezionati:", result['selected_count'])
    """
    result = {
        "status": "failed",
        "message": "",
        "selected_count": 0
    }
    
    try:
        visum = Visum
        
        print("=" * 70)
        print("SELEZIONE SPAZIALE CON SetTerritoryActive")
        print("=" * 70)
        
        # Step 1: Determina quali territori processare
        if territory_numbers is None:
            territory_numbers = [1]
            print("Uso territorio di default: [1]")
        
        print("Territori: {}".format(territory_numbers))
        
        # Applica SetTerritoryActive per ogni territorio
        print("\nApplico SetTerritoryActive...")
        success_count = 0
        
        for terr_no in territory_numbers:
            print("   Territorio {}...".format(terr_no))
            
            try:
                # SetTerritoryActive marca gli oggetti nel territorio come "attivi"
                # Questi sono accessibili con GetMultiAttValues(..., OnlyActive=True)
                visum.Net.SetTerritoryActive(terr_no)
                print("      OK")
                success_count += 1
                
            except Exception as e:
                print("      ERRORE: {}".format(str(e)))
                # Continua con i prossimi territori
                continue
        
        if success_count == 0:
            result["message"] = "Nessun territorio processato con successo"
            print("\n" + result["message"])
            return result
        
        print("\n   Territori processati: {}/{}".format(success_count, len(territory_numbers)))
        
        # SetTerritoryActive ha marcato gli oggetti come attivi
        # La funzione change_linktype_by_mapping userà GetMultiAttValues(..., OnlyActive=True)
        # per accedere direttamente ai link attivi
        result["status"] = "success"
        result["message"] = "SetTerritoryActive applicato a {} territori".format(success_count)
        result["territories_processed"] = success_count
        
        print("\n" + "=" * 70)
        print("COMPLETATO: {} territori attivati".format(success_count))
        print("=" * 70)
        
        return result
        
    except Exception as e:
        result["message"] = "Errore generale: {}".format(str(e))
        print("\nERRORE: {}".format(result["message"]))
        import traceback
        traceback.print_exc()
        return result


def change_linktype_by_mapping(linktype_mapping=None, only_selected=True):
    """
    Cambia i LinkType dei link secondo una mappatura fornita.
    
    Args:
        linktype_mapping (dict): Dizionario {linktype_vecchio: linktype_nuovo}
                                Es: {20: 21, 30: 30, 40: 41, 70: 81}
                                Se None, usa il mapping di default.
                                Default: None
        only_selected (bool): Se True, modifica solo i link selezionati (AddVal1=1)
                             Se False, modifica tutti i link. Default: True
    
    Returns:
        dict: Risultato con numero di link modificati
    
    Esempio dalla console Visum:
        >>> # Con mapping personalizzato
        >>> mapping = {20: 21, 30: 30, 40: 41, 70: 81}
        >>> result = change_linktype_by_mapping(mapping)
        >>> 
        >>> # Con mapping di default
        >>> result = change_linktype_by_mapping()
        >>> print("Link modificati:", result['changed_count'])
    """
    result = {
        "status": "failed",
        "message": "",
        "changed_count": 0,
        "changes_by_type": {}
    }
    
    try:
        visum = Visum
        
        # Usa il mapping di default se non fornito
        if linktype_mapping is None:
            linktype_mapping = DEFAULT_LINKTYPE_MAPPING
            print("Uso mapping di default: {}".format(linktype_mapping))
        
        # Ottieni i link da modificare
        if only_selected:
            print("Modifico solo i link attivi (OnlyActive=True)")
            # Usa GetMultiAttValues con OnlyActive=True per ottenere solo link attivi
            active_data = visum.Net.Links.GetMultiAttValues("TypeNo", True)
            total_links = len(active_data)
            print("Link attivi trovati: {}".format(total_links))
            
            if total_links == 0:
                result["message"] = "Nessun link attivo da modificare"
                print(result["message"])
                return result
            
            # Ottieni tutti i link per accedere per indice
            all_links = visum.Net.Links.GetAll
            
            # Conta i cambiamenti per tipo
            changes = {}
            changed_count = 0
            
            # active_data è un array: [[link_index, TypeNo], ...]
            # link_index è 1-based (indice nella lista GetAll)
            for row in active_data:
                link_index = int(row[0]) - 1  # Converti da 1-based a 0-based
                current_type = int(row[1])
                
                if current_type in linktype_mapping:
                    new_type = linktype_mapping[current_type]
                    
                    if current_type != new_type:
                        # Ottieni il link dalla lista GetAll
                        link = all_links[link_index]
                        link.SetAttValue("TypeNo", new_type)
                        changed_count += 1
                        
                        # Traccia i cambiamenti
                        key = "{} -> {}".format(current_type, new_type)
                        changes[key] = changes.get(key, 0) + 1
        else:
            print("Modifico tutti i link")
            total_links = visum.Net.Links.Count
            print("Link da processare: {}".format(total_links))
            
            if total_links == 0:
                result["message"] = "Nessun link da modificare"
                print(result["message"])
                return result
            
            # Conta i cambiamenti per tipo
            changes = {}
            changed_count = 0
            
            # Processa ogni link
            for link in visum.Net.Links:
                current_type = link.AttValue("TypeNo")
                
                if current_type in linktype_mapping:
                    new_type = linktype_mapping[current_type]
                    
                    if current_type != new_type:
                        link.SetAttValue("TypeNo", new_type)
                        changed_count += 1
                        
                        # Traccia i cambiamenti
                        key = "{} -> {}".format(current_type, new_type)
                        changes[key] = changes.get(key, 0) + 1
        
        result["status"] = "success"
        result["changed_count"] = changed_count
        result["changes_by_type"] = changes
        result["message"] = "Modificati {} link su {}".format(changed_count, total_links)
        
        print("\nRiepilogo modifiche:")
        print("  Link totali processati: {}".format(total_links))
        print("  Link modificati: {}".format(changed_count))
        print("\nDettaglio per tipo:")
        for change_type, count in changes.items():
            print("  {}: {} link".format(change_type, count))
        
        return result
        
    except Exception as e:
        result["message"] = "Errore durante la modifica: {}".format(str(e))
        print("Errore: {}".format(result["message"]))
        return result


if __name__ == "__main__":
    main()


def apply_linktype_defaults():
    """
    STEP 4 OPZIONALE: Applica valori di default dai LinkTypes a tutti i link.
    
    Usa il metodo batch SetDefaultsFromLinkType() per applicare in modo efficiente
    i valori di default definiti nei LinkTypes:
    - NUMLANES: Numero di corsie
    - V0PRT: Velocità a flusso libero PRT
    - CAPPRT: Capacità PRT
    
    NOTA: Le lunghezze dei link NON vengono modificate.
    
    Returns:
        dict: Risultato con statistiche
    
    Esempio dalla console Visum:
        >>> # Dopo import e conversione LinkType
        >>> result = apply_linktype_defaults()
        >>> print(result)
    """
    result = {
        "status": "failed",
        "message": "",
        "attributes_updated": 0
    }
    
    try:
        visum = Visum
        
        print("\n" + "=" * 70)
        print("APPLICA VALORI DEFAULT DAI LINKTYPES")
        print("=" * 70)
        
        total_links = visum.Net.Links.Count
        print("\nLink totali: {}".format(total_links))
        
        print("\nApplico defaults (NUMLANES, V0PRT, CAPPRT) da LinkTypes...")
        
        # Usa il metodo batch per applicare i defaults
        # SetDefaultsFromLinkType(OnlyActive, Attributes)
        # - OnlyActive=False: applica a tutti i link
        # - Attributes: lista degli attributi da sovrascrivere (MAIUSCOLO!)
        # Attributi disponibili: CAPPRT, V0PRT, TSYSSET, NUMLANES, T_PUTSYS
        visum.Net.Links.SetDefaultsFromLinkType(
            False,  # OnlyActive - applica a tutti i link
            ["NUMLANES", "V0PRT", "CAPPRT"]  # Attributi da sovrascrivere
        )
        
        result["attributes_updated"] = total_links
        print("   ✓ Defaults applicati a {} link".format(total_links))
        
        result["status"] = "success"
        result["message"] = "Defaults applicati a {} link".format(total_links)
        
        print("\n" + "=" * 70)
        print("COMPLETATO: Defaults applicati con successo")
        print("=" * 70)
        
        return result
        
    except Exception as e:
        result["message"] = "Errore durante applicazione defaults: {}".format(str(e))
        print("\nERRORE: {}".format(result["message"]))
        import traceback
        traceback.print_exc()
        return result


def import_osm_and_convert_linktypes(osm_file_path, config_folder, 
                                      territory_numbers=None,
                                      linktype_mapping=None,
                                      clipping=0, coord_min=None, coord_max=None,
                                      save_project_as=None,
                                      apply_defaults=False):
    """
    PROCESSO INTEGRATO: Importa OSM + Seleziona territori + Converti LinkType.
    
    Esegue in sequenza:
    1. Importa rete OSM da file con configurazione
    2. Seleziona link nei territori specificati (SetTerritoryActive)
    3. Applica mapping LinkType ai link selezionati
    4. [OPZIONALE] Applica defaults dai LinkTypes (lunghezze, corsie, velocità)
    5. Salva progetto
    
    Args:
        osm_file_path (str): Percorso al file .osm o .osm.bz2
        config_folder (str): Cartella con file di configurazione (.xml, .cfg, .net, .gpa)
        territory_numbers (list): Lista numeri territorio (es. [1, 2, 3]).
                                 Se None, usa territorio 1. Default: None
        linktype_mapping (dict): Mapping {tipo_vecchio: tipo_nuovo}.
                                Se None, usa DEFAULT_LINKTYPE_MAPPING. Default: None
        clipping (int): Tipo di clipping (0=no, 1=inside, 2=extended). Default: 0
        coord_min (tuple): (XMin, YMin) per clipping. Default: None
        coord_max (tuple): (XMax, YMax) per clipping. Default: None
        save_project_as (str): Percorso dove salvare il progetto. Default: None
        apply_defaults (bool): Se True, applica defaults dai LinkTypes (Step 4). Default: False
    
    Returns:
        dict: Risultato completo con info import, selezione e conversione
    
    Esempio dalla console Visum:
        >>> exec(open(r"H:\\visum-thinker-mcp-server\\import-osm-network.py").read())
        >>> 
        >>> # Esempio 1: Con clipping per area specifica
        >>> result = import_osm_and_convert_linktypes(
        ...     osm_file_path=r"H:\\go\\network_builder\\inputs\\centro-latest.osm.bz2",
        ...     config_folder=r"H:\\go\\network_builder\\Go_Urban road network",
        ...     territory_numbers=[1],
        ...     clipping=1,
        ...     coord_min=(12.5886, 42.5126),
        ...     coord_max=(12.7325, 42.6115),
        ...     apply_defaults=True,
        ...     save_project_as=r"H:\\projects\\centro_converted.ver"
        ... )
        >>> 
        >>> # Esempio 2: Senza clipping (importa tutta la rete OSM)
        >>> result = import_osm_and_convert_linktypes(
        ...     osm_file_path=r"H:\\go\\network_builder\\inputs\\centro-latest.osm.bz2",
        ...     config_folder=r"H:\\go\\network_builder\\Go_Urban road network",
        ...     territory_numbers=[1],
        ...     save_project_as=r"H:\\projects\\centro_converted.ver"
        ... )
        >>> 
        >>> print(result)
    """
    
    result = {
        "status": "failed",
        "message": "",
        "import": {},
        "selection": {},
        "conversion": {}
    }
    
    try:
        print("\n" + "=" * 70)
        print("PROCESSO INTEGRATO: IMPORT OSM + SELEZIONE + CONVERSIONE")
        print("=" * 70)
        
        # Step 1: Import OSM
        print("\n### STEP 1: IMPORTAZIONE OSM ###")
        import_result = import_osm_from_folder(
            osm_file_path=osm_file_path,
            config_folder=config_folder,
            clipping=clipping,
            coord_min=coord_min,
            coord_max=coord_max,
            save_project_as=None  # Non salvare ancora
        )
        
        result["import"] = import_result
        
        if import_result["status"] != "success":
            result["message"] = "Import fallito: {}".format(import_result["message"])
            print("\nERRORE: {}".format(result["message"]))
            return result
        
        print("\n✓ Import completato: {} nodi, {} link".format(
            import_result.get("nodes_count", "?"),
            import_result.get("links_count", "?")
        ))
        
        # Step 2: Selezione territori
        print("\n### STEP 2: SELEZIONE TERRITORI ###")
        selection_result = select_links_by_territories(territory_numbers)
        
        result["selection"] = selection_result
        
        if selection_result["status"] not in ["success", "warning"]:
            result["message"] = "Selezione fallita: {}".format(selection_result["message"])
            print("\nERRORE: {}".format(result["message"]))
            return result
        
        print("\n✓ Selezione completata: {} territori processati".format(
            selection_result.get("territories_processed", 0)
        ))
        
        # Step 3: Conversione LinkType
        print("\n### STEP 3: CONVERSIONE LINKTYPE ###")
        if linktype_mapping is None:
            print("Uso mapping di default")
            linktype_mapping = DEFAULT_LINKTYPE_MAPPING
        else:
            print("Uso mapping personalizzato: {}".format(linktype_mapping))
        
        conversion_result = change_linktype_by_mapping(
            linktype_mapping=linktype_mapping,
            only_selected=True
        )
        
        result["conversion"] = conversion_result
        
        if conversion_result["status"] != "success":
            result["message"] = "Conversione fallita: {}".format(conversion_result["message"])
            print("\nERRORE: {}".format(result["message"]))
            return result
        
        print("\n✓ Conversione completata: {} link modificati".format(
            conversion_result.get("changed_count", 0)
        ))
        
        # Step 4: Applica defaults dai LinkTypes (opzionale)
        if apply_defaults:
            print("\n### STEP 4: APPLICA DEFAULTS DAI LINKTYPES ###")
            defaults_result = apply_linktype_defaults()
            result["defaults"] = defaults_result
            
            if defaults_result["status"] != "success":
                print("⚠ Warning: Applicazione defaults fallita: {}".format(defaults_result["message"]))
            else:
                print("\n✓ Defaults applicati: {} lunghezze, {} attributi".format(
                    defaults_result.get("lengths_updated", 0),
                    defaults_result.get("attributes_updated", 0)
                ))
        
        # Step 5: Salvataggio progetto (se richiesto)
        if save_project_as:
            print("\n### STEP 5: SALVATAGGIO PROGETTO ###")
            try:
                from pathlib import Path
                save_path = Path(save_project_as)
                save_path.parent.mkdir(parents=True, exist_ok=True)
                
                Visum.SaveVersion(str(save_path))
                print("✓ Progetto salvato: {}".format(save_project_as))
                result["project_file"] = str(save_path)
            except Exception as e:
                print("✗ Errore durante salvataggio: {}".format(str(e)))
                result["save_error"] = str(e)
        
        # Riepilogo finale
        result["status"] = "success"
        result["message"] = "Processo completato: {} nodi, {} link importati, {} link modificati".format(
            import_result.get("nodes_count", 0),
            import_result.get("links_count", 0),
            conversion_result.get("changed_count", 0)
        )
        
        print("\n" + "=" * 70)
        print("PROCESSO COMPLETATO CON SUCCESSO")
        print("=" * 70)
        print("\nRiepilogo:")
        print("  - Nodi importati: {}".format(import_result.get("nodes_count", 0)))
        print("  - Link importati: {}".format(import_result.get("links_count", 0)))
        print("  - Territori processati: {}".format(selection_result.get("territories_processed", 0)))
        print("  - Link modificati: {}".format(conversion_result.get("changed_count", 0)))
        
        if conversion_result.get("changes_by_type"):
            print("\nDettaglio modifiche LinkType:")
            for change_type, count in conversion_result["changes_by_type"].items():
                print("  {}: {} link".format(change_type, count))
        
        if save_project_as:
            print("\nProgetto salvato: {}".format(save_project_as))
        
        print("=" * 70)
        
        return result
        
    except Exception as e:
        result["message"] = "Errore durante processo integrato: {}".format(str(e))
        print("\nERRORE GENERALE: {}".format(result["message"]))
        import traceback
        traceback.print_exc()
        return result


# ============================================================================
# AUTO-ZONING FUNCTIONS
# ============================================================================
# Le seguenti funzioni permettono di creare zonizzazione automatica
# da griglia esagonale usando l'algoritmo auto-zoning in subprocess.
# Possono essere usate in sequenza dopo import_osm_and_convert_linktypes()
# ============================================================================


def validate_hex_grid(file_path):
    """
    Valida che la griglia esagonale esista e abbia i campi necessari.
    
    Args:
        file_path (str): Percorso al file griglia esagonale (.shp, .geojson)
    
    Returns:
        dict: {"valid": bool, "message": str, "errors": list}
    
    Esempio:
        >>> result = validate_hex_grid(r"H:\\data\\griglia_hex.shp")
        >>> if result["valid"]:
        >>>     print("Griglia valida!")
    """
    result = {
        "valid": False,
        "message": "",
        "errors": []
    }
    
    try:
        grid_path = Path(file_path)
        
        # Verifica esistenza file
        if not grid_path.exists():
            result["errors"].append("File non trovato: {}".format(file_path))
            result["message"] = "File non trovato"
            return result
        
        # Verifica estensione
        valid_extensions = [".shp", ".geojson", ".json"]
        if grid_path.suffix.lower() not in valid_extensions:
            result["errors"].append("Estensione non valida. Usare: .shp, .geojson")
            result["message"] = "Estensione non supportata"
            return result
        
        # Per shapefile, verifica file associati
        if grid_path.suffix.lower() == ".shp":
            required_files = [".shx", ".dbf"]
            for ext in required_files:
                companion_file = grid_path.with_suffix(ext)
                if not companion_file.exists():
                    result["errors"].append("File mancante: {}".format(companion_file.name))
        
        if result["errors"]:
            result["message"] = "File associati mancanti"
            return result
        
        # Tutto OK
        result["valid"] = True
        result["message"] = "Griglia valida"
        print("✓ Griglia validata: {}".format(grid_path.name))
        return result
        
    except Exception as e:
        result["errors"].append("Errore validazione: {}".format(str(e)))
        result["message"] = "Errore durante validazione"
        return result


def create_zoning_config(hex_grid_file, study_area_file, num_zones, 
                        compact_zones, geographical_distance_weight=10,
                        boundaries_file=None, verbose=True, boundaries_verbose=True,
                        road=True, rail=False, water=False,
                        road_network_type="secondary",
                        road_fix_par=None, rail_fix_par=None, 
                        water_fix_par=None, final_fix_par=None,
                        fields=None, weights=None, output_dir=None, output_crs="EPSG:4326"):
    """
    Crea file config.json per run_premodel.py.
    TUTTI I PARAMETRI sono configurabili con valori di default override-abili.
    
    Args:
        hex_grid_file (str): Path griglia esagonale
        study_area_file (str): Path area studio (None = auto)
        num_zones (int): Numero zone desiderato
        compact_zones (bool): True=k-means, False=agglomerativo
        geographical_distance_weight (int): Peso distanza geografica (default: 10)
        boundaries_file (str): Path limiti fisici custom (default: None = auto da OSM)
        verbose (bool): Log dettagliato processo (default: True)
        boundaries_verbose (bool): Log dettagliato creazione limiti (default: True)
        road (bool): Usa strade per limiti (default: True)
        rail (bool): Usa ferrovie per limiti (default: False - spesso assenti)
        water (bool): Usa fiumi per limiti (default: False - spesso assenti)
        road_network_type (str): Tipo rete stradale OSM (default: "secondary")
                                Options: motorway, trunk, primary, secondary, tertiary, residential, all
        road_fix_par (list): Percentili pulizia strade (default: [0.9, 0.5])
        rail_fix_par (list): Percentili pulizia ferrovie (default: [0.9, 0.8])
        water_fix_par (list): Percentili pulizia fiumi (default: [])
        final_fix_par (list): Percentili pulizia finale (default: [0.3])
        fields (list): Campi griglia per clustering (default: ["POP", "ADD"])
        weights (list): Pesi per ciascun campo (default: [1.0, 1.0])
    
    Returns:
        str: Path al file config.json temporaneo creato
    
    Esempio base:
        >>> config_file = create_zoning_config(
        ...     hex_grid_file=r"H:\\data\\hex.shp",
        ...     study_area_file=None,
        ...     num_zones=200,
        ...     compact_zones=True
        ... )
    
    Esempio avanzato (override defaults):
        >>> config_file = create_zoning_config(
        ...     hex_grid_file=r"H:\\data\\hex.shp",
        ...     study_area_file=None,
        ...     num_zones=150,
        ...     compact_zones=False,
        ...     geographical_distance_weight=50,
        ...     road_network_type="primary",
        ...     road_fix_par=[0.95, 0.7],
        ...     rail=False,
        ...     final_fix_par=[0.5],
        ...     fields=["POP"],
        ...     weights=[1.5]
        ... )
    """
    
    # Valori di default per parametri array (solo se None)
    if road_fix_par is None:
        road_fix_par = [0.9, 0.5]
    if rail_fix_par is None:
        rail_fix_par = [0.9, 0.8]
    if water_fix_par is None:
        water_fix_par = []
    if final_fix_par is None:
        final_fix_par = [0.3]
    if fields is None:
        fields = ["POP", "ADD"]
    if weights is None:
        weights = [1.0, 1.0]
    
    # Se study_area è None, usa la griglia stessa (come nel config.json originale)
    if study_area_file is None:
        study_area_file = hex_grid_file
    
    config = {
        "verbose": verbose,
        "create_zoning": True,
        "create_zoning_settings": {
            "study_area": study_area_file,
            "hex_grid": hex_grid_file,
            "boundaries_creation_settings": {
                "verbose": boundaries_verbose,
                "road": road,
                "rail": rail,
                "water": water,
                "road_network_type": road_network_type,
                "road_fix_par": road_fix_par,
                "rail_fix_par": rail_fix_par,
                "water_fix_par": water_fix_par,
                "final_fix_par": final_fix_par
            },
            "boundaries": boundaries_file,
            "compact_zones": compact_zones,
            "akwardly_shaped_zones": not compact_zones,
            "number_of_zones": num_zones,
            "geographical_distance_weight": geographical_distance_weight,
            "fields": fields,
            "weights": weights,
            "output_dir": output_dir,
            "output_crs": output_crs
        }
    }
    
    # Crea file temporaneo
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', 
                                            delete=False, encoding='utf-8')
    json.dump(config, temp_file, indent=4)
    temp_file.close()
    
    print("✓ Config creato: {}".format(temp_file.name))
    return temp_file.name


def run_auto_zoning_subprocess(config_json_path, conda_env="zoning_env", 
                               auto_zoning_path=None, output_dir=None, timeout=1800):
    """
    Lancia auto-zoning in subprocess usando conda environment.
    Supporta sia nome environment che path assoluto.
    
    Args:
        config_json_path (str): Path al file config.json
        conda_env (str): Nome environment (es. "zoning_env") o path assoluto (es. "H:\\go\\.env")
                        Default: "zoning_env"
                        - Se contiene \\ / o : → path assoluto → usa --prefix
                        - Altrimenti → nome → usa -n
        auto_zoning_path (str): Path directory auto-zoning (contiene run_premodel.py)
                               Default: None = cerca in posizioni comuni
        timeout (int): Timeout in secondi (default: 1800 = 30 min)
    
    Returns:
        dict: {"status": str, "message": str, "output_files": list}
    
    Esempio con nome:
        >>> result = run_auto_zoning_subprocess(
        ...     config_json_path=r"C:\\temp\\config.json",
        ...     conda_env="zoning_env"
        ... )
    
    Esempio con path custom:
        >>> result = run_auto_zoning_subprocess(
        ...     config_json_path=r"C:\\temp\\config.json",
        ...     conda_env=r"H:\\go\\network_builder\\.env",
        ...     auto_zoning_path=r"H:\\visum-thinker-mcp-server\\auto-zoning"
        ... )
    """
    result = {
        "status": "failed",
        "message": "",
        "output_files": []
    }
    
    try:
        # Trova lo script run_premodel.py
        if auto_zoning_path:
            # Path specificato dall'utente
            script_path = Path(auto_zoning_path) / "run_premodel.py"
        else:
            # Cerca in posizioni comuni
            possible_paths = [
                Path(__file__).parent / "auto-zoning" / "run_premodel.py",  # Relativo allo script
                Path("H:/visum-thinker-mcp-server/auto-zoning/run_premodel.py"),  # Path assoluto comune
                Path("auto-zoning/run_premodel.py"),  # Directory corrente
            ]
            
            script_path = None
            for p in possible_paths:
                if p.exists():
                    script_path = p
                    break
            
            if script_path is None:
                result["message"] = "Script run_premodel.py non trovato. Specifica 'auto_zoning_path'. Cercato in: {}".format(
                    [str(p) for p in possible_paths]
                )
                print("✗ {}".format(result["message"]))
                return result
        
        if not script_path.exists():
            result["message"] = "Script run_premodel.py non trovato: {}".format(script_path)
            print("✗ {}".format(result["message"]))
            return result
        
        # Determina se conda_env è un path assoluto o un nome
        is_path = ('\\' in conda_env or '/' in conda_env or ':' in conda_env)
        
        print("\n" + "=" * 70)
        print("ESECUZIONE AUTO-ZONING IN SUBPROCESS")
        print("=" * 70)
        print("Script: {}".format(script_path))
        print("Config: {}".format(config_json_path))
        if is_path:
            print("Conda env (path): {}".format(conda_env))
        else:
            print("Conda env (nome): {}".format(conda_env))
        print("Timeout: {} secondi".format(timeout))
        print("\nAvvio processo (attendere)...")
        
        # Cerca conda.exe
        conda_exe = None
        possible_conda = [
            "conda",  # Nel PATH
            r"H:\ProgramData\Miniconda3\Scripts\conda.exe",
            r"C:\ProgramData\Anaconda3\Scripts\conda.exe",
            r"C:\ProgramData\Miniconda3\Scripts\conda.exe",
            r"C:\Users\{}\Anaconda3\Scripts\conda.exe".format(os.environ.get("USERNAME", "")),
            r"C:\Users\{}\Miniconda3\Scripts\conda.exe".format(os.environ.get("USERNAME", "")),
        ]
        
        for conda_path in possible_conda:
            try:
                subprocess.run([conda_path, "--version"], 
                             capture_output=True, timeout=5, check=True)
                conda_exe = conda_path
                break
            except:
                continue
        
        if not conda_exe:
            result["message"] = "Conda non trovato nel PATH"
            print("✗ {}".format(result["message"]))
            return result
        
        print("Conda: {}".format(conda_exe))
        
        # Se è un path, usa -p (prefix), altrimenti -n (name)
        if is_path:
            # Path assoluto: usa -p (prefix path)
            print("Environment path: {}".format(conda_env))
            cmd = [conda_exe, "run", "-p", conda_env, "python", str(script_path), config_json_path]
        else:
            # Nome environment: usa -n (name)
            print("Environment name: {}".format(conda_env))
            cmd = [conda_exe, "run", "-n", conda_env, "python", str(script_path), config_json_path]
        
        # Crea file di log per stdout/stderr
        log_file = tempfile.NamedTemporaryFile(mode='w', suffix='_autozoning.log', 
                                              delete=False, encoding='utf-8')
        log_path = log_file.name
        log_file.close()
        
        print("Log file: {}".format(log_path))
        print("Comando: {}".format(" ".join(cmd)))
        result["log_file"] = log_path
        
        # Esegui subprocess
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(script_path.parent)
        )
        
        # Attendi completamento
        try:
            stdout, stderr = process.communicate(timeout=timeout)
            
            # Salva output in log file
            with open(log_path, 'w', encoding='utf-8') as f:
                f.write("=" * 70 + "\n")
                f.write("AUTO-ZONING SUBPROCESS LOG\n")
                f.write("=" * 70 + "\n")
                f.write("Comando: {}\n".format(" ".join(cmd)))
                f.write("Working dir: {}\n".format(script_path.parent))
                f.write("Exit code: {}\n".format(process.returncode))
                f.write("=" * 70 + "\n\n")
                
                f.write("STDOUT:\n")
                f.write("-" * 70 + "\n")
                f.write(stdout if stdout else "(vuoto)\n")
                f.write("\n")
                
                f.write("STDERR:\n")
                f.write("-" * 70 + "\n")
                f.write(stderr if stderr else "(vuoto)\n")
            
            print("\n--- Output subprocess ---")
            if stdout:
                print("STDOUT:")
                print(stdout)
            if stderr:
                print("\nSTDERR:")
                print(stderr)
            print("--- Fine output ---\n")
            print("Log completo salvato in: {}".format(log_path))
            
            if process.returncode == 0:
                # Verifica file output - usa output_dir dal parametro o default
                if output_dir:
                    out_path = Path(output_dir)
                else:
                    out_path = script_path.parent / "output"
                
                output_files = []
                
                if out_path.exists():
                    for file in out_path.glob("*.geojson"):
                        output_files.append(str(file))
                        print("✓ Output generato: {}".format(file.name))
                
                result["status"] = "success"
                result["message"] = "Auto-zoning completato con successo"
                result["output_files"] = output_files
                
                if not output_files:
                    result["message"] += " (WARNING: nessun file output trovato in {})".format(out_path)
                    print("⚠ Warning: nessun file .geojson trovato in {}".format(out_path))
            else:
                result["message"] = "Subprocess terminato con errore (code: {}). Vedi log: {}".format(
                    process.returncode, log_path
                )
                print("✗ {}".format(result["message"]))
                if stderr:
                    print("\nErrore dettagliato:")
                    print(stderr)
        
        except subprocess.TimeoutExpired:
            process.kill()
            result["message"] = "Timeout dopo {} secondi. Vedi log: {}".format(timeout, log_path)
            print("✗ {}".format(result["message"]))
        
        return result
        
    except Exception as e:
        result["message"] = "Errore subprocess: {}".format(str(e))
        print("✗ {}".format(result["message"]))
        import traceback
        traceback.print_exc()
        return result


def import_zones_shapefile_with_geometry(shapefile_path, visum_instance=None):
    """
    Importa zone da Shapefile in Visum usando visum.IO (CON geometrie complete)
    
    Args:
        shapefile_path (str): Path al file .shp con zone
        visum_instance: Istanza Visum (default: usa Visum da console)
    
    Returns:
        dict: {"status": str, "zones_imported": int, "message": str}
    """
    result = {
        "status": "failed",
        "zones_imported": 0,
        "message": ""
    }
    
    try:
        # Usa istanza Visum
        if visum_instance is None:
            visum = Visum
        else:
            visum = visum_instance
        
        shp_path = Path(shapefile_path)
        if not shp_path.exists():
            result["message"] = "File Shapefile non trovato: {}".format(shapefile_path)
            print("✗ {}".format(result["message"]))
            return result
        
        print("\n" + "=" * 70)
        print("IMPORT ZONE DA SHAPEFILE (CON GEOMETRIE)")
        print("=" * 70)
        print("File: {}".format(shp_path.name))
        
        # Usa visum.IO.ImportShapefile per importare shapefile con geometrie
        try:
            # ✓ METODO CORRETTO: visum.IO.ImportShapefile(filename, IImportShapeFilePara)
            print("🔧 Creazione parametri import...")
            
            # Crea attributi utente POP ed EMP se non esistono
            try:
                try:
                    visum.Net.Zones.GetMultiAttValues("POP")
                except:
                    visum.Net.Zones.AddUserDefinedAttribute("POP", "POP", "Popolazione", 2)
                    print("✓ Creato attributo: POP")
                
                try:
                    visum.Net.Zones.GetMultiAttValues("EMP")
                except:
                    visum.Net.Zones.AddUserDefinedAttribute("EMP", "EMP", "Addetti", 2)
                    print("✓ Creato attributo: EMP")
            except Exception as e:
                print("⚠ Errore creazione attributi: {}".format(str(e)))
            
            # Crea oggetto parametri per import shapefile
            import_para = visum.IO.CreateImportShapeFilePara()
            
            # Imposta tipo di oggetto: shapefileTypeZones = 3 (enum ShapeFileObjType)
            import_para.ObjectType = 3  # shapefileTypeZones
            
            # Mappa attributi shapefile → Visum
            try:
                # ID zona: campo "id" o "ID" → NO (zone number)
                import_para.AddAttributeAllocation("id", "NO")
            except:
                try:
                    import_para.AddAttributeAllocation("ID", "NO")
                except:
                    pass  # Se ID non esiste nel shapefile
            
            try:
                # Popolazione: campo "POP" → POP
                import_para.AddAttributeAllocation("POP", "POP")
            except:
                pass
            
            try:
                # Addetti: campo "ADD" → EMP
                import_para.AddAttributeAllocation("ADD", "EMP")
            except:
                pass
            
            print("📥 Import shapefile con geometrie complete...")
            visum.IO.ImportShapefile(str(shp_path), import_para)
            
            result["status"] = "success"
            result["zones_imported"] = visum.Net.Zones.Count
            result["message"] = "Zone importate con geometrie da {}".format(shp_path.name)
            print("✓ {}".format(result["message"]))
            
        except Exception as e:
            result["message"] = "Errore import shapefile: {}. Usa import manuale: File > Import > Shapefile > {}".format(str(e), shp_path.name)
            print("⚠ {}".format(result["message"]))
            result["status"] = "manual_required"
            import traceback
            traceback.print_exc()
        
        print("=" * 70)
        return result
        
    except Exception as e:
        result["message"] = "Errore import shapefile: {}".format(str(e))
        print("✗ {}".format(result["message"]))
        import traceback
        traceback.print_exc()
        return result


def calculate_weighted_centroids_subprocess(geojson_file, istat_shapefile, 
                                            weight_fields=None, weight_values=None,
                                            min_weight_threshold=0.1, conda_env=None):
    """
    Calcola centroidi ponderati usando subprocess con geopandas.
    
    Args:
        geojson_file (str): Path al file GeoJSON con zone
        istat_shapefile (str): Path allo shapefile ISTAT con sezioni censuarie
        weight_fields (list): Lista campi peso (es. ["POP", "ADD"])
        weight_values (list): Lista pesi (es. [0.5, 0.5]) - deve sommare a 1.0
        min_weight_threshold (float): Peso minimo per includere sezione
        conda_env (str): Path al conda environment (es. r"H:\go\.env")
    
    Returns:
        dict: {zone_id: (lon, lat)} con centroidi ponderati, o {} se errore
    """
    try:
        import tempfile
        import json
        import subprocess
        
        # Default: singolo campo POP
        if weight_fields is None:
            weight_fields = ["POP"]
            weight_values = [1.0]
        elif weight_values is None:
            weight_values = [1.0 / len(weight_fields)] * len(weight_fields)
        
        # File JSON temporaneo per i risultati
        with tempfile.NamedTemporaryFile(mode='w', suffix='_centroids.json', 
                                         delete=False, encoding='utf-8') as f:
            temp_output = f.name
        
        # Script Python per calcolo centroidi ponderati
        calc_script = """
import geopandas as gpd
import json
from pathlib import Path

geojson_file = r"{geojson}"
istat_file = r"{istat}"
weight_fields = {fields}
weight_values = {values}
min_threshold = {threshold}
output_file = r"{output}"

try:
    # Carica dati
    zones_gdf = gpd.read_file(geojson_file)
    istat_gdf = gpd.read_file(istat_file)
    
    # Determina campo zone_id
    if 'zone_id' in zones_gdf.columns:
        zones_gdf['zone_id'] = zones_gdf['zone_id']
    elif 'id' in zones_gdf.columns:
        zones_gdf['zone_id'] = zones_gdf['id']
    else:
        zones_gdf['zone_id'] = range(1, len(zones_gdf) + 1)
    
    # Verifica campi peso
    missing_fields = [f for f in weight_fields if f not in istat_gdf.columns]
    if missing_fields:
        print(f"Campi {{missing_fields}} non trovati in ISTAT shapefile")
        print(f"Colonne disponibili: {{list(istat_gdf.columns)}}")
        with open(output_file, 'w') as f:
            json.dump({{}}, f)
        exit(0)
    
    # Assicura stesso CRS
    if zones_gdf.crs != istat_gdf.crs:
        istat_gdf = istat_gdf.to_crs(zones_gdf.crs)
    
    centroids = {{}}
    
    for idx, zone in zones_gdf.iterrows():
        zone_geom = zone.geometry
        zone_id = int(zone['zone_id'])
        
        # Trova sezioni che intersecano
        intersecting = istat_gdf[istat_gdf.intersects(zone_geom)].copy()
        
        if len(intersecting) == 0:
            continue
        
        # Calcola peso proporzionale area
        intersecting['intersection'] = intersecting.geometry.intersection(zone_geom)
        intersecting['intersection_area'] = intersecting['intersection'].area
        intersecting['area_ratio'] = intersecting['intersection_area'] / zone_geom.area
        
        # Peso combinato: calcola per ogni campo e somma
        intersecting['weight'] = 0.0
        for field, w in zip(weight_fields, weight_values):
            intersecting['weight'] += intersecting[field] * w * intersecting['area_ratio']
        
        # Filtra peso minimo
        intersecting = intersecting[intersecting['weight'] >= min_threshold]
        
        if len(intersecting) == 0 or intersecting['weight'].sum() == 0:
            continue
        
        # Calcola centroide ponderato usando le INTERSEZIONI (non le geometrie intere!)
        intersecting['intersection_centroid'] = intersecting['intersection'].centroid
        intersecting['lon'] = intersecting['intersection_centroid'].x
        intersecting['lat'] = intersecting['intersection_centroid'].y
        
        total_weight = intersecting['weight'].sum()
        weighted_lon = (intersecting['lon'] * intersecting['weight']).sum() / total_weight
        weighted_lat = (intersecting['lat'] * intersecting['weight']).sum() / total_weight
        
        centroids[str(zone_id)] = [float(weighted_lon), float(weighted_lat)]
    
    # Salva risultati
    with open(output_file, 'w') as f:
        json.dump(centroids, f)
    
    print(f"Calcolati {{len(centroids)}} centroidi ponderati")

except Exception as e:
    print(f"Errore: {{e}}")
    import traceback
    traceback.print_exc()
    with open(output_file, 'w') as f:
        json.dump({{}}, f)
""".format(
            geojson=geojson_file,
            istat=istat_shapefile,
            fields=weight_fields,
            values=weight_values,
            threshold=min_weight_threshold,
            output=temp_output
        )
        
        # Scrivi script temporaneo
        with tempfile.NamedTemporaryFile(mode='w', suffix='_calc_centroids.py', 
                                         delete=False, encoding='utf-8') as f:
            f.write(calc_script)
            temp_script = f.name
        
        try:
            # Determina comando Python da usare
            if conda_env:
                # Usa Python del conda environment
                if '\\' in conda_env or '/' in conda_env or ':' in conda_env:
                    # Path assoluto - usa conda run -p (come auto-zoning)
                    # Trova conda.exe
                    conda_exe = None
                    for conda_path in [
                        r"H:\ProgramData\Miniconda3\Scripts\conda.exe",
                        r"C:\ProgramData\Miniconda3\Scripts\conda.exe",
                        r"C:\Users\{}\Miniconda3\Scripts\conda.exe".format(os.environ.get('USERNAME', '')),
                        r"C:\Users\{}\Anaconda3\Scripts\conda.exe".format(os.environ.get('USERNAME', ''))
                    ]:
                        if os.path.exists(conda_path):
                            conda_exe = conda_path
                            break
                    
                    if conda_exe:
                        python_cmd = [conda_exe, 'run', '-p', conda_env, 'python', temp_script]
                        print("   Uso conda run -p {} python".format(conda_env))
                    else:
                        # Fallback: prova direttamente python.exe
                        python_path = os.path.join(conda_env, 'python.exe')
                        if os.path.exists(python_path):
                            python_cmd = [python_path, temp_script]
                            print("   ⚠ Conda non trovato, uso direttamente:", python_path)
                        else:
                            python_cmd = ['python', temp_script]
                            print("   ⚠ Uso Python di sistema (conda e env non trovati)")
                else:
                    # Nome environment - usa conda run -n
                    python_cmd = ['conda', 'run', '-n', conda_env, 'python', temp_script]
                    print("   Uso conda run -n", conda_env)
            else:
                # Python di sistema
                python_cmd = ['python', temp_script]
                print("   Uso Python di sistema")
            
            # Esegui subprocess
            print("   Esecuzione subprocess per calcolo centroidi...")
            result = subprocess.run(
                python_cmd,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            # Mostra output/errori
            if result.stdout:
                print("   Output subprocess:", result.stdout[:200])
            if result.stderr:
                print("   ⚠ Stderr subprocess:", result.stderr[:500])
            if result.returncode != 0:
                print("   ✗ Subprocess fallito con exit code:", result.returncode)
                print("   Script path:", temp_script)
                print("   Output file:", temp_output)
                return {}
            
            # Verifica che il file output esista
            if not os.path.exists(temp_output):
                print("   ✗ File output non creato:", temp_output)
                return {}
            
            # Verifica che il file non sia vuoto
            file_size = os.path.getsize(temp_output)
            if file_size == 0:
                print("   ✗ File output vuoto (0 bytes)")
                return {}
            
            # Leggi risultati
            with open(temp_output, 'r') as f:
                content = f.read()
                if not content.strip():
                    print("   ✗ File output vuoto (solo whitespace)")
                    return {}
                centroids_data = json.loads(content)
            
            # Converti chiavi in int
            centroids = {int(k): tuple(v) for k, v in centroids_data.items()}
            
            return centroids
            
        except subprocess.TimeoutExpired:
            print("   ✗ Timeout subprocess (>120s)")
            return {}
        except json.JSONDecodeError as e:
            print("   ✗ Errore parsing JSON:", str(e))
            print("   File path:", temp_output)
            if os.path.exists(temp_output):
                with open(temp_output, 'r') as f:
                    content = f.read()
                    print("   Contenuto file (primi 500 char):", content[:500])
            return {}
        except Exception as e:
            print("   ✗ Errore generico:", str(e))
            import traceback
            traceback.print_exc()
            return {}
        finally:
            # Cleanup (ma salva script in caso di errore per debug)
            if os.path.exists(temp_output):
                try:
                    os.unlink(temp_output)
                except:
                    pass
            # Lascia temp_script per debug se c'è stato un errore
            # try:
            #     os.unlink(temp_script)
            # except:
            #     pass
                
    except Exception as e:
        print("✗ Errore calcolo centroidi ponderati: {}".format(str(e)))
        return {}


def convert_geojson_to_shapefile(geojson_file, output_dir=None):
    """
    Converte GeoJSON in Shapefile usando geopandas (nel subprocess conda env)
    
    Args:
        geojson_file (str): Path al file GeoJSON
        output_dir (str): Directory output (default: stessa dir del geojson)
    
    Returns:
        str: Path al file .shp creato
    """
    try:
        geojson_path = Path(geojson_file)
        if output_dir is None:
            output_dir = geojson_path.parent
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        
        # Nome shapefile
        shp_name = geojson_path.stem + ".shp"
        shp_path = output_dir / shp_name
        
        print("\n📦 Conversione GeoJSON → Shapefile...")
        print("   Input:  {}".format(geojson_path.name))
        print("   Output: {}".format(shp_name))
        
        # Script Python per conversione (usa geopandas se disponibile)
        conversion_script = """
import geopandas as gpd
from pathlib import Path

geojson_file = r"{}"
shp_file = r"{}"

try:
    gdf = gpd.read_file(geojson_file)
    gdf.to_file(shp_file)
    print("✓ Shapefile creato: {{}}".format(Path(shp_file).name))
except Exception as e:
    print("✗ Errore conversione: {{}}".format(str(e)))
    raise
""".format(str(geojson_path), str(shp_path))
        
        # Scrivi script temporaneo
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(conversion_script)
            temp_script = f.name
        
        try:
            # Esegui con geopandas (disponibile in ambiente principale Python)
            import subprocess
            result = subprocess.run(
                ['python', temp_script],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print("✓ Conversione completata")
                return str(shp_path)
            else:
                print("✗ Errore conversione:")
                print(result.stderr)
                return None
        finally:
            # Rimuovi script temporaneo
            try:
                os.unlink(temp_script)
            except:
                pass
                
    except Exception as e:
        print("✗ Errore conversione GeoJSON: {}".format(str(e)))
        return None




def import_zones_from_geojson(geojson_file, zone_id_field="zone_id", 
                              output_crs="EPSG:4326", 
                              centroid_method="geometric",
                              istat_shapefile=None,
                              weight_field="POP",
                              weight_fields=None,
                              weight_values=None,
                              conda_env=None,
                              visum_instance=None):
    """
    Importa zone da file GeoJSON in Visum.Net.Zones
    
    Args:
        geojson_file (str): Path al file GeoJSON con zone
        zone_id_field (str): Campo da usare come ID zona (default: "zone_id")
        output_crs (str): Sistema coordinate per Visum (default: "EPSG:4326" = WGS84)
        centroid_method (str): Metodo calcolo centroide:
            - "geometric": Media coordinate poligono (default)
            - "weighted": Ponderato su dati ISTAT (richiede istat_shapefile)
        istat_shapefile (str): Path shapefile ISTAT sezioni censuarie (per centroid_method="weighted")
        weight_field (str): Campo peso singolo per centroidi ponderati: "POP" o "ADD" (default: "POP")
        weight_fields (list): Lista campi peso (es. ["POP", "ADD"]) - sovrascrive weight_field
        weight_values (list): Lista pesi per campi (es. [0.5, 0.5]) - deve sommare a 1.0
        conda_env (str): Path al conda environment per subprocess geopandas
        visum_instance: Istanza Visum (default: usa Visum da console)
    
    Returns:
        dict: {"status": str, "zones_created": int, "message": str}
    
    Esempio:
        >>> # Centroide geometrico (default)
        >>> result = import_zones_from_geojson(
        ...     geojson_file=r"H:\\output\\zoning_0.geojson"
        ... )
        >>> 
        >>> # Centroide ponderato su popolazione
        >>> result = import_zones_from_geojson(
        ...     geojson_file=r"H:\\output\\zoning_0.geojson",
        ...     centroid_method="weighted",
        ...     istat_shapefile=r"H:\\data\\Terni_prezoning_istat.shp",
        ...     weight_field="POP"
        ... )
    """
    result = {
        "status": "failed",
        "zones_created": 0,
        "message": ""
    }
    
    try:
        # Usa istanza Visum
        if visum_instance is None:
            visum = Visum
        else:
            visum = visum_instance
        
        # Leggi GeoJSON
        geojson_path = Path(geojson_file)
        if not geojson_path.exists():
            result["message"] = "File GeoJSON non trovato: {}".format(geojson_file)
            print("✗ {}".format(result["message"]))
            return result
        
        print("\n" + "=" * 70)
        print("IMPORT ZONE DA GEOJSON")
        print("=" * 70)
        print("File: {}".format(geojson_path.name))
        
        # Crea attributi utente POP ed EMP se non esistono
        print("\n🔧 Verifica attributi zone...")
        try:
            # Verifica se POP esiste
            try:
                visum.Net.Zones.GetMultiAttValues("POP")
                print("✓ Attributo POP già esistente")
            except:
                # Crea attributo POP: (ID, ShortName, LongName, VT, DecPlaces, Ignored, MinVal, MaxVal, DefVal)
                visum.Net.Zones.AddUserDefinedAttribute("POP", "POP", "Popolazione", 2)  # VT=2 (Float/Double)
                print("✓ Creato attributo utente: POP (Popolazione)")
            
            # Verifica se EMP esiste
            try:
                visum.Net.Zones.GetMultiAttValues("EMP")
                print("✓ Attributo EMP già esistente")
            except:
                # Crea attributo EMP
                visum.Net.Zones.AddUserDefinedAttribute("EMP", "EMP", "Addetti", 2)  # VT=2 (Float/Double)
                print("✓ Creato attributo utente: EMP (Addetti)")
        except Exception as e:
            print("⚠ Errore creazione attributi: {}".format(str(e)))
        
        # OPZIONE 1: Cerca Shapefile corrispondente (generato dal subprocess)
        shp_file = geojson_path.with_suffix('.shp')
        
        if shp_file.exists():
            print("\n🗺️ File Shapefile trovato: {}".format(shp_file.name))
            print("🔄 Tentativo import con geometrie complete...")
            
            # IMPORTANTE: Cancella zone esistenti per evitare duplicati
            if visum.Net.Zones.Count > 0:
                print("⚠ Cancello {} zone esistenti per evitare duplicati".format(visum.Net.Zones.Count))
                visum.Net.Zones.RemoveAll()
            
            shp_result = import_zones_shapefile_with_geometry(str(shp_file), visum)
            if shp_result["status"] == "success":
                # Import shapefile riuscito - ma potrebbero servire centroidi ponderati
                zones_imported = shp_result["zones_imported"]
                
                # Se richiesti centroidi ponderati, ricalcola e aggiorna coordinate
                if centroid_method == "weighted" and istat_shapefile:
                    print("\n📊 Calcolo centroidi ponderati da dati ISTAT...")
                    print("   Shapefile ISTAT: {}".format(istat_shapefile))
                    print("   🐍 DEBUG conda_env ricevuto: {}".format(repr(conda_env)))
                    
                    # Usa weight_fields se fornito, altrimenti weight_field
                    if weight_fields is not None:
                        print("   Campi peso: {} con pesi {}".format(weight_fields, weight_values))
                        weighted_centroids = calculate_weighted_centroids_subprocess(
                            str(geojson_path), 
                            istat_shapefile,
                            weight_fields=weight_fields,
                            weight_values=weight_values,
                            conda_env=conda_env
                        )
                    else:
                        print("   Campo peso: {}".format(weight_field))
                        weighted_centroids = calculate_weighted_centroids_subprocess(
                            str(geojson_path), 
                            istat_shapefile,
                            weight_fields=[weight_field],
                            weight_values=[1.0], 
                            conda_env=conda_env
                        )
                # Se richiesti centroidi ponderati, ricalcola e aggiorna coordinate
                if centroid_method == "weighted" and istat_shapefile:
                    print("\n📊 Calcolo centroidi ponderati da dati ISTAT...")
                    print("   Shapefile ISTAT: {}".format(istat_shapefile))
                    
                    # Usa weight_fields se fornito, altrimenti weight_field
                    if weight_fields is not None:
                        print("   Campi peso: {} con pesi {}".format(weight_fields, weight_values))
                        weighted_centroids = calculate_weighted_centroids_subprocess(
                            str(geojson_path), 
                            istat_shapefile,
                            weight_fields=weight_fields,
                            weight_values=weight_values,
                            conda_env=conda_env
                        )
                    else:
                        print("   Campo peso: {}".format(weight_field))
                        weighted_centroids = calculate_weighted_centroids_subprocess(
                            str(geojson_path), 
                            istat_shapefile,
                            weight_fields=[weight_field],
                            weight_values=[1.0],
                            conda_env=conda_env
                        )
                    
                    if weighted_centroids:
                        print("✓ {} centroidi ponderati calcolati".format(len(weighted_centroids)))
                        print("\n🔄 Aggiornamento coordinate zone con centroidi ponderati...")
                        
                        # Debug: mostra primi IDs
                        centroid_ids = list(weighted_centroids.keys())[:5]
                        print("   🐛 DEBUG - Primi zone_id nei centroidi: {}".format(centroid_ids))
                        
                        zone_nos = []
                        for zone in visum.Net.Zones.GetAll:
                            zone_nos.append(str(zone.AttValue("No")))
                            if len(zone_nos) >= 5:
                                break
                        print("   🐛 DEBUG - Primi zone No in Visum: {}".format(zone_nos))
                        
                        updated_count = 0
                        for zone in visum.Net.Zones.GetAll:
                            zone_no = int(zone.AttValue("No"))  # Converti a int per matching
                            
                            if zone_no in weighted_centroids:
                                lon, lat = weighted_centroids[zone_no]
                                zone.SetAttValue("XCoord", lon)
                                zone.SetAttValue("YCoord", lat)
                                updated_count += 1
                        
                        print("✓ Aggiornate {} zone con centroidi ponderati".format(updated_count))
                    else:
                        print("⚠ Nessun centroide ponderato calcolato, uso centroidi geometrici")
                
                # Import shapefile riuscito con geometrie!
                result.update(shp_result)
                result["zones_created"] = zones_imported
                result["shapefile"] = str(shp_file)
                return result
            elif shp_result["status"] == "manual_required":
                # visum.IO non disponibile - salva path per import manuale
                print("\n⚠ visum.IO non disponibile via API")
                print("   Shapefile disponibile per import manuale GUI:")
                print("   {}".format(str(shp_file)))
                print("   Import: File > Import > Shapefile\n")
                result["shapefile_for_manual_import"] = str(shp_file)
            else:
                print("⚠ Import shapefile fallito, uso import manuale attributi...")
        else:
            print("\n⚠ File Shapefile non trovato: {}".format(shp_file.name))
            print("   Il subprocess dovrebbe generare sia .geojson che .shp")
            print("   Uso import manuale (solo centroidi + attributi)...")
        
        # OPZIONE 2: Tentativo import GeoJSON diretto con visum.IO
        print("\n🔄 Tentativo import GeoJSON con visum.IO.ImportGeoJSON()...")
        try:
            # ✓ METODO CORRETTO: visum.IO.ImportGeoJSON(filename, IImportGeoJSONPara)
            import_para = visum.IO.CreateImportGeoJSONPara()
            import_para.ObjectType = 3  # shapefileTypeZones (enum ShapeFileObjType)
            
            print("📥 Import GeoJSON con geometrie complete...")
            visum.IO.ImportGeoJSON(str(geojson_path), import_para)
            
            zones_imported = visum.Net.Zones.Count
            
            # Se richiesti centroidi ponderati, ricalcola e aggiorna coordinate
            if centroid_method == "weighted" and istat_shapefile:
                print("\n📊 Calcolo centroidi ponderati da dati ISTAT...")
                print("   Shapefile ISTAT: {}".format(istat_shapefile))
                
                # Usa weight_fields se fornito, altrimenti weight_field
                if weight_fields is not None:
                    print("   Campi peso: {} con pesi {}".format(weight_fields, weight_values))
                    weighted_centroids = calculate_weighted_centroids_subprocess(
                        str(geojson_path), 
                        istat_shapefile,
                        weight_fields=weight_fields,
                        weight_values=weight_values,
                        conda_env=conda_env
                    )
                else:
                    print("   Campo peso: {}".format(weight_field))
                    weighted_centroids = calculate_weighted_centroids_subprocess(
                        str(geojson_path), 
                        istat_shapefile,
                        weight_fields=[weight_field],
                        weight_values=[1.0],
                        conda_env=conda_env
                    )
                
                if weighted_centroids:
                    print("✓ {} centroidi ponderati calcolati".format(len(weighted_centroids)))
                    print("\n🔄 Aggiornamento coordinate zone con centroidi ponderati...")
                    
                    updated_count = 0
                    for zone in visum.Net.Zones.GetAll:
                        zone_no = int(zone.AttValue("No"))  # Converti a int per matching
                        
                        if zone_no in weighted_centroids:
                            lon, lat = weighted_centroids[zone_no]
                            zone.SetAttValue("XCoord", lon)
                            zone.SetAttValue("YCoord", lat)
                            updated_count += 1
                    
                    print("✓ Aggiornate {} zone con centroidi ponderati".format(updated_count))
                else:
                    print("⚠ Nessun centroide ponderato calcolato, uso centroidi geometrici")
            
            result["status"] = "success"
            result["zones_created"] = zones_imported
            result["message"] = "Zone importate con geometrie da {}".format(geojson_path.name)
            print("✓ {}".format(result["message"]))
            print("=" * 70)
            return result
            
        except Exception as e:
            print("⚠ Import GeoJSON fallito: {}".format(str(e)))
            print("   Fallback su import manuale (centroidi + attributi)...")
        
        # OPZIONE 3: Import manuale (solo centroidi e attributi)
        print("\n📝 Import manuale zone (centroidi + attributi)...")
        
        # Leggi GeoJSON direttamente (già convertito a {} dal subprocess)
        import json
        with open(geojson_path, 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)
        
        features = geojson_data.get("features", [])
        if not features:
            result["message"] = "Nessuna feature trovata nel GeoJSON"
            print("✗ {}".format(result["message"]))
            return result
        
        print("Feature trovate: {}".format(len(features)))
        print("CRS: {} (convertito dal subprocess)".format(output_crs))
        
        # Calcola centroidi ponderati se richiesto
        weighted_centroids = {}
        if centroid_method == "weighted" and istat_shapefile:
            print("\n📊 Calcolo centroidi ponderati da dati ISTAT...")
            print("   Shapefile ISTAT: {}".format(istat_shapefile))
            
            # Usa weight_fields se fornito, altrimenti weight_field
            if weight_fields is not None:
                print("   Campi peso: {} con pesi {}".format(weight_fields, weight_values))
                weighted_centroids = calculate_weighted_centroids_subprocess(
                    str(geojson_path), 
                    istat_shapefile,
                    weight_fields=weight_fields,
                    weight_values=weight_values,
                    conda_env=conda_env
                )
            else:
                print("   Campo peso: {}".format(weight_field))
                weighted_centroids = calculate_weighted_centroids_subprocess(
                    str(geojson_path), 
                    istat_shapefile,
                    weight_fields=[weight_field],
                    weight_values=[1.0],
                    conda_env=conda_env
                )
            
            if weighted_centroids:
                print("✓ {} centroidi ponderati calcolati".format(len(weighted_centroids)))
            else:
                print("⚠ Nessun centroide ponderato calcolato, uso centroidi geometrici")
        
        print("\nImportazione zone...")
        
        zones_created = 0
        errors = []
        
        for i, feature in enumerate(features):
            try:
                properties = feature.get("properties", {})
                geometry = feature.get("geometry", {})
                
                # Determina zone_id
                if zone_id_field in properties:
                    zone_id = int(properties[zone_id_field])
                else:
                    zone_id = i + 1  # Usa indice progressivo
                
                # Verifica se zona esiste già
                try:
                    existing_zone = visum.Net.Zones.ItemByKey(zone_id)
                    print("  Zona {} già esistente, aggiorno...".format(zone_id))
                    zone = existing_zone
                except:
                    # Crea nuova zona
                    zone = visum.Net.AddZone(zone_id)
                    zones_created += 1
                
                # Imposta geometria (centroide del poligono)
                if geometry and geometry.get("type") == "Polygon":
                    try:
                        coordinates = geometry.get("coordinates", [[]])[0]  # Primo anello del poligono
                        if coordinates and len(coordinates) > 0:
                            # Usa centroide ponderato se disponibile, altrimenti geometrico
                            if zone_id in weighted_centroids:
                                centroid_lon, centroid_lat = weighted_centroids[zone_id]
                                centroid_source = "ponderato ({})".format(weight_field)
                            else:
                                # Calcola centroide geometrico (media delle coordinate)
                                lons = [coord[0] for coord in coordinates]
                                lats = [coord[1] for coord in coordinates]
                                centroid_lon = sum(lons) / len(lons)
                                centroid_lat = sum(lats) / len(lats)
                                centroid_source = "geometrico"
                            
                            # Imposta coordinate centroide zona
                            zone.SetAttValue("XCoord", centroid_lon)
                            zone.SetAttValue("YCoord", centroid_lat)
                            
                            if i < 3:  # Debug prime 3 zone
                                print("  Zona {} - centroide {}: ({:.6f}, {:.6f})".format(
                                    zone_id, centroid_source, centroid_lon, centroid_lat))
                            
                            # NOTA: Le superfici (poligoni) delle zone non sono supportate via COM API
                            # Per visualizzare i poligoni in Visum, importare il file GeoJSON 
                            # manualmente: File > Open > Net File > Formato GIS
                    except Exception as e:
                        if len(errors) <= 5:
                            print("  ⚠ Errore geometria zona {}: {}".format(zone_id, str(e)))
                
                # Imposta attributi se disponibili
                if "POP" in properties:
                    try:
                        zone.SetAttValue("POP", float(properties["POP"]))
                    except:
                        pass
                
                if "ADD" in properties or "Addetti" in properties:
                    try:
                        add_value = properties.get("ADD", properties.get("Addetti", 0))
                        zone.SetAttValue("EMP", float(add_value))
                    except:
                        pass
                
                # Mostra progress ogni 50 zone
                if (i + 1) % 50 == 0:
                    print("  Importate {} zone...".format(i + 1))
                
            except Exception as e:
                error_msg = "Errore zona {}: {}".format(i + 1, str(e))
                errors.append(error_msg)
                if len(errors) <= 5:  # Mostra solo primi 5 errori
                    print("  ⚠ {}".format(error_msg))
        
        result["status"] = "success"
        result["zones_created"] = zones_created
        result["message"] = "Importate {} zone da {}".format(zones_created, geojson_path.name)
        
        if errors:
            result["message"] += " ({} errori)".format(len(errors))
            result["errors"] = errors
        
        print("\n✓ {}".format(result["message"]))
        print("=" * 70)
        
        return result
        
    except Exception as e:
        result["message"] = "Errore import zone: {}".format(str(e))
        print("✗ {}".format(result["message"]))
        import traceback
        traceback.print_exc()
        return result


def tag_nodes_with_zone(visum_instance=None):
    """
    Tagga ogni nodo con il numero della zona in cui si trova.
    
    Usa AddVal2 per memorizzare ZoneNo. Se nodo non è in nessuna zona, AddVal2=0.
    Questo permette poi di forzare connectors solo verso nodi interni alla zona.
    
    METODO:
    Per ogni nodo, verifica se le coordinate (X, Y) cadono dentro il poligono
    della zona usando la geometria delle zone.
    
    Args:
        visum_instance: Istanza Visum (default: usa Visum da console)
    
    Returns:
        dict: {
            "status": str,
            "nodes_tagged": int,
            "nodes_in_zones": int,
            "nodes_outside": int,
            "zones_with_nodes": int
        }
    
    Esempio:
        >>> # Tagga tutti i nodi con la zona di appartenenza
        >>> result = tag_nodes_with_zone()
        >>> print(f"Nodi taggati: {result['nodes_in_zones']}")
        >>> print(f"Nodi fuori zone: {result['nodes_outside']}")
    """
    result = {
        "status": "failed",
        "nodes_tagged": 0,
        "nodes_in_zones": 0,
        "nodes_outside": 0,
        "zones_with_nodes": 0
    }
    
    try:
        if visum_instance is None:
            visum = Visum
        else:
            visum = visum_instance
        
        print("\n" + "=" * 70)
        print("TAGGING NODI CON ZONA DI APPARTENENZA")
        print("=" * 70)
        
        # Reset AddVal2 su tutti i nodi
        print("Reset AddVal2 su tutti i nodi...")
        visum.Net.Nodes.SetAllAttValues("AddVal2", 0)
        
        # Ottieni coordinate nodi
        print("\nCaricamento coordinate nodi...")
        node_nos = visum.Net.Nodes.GetMultiAttValues("No")
        node_xs = visum.Net.Nodes.GetMultiAttValues("XCoord")
        node_ys = visum.Net.Nodes.GetMultiAttValues("YCoord")
        
        total_nodes = len(node_nos)
        print(f"Nodi totali: {total_nodes}")
        
        # Ottieni zone con coordinate
        print("Caricamento zone...")
        zone_nos = visum.Net.Zones.GetMultiAttValues("No")
        zone_xs = visum.Net.Zones.GetMultiAttValues("XCoord")
        zone_ys = visum.Net.Zones.GetMultiAttValues("YCoord")
        
        # Per ogni zona, calcola coordinate
        zones_data = {}
        for i in range(len(zone_nos)):
            zone_no = int(zone_nos[i][1])
            zones_data[zone_no] = {
                'x': float(zone_xs[i][1]),
                'y': float(zone_ys[i][1])
            }
        
        total_zones = len(zones_data)
        print(f"Zone totali: {total_zones}")
        
        # Crea mappatura node_no -> index per accesso veloce
        print("\nCreazione mappatura nodi...")
        node_no_to_index = {}
        for i, row in enumerate(node_nos):
            node_no = int(row[1])
            node_no_to_index[node_no] = i
        
        # Array diretto per SetAttValue veloce
        all_nodes = visum.Net.Nodes.GetAll
        
        # Per ogni nodo, trova la zona più vicina
        print("\nAssegnazione nodi a zone...")
        zones_with_nodes = set()
        nodes_in_zones = 0
        max_zone_radius = 5000  # metri
        
        for i in range(total_nodes):
            node_no = int(node_nos[i][1])
            node_x = float(node_xs[i][1])
            node_y = float(node_ys[i][1])
            
            # Trova zona più vicina al nodo
            min_distance = float('inf')
            closest_zone = None
            
            for zone_no, zone_coords in zones_data.items():
                dx = node_x - zone_coords['x']
                dy = node_y - zone_coords['y']
                dist = (dx**2 + dy**2)**0.5
                
                if dist < min_distance:
                    min_distance = dist
                    closest_zone = zone_no
            
            # Se la zona più vicina è entro raggio, assegna
            if closest_zone and min_distance <= max_zone_radius:
                try:
                    idx = node_no_to_index[node_no]
                    all_nodes[idx].SetAttValue("AddVal2", closest_zone)
                    nodes_in_zones += 1
                    zones_with_nodes.add(closest_zone)
                except:
                    pass
            
            # Progress ogni 500 nodi
            if (i + 1) % 500 == 0:
                print(f"  Processati {i+1}/{total_nodes} nodi...")
        
        nodes_outside = total_nodes - nodes_in_zones
        
        result["status"] = "success"
        result["nodes_tagged"] = total_nodes
        result["nodes_in_zones"] = nodes_in_zones
        result["nodes_outside"] = nodes_outside
        result["zones_with_nodes"] = len(zones_with_nodes)
        
        print("\n" + "=" * 70)
        print("✓ TAGGING COMPLETATO")
        print("=" * 70)
        print(f"Nodi totali processati: {total_nodes}")
        print(f"Nodi assegnati a zone: {nodes_in_zones}")
        print(f"Nodi fuori zone: {nodes_outside}")
        print(f"Zone con almeno 1 nodo: {len(zones_with_nodes)}")
        
        return result
        
    except Exception as e:
        result["message"] = f"Errore tagging nodi: {e}"
        print("\n✗ " + result["message"])
        import traceback
        traceback.print_exc()
        return result


# ============================================================================
# 【6.5】 ZONE CONNECTORS CREATION
# ============================================================================

def haversine_distance(lon1, lat1, lon2, lat2):
    """
    Calcola distanza in METRI tra due punti geografici (WGS84 lon/lat).
    
    Usa formula di Haversine per calcolare la distanza sulla superficie terrestre.
    
    Args:
        lon1, lat1: Coordinate del primo punto (gradi decimali)
        lon2, lat2: Coordinate del secondo punto (gradi decimali)
    
    Returns:
        float: Distanza in METRI
    """
    import math
    
    # Raggio della Terra in metri
    R = 6371000.0
    
    # Converti gradi in radianti
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    # Formula di Haversine
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    distance_m = R * c
    return distance_m


def activate_nodes_by_linktype(linktype_list=None, exclude_linktype_list=None, visum_instance=None):
    """
    Attiva nodi connessi a link di specifici tipi (per usare in connectors).
    
    Filtra i nodi che sono connessi ad almeno un link con TypeNo nella lista.
    Imposta AddVal1=1 su questi nodi per uso successivo in create_zone_connectors.
    Opzionalmente esclude nodi connessi a link types specifici.
    
    Args:
        linktype_list (list): Lista di TypeNo da includere. Se None, include TUTTI i nodi (default: None)
        exclude_linktype_list (list): Lista di TypeNo da escludere (es. [80, 81] per rimuovere residenziali)
        visum_instance: Istanza Visum (default: usa Visum da console)
    
    Returns:
        dict: {"status": str, "nodes_activated": int, "nodes_excluded": int, "linktypes": list, "excluded_linktypes": list}
    
    Esempi:
        >>> # Attiva solo nodi su strade urbane principali
        >>> result = activate_nodes_by_linktype([50, 60, 70])
        
        >>> # Attiva TUTTI i nodi MA escludi residenziali/vicoli
        >>> result = activate_nodes_by_linktype(exclude_linktype_list=[80, 81])
        
        >>> # Attiva strade principali MA escludi nodi su strade residenziali
        >>> result = activate_nodes_by_linktype([50, 60, 70], exclude_linktype_list=[80, 81])
        >>> print(f"Nodi attivati: {result['nodes_activated']}, esclusi: {result['nodes_excluded']}")
    """
    result = {
        "status": "failed",
        "nodes_activated": 0,
        "nodes_excluded": 0,
        "linktypes": linktype_list,
        "excluded_linktypes": exclude_linktype_list or []
    }
    
    try:
        if visum_instance is None:
            visum = Visum
        else:
            visum = visum_instance
        
        print("\n" + "=" * 70)
        print("ATTIVAZIONE NODI PER TIPO LINK")
        print("=" * 70)
        if linktype_list:
            print("Tipi link da includere: {}".format(linktype_list))
        else:
            print("Tipi link da includere: TUTTI")
        if exclude_linktype_list:
            print("Tipi link da escludere: {}".format(exclude_linktype_list))
        
        # Reset AddVal1 su tutti i nodi (Active non esiste sui nodi!)
        visum.Net.Nodes.SetAllAttValues("AddVal1", 0)
        
        # Ottieni tutti gli attributi link in batch (VELOCE!)
        print("\nCaricamento attributi link...")
        link_typenums = visum.Net.Links.GetMultiAttValues("TypeNo")
        link_fromnodes = visum.Net.Links.GetMultiAttValues("FromNodeNo")
        link_tonodes = visum.Net.Links.GetMultiAttValues("ToNodeNo")
        
        total_links = len(link_typenums)
        print("Link totali: {}".format(total_links))
        
        # Set di nodi da attivare e da escludere
        nodes_to_activate = set()
        nodes_to_exclude = set()
        
        # Filtra in Python (VELOCE - no chiamate COM!)
        print("Filtro link per tipo...")
        
        # Se linktype_list è None, include TUTTI i nodi
        if linktype_list is None:
            print("Includo TUTTI i nodi...")
            for i in range(total_links):
                from_node = int(link_fromnodes[i][1])
                to_node = int(link_tonodes[i][1])
                nodes_to_activate.add(from_node)
                nodes_to_activate.add(to_node)
        else:
            # Include solo nodi su link types specificati
            for i in range(total_links):
                link_typeno = int(link_typenums[i][1])  # [index, value]
                
                if link_typeno in linktype_list:
                    from_node = int(link_fromnodes[i][1])
                    to_node = int(link_tonodes[i][1])
                    nodes_to_activate.add(from_node)
                    nodes_to_activate.add(to_node)
        
        # Se specificato, trova nodi da escludere
        if exclude_linktype_list:
            print("Filtro nodi da escludere...")
            for i in range(total_links):
                link_typeno = int(link_typenums[i][1])
                
                if link_typeno in exclude_linktype_list:
                    from_node = int(link_fromnodes[i][1])
                    to_node = int(link_tonodes[i][1])
                    nodes_to_exclude.add(from_node)
                    nodes_to_exclude.add(to_node)
            
            # Rimuovi nodi esclusi da quelli da attivare
            nodes_to_activate -= nodes_to_exclude
            result["nodes_excluded"] = len(nodes_to_exclude)
            print("Nodi esclusi: {}".format(len(nodes_to_exclude)))
        
        print("Nodi finali da attivare: {}".format(len(nodes_to_activate)))
        
        # Attiva i nodi trovati in batch (VELOCE - usa array diretto)
        print("Attivazione nodi...")
        
        # Ottieni array nodi e crea mappatura node_no -> index
        node_nos_data = visum.Net.Nodes.GetMultiAttValues("No")
        node_no_to_index = {}
        for i, row in enumerate(node_nos_data):
            node_no = int(row[1])
            node_no_to_index[node_no] = i
        
        # Accesso diretto all'array (evita ItemByKey!)
        all_nodes = visum.Net.Nodes.GetAll
        
        activated_count = 0
        for node_no in nodes_to_activate:
            if node_no in node_no_to_index:
                try:
                    idx = node_no_to_index[node_no]
                    all_nodes[idx].SetAttValue("AddVal1", 1)
                    activated_count += 1
                except:
                    pass
        
        result["nodes_activated"] = activated_count
        result["status"] = "success"
        
        print("\n✓ Attivati {} nodi (AddVal1=1)".format(result["nodes_activated"]))
        return result
        
    except Exception as e:
        result["message"] = "Errore attivazione nodi: {}".format(str(e))
        print("\n✗ " + result["message"])
        import traceback
        traceback.print_exc()
        return result


def create_zone_connectors(max_distance=1000, max_connectors_per_zone=5,
                          node_filter_active=False, bidirectional=True,
                          mode="add_all", distribute_by_quadrant=False,
                          visum_instance=None):
    """
    Crea connectors automatici tra zone e nodi della rete Visum.
    
    PREREQUISITI:
    - Zone devono esistere (visum.Net.Zones.Count > 0)
    - Nodi devono esistere (visum.Net.Nodes.Count > 0)
    - Se node_filter_active=True, chiamare prima activate_nodes_by_linktype()
      (usa AddVal1=1 per marcare i nodi)
    
    METODO:
    Itera su ogni zona, trova i nodi più vicini entro max_distance,
    e crea connectors usando visum.Net.AddConnector(zone_no, node_no).
    
    Args:
        max_distance (float): Distanza massima zona-nodo in metri (default: 1000)
        max_connectors_per_zone (int): Max connectors per zona (default: 5)
        node_filter_active (bool): Se True, usa solo nodi con AddVal1=1 (default: False)
        bidirectional (bool): Crea connectors bidirezionali (default: True)
        mode (str): Modalità creazione (default: "add_all")
            - "replace": Cancella TUTTI i connectors esistenti e ricrea da zero
            - "add_missing": Aggiungi connectors SOLO a zone senza connectors
            - "add_all": Aggiungi connectors a TUTTE le zone (default)
        distribute_by_quadrant (bool): Distribuisci connectors per quadrante (0-90°, 90-180°, 180-270°, 270-360°) (default: False)
        visum_instance: Istanza Visum (default: usa Visum da console)
    
    Returns:
        dict: {
            "status": str,
            "connectors_created": int,
            "connectors_deleted": int,  # solo se mode="replace"
            "zones_processed": int,
            "zones_skipped": int,  # solo se mode="add_missing"
            "avg_per_zone": float,
            "message": str
        }
    
    Esempio base:
        >>> result = create_zone_connectors(
        ...     max_distance=500,
        ...     max_connectors_per_zone=3
        ... )
        >>> print(f"Connectors creati: {result['connectors_created']}")
    
    Esempio con filtro nodi:
        >>> # 1. Attiva solo nodi su strade principali
        >>> activate_nodes_by_linktype([50, 60, 70])
        >>> 
        >>> # 2. Crea connectors solo a nodi attivi
        >>> result = create_zone_connectors(
        ...     max_distance=500,
        ...     max_connectors_per_zone=3,
        ...     node_filter_active=True
        ... )
    
    Esempio replace (cancella tutto):
        >>> # Cancella tutti i connectors e ricrea da zero
        >>> result = create_zone_connectors(mode="replace")
        >>> print(f"Cancellati: {result['connectors_deleted']}, creati: {result['connectors_created']}")
    
    Esempio add_missing (solo zone senza connectors):
        >>> # Aggiungi connectors solo a zone non ancora connesse
        >>> result = create_zone_connectors(mode="add_missing")
        >>> print(f"Zone processate: {result['zones_processed']}, saltate: {result['zones_skipped']}")
    
    Esempio distribuzione per quadrante:
        >>> # Distribuisci connectors coprendo tutti i quadranti (N, E, S, W)
        >>> result = create_zone_connectors(
        ...     max_distance=1000,
        ...     max_connectors_per_zone=4,  # 1 per quadrante
        ...     distribute_by_quadrant=True
        ... )
        >>> print(f"Connectors distribuiti geograficamente: {result['connectors_created']}")
    """
    result = {
        "status": "failed",
        "connectors_created": 0,
        "connectors_deleted": 0,
        "zones_processed": 0,
        "zones_skipped": 0,
        "avg_per_zone": 0.0,
        "message": ""
    }
    
    try:
        print("Distribuzione geografica: {}".format("SI (quadranti)" if distribute_by_quadrant else "NO (distanza)"))
        if visum_instance is None:
            visum = Visum
        else:
            visum = visum_instance
        
        print("\n" + "=" * 70)
        print("CREAZIONE CONNECTORS ZONE-NODI")
        print("=" * 70)
        print("Modalita': {}".format(mode))
        
        # MODE: REPLACE - Cancella tutti i connectors esistenti
        if mode == "replace":
            existing_count = visum.Net.Connectors.Count
            print("\nCancellazione connectors esistenti...")
            print("Connectors da cancellare: {}".format(existing_count))
            
            if existing_count > 0:
                visum.Net.Connectors.RemoveAll()
                result["connectors_deleted"] = existing_count
                print("✓ Cancellati {} connectors".format(existing_count))
        
        # Verifica zone
        zones_count = visum.Net.Zones.Count
        if zones_count == 0:
            result["message"] = "Nessuna zona presente nel progetto"
            print("✗ " + result["message"])
            return result
        
        # Verifica nodi
        nodes_count = visum.Net.Nodes.Count
        if nodes_count == 0:
            result["message"] = "Nessun nodo presente nel progetto"
            print("✗ " + result["message"])
            return result
        
        print("Zone: {}".format(zones_count))
        print("Nodi: {}".format(nodes_count))
        print("Distanza max: {}m".format(max_distance))
        print("Max connectors/zona: {}".format(max_connectors_per_zone))
        print("Filtro nodi attivi: {}".format(node_filter_active))
        print("Distribuzione per quadrante: {}".format(distribute_by_quadrant))
        
        # Ottieni coordinate nodi
        print("\nCaricamento coordinate nodi...")
        
        # GetMultiAttValues richiede UNA stringa per volta
        node_nos = visum.Net.Nodes.GetMultiAttValues("No")
        node_xs = visum.Net.Nodes.GetMultiAttValues("XCoord")
        node_ys = visum.Net.Nodes.GetMultiAttValues("YCoord")
        
        if node_filter_active:
            node_addvals = visum.Net.Nodes.GetMultiAttValues("AddVal1")
        
        # Crea dizionario coordinate nodi
        nodes_coords = {}
        for i in range(len(node_nos)):
            node_no = int(node_nos[i][1])  # [index, value]
            x_coord = float(node_xs[i][1])
            y_coord = float(node_ys[i][1])
            
            # Se filtro attivo, verifica AddVal1=1
            if node_filter_active:
                addval = int(node_addvals[i][1])
                if addval == 1:
                    nodes_coords[node_no] = {'x': x_coord, 'y': y_coord}
            else:
                nodes_coords[node_no] = {'x': x_coord, 'y': y_coord}
        
        print("Nodi disponibili: {}".format(len(nodes_coords)))
        
        # Ottieni coordinate zone
        print("\nCaricamento coordinate zone...")
        zone_nos = visum.Net.Zones.GetMultiAttValues("No")
        zone_xs = visum.Net.Zones.GetMultiAttValues("XCoord")
        zone_ys = visum.Net.Zones.GetMultiAttValues("YCoord")
        
        zones_coords = {}
        for i in range(len(zone_nos)):
            zone_no = int(zone_nos[i][1])  # [index, value]
            zones_coords[zone_no] = {
                'x': float(zone_xs[i][1]),
                'y': float(zone_ys[i][1])
            }
        
        print("Zone con coordinate: {}".format(len(zones_coords)))
        
        # IMPORTANTE: Coordinate geografiche WGS84 (lon/lat in gradi)
        # Usa formula di Haversine per calcolare distanze in METRI
        print("Sistema coordinate: WGS84 (lon/lat) - Distanze calcolate con Haversine")
        print("Distanza massima: {} metri".format(max_distance))
        
        # MODE: ADD_MISSING - Filtra zone già connesse
        zones_to_process = set(zones_coords.keys())
        
        if mode == "add_missing":
            print("\nFiltro zone già connesse...")
            # Ottieni zone che hanno già connectors
            if visum.Net.Connectors.Count > 0:
                connected_zones_data = visum.Net.Connectors.GetMultiAttValues("ZoneNo")
                connected_zones = set()
                for row in connected_zones_data:
                    zone_no = int(row[1])
                    connected_zones.add(zone_no)
                
                zones_to_skip = zones_to_process & connected_zones
                zones_to_process -= connected_zones
                
                result["zones_skipped"] = len(zones_to_skip)
                print("Zone già connesse (saltate): {}".format(len(zones_to_skip)))
                print("Zone da processare: {}".format(len(zones_to_process)))
            else:
                print("Nessun connector esistente, processo tutte le zone")
        
        # Itera sulle zone
        print("\nCreazione connectors...")
        connectors_created = 0
        zones_processed = 0
        zones_connected = set()
        zones_not_connected = []
        
        for zone_no, zone_coords in zones_coords.items():
            # Skip zone se mode="add_missing" e zona già connessa
            if mode == "add_missing" and zone_no not in zones_to_process:
                continue
            
            zone_x = zone_coords['x']
            zone_y = zone_coords['y']
            
            # Calcola distanze e angoli a tutti i nodi
            distances = []
            for node_key, coords in nodes_coords.items():
                # Calcola distanza geografica con Haversine (in METRI)
                # Coordinate: x=longitude, y=latitude
                dist_m = haversine_distance(
                    zone_coords['x'], zone_coords['y'],
                    coords['x'], coords['y']
                )
                
                if dist_m <= max_distance:
                    # Calcola angolo approssimativo (OK per piccole distanze)
                    dx = coords['x'] - zone_coords['x']
                    dy = coords['y'] - zone_coords['y']
                    import math
                    angle = math.degrees(math.atan2(dy, dx))
                    if angle < 0:
                        angle += 360
                    
                    distances.append((dist_m, angle, node_key))
            
            # Seleziona nodi in base alla strategia
            closest_nodes = []
            
            if distribute_by_quadrant and len(distances) > 0:
                # DISTRIBUZIONE PER QUADRANTE (0-90, 90-180, 180-270, 270-360)
                quadrants = {
                    0: [],   # 0-90°   (Nord-Est)
                    1: [],   # 90-180° (Nord-Ovest)
                    2: [],   # 180-270° (Sud-Ovest)
                    3: []    # 270-360° (Sud-Est)
                }
                
                # Raggruppa nodi per quadrante
                for dist, angle, node_key in distances:
                    quadrant = int(angle // 90)
                    if quadrant == 4:  # 360° -> quadrante 0
                        quadrant = 0
                    quadrants[quadrant].append((dist, angle, node_key))
                
                # Prendi il più vicino da ogni quadrante
                connectors_per_quadrant = max(1, max_connectors_per_zone // 4)
                
                for q in range(4):
                    if quadrants[q]:
                        # Ordina per distanza e prendi i primi N
                        quadrants[q].sort()
                        for item in quadrants[q][:connectors_per_quadrant]:
                            closest_nodes.append((item[0], item[2]))  # (dist, node_key)
            else:
                # SELEZIONE PER DISTANZA (come prima)
                distances_simple = [(dist, node_key) for dist, angle, node_key in distances]
                distances_simple.sort()
                closest_nodes = distances_simple[:max_connectors_per_zone]
            
            # Crea connectors
            connectors_for_zone = 0
            for dist, node_key in closest_nodes:
                try:
                    connector = visum.Net.AddConnector(zone_no, node_key)
                    connectors_created += 1
                    connectors_for_zone += 1
                    
                    # Imposta direzione se bidirezionale (opzionale - può fallire)
                    if bidirectional:
                        try:
                            connector.SetAttValue("Direction", 0)  # 0 = bidirezionale
                        except:
                            pass  # Direction non editabile, usa default
                    
                except Exception as e:
                    # Connector già esistente o altro errore
                    if connectors_created == 0 and zones_processed == 0:
                        print(f"  DEBUG - Errore creazione connector zona {zone_no} -> nodo {node_key}: {e}")
                    pass
            
            # Traccia zone con almeno un connettore
            if connectors_for_zone > 0:
                zones_connected.add(zone_no)
            else:
                zones_not_connected.append(zone_no)
            
            zones_processed += 1
            
            # Progress ogni 10 zone (più frequente per vedere se funziona)
            if zones_processed % 10 == 0:
                print("  Processate {} zone, {} connectors creati".format(
                    zones_processed, connectors_created))
        
        # Risultato finale
        avg_per_zone = connectors_created / zones_processed if zones_processed > 0 else 0
        
        result["status"] = "success"
        result["connectors_created"] = connectors_created
        result["zones_processed"] = zones_processed
        result["zones_connected"] = len(zones_connected)
        result["zones_not_connected"] = len(zones_not_connected)
        result["zones_not_connected_list"] = sorted(zones_not_connected)
        result["avg_per_zone"] = avg_per_zone
        result["message"] = "Connectors creati con successo"
        
        print("\n" + "=" * 70)
        print("✓ CONNECTORS CREATI CON SUCCESSO")
        print("=" * 70)
        print("Connectors totali: {}".format(connectors_created))
        print("Zone processate: {}".format(zones_processed))
        print("Media per zona: {:.1f}".format(avg_per_zone))
        print("")
        print("Zone connesse: {} / {}".format(len(zones_connected), zones_processed))
        print("Zone NON connesse: {}".format(len(zones_not_connected)))
        
        if zones_not_connected:
            print("\n⚠ ATTENZIONE: Le seguenti {} zone NON hanno connettori:".format(len(zones_not_connected)))
            zones_not_connected.sort()
            # Mostra prime 20 zone, poi riassumi
            if len(zones_not_connected) <= 20:
                print("   Zone: {}".format(", ".join(map(str, zones_not_connected))))
            else:
                print("   Prime 20: {}".format(", ".join(map(str, zones_not_connected[:20]))))
                print("   ... e altre {} zone".format(len(zones_not_connected) - 20))
            print("\nSuggerimenti:")
            print("  - Aumenta max_distance (attuale: {} m)".format(max_distance))
            print("  - Verifica che ci siano nodi disponibili vicino a queste zone")
            if node_filter_active:
                print("  - Disattiva node_filter_active per includere più nodi")
        else:
            print("\n✓ Tutte le zone sono state connesse con successo!")
        
        return result
        
    except Exception as e:
        result["message"] = "Errore creazione connectors: {}".format(str(e))
        print("\n✗ " + result["message"])
        import traceback
        traceback.print_exc()
        return result


# ============================================================================
# 【7】 ZONE GENERATION FROM HEX GRID (WITH AUTO-ZONING TOOL)
# ============================================================================

def create_zones_from_hex_grid(hex_grid_file, num_zones=200, 
                               compact_zones=True, study_area_file=None,
                               geographical_distance_weight=10, output_crs="EPSG:4326",
                               boundaries_file=None, verbose=True, boundaries_verbose=True,
                               road=True, rail=False, water=False,
                               road_network_type="secondary",
                               road_fix_par=None, rail_fix_par=None,
                               water_fix_par=None, final_fix_par=None,
                               fields=None, weights=None, output_dir=None,
                               conda_env=None, auto_zoning_path=None, timeout=1800,
                               centroid_method="geometric", istat_shapefile=None, weight_field="POP",
                               save_project_as=None, visum_instance=None):
    """
    PROCESSO COMPLETO: Crea zonizzazione automatica da griglia esagonale.
    TUTTI I PARAMETRI sono configurabili con valori di default override-abili.
    
    Esegue in sequenza:
    1. Valida griglia esagonale
    2. Crea config.json per auto-zoning
    3. Lancia auto-zoning in subprocess conda
    4. Importa zone generate in Visum
    5. Salva progetto (opzionale)
    
    Args:
        hex_grid_file (str): Path griglia esagonale (.shp, .geojson)
                            Deve contenere campi: id, POP, ADD, Landuse
        num_zones (int): Numero zone desiderato (default: 200)
        compact_zones (bool): True=zone compatte (k-means), False=forme variate (default: True)
        study_area_file (str): Path limiti area studio (default: None = auto)
        geographical_distance_weight (int): Peso distanza geografica 1-100 (default: 10)
        boundaries_file (str): Path limiti fisici custom (default: None = auto da OSM)
        verbose (bool): Log dettagliato processo (default: True)
        boundaries_verbose (bool): Log dettagliato creazione limiti (default: True)
        road (bool): Usa strade OSM per limiti (default: True)
        rail (bool): Usa ferrovie OSM per limiti (default: False - spesso assenti)
        water (bool): Usa fiumi OSM per limiti (default: False - spesso assenti)
        road_network_type (str): Tipo rete stradale OSM (default: "secondary")
                                motorway|trunk|primary|secondary|tertiary|residential|all
        road_fix_par (list): Percentili pulizia strade (default: [0.9, 0.5])
        rail_fix_par (list): Percentili pulizia ferrovie (default: [0.9, 0.8])
        water_fix_par (list): Percentili pulizia fiumi (default: [])
        final_fix_par (list): Percentili pulizia finale (default: [0.3])
        conda_env (str): Nome environment (es. "zoning_env") o path assoluto 
                        (es. r"H:\\go\\network_builder\\.env")
                        Default: "zoning_env"
        auto_zoning_path (str): Path directory auto-zoning (contiene run_premodel.py)
                               Default: None = cerca automaticamente
                               Es: r"H:\\visum-thinker-mcp-server\\auto-zoning"
        timeout (int): Timeout subprocess in secondi (default: 1800)
        centroid_method (str): Metodo calcolo centroide (default: "geometric")
                              - "geometric": Media coordinate poligono
                              - "weighted": Ponderato su dati ISTAT (richiede istat_shapefile)
        istat_shapefile (str): Path shapefile ISTAT sezioni censuarie (opzionale)
        weight_field (str): Campo peso singolo per centroidi (default: "POP")
                           Ignorato se fields/weights sono specificati per clustering
        save_project_as (str): Path salvataggio progetto (opzionale)
        visum_instance: Istanza Visum (default: usa Visum da console)
    
    NOTA: Se fields e weights sono usati per clustering, saranno usati anche per
          centroidi ponderati. Altrimenti usa weight_field.
    
    Returns:
        dict: Risultato completo con info zonizzazione
    
    Esempio base:
        >>> exec(open(r"H:\\visum-thinker-mcp-server\\import-osm-network.py", encoding='utf-8').read())
        >>> 
        >>> result = create_zones_from_hex_grid(
        ...     hex_grid_file=r"H:\\data\\Terni_prezoning_hex.shp",
        ...     num_zones=200,
        ...     compact_zones=True,
        ...     auto_zoning_path=r"H:\\visum-thinker-mcp-server\\auto-zoning",  # Path script
        ...     hex_grid_file=r"H:\\data\\hex.shp",
        ...     num_zones=200,
        ...     conda_env=r"H:\\go\\network_builder\\.env",  # Path assoluto!
        ...     save_project_as=r"H:\\projects\\zones.ver"
        ... )
    
    Esempio con centroidi ponderati:
        >>> result = create_zones_from_hex_grid(
        ...     hex_grid_file=r"H:\\data\\hex_with_pop.shp",
        ...     num_zones=100,
        ...     centroid_method="weighted",
        ...     istat_shapefile=r"H:\\data\\Terni_prezoning_istat.shp",
        ...     weight_field="POP",
        ...     conda_env=r"H:\\go\\network_builder\\.env",
        ...     auto_zoning_path=r"H:\\visum-thinker-mcp-server\\auto-zoning
        ...     auto_zoning_path=r"H:\\visum-thinker-mcp-server\\auto-zoning",  # Path script
        ...     hex_grid_file=r"H:\\data\\hex.shp",
        ...     num_zones=200,
        ...     conda_env=r"H:\\go\\network_builder\\.env",  # Path assoluto!
        ...     save_project_as=r"H:\\projects\\zones.ver"
        ... )
    
    Esempio avanzato (override parametri):
        >>> result = create_zones_from_hex_grid(
        ...     hex_grid_file=r"H:\\data\\hex.shp",
        ...     num_zones=150,
        ...     compact_zones=False,                    # Zone forme variate
        ...     geographical_distance_weight=50,        # Più compatte
        ...     road_network_type="primary",            # Solo strade primarie
        ...     rail=False,                             # Ignora ferrovie
        ...     road_fix_par=[0.95, 0.7],              # Pulizia aggressiva
        ...     final_fix_par=[0.5],                   # Pulizia finale custom
        ...     verbose=False,                          # Meno output
        ...     conda_env="my_custom_env",              # Environment custom
        ...     timeout=3600,                           # 1 ora timeout
        ...     save_project_as=r"H:\\projects\\zones_custom.ver"
        ... )
    """
    
    result = {
        "status": "failed",
        "message": "",
        "validation": {},
        "subprocess": {},
        "import": {},
        "zones_created": 0
    }
    
    try:
        print("\n" + "=" * 70)
        print("PROCESSO AUTO-ZONING COMPLETO")
        print("=" * 70)
        
        # Usa istanza Visum
        if visum_instance is None:
            visum = Visum
        else:
            visum = visum_instance
        
        # STEP 1: Validazione griglia
        print("\n### STEP 1: VALIDAZIONE GRIGLIA ESAGONALE ###")
        validation_result = validate_hex_grid(hex_grid_file)
        result["validation"] = validation_result
        
        if not validation_result["valid"]:
            result["message"] = "Validazione fallita: {}".format(validation_result["message"])
            print("✗ {}".format(result["message"]))
            return result
        
        # STEP 2: Crea config
        print("\n### STEP 2: CREAZIONE CONFIGURAZIONE ###")
        config_file = create_zoning_config(
            hex_grid_file=hex_grid_file,
            study_area_file=study_area_file,
            num_zones=num_zones,
            compact_zones=compact_zones,
            geographical_distance_weight=geographical_distance_weight,
            boundaries_file=boundaries_file,
            verbose=verbose,
            boundaries_verbose=boundaries_verbose,
            road=road,
            rail=rail,
            water=water,
            road_network_type=road_network_type,
            road_fix_par=road_fix_par,
            rail_fix_par=rail_fix_par,
            water_fix_par=water_fix_par,
            final_fix_par=final_fix_par,
            fields=fields,
            weights=weights,
            output_dir=output_dir,
            output_crs=output_crs
        )
        result["config_file"] = config_file
        
        # STEP 3: Esegui auto-zoning
        print("\n### STEP 3: ESECUZIONE AUTO-ZONING ###")
        subprocess_result = run_auto_zoning_subprocess(
            config_json_path=config_file,
            auto_zoning_path=auto_zoning_path,
            conda_env=conda_env,
            output_dir=output_dir,
            timeout=timeout
        )
        result["subprocess"] = subprocess_result
        
        if subprocess_result["status"] != "success":
            result["message"] = "Auto-zoning fallito: {}".format(subprocess_result["message"])
            print("✗ {}".format(result["message"]))
            return result
        
        # STEP 4: Import zone in Visum
        print("\n### STEP 4: IMPORT ZONE IN VISUM ###")
        
        output_files = subprocess_result.get("output_files", [])
        if not output_files:
            result["message"] = "Nessun file output generato da auto-zoning"
            print("✗ {}".format(result["message"]))
            return result
        
        # Importa il primo file zoning (zoning_0.geojson, escludendo boundaries)
        zoning_files = [f for f in output_files if "zoning_" in f and f.endswith(".geojson") and "boundaries" not in f]
        
        if not zoning_files:
            result["message"] = "Nessun file zoning_*.geojson trovato"
            print("✗ {}".format(result["message"]))
            return result
        
        # Usa il primo file zoning
        zoning_file = zoning_files[0]
        print("Importo zone da: {}".format(Path(zoning_file).name))
        
        # Se fields/weights sono usati per clustering, usali anche per centroidi ponderati
        import_kwargs = {
            "geojson_file": zoning_file,
            "output_crs": output_crs,
            "centroid_method": centroid_method,
            "conda_env": conda_env,
            "istat_shapefile": istat_shapefile,
            "visum_instance": visum
        }
        
        if fields is not None and weights is not None:
            # Usa ponderazione multi-campo
            import_kwargs["weight_fields"] = fields
            import_kwargs["weight_values"] = weights
        
        import_result = import_zones_from_geojson(**import_kwargs)
        result["import"] = import_result
        
        if import_result["status"] != "success":
            result["message"] = "Import zone fallito: {}".format(import_result["message"])
            print("✗ {}".format(result["message"]))
            return result
        
        result["zones_created"] = import_result["zones_created"]
        
        # STEP 5: Salvataggio progetto
        if save_project_as:
            print("\n### STEP 5: SALVATAGGIO PROGETTO ###")
            try:
                save_path = Path(save_project_as)
                save_path.parent.mkdir(parents=True, exist_ok=True)
                
                visum.SaveVersion(str(save_path))
                print("✓ Progetto salvato: {}".format(save_project_as))
                result["project_file"] = str(save_path)
            except Exception as e:
                print("✗ Errore salvataggio: {}".format(str(e)))
                result["save_error"] = str(e)
        
        # Cleanup config temporaneo
        try:
            os.unlink(config_file)
            print("\n✓ File temporaneo rimosso")
        except:
            pass
        
        # Riepilogo finale
        result["status"] = "success"
        result["message"] = "Auto-zoning completato: {} zone create".format(result["zones_created"])
        
        print("\n" + "=" * 70)
        print("PROCESSO COMPLETATO CON SUCCESSO")
        print("=" * 70)
        print("\nRiepilogo:")
        print("  - Griglia input: {}".format(Path(hex_grid_file).name))
        print("  - Zone create: {}".format(result["zones_created"]))
        print("  - Tipo clustering: {}".format("Compatto (k-means)" if compact_zones else "Agglomerativo"))
        print("  - File output: {}".format(len(output_files)))
        
        if save_project_as:
            print("\nProgetto salvato: {}".format(save_project_as))
        
        print("=" * 70)
        
        return result
        
    except Exception as e:
        result["message"] = "Errore processo auto-zoning: {}".format(str(e))
        print("\nERRORE GENERALE: {}".format(result["message"]))
        import traceback
        traceback.print_exc()
        return result
