"""
Inline Visum Congestion Analysis Script
Can be executed directly in Visum Python console or via TCP server

This script assumes 'Visum' object is already available in scope.
Returns JSON result for MCP integration.

Usage in Visum Console:
    exec(open('analyze-congestion-inline.py', encoding='utf-8').read())

Usage via TCP/MCP:
    Send this entire script as Python code to execute
"""

# Configuration
ANALYSIS_PERIOD = "AP"
TOP_N = 10

try:
    # Find top congested links
    links = Visum.Net.Links
    total_links = links.Count
    
    # Get all required attributes
    attr_vc = f"VolCapRatioPrT({ANALYSIS_PERIOD})"
    attr_vol = f"VolVehPrT({ANALYSIS_PERIOD})"
    
    print(f"\n🔍 Debug Info:")
    print(f"   • Total links in network: {total_links:,}")
    print(f"   • Retrieving attribute: {attr_vc}")
    
    # Retrieve data - GetMultiAttValues returns tuple of (index, value) pairs
    vc_data_raw = links.GetMultiAttValues(attr_vc)
    
    print(f"   • VC data type: {type(vc_data_raw)}")
    print(f"   • VC data length: {len(vc_data_raw)}")
    print(f"   • First 3 items: {vc_data_raw[:3]}")
    
    # Check if we got data
    if not isinstance(vc_data_raw, (tuple, list)) or len(vc_data_raw) == 0:
        raise ValueError(f"No data returned for {attr_vc}. Assignment may not be executed.")
    
    # Extract just the values (second element of each tuple)
    vc_ratios = [item[1] if isinstance(item, tuple) else item for item in vc_data_raw]
    
    print(f"   • Total values: {len(vc_ratios):,}")
    print(f"   • First 5 VC ratios: {vc_ratios[:5]}")
    print(f"   • Max VC ratio: {max(vc_ratios):.3f}")
    
    # Get node IDs (FromNode and ToNode) - extract values from (index, value) tuples
    from_nodes_raw = links.GetMultiAttValues("FROMNODENO")
    from_nodes = [item[1] if isinstance(item, tuple) else item for item in from_nodes_raw]
    
    to_nodes_raw = links.GetMultiAttValues("TONODENO")
    to_nodes = [item[1] if isinstance(item, tuple) else item for item in to_nodes_raw]
    
    # Get other attributes - extract values
    volumes_raw = links.GetMultiAttValues(attr_vol)
    volumes = [item[1] if isinstance(item, tuple) else item for item in volumes_raw]
    
    lengths_raw = links.GetMultiAttValues("LENGTH")
    lengths = [item[1] if isinstance(item, tuple) else item for item in lengths_raw]
    
    capacities_raw = links.GetMultiAttValues("CAPPRT")
    capacities = [item[1] if isinstance(item, tuple) else item for item in capacities_raw]
    
    type_nos_raw = links.GetMultiAttValues("TYPENO")
    type_nos = [item[1] if isinstance(item, tuple) else item for item in type_nos_raw]
    
    names_raw = links.GetMultiAttValues("NAME")
    names = [item[1] if isinstance(item, tuple) else item for item in names_raw]
    
    try:
        v0_speeds_raw = links.GetMultiAttValues("V0PRT")
        v0_speeds = [item[1] if isinstance(item, tuple) else item for item in v0_speeds_raw]
    except:
        v0_speeds = [None] * len(vc_ratios)
    
    # Build congested links list
    congested_links = []
    for i in range(len(vc_ratios)):
        vc_ratio = vc_ratios[i]
        if vc_ratio > 0:
            # Get from/to nodes from separate arrays
            from_node = from_nodes[i] if i < len(from_nodes) else 0
            to_node = to_nodes[i] if i < len(to_nodes) else 0
            
            congested_links.append({
                'from_node': from_node,
                'to_node': to_node,
                'vc_ratio': vc_ratio,
                'volume': volumes[i] if i < len(volumes) else 0,
                'capacity': capacities[i] if i < len(capacities) else 0,
                'length': lengths[i] if i < len(lengths) else 0,
                'type_no': type_nos[i] if i < len(type_nos) else 0,
                'name': names[i] if i < len(names) and names[i] else f"{from_node}->{to_node}",
                'v0_speed': v0_speeds[i] if i < len(v0_speeds) else None
            })
    
    # Sort by V/C ratio descending
    congested_links.sort(key=lambda x: x['vc_ratio'], reverse=True)
    
    # Get top N
    top_congested = congested_links[:TOP_N]
    
    # Statistics
    total_with_traffic = len(congested_links)
    total_congested = sum(1 for link in congested_links if link['vc_ratio'] > 0.9)
    total_overcapacity = sum(1 for link in congested_links if link['vc_ratio'] > 1.0)
    
    # Format output
    print(f"\n{'='*80}")
    print(f"🚦 TOP {TOP_N} MOST CONGESTED LINKS ({ANALYSIS_PERIOD})")
    print(f"{'='*80}")
    print(f"\n📊 Statistics:")
    print(f"   • Total links: {total_links:,}")
    print(f"   • Links with traffic: {total_with_traffic:,}")
    print(f"   • Congested (V/C > 0.9): {total_congested:,}")
    print(f"   • Over-capacity (V/C > 1.0): {total_overcapacity:,}")
    
    print(f"\n{'Rank':<6} {'From':<10} {'To':<10} {'V/C':>8} {'Volume':>12} {'Capacity':>12} {'Length':>10}")
    print(f"{'-'*80}")
    
    for rank, link in enumerate(top_congested, 1):
        # Status indicator
        vc = link['vc_ratio']
        if vc > 1.5:
            status = "SEVERE"
        elif vc > 1.0:
            status = "OVERCAP"
        elif vc > 0.9:
            status = "CONG"
        else:
            status = "HIGH"
        
        print(f"{rank:<6} {link['from_node']:<10} {link['to_node']:<10} "
              f"{link['vc_ratio']:>7.3f} {link['volume']:>12,.1f} "
              f"{link['capacity']:>12,.1f} {link['length']:>9,.1f}m  [{status}]")
    
    print(f"{'='*80}\n")
    
    # Generate zoomed maps for each congested link
    print("\n" + "="*80)
    print("🗺️  GENERATING ZOOMED MAPS FOR TOP CONGESTED LINKS")
    print("="*80)
    
    maps_generated = []
    
    for rank, link in enumerate(top_congested, 1):
        try:
            from_node = link['from_node']
            to_node = link['to_node']
            
            # Get link object
            link_obj = Visum.Net.Links.ItemByKey(from_node, to_node)
            
            # Get node coordinates
            from_node_obj = Visum.Net.Nodes.ItemByKey(from_node)
            to_node_obj = Visum.Net.Nodes.ItemByKey(to_node)
            
            from_x = from_node_obj.AttValue("XCOORD")
            from_y = from_node_obj.AttValue("YCOORD")
            to_x = to_node_obj.AttValue("XCOORD")
            to_y = to_node_obj.AttValue("YCOORD")
            
            # Calculate link length
            link_length = link['length']
            
            # Debug: show actual coordinates
            print(f"   Node coords: ({from_x:.2f}, {from_y:.2f}) -> ({to_x:.2f}, {to_y:.2f})")
            
            # Calculate distance in coordinate units (not meters!)
            coord_dist_x = abs(to_x - from_x)
            coord_dist_y = abs(to_y - from_y)
            coord_dist = max(coord_dist_x, coord_dist_y, 0.0001)  # Avoid zero
            
            # Buffer: If link is very short, use small fixed buffer (0.01 = ~1km at this scale)
            # Otherwise 3x the coordinate distance
            if coord_dist < 0.01:
                zoom_buffer = 0.01  # Small fixed buffer for very short links
            else:
                zoom_buffer = coord_dist * 3
            
            print(f"   Coordinate distance: {coord_dist:.3f} units, buffer: {zoom_buffer:.3f} units")
            
            # Calculate bounding box with buffer
            left = min(from_x, to_x) - zoom_buffer
            right = max(from_x, to_x) + zoom_buffer
            bottom = min(from_y, to_y) - zoom_buffer
            top = max(from_y, to_y) + zoom_buffer
            
            # Calculate box dimensions
            width_m = right - left
            height_m = top - bottom
            
            print(f"   Link {from_node}->{to_node}: length={link_length:.0f}m, buffer={zoom_buffer:.0f}m")
            print(f"   Export bounds: L={left:.2f}, B={bottom:.2f}, R={right:.2f}, T={top:.2f}")
            print(f"   Box size: {width_m:.0f}m × {height_m:.0f}m")
            
            # Save screenshot using ExportNetworkImageFile
            screenshot_file = f"congested_link_{rank:02d}_{from_node}_{to_node}.png"
            
            # Calculate image dimensions (16:9 aspect ratio, 1920px width)
            image_width = 1920
            image_height = 1080
            dpi = 150
            quality = 95
            
            # Export network image with bounds (left, bottom, right, top)
            Visum.Graphic.ExportNetworkImageFile(
                screenshot_file,
                left, bottom, right, top,
                image_width,
                dpi,
                quality
            )
            
            maps_generated.append({
                "rank": rank,
                "file": screenshot_file,
                "from_node": from_node,
                "to_node": to_node,
                "vc_ratio": link['vc_ratio']
            })
            
            print(f"✅ Rank {rank}: {screenshot_file} (V/C={link['vc_ratio']:.3f})")
            
        except Exception as map_error:
            print(f"⚠️  Rank {rank}: Failed to generate map - {str(map_error)}")
    
    if maps_generated:
        print(f"\n✅ Generated {len(maps_generated)} maps")
        print(f"📁 Files saved in current directory")
    else:
        print(f"\n⚠️  No maps generated (errors occurred)")
    
    print("="*80 + "\n")
    
    # Analyze OD flow for congested links
    print("\n" + "="*80)
    print("📊 OD FLOW ANALYSIS FOR TOP CONGESTED LINKS")
    print("="*80)
    
    od_analysis_results = []
    
    for rank, link in enumerate(top_congested, 1):
        try:
            from_node = link['from_node']
            to_node = link['to_node']
            
            print(f"\n🔍 Rank {rank}: Link {from_node}->{to_node} (V/C={link['vc_ratio']:.3f})")
            
            # Get link object
            link_obj = Visum.Net.Links.ItemByKey(from_node, to_node)
            
            # Create Flow Bundle to analyze OD flows through this link
            try:
                link_volume = link['volume']
                print(f"   Total link volume: {link_volume:,.1f} vehicles")
                
                # Get Flow Bundle object
                fb = Visum.Net.FlowBundle
                fb.Clear()
                
                # Set demand segments (all PrT segments)
                # Get all PrT demand segments
                all_demand_segments = Visum.Net.DemandSegments
                prt_segments = []
                
                # Get PrT modes first
                prt_modes = set()
                for mode in Visum.Net.Modes:
                    try:
                        tsys_set = mode.AttValue("TSYSSET")
                        # Check if any TSys in the set is PrT type
                        for tsys in Visum.Net.TSystems:
                            if tsys.AttValue("CODE") in tsys_set and tsys.AttValue("TYPE") == "PRT":
                                prt_modes.add(mode.AttValue("CODE"))
                                break
                    except:
                        pass
                
                # If no PrT modes found via TSys, use common PrT mode codes
                if not prt_modes:
                    prt_modes = {"C", "H", "LGV", "HGV", "CAR", "TRUCK"}
                
                print(f"   PrT modes detected: {', '.join(sorted(prt_modes))}")
                
                # Get all demand segments for PrT modes
                for dseg in all_demand_segments:
                    try:
                        dseg_code = dseg.AttValue("CODE")
                        mode_code = dseg.AttValue("MODE")
                        # Include PrT segments
                        if mode_code in prt_modes:
                            prt_segments.append(dseg_code)
                    except:
                        pass
                
                if not prt_segments:
                    print(f"   ⚠️  No PrT demand segments found")
                else:
                    # Set demand segments for flow bundle - USE ALL SEGMENTS!
                    dseg_string = ",".join(prt_segments)
                    fb.DemandSegments = dseg_string
                    
                    print(f"   Using {len(prt_segments)} demand segments:")
                    for dseg in prt_segments:
                        print(f"      • {dseg}")
                    
                    # Verify what FlowBundle actually received
                    try:
                        actual_dsegs = fb.DemandSegments
                        print(f"   ✓ FlowBundle.DemandSegments = '{actual_dsegs}'")
                    except Exception as verify_err:
                        print(f"   ⚠️  Could not verify DemandSegments: {str(verify_err)}")
                    
                    # Create NetElements container with the link
                    net_elements = Visum.CreateNetElements()
                    net_elements.Add(link_obj)
                    
                    # Execute flow bundle calculation
                    print(f"   Calculating flow bundle...")
                    fb.Execute(net_elements)
                    print(f"   ✓ Flow bundle executed successfully")
                    
                    # Get the flow bundle matrix to extract OD data
                    od_data = []
                    
                    # Iterate through ALL demand segments to get OD pairs
                    for dseg_code in prt_segments:
                        try:
                            dseg = Visum.Net.DemandSegments.ItemByKey(dseg_code)
                            # Get flow bundle matrix for this demand segment
                            fb_matrix = fb.GetOrCreateFlowBundleMatrix(dseg)
                            
                            if fb_matrix:
                                # Get non-zero OD pairs from matrix
                                # Note: Matrix iteration can be expensive, so we sample
                                pass
                        except Exception as dseg_error:
                            pass
                    
                    # Get flow bundle results from matrices
                    try:
                        print(f"   Extracting OD flows from flow bundle matrices...")
                        
                        # Prepare CSV output
                        csv_filename = f"flowbundle_link_{from_node}_{to_node}.csv"
                        csv_rows = []
                        csv_rows.append("Origin,Destination,Volume,DemandSegment")
                        
                        # Store results by demand segment for top 5 reporting
                        results_by_dseg = {}
                        
                        # For each demand segment, get the flow bundle matrix - USE ALL!
                        for dseg_code in prt_segments:
                            try:
                                dseg = Visum.Net.DemandSegments.ItemByKey(dseg_code)
                                fb_matrix = fb.GetOrCreateFlowBundleMatrix(dseg)
                                
                                if fb_matrix:
                                    dseg_od_flows = []
                                    
                                    # Get matrix info for debug
                                    matrix_no = fb_matrix.AttValue("NO")
                                    matrix_code = fb_matrix.AttValue("CODE")
                                    matrix_sum = fb_matrix.AttValue("SUM")
                                    
                                    # Get matrix values - ALL zones this time
                                    zones = Visum.Net.Zones
                                    zone_count = zones.Count
                                    
                                    print(f"      Scanning {dseg_code}:")
                                    print(f"         Matrix #{matrix_no} (CODE={matrix_code})")
                                    print(f"         Matrix SUM = {matrix_sum:.2f}")
                                    print(f"         Zones = {zone_count}")
                                    
                                    # Get all zone numbers using GetMultiAttValues
                                    zone_numbers_raw = zones.GetMultiAttValues("NO")
                                    zone_numbers = [item[1] if isinstance(item, tuple) else item for item in zone_numbers_raw]
                                    
                                    print(f"         Zone numbers: {zone_numbers[:10]}... (showing first 10)")
                                    
                                    # Test: try to read first non-zero value to verify matrix access
                                    test_count = 0
                                    test_found = False
                                    for origin_no in zone_numbers[:10]:
                                        for dest_no in zone_numbers[:10]:
                                            if origin_no != dest_no:
                                                test_val = fb_matrix.GetValue(origin_no, dest_no)
                                                test_count += 1
                                                if test_val > 0:
                                                    print(f"         🔍 Test: Matrix[{origin_no},{dest_no}] = {test_val:.4f}")
                                                    test_found = True
                                                    break
                                        if test_found:
                                            break
                                    
                                    if not test_found:
                                        print(f"         ⚠️  WARNING: No values found in first {test_count} cells tested!")
                                        print(f"         ⚠️  Matrix may be sparse or using different zone numbering")
                                    
                                    # Scan all zone pairs
                                    print(f"         Scanning {len(zone_numbers)} × {len(zone_numbers)} = {len(zone_numbers)**2} OD pairs...")
                                    cells_scanned = 0
                                    values_found = 0
                                    
                                    for origin_no in zone_numbers:
                                        for dest_no in zone_numbers:
                                            if origin_no != dest_no:
                                                cells_scanned += 1
                                                try:
                                                    # Get flow bundle matrix value
                                                    flow = fb_matrix.GetValue(origin_no, dest_no)
                                                    
                                                    if flow > 0:  # Any positive value
                                                        values_found += 1
                                                        dseg_od_flows.append({
                                                            'origin': origin_no,
                                                            'destination': dest_no,
                                                            'volume': flow
                                                        })
                                                        
                                                        # Add to CSV
                                                        csv_rows.append(f"{origin_no},{dest_no},{flow:.4f},{dseg_code}")
                                                        
                                                        # Add to aggregated od_data
                                                        found = False
                                                        for od in od_data:
                                                            if od['origin'] == origin_no and od['destination'] == dest_no:
                                                                od['volume'] += flow
                                                                found = True
                                                                break
                                                        
                                                        if not found:
                                                            od_data.append({
                                                                'origin': origin_no,
                                                                'destination': dest_no,
                                                                'volume': flow
                                                            })
                                                except Exception as cell_error:
                                                    pass
                                    
                                    print(f"         ✓ Scanned {cells_scanned} cells, found {values_found} values > 0")
                                    
                                    # Sort and get top 5 for this demand segment
                                    dseg_od_flows.sort(key=lambda x: x['volume'], reverse=True)
                                    results_by_dseg[dseg_code] = dseg_od_flows[:5]
                                    
                                    print(f"      Found {len(dseg_od_flows)} OD pairs with flow > 0")
                                    
                            except Exception as dseg_err:
                                print(f"      ⚠️  Error with {dseg_code}: {str(dseg_err)}")
                        
                        # Write CSV file
                        try:
                            with open(csv_filename, 'w', encoding='utf-8') as f:
                                f.write('\n'.join(csv_rows))
                            print(f"\n   📄 Exported: {csv_filename} ({len(csv_rows)-1} OD pairs)")
                        except Exception as csv_err:
                            print(f"   ⚠️  Could not write CSV: {str(csv_err)}")
                        
                        # Report top 5 for each demand segment
                        if results_by_dseg:
                            print(f"\n   🔝 Top 5 OD pairs by demand segment:")
                            for dseg_code, top_flows in results_by_dseg.items():
                                if top_flows:
                                    print(f"\n   📊 {dseg_code}:")
                                    print(f"      {'Origin':<12} {'Dest':<12} {'Volume':>12}")
                                    print(f"      {'-'*40}")
                                    for flow in top_flows:
                                        print(f"      {flow['origin']:<12} {flow['destination']:<12} {flow['volume']:>12,.2f}")
                        
                        if od_data:
                            # Sort by volume descending
                            od_data.sort(key=lambda x: x['volume'], reverse=True)
                            
                            # Show top 10 OD pairs
                            top_od = od_data[:10]
                            total_od_volume = sum(x['volume'] for x in od_data)
                            
                            print(f"\n   Top 10 OD pairs from sample (total: {total_od_volume:.1f}):")
                            print(f"   {'Origin':<12} {'Dest':<12} {'Volume':>12} {'%':>8}")
                            print(f"   {'-'*50}")
                            
                            for i, od in enumerate(top_od, 1):
                                pct = (od['volume'] / total_od_volume * 100) if total_od_volume > 0 else 0
                                print(f"   {od['origin']:<12} {od['destination']:<12} {od['volume']:>12,.1f} {pct:>7.1f}%")
                            
                            od_analysis_results.append({
                                'rank': rank,
                                'from_node': from_node,
                                'to_node': to_node,
                                'vc_ratio': link['vc_ratio'],
                                'sampled_od_pairs': len(od_data),
                                'total_sampled_volume': round(total_od_volume, 2),
                                'top_10_od_pairs': [
                                    {
                                        'origin': od['origin'],
                                        'destination': od['destination'],
                                        'volume': round(od['volume'], 2),
                                        'percentage': round((od['volume'] / total_od_volume * 100), 2)
                                    }
                                    for od in top_od
                                ]
                            })
                        else:
                            print(f"   ⚠️  No OD pairs found in sample")
                    
                    except Exception as od_error:
                        print(f"   ⚠️  Could not analyze OD pairs: {str(od_error)}")
                    
            except Exception as fb_error:
                print(f"   ⚠️  Could not create flow bundle: {str(fb_error)}")
            
        except Exception as e:
            print(f"   ❌ Error analyzing link: {str(e)}")
    
    print("\n" + "="*80)
    print(f"✅ OD Analysis completed for {len(od_analysis_results)} links")
    print("="*80 + "\n")
    
    # Build result for MCP
    result = {
        "status": "success",
        "analysis_period": ANALYSIS_PERIOD,
        "total_links": total_links,
        "links_with_traffic": total_with_traffic,
        "congested_links": total_congested,
        "overcapacity_links": total_overcapacity,
        "maps_generated": len(maps_generated),
        "map_files": [m["file"] for m in maps_generated],
        "od_analysis": od_analysis_results,
        "top_congested": [
            {
                "rank": i+1,
                "from_node": link['from_node'],
                "to_node": link['to_node'],
                "name": link['name'],
                "vc_ratio": round(link['vc_ratio'], 4),
                "volume": round(link['volume'], 2),
                "capacity": round(link['capacity'], 2),
                "length": round(link['length'], 2),
                "type_no": link['type_no']
            }
            for i, link in enumerate(top_congested)
        ]
    }

except Exception as e:
    import traceback
    result = {
        "status": "error",
        "error": str(e),
        "traceback": traceback.format_exc()
    }
    print(f"\n❌ Error: {e}")
    traceback.print_exc()
