"""
Analyze PrT Assignment Results - Top 10 Most Congested Links

This script analyzes a Visum project with completed PrT assignment
and identifies the 10 most congested links based on Volume/Capacity ratio.

Usage:
    python analyze-congestion.py

Requirements:
    - Visum project already opened with active assignment results
    - VolCapRatioPrT(AP) attribute available on links
"""

import win32com.client
import sys

def find_top_congested_links(visum, analysis_period="AP", top_n=10):
    """
    Find the top N most congested links in the network.
    
    Args:
        visum: Visum COM object
        analysis_period: Analysis period code (default: "AP")
        top_n: Number of top congested links to return (default: 10)
    
    Returns:
        list: List of dictionaries with link info and congestion data
    """
    print(f"\n🔍 Analyzing congestion for period: {analysis_period}")
    print("=" * 80)
    
    try:
        links = visum.Net.Links
        total_links = links.Count
        print(f"📊 Total links in network: {total_links:,}")
        
        # Get all required attributes in one call for efficiency
        attr_vc = f"VolCapRatioPrT({analysis_period})"
        attr_vol = f"VolVehPrT({analysis_period})"
        
        print(f"\n⏳ Retrieving link data...")
        
        # Get Volume/Capacity ratios
        vc_data = links.GetMultiAttValues(attr_vc)
        keys = vc_data[0]  # List of (FromNode, ToNode) tuples
        vc_ratios = vc_data[1]  # List of V/C ratio values
        
        # Get volumes
        vol_data = links.GetMultiAttValues(attr_vol)
        volumes = vol_data[1]
        
        # Get additional attributes for each link
        print(f"⏳ Retrieving additional link attributes...")
        lengths = links.GetMultiAttValues("LENGTH")[1]
        capacities = links.GetMultiAttValues("CAPPRT")[1]
        type_nos = links.GetMultiAttValues("TYPENO")[1]
        names = links.GetMultiAttValues("NAME")[1]
        
        # Get V0PRT (free flow speed)
        try:
            v0_speeds = links.GetMultiAttValues("V0PRT")[1]
        except:
            v0_speeds = [None] * len(keys)
        
        print(f"✅ Retrieved data for {len(keys):,} links")
        
        # Build list of congested links
        congested_links = []
        for i, (from_node, to_node) in enumerate(keys):
            vc_ratio = vc_ratios[i]
            
            # Only consider links with actual traffic (V/C > 0)
            if vc_ratio > 0:
                link_info = {
                    'from_node': from_node,
                    'to_node': to_node,
                    'vc_ratio': vc_ratio,
                    'volume': volumes[i],
                    'capacity': capacities[i],
                    'length': lengths[i],
                    'type_no': type_nos[i],
                    'name': names[i] if names[i] else f"{from_node}->{to_node}",
                    'v0_speed': v0_speeds[i]
                }
                congested_links.append(link_info)
        
        # Sort by V/C ratio descending
        congested_links.sort(key=lambda x: x['vc_ratio'], reverse=True)
        
        # Get statistics
        total_congested = sum(1 for link in congested_links if link['vc_ratio'] > 0.9)
        total_overcapacity = sum(1 for link in congested_links if link['vc_ratio'] > 1.0)
        
        print(f"\n📈 Congestion Statistics:")
        print(f"   • Links with traffic: {len(congested_links):,}")
        print(f"   • Congested links (V/C > 0.9): {total_congested:,}")
        print(f"   • Over-capacity links (V/C > 1.0): {total_overcapacity:,}")
        
        # Return top N
        return congested_links[:top_n]
        
    except Exception as e:
        print(f"❌ Error analyzing congestion: {e}")
        import traceback
        traceback.print_exc()
        return []


