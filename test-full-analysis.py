import sys
import os
sys.path.append(r"H:\Program Files\PTV Vision\PTV Visum 2025\Exe")

try:
    import win32com.client
    
    print("=== VISUM MCP NETWORK ANALYSIS ===")
    print(f"Analysis Type: DETAILED")
    print("=" * 40)
    
    # Always use DispatchEx as GetActiveObject doesn't work with Visum 2025
    print("Creating Visum COM instance...")
    visum = win32com.client.DispatchEx("Visum.Visum")
    print("✅ COM instance created")
    
    # Check if network is empty and try to load default project
    initial_nodes = visum.Net.Nodes.Count
    print(f"Initial nodes: {initial_nodes}")
    
    if initial_nodes == 0:
        print("Network empty - attempting to load Campoleone project...")
        campoleone_path = r"H:\go\italferr2025\Campoleone\100625_Versione_base_v0.3_sub_ok_priv.ver"
        if os.path.exists(campoleone_path):
            try:
                print("📂 Loading project...")
                visum.LoadVersion(campoleone_path)
                print("✅ Campoleone project loaded successfully")
            except Exception as load_error:
                print(f"❌ Failed to load project: {load_error}")
        else:
            print("❌ Default project not found at expected location")
    
    # Get network statistics
    nodes = visum.Net.Nodes.Count
    links = visum.Net.Links.Count  
    zones = visum.Net.Zones.Count
    
    print(f"\nBASIC STATISTICS:")
    print(f"Nodes: {nodes:,}")
    print(f"Links: {links:,}")
    print(f"Zones: {zones:,}")
    
    if nodes == 0:
        print("\nWARNING: Network appears empty")
        print("- Check if a project is loaded in Visum")
        print("- Use 'visum_launch' to load a project first")
    else:
        print(f"\nNETWORK DENSITY:")
        connectivity = links / nodes if nodes > 0 else 0
        print(f"Links per node: {connectivity:.2f}")
        
        print("\nDETAILED ANALYSIS:")
        try:
            # Sample analysis of network characteristics
            sample_size = min(100, links)
            print(f"Analyzing sample of {sample_size} links...")
            
            # Try to access link attributes
            print("🔍 Testing link attribute access...")
            test_links = 0
            for i in range(1, min(11, links + 1)):  # Test first 10 links
                try:
                    # Get all links and try to access one
                    link_set = visum.Net.Links
                    print(f"   Link collection type: {type(link_set)}")
                    
                    # Try different access methods
                    if hasattr(link_set, 'GetMultipleAttributes'):
                        print("   Using GetMultipleAttributes...")
                        # Get basic attributes
                        attrs = link_set.GetMultipleAttributes(['No', 'Length'])
                        if attrs and len(attrs) > 0:
                            print(f"   First link - No: {attrs[0][0]}, Length: {attrs[0][1]}")
                            test_links = len(attrs)
                        break
                    else:
                        print("   GetMultipleAttributes not available")
                        break
                        
                except Exception as attr_error:
                    print(f"   Link access attempt {i} failed: {attr_error}")
                    continue
            
            print(f"Successfully analyzed {test_links} links")
            
        except Exception as detail_error:
            print(f"Detailed analysis limited: {detail_error}")
        
        # Network type classification
        if connectivity < 1.5:
            network_type = "Sparse (low connectivity)"
        elif connectivity < 2.5:
            network_type = "Medium density"
        else:
            network_type = "Dense (high connectivity)"
        print(f"Network type: {network_type}")
    
    print("\n=== ANALYSIS COMPLETE ===")
    print("MCP Visum network analysis finished successfully")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    print("\nTROUBLESHOOTING:")
    print("- Ensure Visum is installed")
    print("- Try launching Visum with a project first")
    print("- Check COM permissions")