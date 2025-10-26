"""
Export Visum Graphic Parameters (.gpa) to Image Files (PNG/JPG)

This script loads a .gpa file (graphic parameters) and exports the network view as an image.
Useful for creating reports, presentations, or documentation from Visum network visualizations.

Usage:
    1. Open your Visum project
    2. Run this script in VisumPy console or via project_execute
    3. Script will find all .gpa files in project directory
    4. Exports each .gpa as a PNG image

Configuration:
    - Image width: 1920 pixels (HD resolution)
    - Image format: PNG (can also use .jpg, .bmp, .tif)
    - DPI: 150 (default, can be changed)
    - Quality: 100 (for JPG only)
"""

import os
import sys

print("\n" + "=" * 70)
print("🎨 VISUM GPA TO IMAGE EXPORT - STARTING")
print("=" * 70)

# =============================================================================
# CONFIGURATION
# =============================================================================

# Paper format presets (width, height in mm)
PAPER_FORMATS = {
    'A5': (148, 210),        # A5 landscape
    'A5_portrait': (210, 148),
    'A4': (210, 297),        # A4 landscape  
    'A4_portrait': (297, 210),
    'A3': (297, 420),        # A3 landscape
    'A3_portrait': (420, 297),
    'custom': None           # Use IMAGE_WIDTH_PIXELS directly
}

# Image export settings
PAPER_FORMAT = 'A4'         # A5, A4, A3, A5_portrait, A4_portrait, A3_portrait, custom
IMAGE_WIDTH_PIXELS = 1920   # Only used if PAPER_FORMAT='custom'
IMAGE_FORMAT = 'png'        # png, jpg, bmp, tif
IMAGE_DPI = 150            # Resolution (96 = screen, 150 = print quality, 300 = high quality)
JPEG_QUALITY = 100         # Quality for JPEG (1-100)

# Output filename pattern
OUTPUT_PATTERN = "{project_name}_{gpa_name}.{format}"

# =============================================================================
# PAPER SIZE UTILITIES
# =============================================================================

def calculate_pixels_from_paper(paper_format, dpi=150, orientation='landscape'):
    """
    Calculate image dimensions in pixels from paper format.
    
    Args:
        paper_format: Paper size (A5, A4, A3, etc.)
        dpi: Dots per inch (resolution)
        orientation: 'landscape' or 'portrait'
    
    Returns:
        tuple: (width_px, height_px)
    
    Examples:
        A4 @ 150 DPI landscape: 1240 × 1754 pixels
        A4 @ 300 DPI landscape: 2480 × 3508 pixels
        A5 @ 150 DPI portrait: 1240 × 874 pixels
    """
    if paper_format == 'custom':
        return None
    
    # Get paper dimensions in mm
    if orientation == 'portrait':
        # Swap width and height for portrait
        key = f"{paper_format}_portrait" if paper_format in ['A5', 'A4', 'A3'] else paper_format
    else:
        key = paper_format
    
    if key not in PAPER_FORMATS:
        raise ValueError(f"Unknown paper format: {paper_format}")
    
    width_mm, height_mm = PAPER_FORMATS[key]
    
    # Convert mm to inches (1 inch = 25.4 mm)
    width_inches = width_mm / 25.4
    height_inches = height_mm / 25.4
    
    # Convert inches to pixels
    width_px = int(width_inches * dpi)
    height_px = int(height_inches * dpi)
    
    return width_px, height_px


def get_paper_info(paper_format, dpi=150):
    """Get human-readable paper format info."""
    if paper_format == 'custom':
        return "Custom size"
    
    if paper_format not in PAPER_FORMATS:
        return f"Unknown format: {paper_format}"
    
    width_mm, height_mm = PAPER_FORMATS[paper_format]
    width_px, height_px = calculate_pixels_from_paper(paper_format.replace('_portrait', ''), 
                                                       dpi, 
                                                       'portrait' if '_portrait' in paper_format else 'landscape')
    
    return f"{paper_format}: {width_mm}×{height_mm}mm = {width_px}×{height_px}px @ {dpi} DPI"

# =============================================================================
# VISUM CONNECTION
# =============================================================================

# Check if running in Visum or need to connect
try:
    # Test if visum is available (running in VisumPy console)
    visum.GetVersion()
    print("✓ Running in Visum environment")
