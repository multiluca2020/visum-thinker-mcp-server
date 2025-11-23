"""
Test Legend Scaling Functionality

This script tests the automatic legend text scaling when exporting GPA files
with different paper formats.
"""

import os
import sys

# Test configuration
PROJECT_PATH = r"H:\go\reports\Input\S000009result.ver"
GPA_FILE = "Flussogramma_tpb.gpa"  # Replace with actual GPA filename
OUTPUT_DIR = r"H:\visum-thinker-mcp-server\test-exports"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 70)
print("🧪 LEGEND SCALING TEST")
print("=" * 70)

try:
    # Connect to Visum
    import win32com.client
    visum = win32com.client.Dispatch("Visum.Visum.250")
    
    print(f"\n📂 Loading project: {os.path.basename(PROJECT_PATH)}")
    visum.LoadVersion(PROJECT_PATH)
    print("✅ Project loaded")
    
    # Get project directory
    project_dir = os.path.dirname(PROJECT_PATH)
    gpa_path = os.path.join(project_dir, GPA_FILE)
    
    if not os.path.exists(gpa_path):
        print(f"\n❌ GPA file not found: {gpa_path}")
        print("\n📁 Available GPA files in project directory:")
        for file in os.listdir(project_dir):
            if file.endswith('.gpa'):
                print(f"   • {file}")
        sys.exit(1)
    
    # Test cases: different paper formats
    test_cases = [
        ('A5', 150, 'small'),
        ('A4', 150, 'standard'),
        ('A4', 300, 'high_quality'),
        ('A5', 600, 'professional'),
    ]
    
    print(f"\n🎨 Testing {len(test_cases)} export configurations...")
    print(f"📍 GPA file: {GPA_FILE}\n")
    
    for paper_format, dpi, label in test_cases:
        output_file = os.path.join(OUTPUT_DIR, f"test_legend_{paper_format}_{dpi}dpi_{label}.png")
        
        print(f"\n{'=' * 70}")
        print(f"📋 Test: {paper_format} @ {dpi} DPI ({label})")
        print(f"{'=' * 70}")
        
        # Load GPA
        visum.Net.GraphicParameters.Open(gpa_path)
        
        # Calculate dimensions
        if paper_format == 'A5':
            width_mm, height_mm = 148, 210
        else:  # A4
            width_mm, height_mm = 210, 297
        
        width_px = int((width_mm / 25.4) * dpi)
        height_px = int((height_mm / 25.4) * dpi)
        
        # Calculate scale factor
        reference_width = 1240  # A4 @ 150 DPI
        scale_factor = width_px / reference_width
        
        print(f"📐 Dimensions: {width_px}×{height_px}px")
        print(f"🔧 Legend scale factor: {scale_factor:.3f}x")
        
        # Try to scale legend
        try:
            legend_params = visum.Net.GraphicParameters.LegendParameters
            if legend_params:
                legend_general = legend_params.LegendGeneralParameters
                
                # Scale title
                try:
                    title_text = legend_general.TitleTextParameters
                    old_size = title_text.AttValue('TEXTSIZE')
                    new_size = old_size * scale_factor
                    title_text.SetAttValue('TEXTSIZE', new_size)
                    print(f"   ✅ Title: {old_size:.2f}mm → {new_size:.2f}mm")
                except Exception as e:
                    print(f"   ⚠️  Title: {e}")
                
                # Scale elements
                try:
                    elem_text = legend_general.ElementTextParameters
                    old_size = elem_text.AttValue('TEXTSIZE')
                    new_size = old_size * scale_factor
                    elem_text.SetAttValue('TEXTSIZE', new_size)
                    print(f"   ✅ Elements: {old_size:.2f}mm → {new_size:.2f}mm")
                except Exception as e:
                    print(f"   ⚠️  Elements: {e}")
                
                print("   ✅ Legend scaling completed")
            else:
                print("   ⚠️  No legend in this GPA")
        except Exception as e:
            print(f"   ❌ Legend scaling failed: {e}")
        
        # Export
        print(f"🎨 Exporting...")
        printArea = visum.Net.PrintParameters.PrintArea
        left = printArea.AttValue('LEFTMARGIN')
        bottom = printArea.AttValue('BOTTOMMARGIN')
        right = printArea.AttValue('RIGHTMARGIN')
        top = printArea.AttValue('TOPMARGIN')
        
        visum.Graphic.ExportNetworkImageFile(
            output_file,
            left, bottom, right, top,
            width_px,
            dpi,
            100  # quality
        )
        
        if os.path.exists(output_file):
            size_mb = os.path.getsize(output_file) / (1024 * 1024)
            print(f"✅ Export successful: {size_mb:.2f} MB")
            print(f"📁 {output_file}")
        else:
            print(f"❌ Export failed")
    
    print(f"\n{'=' * 70}")
    print("✅ ALL TESTS COMPLETED")
    print(f"{'=' * 70}")
    print(f"\n📁 Check results in: {OUTPUT_DIR}")
    
except Exception as e:
    print(f"\n❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
