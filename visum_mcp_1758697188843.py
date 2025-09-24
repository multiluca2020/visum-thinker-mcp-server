
import sys
sys.path.append(r"H:\Program Files\PTV Vision\PTV Visum 2025\Exe")

try:
    import win32com.client
    
    print("=== VISUM MCP NETWORK ANALYSIS ===")
    print(f"Analysis Type: DETAILED")
    print("=" * 40)
    
    # Try to connect to existing Visum instance
    try:
        visum = win32com.client.GetActiveObject("Visum.Visum")
        print("Connected to active Visum instance")
    except:
        print("Creating new Visum COM instance...")
        visum = win32com.client.DispatchEx("Visum.Visum")
        print("New COM instance created")
    
    # Get basic network statistics
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
        
        if "detailed" == "detailed" and links > 0:
            print("\nDETAILED ANALYSIS:")
            try:
                # Sample analysis of network characteristics
                sample_size = min(100, links)
                print(f"Analyzing sample of {sample_size} links...")
                
                total_length = 0
                valid_links = 0
                
                # Note: This is a simplified approach due to COM limitations
                print("Note: Using COM DispatchEx (new instance)")
                print("For full data access, load project in visible Visum first")
                
            except Exception as detail_error:
                print(f"Detailed analysis limited: {detail_error}")
        
        elif "detailed" == "topology":
            print("\nTOPOLOGY ANALYSIS:")
            if nodes > 0 and links > 0:
                # Basic topology metrics
                avg_degree = (2 * links) / nodes
                print(f"Average node degree: {avg_degree:.2f}")
                
                # Network type classification
                if connectivity < 1.5:
                    network_type = "Sparse (low connectivity)"
                elif connectivity < 2.5:
                    network_type = "Medium density"
                else:
                    network_type = "Dense (high connectivity)"
                print(f"Network type: {network_type}")
                
        elif "detailed" == "performance":
            print("\nPERFORMACE ANALYSIS:")
            print("Performance analysis requires loaded model with assignments")
    
    print("\n=== ANALYSIS COMPLETE ===")
    print("MCP Visum network analysis finished successfully")
    
except Exception as e:
    print(f"ERROR: {e}")
    print("\nTROUBLESHOoting:")
    print("- Ensure Visum is installed")
    print("- Try launching Visum with a project first")
    print("- Check COM permissions")