except NameError:
    # Not in Visum - try to connect via COM
    print("⚠ Not in Visum - attempting COM connection...")
    try:
        import win32com.client
        visum = win32com.client.Dispatch("Visum.Visum.250")
        print("✓ Connected to Visum via COM")
    except Exception as e:
        print(f"❌ Cannot connect to Visum: {e}")
        print("\nPlease run this script in one of these ways:")
        print("1. Load and run in Visum's VisumPy console (Scripts > Run Script)")
        print("2. Use project_execute MCP tool")
        sys.exit(1)

# =============================================================================
# MAIN SCRIPT
# =============================================================================

def export_gpa_to_image(gpa_file_path, output_image_path, width=None, height=None, dpi=150, quality=100, paper_format=None):
    """
    Export a .gpa file to an image file.
    
    Args:
        gpa_file_path: Full path to .gpa file
        output_image_path: Full path to output image file
        width: Image width in pixels (ignored if paper_format specified)
        height: Image height in pixels (ignored if paper_format specified)
        dpi: Image resolution (dots per inch)
        quality: JPEG quality (1-100)
        paper_format: Paper format (A5, A4, A3, etc.) - overrides width/height
    
    Returns:
        dict: Result with success status and file info
    """
    result = {
        'gpa_file': os.path.basename(gpa_file_path),
        'output_file': os.path.basename(output_image_path),
        'success': False
    }
    
    try:
        # Determine image dimensions
        if paper_format and paper_format != 'custom':
            orientation = 'portrait' if '_portrait' in paper_format else 'landscape'
            base_format = paper_format.replace('_portrait', '')
            width_px, height_px = calculate_pixels_from_paper(base_format, dpi, orientation)
            result['paper_format'] = paper_format
            result['paper_info'] = get_paper_info(paper_format, dpi)
            print(f"📄 Paper format: {result['paper_info']}")
        elif width and height:
            width_px = width
            height_px = height
            result['paper_format'] = 'custom (specified dimensions)'
        elif width:
            width_px = width
            height_px = None  # Will be calculated from aspect ratio
            result['paper_format'] = 'custom (width only)'
        else:
            width_px = 1920
            height_px = None
            result['paper_format'] = 'default (1920px width)'
        
        # Load GPA (Graphic Parameters)
        print(f"📂 Loading GPA: {os.path.basename(gpa_file_path)}")
        visum.Net.GraphicParameters.Open(gpa_file_path)
        result['gpa_loaded'] = True
        
        # Get network bounds from Print Area
        print(f"📐 Getting network bounds...")
        printArea = visum.Net.PrintParameters.PrintArea
        left = printArea.AttValue('LEFTMARGIN')
        bottom = printArea.AttValue('BOTTOMMARGIN')
        right = printArea.AttValue('RIGHTMARGIN')
        top = printArea.AttValue('TOPMARGIN')
        
        result['bounds'] = {
            'left': left,
            'bottom': bottom,
            'right': right,
            'top': top
        }
        
        print(f"   Bounds: ({left:.2f}, {bottom:.2f}) to ({right:.2f}, {top:.2f})")
        
        # Calculate aspect ratio
        width_net = right - left
        height_net = top - bottom
        aspect_ratio = height_net / width_net if width_net > 0 else 1.0
        result['aspect_ratio'] = round(aspect_ratio, 3)
        
        # If height not specified, calculate from aspect ratio
        if height_px is None:
            height_px = int(width_px * aspect_ratio)
            print(f"📐 Calculated height from aspect ratio: {height_px}px")
        
        result['dimensions'] = {
            'width_px': width_px,
            'height_px': height_px,
            'aspect_ratio': aspect_ratio
        }
        
        # Export network image
        print(f"🎨 Exporting to {IMAGE_FORMAT.upper()} ({width_px}×{height_px}px @ {dpi} DPI)...")
        visum.Graphic.ExportNetworkImageFile(
            output_image_path,
            left, bottom, right, top,
            width_px,
            dpi,
            quality
        )
        
        # Verify file was created
        if os.path.exists(output_image_path):
            file_size_kb = os.path.getsize(output_image_path) / 1024
            result['success'] = True
            result['size_kb'] = round(file_size_kb, 2)
            result['size_mb'] = round(file_size_kb / 1024, 2)
            result['width_px'] = width_px
            result['height_px'] = height_px
            result['dpi'] = dpi
            print(f"✅ Export successful: {file_size_kb:.2f} KB")
        else:
            result['error'] = 'File not created'
            print(f"❌ Export failed: File not created")
        
    except Exception as e:
        result['error'] = str(e)
        print(f"❌ Error: {e}")
    
    return result


