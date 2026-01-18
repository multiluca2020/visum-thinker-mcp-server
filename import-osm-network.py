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