def print_congested_links(congested_links, analysis_period="AP"):
    """
    Print formatted table of congested links.
    
    Args:
        congested_links: List of link dictionaries
        analysis_period: Analysis period code
    """
    if not congested_links:
        print("\n⚠️ No congested links found or error occurred")
        return
    
    print(f"\n🚨 TOP {len(congested_links)} MOST CONGESTED LINKS ({analysis_period})")
    print("=" * 80)
    print(f"{'Rank':<6} {'From':<8} {'To':<8} {'V/C':>8} {'Volume':>10} {'Capacity':>10} {'Length':>8} {'Type':<6}")
    print("-" * 80)
    
    for rank, link in enumerate(congested_links, 1):
        from_node = link['from_node']
        to_node = link['to_node']
        vc_ratio = link['vc_ratio']
        volume = link['volume']
        capacity = link['capacity']
        length = link['length']
        type_no = link['type_no']
        
        # Color coding for congestion level
        if vc_ratio > 1.5:
            status = "🔴"  # Severe
        elif vc_ratio > 1.0:
            status = "🟠"  # Over capacity
        elif vc_ratio > 0.9:
            status = "🟡"  # Congested
        else:
            status = "🟢"  # Normal
        
        print(f"{status} {rank:<4} {from_node:<8} {to_node:<8} {vc_ratio:>7.2f} {volume:>10,.0f} {capacity:>10,.0f} {length:>7,.0f}m {type_no:<6}")
    
    print("=" * 80)
    print("\nLegend:")
    print("  🔴 Severe congestion (V/C > 1.5)")
    print("  🟠 Over capacity (V/C > 1.0)")
    print("  🟡 Congested (V/C > 0.9)")
    print("  🟢 High utilization (V/C < 0.9)")


def export_to_csv(congested_links, output_file, analysis_period="AP"):
    """
    Export congested links to CSV file.
    
    Args:
        congested_links: List of link dictionaries
        output_file: Output CSV file path
        analysis_period: Analysis period code
    """
    import csv
    
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['Rank', 'FromNode', 'ToNode', 'Name', 'VC_Ratio', 'Volume', 
                         'Capacity', 'Length_m', 'TypeNo', 'V0Speed', 'AnalysisPeriod']
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
            
            writer.writeheader()
            
            for rank, link in enumerate(congested_links, 1):
                writer.writerow({
                    'Rank': rank,
                    'FromNode': link['from_node'],
                    'ToNode': link['to_node'],
                    'Name': link['name'],
                    'VC_Ratio': f"{link['vc_ratio']:.4f}",
                    'Volume': f"{link['volume']:.2f}",
                    'Capacity': f"{link['capacity']:.2f}",
                    'Length_m': f"{link['length']:.2f}",
                    'TypeNo': link['type_no'],
                    'V0Speed': link['v0_speed'] if link['v0_speed'] is not None else '',
                    'AnalysisPeriod': analysis_period
                })
        
        print(f"\n✅ Results exported to: {output_file}")
        
    except Exception as e:
        print(f"❌ Error exporting to CSV: {e}")


def main():
    """Main execution function."""
    print("=" * 80)
    print("🚦 VISUM CONGESTION ANALYSIS - TOP 10 MOST CONGESTED LINKS")
    print("=" * 80)
    
    try:
        # Connect to running Visum instance
        print("\n⏳ Connecting to Visum...")
        visum = win32com.client.Dispatch("Visum.Visum.250")
        print("✅ Connected to Visum")
        
        # Get project info
        try:
            project_name = visum.GetPath(4)  # 4 = Project name
            print(f"📁 Project: {project_name}")
        except:
            project_name = "Unknown"
        
        # Analysis period (can be modified)
        analysis_period = "AP"
        
        # Find top 10 congested links
        top_congested = find_top_congested_links(visum, analysis_period, top_n=10)
        
        if top_congested:
            # Print results
            print_congested_links(top_congested, analysis_period)
            
            # Export to CSV
            output_file = f"top_congested_links_{analysis_period}.csv"
            export_to_csv(top_congested, output_file, analysis_period)
            
            # Print summary
            print(f"\n📊 SUMMARY:")
            print(f"   • Analysis Period: {analysis_period}")
            print(f"   • Top congested links: {len(top_congested)}")
            print(f"   • Most congested V/C ratio: {top_congested[0]['vc_ratio']:.2f}")
            print(f"   • CSV export: {output_file}")
            
        else:
            print("\n⚠️ No results found. Possible reasons:")
            print("   • Assignment not yet executed")
            print("   • No traffic on the network")
            print("   • Wrong analysis period code")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("\n" + "=" * 80)
    print("✅ Analysis completed")
    print("=" * 80)


if __name__ == "__main__":
    main()
