"""
Export Visum Graphic Parameters (.gpa) to Image Files (PNG/JPG/SVG)

This script loads a .gpa file (graphic parameters) and exports the network view as an image.
Useful for creating reports, presentations, or documentation from Visum network visualizations.

Supported formats:
    - Raster: PNG, JPG, BMP, TIF (pixel-based, DPI-dependent)
    - Vector: SVG (scalable, resolution-independent, requires GUI)

Usage:
    1. Open your Visum project
    2. Run this script in VisumPy console or via project_execute
    3. Script will find all .gpa files in project directory
    4. Exports each .gpa in the selected format

Configuration (edit CONFIGURATION section below):
    RASTER FORMATS (PNG/JPG/BMP/TIF):
        - Paper format: A5, A4, A3, portrait/landscape
        - Image width: 1920 pixels (or custom)
        - DPI: 150 (screen: 96, print: 150-300)
        - Quality: 100 (JPEG only)
    
    VECTOR FORMAT (SVG):
        - Non-scaling stroke: True (keeps line widths constant)
        - Copy pictures: False (don't copy external images)
        - ⚠️  Requires Visum GUI to be open and visible!

Examples:
    - High-quality print: EXPORT_FORMAT='png', PAPER_FORMAT='A4', IMAGE_DPI=300
    - Screen display: EXPORT_FORMAT='png', PAPER_FORMAT='custom', IMAGE_WIDTH_PIXELS=1920
    - Vector (editable): EXPORT_FORMAT='svg' (requires visible GUI)
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

# Export format selection
EXPORT_FORMAT = 'png'       # png, jpg, svg, bmp, tif

# Image export settings (for raster formats: png, jpg, bmp, tif)
PAPER_FORMAT = 'A5'         # A5, A4, A3, A5_portrait, A4_portrait, A3_portrait, custom
IMAGE_WIDTH_PIXELS = 1920   # Only used if PAPER_FORMAT='custom'
IMAGE_DPI = 600            # Resolution (96 = screen, 150 = print, 300 = high quality, 600 = ultra high, 1200 = maximum)
JPEG_QUALITY = 100         # Quality for JPEG (1-100)

# DPI PRESETS:
# - 96 DPI:   Screen display, web (A5: 559×827px, A4: 791×1119px)
# - 150 DPI:  Standard print (A5: 874×1240px, A4: 1240×1754px)
# - 300 DPI:  High quality print (A5: 1748×2480px, A4: 2480×3508px)
# - 600 DPI:  Professional print, large format (A5: 3496×4960px, A4: 4960×7016px)
# - 1200 DPI: Maximum detail, photo-quality (A5: 6992×9921px, A4: 9921×14031px)

# SVG export settings (for vector format)
SVG_USE_NON_SCALING_STROKE = True   # Keep line widths constant when scaling
SVG_COPY_PICTURES = False           # Copy external image files

# Output filename pattern
OUTPUT_PATTERN = "{project_name}_{gpa_name}.{format}"

# =============================================================================
# PAPER SIZE UTILITIES
# =============================================================================

def scale_legend_text_sizes(scale_factor):
    """
    Scale legend text sizes by a given factor.
    This ensures the legend scales proportionally with the paper format.
    
    Args:
        scale_factor: Multiplication factor (e.g., 2.0 for double size)
    
    Returns:
        dict: Result with scaled attributes or error info
    """
    result = {
        'success': False,
        'scaled_elements': []
    }
    
    try:
        # Try to access legend parameters
        legend_params = visum.Net.GraphicParameters.LegendParameters
        if not legend_params:
            result['error'] = 'LegendParameters not available in this GPA'
            return result
        
        legend_general = legend_params.LegendGeneralParameters
        
        # Scale title text
        try:
            title_text = legend_general.TitleTextParameters
            old_size = title_text.AttValue('TEXTSIZE')
            new_size = old_size * scale_factor
            title_text.SetAttValue('TEXTSIZE', new_size)
            result['scaled_elements'].append(f'Title: {old_size:.2f} → {new_size:.2f}mm')
        except Exception as e:
            result['scaled_elements'].append(f'Title: FAILED ({str(e)})')
        
        # Scale element text
        try:
            element_text = legend_general.ElementTextParameters
            old_size = element_text.AttValue('TEXTSIZE')
            new_size = old_size * scale_factor
            element_text.SetAttValue('TEXTSIZE', new_size)
            result['scaled_elements'].append(f'Elements: {old_size:.2f} → {new_size:.2f}mm')
        except Exception as e:
            result['scaled_elements'].append(f'Elements: FAILED ({str(e)})')
        
        # Scale attribute text
        try:
            attr_text = legend_general.AttributeTextParameters
            old_size = attr_text.AttValue('TEXTSIZE')
            new_size = old_size * scale_factor
            attr_text.SetAttValue('TEXTSIZE', new_size)
            result['scaled_elements'].append(f'Attributes: {old_size:.2f} → {new_size:.2f}mm')
        except Exception as e:
            result['scaled_elements'].append(f'Attributes: FAILED ({str(e)})')
        
        # Scale label text
        try:
            label_text = legend_general.LabelTextParameters
            old_size = label_text.AttValue('TEXTSIZE')
            new_size = old_size * scale_factor
            label_text.SetAttValue('TEXTSIZE', new_size)
            result['scaled_elements'].append(f'Labels: {old_size:.2f} → {new_size:.2f}mm')
        except Exception as e:
            result['scaled_elements'].append(f'Labels: FAILED ({str(e)})')
        
        # Scale sub-element text
        try:
            sub_text = legend_general.SubElementTextParameters
            old_size = sub_text.AttValue('TEXTSIZE')
            new_size = old_size * scale_factor
            sub_text.SetAttValue('TEXTSIZE', new_size)
            result['scaled_elements'].append(f'SubElements: {old_size:.2f} → {new_size:.2f}mm')
        except Exception as e:
            result['scaled_elements'].append(f'SubElements: FAILED ({str(e)})')
        
        # Scale graphic scale text
        try:
            scale_text = legend_general.GraphicScaleTextParameters
            old_size = scale_text.AttValue('TEXTSIZE')
            new_size = old_size * scale_factor
            scale_text.SetAttValue('TEXTSIZE', new_size)
            result['scaled_elements'].append(f'GraphicScale: {old_size:.2f} → {new_size:.2f}mm')
        except Exception as e:
            result['scaled_elements'].append(f'GraphicScale: FAILED ({str(e)})')
        
        result['success'] = True
        result['scale_factor'] = scale_factor
        
    except Exception as e:
        result['error'] = str(e)
    
    return result


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
        
        # Scale legend text sizes based on paper format
        # Base reference: A4 @ 150 DPI (standard print size)
        # Calculate scale factor based on deviation from this reference
        if paper_format and paper_format != 'custom':
            base_format = paper_format.replace('_portrait', '')
            
            # Reference: A4 landscape @ 150 DPI = 1240px width
            reference_width = 1240  # A4 landscape @ 150 DPI
            scale_factor = width_px / reference_width
            
            print(f"🔧 Scaling legend text by {scale_factor:.2f}x (for {base_format} @ {dpi} DPI)...")
            legend_scale_result = scale_legend_text_sizes(scale_factor)
            
            if legend_scale_result['success']:
                print(f"   ✅ Legend scaled:")
                for element in legend_scale_result['scaled_elements']:
                    print(f"      • {element}")
                result['legend_scaled'] = True
                result['legend_scale_factor'] = scale_factor
            else:
                print(f"   ⚠️  Legend scaling skipped: {legend_scale_result.get('error', 'No legend in GPA')}")
                result['legend_scaled'] = False
        
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
        
        # Determine output format from file extension
        output_format = os.path.splitext(output_image_path)[1].replace('.', '').upper()
        
        # Export network image
        print(f"🎨 Exporting to {output_format} ({width_px}×{height_px}px @ {dpi} DPI)...")
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


def export_gpa_to_svg(gpa_file_path, output_svg_path, use_non_scaling_stroke=True, copy_pictures=False):
    """
    Export a .gpa file to SVG (vector) format.
    
    Args:
        gpa_file_path: Full path to .gpa file
        output_svg_path: Full path to output SVG file
        use_non_scaling_stroke: Keep line widths constant when scaling
        copy_pictures: Copy external image files
    
    Returns:
        dict: Result with success status and file info
    
    Note:
        SVG export requires Visum GUI to be open and visible.
        Use PNG/JPG for headless/background execution.
    """
    result = {
        'gpa_file': os.path.basename(gpa_file_path),
        'output_file': os.path.basename(output_svg_path),
        'success': False,
        'format': 'svg'
    }
    
    try:
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
        
        # Set the view window to the PrintArea bounds
        print(f"🗺️  Setting view to PrintArea bounds...")
        visum.Graphic.SetWindow(left, bottom, right, top)
        
        # Export SVG
        print(f"🎨 Exporting to SVG (vector format)...")
        visum.Graphic.WriteSVG(
            output_svg_path,
            UseNonScalingStroke=use_non_scaling_stroke,
            CopyPictures=copy_pictures
        )
        
        # Verify file was created
        if os.path.exists(output_svg_path):
            file_size_kb = os.path.getsize(output_svg_path) / 1024
            result['success'] = True
            result['size_kb'] = round(file_size_kb, 2)
            result['size_mb'] = round(file_size_kb / 1024, 2)
            result['format_type'] = 'SVG (vector)'
            result['scalable'] = True
            print(f"✅ Export successful: {file_size_kb:.2f} KB (vector format)")
        else:
            result['error'] = 'File not created'
            print(f"❌ Export failed: File not created")
        
    except Exception as e:
        result['error'] = str(e)
        print(f"❌ Error: {e}")
        if "SetWindow" in str(e) or "GUI" in str(e):
            result['error'] += " (SVG requires Visum GUI to be visible)"
    
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
        
        # Show export format
        print(f"\n🎨 Export format: {EXPORT_FORMAT.upper()}")
        
        # Show format-specific configuration
        if EXPORT_FORMAT.lower() == 'svg':
            print(f"📐 Vector format (scalable)")
            print(f"   - Non-scaling stroke: {SVG_USE_NON_SCALING_STROKE}")
            print(f"   - Copy pictures: {SVG_COPY_PICTURES}")
            print(f"\n⚠️  SVG export requires Visum GUI to be open and visible!")
            print(f"   If running headless, use PNG/JPG instead.")
        else:
            # Show paper format configuration for raster formats
            if PAPER_FORMAT != 'custom':
                print(f"📄 Paper format: {get_paper_info(PAPER_FORMAT, IMAGE_DPI)}")
            else:
                print(f"📐 Custom size: {IMAGE_WIDTH_PIXELS}px width @ {IMAGE_DPI} DPI")
        
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
                format=EXPORT_FORMAT
            )
            output_path = os.path.join(project_dir, output_filename)
            
            # Export based on format
            if EXPORT_FORMAT.lower() == 'svg':
                # Vector export
                result = export_gpa_to_svg(
                    gpa_path,
                    output_path,
                    use_non_scaling_stroke=SVG_USE_NON_SCALING_STROKE,
                    copy_pictures=SVG_COPY_PICTURES
                )
            else:
                # Raster export (PNG, JPG, BMP, TIF)
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
            print(f"   - {r['gpa_file']} → {r['output_file']}")
            if r.get('format') == 'svg':
                # SVG format
                print(f"     Vector format (scalable) = {r['size_kb']} KB")
            else:
                # Raster format
                dims = r.get('dimensions', {})
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