def main():
    """Main function to export all .gpa files in project directory."""
    
    print("=" * 70)
    print("🎨 GPA to Image Export Tool")
    print("=" * 70)
    
    try:
        # Get project info
        project_path = visum.GetPath(1)
        project_dir = os.path.dirname(project_path)
        project_name = os.path.splitext(os.path.basename(project_path))[0]
        
        print(f"\n📂 Project: {project_name}")
        print(f"📁 Directory: {project_dir}")
        
        # Show paper format configuration
        if PAPER_FORMAT != 'custom':
            print(f"\n📄 Paper format: {get_paper_info(PAPER_FORMAT, IMAGE_DPI)}")
        else:
            print(f"\n📐 Custom size: {IMAGE_WIDTH_PIXELS}px width @ {IMAGE_DPI} DPI")
        
        # Find all .gpa files
        gpa_files = [f for f in os.listdir(project_dir) if f.lower().endswith('.gpa')]
        
        if not gpa_files:
            print(f"\n⚠️  No .gpa files found in project directory")
            return {'error': 'No GPA files found', 'total': 0}
        
        print(f"\n✅ Found {len(gpa_files)} GPA file(s):")
        for i, gpa in enumerate(gpa_files, 1):
            print(f"   {i}. {gpa}")
        
        # Export each GPA
        results = []
        
        for i, gpa_filename in enumerate(gpa_files, 1):
            print(f"\n{'─' * 70}")
            print(f"📊 Processing {i}/{len(gpa_files)}: {gpa_filename}")
            print(f"{'─' * 70}")
            
            # Build paths
            gpa_path = os.path.join(project_dir, gpa_filename)
            gpa_name = os.path.splitext(gpa_filename)[0]
            
            # Generate output filename
            output_filename = OUTPUT_PATTERN.format(
                project_name=project_name,
                gpa_name=gpa_name,
                format=IMAGE_FORMAT
            )
            output_path = os.path.join(project_dir, output_filename)
            
            # Export with paper format
            result = export_gpa_to_image(
                gpa_path,
                output_path,
                width=IMAGE_WIDTH_PIXELS if PAPER_FORMAT == 'custom' else None,
                dpi=IMAGE_DPI,
                quality=JPEG_QUALITY,
                paper_format=PAPER_FORMAT
            )
            
            results.append(result)
        
        # Summary
        print(f"\n{'=' * 70}")
        print("📊 EXPORT SUMMARY")
        print(f"{'=' * 70}")
        
        successful = [r for r in results if r.get('success')]
        failed = [r for r in results if not r.get('success')]
        
        print(f"\n✅ Successful exports: {len(successful)}/{len(results)}")
        for r in successful:
            dims = r.get('dimensions', {})
            print(f"   - {r['gpa_file']} → {r['output_file']}")
            print(f"     {dims.get('width_px')}×{dims.get('height_px')}px @ {r.get('dpi')} DPI = {r['size_kb']} KB")
        
        if failed:
            print(f"\n❌ Failed exports: {len(failed)}")
            for r in failed:
                print(f"   - {r['gpa_file']}: {r.get('error', 'Unknown error')}")
        
        print(f"\n📁 Output directory: {project_dir}")
        print(f"\n✨ Export complete!")
        
        return {
            'total': len(results),
            'successful': len(successful),
            'failed': len(failed),
            'results': results
        }
        
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        return {'error': str(e)}


# =============================================================================
# EXECUTE
# =============================================================================

print("\n🚀 Starting export process...\n")

if __name__ == "__main__":
    result = main()
    print("\n" + "=" * 70)
    print("✨ SCRIPT COMPLETED")
    print("=" * 70)
    print(f"\nResult: {result}")
else:
    # When imported or run via exec()
    result = main()
    print("\n" + "=" * 70)
    print("✨ SCRIPT COMPLETED")
    print("=" * 70)
    print(f"\nResult: {result}")

# Return result for MCP integration
result
