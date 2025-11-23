"""
Check if Visum project has assignment results

Verifies:
- PrT Assignment results (volumes on links)
- PuT Assignment results (volumes on lines)
- Skim matrices
- Saved paths
"""

import sys

def check_assignment_results():
    """Check if project has assignment results."""
    
    print("=" * 70)
    print("🔍 CHECKING ASSIGNMENT RESULTS")
    print("=" * 70)
    
    results = {
        'has_prt_results': False,
        'has_put_results': False,
        'has_skim_matrices': False,
        'prt_loaded_links': 0,
        'put_loaded_lines': 0,
        'skim_count': 0,
        'details': []
    }
    
    try:
        # Check if visum is available
        try:
            visum.GetVersion()
            print(f"\n✅ Visum version: {visum.GetVersion()}")
        except NameError:
            print("\n❌ Error: Not running in Visum environment")
            print("Run this script in VisumPy console or via project_execute")
            return results
        
        # Check project
        project_path = visum.GetPath(1)
        print(f"📂 Project: {project_path}")
        
        # =====================================================================
        # CHECK PRT ASSIGNMENT RESULTS
        # =====================================================================
        print("\n" + "=" * 70)
        print("🚗 PRT ASSIGNMENT RESULTS")
        print("=" * 70)
        
        links = visum.Net.Links
        link_count = links.Count
        print(f"\n📊 Total links: {link_count:,}")
        
        # Check if VOLPRT attribute exists and has values
        try:
            # Count links with non-zero VOLPRT
            links_with_volume = 0
            total_volume = 0.0
            
            # Sample first 100 links to check
            sample_size = min(100, link_count)
            for i in range(1, sample_size + 1):
                try:
                    link = links.ItemByKey(i)
                    vol = link.AttValue('VOLPRT')
                    if vol and vol > 0:
                        links_with_volume += 1
                        total_volume += vol
                except:
                    continue
            
            if links_with_volume > 0:
                results['has_prt_results'] = True
                results['prt_loaded_links'] = links_with_volume
                print(f"✅ PrT volumes found!")
                print(f"   • Links with traffic (sample): {links_with_volume}/{sample_size}")
                print(f"   • Total volume (sample): {total_volume:,.0f} veh")
                results['details'].append(f"PrT: {links_with_volume} links with volumes")
            else:
                print(f"⚠️  No PrT volumes found (checked {sample_size} links)")
                print(f"   → Attribute VOLPRT exists but all zeros")
                
        except Exception as e:
            print(f"❌ Cannot access VOLPRT: {e}")
            print(f"   → Probably no PrT assignment has been run")
        
        # =====================================================================
        # CHECK PUT ASSIGNMENT RESULTS
        # =====================================================================
        print("\n" + "=" * 70)
        print("🚌 PUT ASSIGNMENT RESULTS")
        print("=" * 70)
        
        try:
            lines = visum.Net.Lines
            line_count = lines.Count
            print(f"\n📊 Total lines: {line_count:,}")
            
            # Check if lines have passenger volumes
            lines_with_pax = 0
            total_pax = 0.0
            
            sample_size = min(50, line_count)
            for i in range(1, sample_size + 1):
                try:
                    line = lines.ItemByKey(i)
                    pax = line.AttValue('PASKM')  # Passenger-km
                    if pax and pax > 0:
                        lines_with_pax += 1
                        total_pax += pax
                except:
                    continue
            
            if lines_with_pax > 0:
                results['has_put_results'] = True
                results['put_loaded_lines'] = lines_with_pax
                print(f"✅ PuT assignment results found!")
                print(f"   • Lines with passengers (sample): {lines_with_pax}/{sample_size}")
                print(f"   • Total pax-km (sample): {total_pax:,.0f}")
                results['details'].append(f"PuT: {lines_with_pax} lines with passengers")
            else:
                print(f"⚠️  No PuT assignment results found")
                
        except Exception as e:
            print(f"❌ Cannot check PuT results: {e}")
        
        # =====================================================================
        # CHECK SKIM MATRICES
        # =====================================================================
        print("\n" + "=" * 70)
        print("📋 SKIM MATRICES")
        print("=" * 70)
        
        try:
            matrices = visum.Net.Matrices
            matrix_count = matrices.Count
            print(f"\n📊 Total matrices: {matrix_count}")
            
            # Count skim matrices (usually have "Skim" or "IMP" in code)
            skim_matrices = []
            for i in range(1, min(matrix_count + 1, 100)):  # Check first 100
                try:
                    matrix = matrices.ItemByKey(i)
                    code = matrix.AttValue('CODE')
                    name = matrix.AttValue('NAME')
                    
                    # Check if it's a skim matrix
                    if 'SKIM' in code.upper() or 'IMP' in code.upper() or 'TIME' in code.upper():
                        skim_matrices.append(f"{code}: {name}")
                except:
                    continue
            
            if skim_matrices:
                results['has_skim_matrices'] = True
                results['skim_count'] = len(skim_matrices)
                print(f"✅ Skim matrices found: {len(skim_matrices)}")
                for skim in skim_matrices[:10]:  # Show first 10
                    print(f"   • {skim}")
                if len(skim_matrices) > 10:
                    print(f"   ... and {len(skim_matrices) - 10} more")
                results['details'].append(f"Skim: {len(skim_matrices)} matrices")
            else:
                print(f"⚠️  No skim matrices found")
                
        except Exception as e:
            print(f"❌ Cannot check matrices: {e}")
        
        # =====================================================================
        # SUMMARY
        # =====================================================================
        print("\n" + "=" * 70)
        print("📊 SUMMARY")
        print("=" * 70)
        
        if results['has_prt_results'] or results['has_put_results'] or results['has_skim_matrices']:
            print("\n✅ PROJECT HAS ASSIGNMENT RESULTS!")
            print("\nFound:")
            for detail in results['details']:
                print(f"  ✓ {detail}")
        else:
            print("\n⚠️  NO ASSIGNMENT RESULTS FOUND")
            print("\nThe project appears to be a base network without:")
            print("  • PrT assignment results (no traffic volumes)")
            print("  • PuT assignment results (no passenger flows)")
            print("  • Skim matrices (no impedance calculations)")
            print("\nYou may need to run assignments to generate results.")
        
        return results
        
    except Exception as e:
        print(f"\n❌ Error checking results: {e}")
        import traceback
        traceback.print_exc()
        return results

# Run check
if __name__ == "__main__":
    results = check_assignment_results()
    
    # Return status code
    if results['has_prt_results'] or results['has_put_results']:
        sys.exit(0)  # Has results
    else:
        sys.exit(1)  # No results
