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
    print("=" * 70)
    print("Script import-osm-network.py caricato correttamente!")
    print("=" * 70)
    print("\nFUNZIONI RACCOMANDATE PER CONSOLE VISUM:")
    print("\n1. Import semplice con preset:")
    print("  >>> result = import_osm_simple(r'C:\\file.osm')")
    print("\n2. Import con cartella di configurazione:")
    print("  >>> result = import_osm_from_folder(")
    print("  ...     r'C:\\file.osm',")
    print("  ...     r'C:\\ConfigFolder')")
    print("\nAltre funzioni:")
    print("  - import_osm_network() - versione completa")
    print("  - list_available_presets() - elenca preset OSM")
    print("  - copy_and_customize_preset() - copia preset")
    print("=" * 70)


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


if __name__ == "__main__":
    main()
