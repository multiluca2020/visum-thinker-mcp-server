"""
Export Visum Graphic Parameters (.gpa) to PDF Files

This script loads a .gpa file (graphic parameters) and prints the network view to PDF.
Uses Windows "Microsoft Print to PDF" printer or any other installed PDF printer.

Usage:
    1. Open your Visum project
    2. Run this script in VisumPy console or via project_execute
    3. Script will find all .gpa files in project directory
    4. Prints each .gpa as a PDF file

Configuration:
    - Paper format: A5, A4, A3, etc.
    - Orientation: Portrait (0) or Landscape (1)
    - Printer: Default is 'Microsoft Print to PDF'
"""

import os
import sys

print("\n" + "=" * 70)
print("📄 VISUM GPA TO PDF EXPORT - STARTING")
print("=" * 70)

# =============================================================================
# CONFIGURATION
# =============================================================================

# PDF export settings
PAPER_FORMAT = 'A4'         # A5, A4, A3, Letter, Legal, etc.
ORIENTATION = 1             # 0 = Portrait, 1 = Landscape, 2 = Automatic
PDF_PRINTER = 'Microsoft Print to PDF'  # Windows printer name

# Output filename pattern
OUTPUT_PATTERN = "{project_name}_{gpa_name}.pdf"

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

def export_gpa_to_pdf(gpa_file_path, output_pdf_path, paper_format='A4', orientation=1, printer_name='Microsoft Print to PDF'):
    """
    Export a .gpa file to PDF using Visum's print functionality.
    
    Args:
        gpa_file_path: Full path to .gpa file
        output_pdf_path: Full path to output PDF file
        paper_format: Paper size (A4, A5, A3, Letter, etc.)
        orientation: 0=Portrait, 1=Landscape, 2=Automatic
        printer_name: Windows printer name
    
    Returns:
        dict: Result with success status and file info
    """
    result = {
        'gpa_file': os.path.basename(gpa_file_path),
        'output_file': os.path.basename(output_pdf_path),
        'success': False
    }
    
    try:
        # Load GPA (Graphic Parameters)
        print(f"📂 Loading GPA: {os.path.basename(gpa_file_path)}")
        visum.Net.GraphicParameters.Open(gpa_file_path)
        result['gpa_loaded'] = True
        
        # Configure print settings
        print(f"📄 Paper format: {paper_format}")
        print(f"📐 Orientation: {'Portrait' if orientation == 0 else 'Landscape' if orientation == 1 else 'Automatic'}")
        print(f"🖨️  Printer: {printer_name}")
        
        result['paper_format'] = paper_format
        result['orientation'] = 'Portrait' if orientation == 0 else 'Landscape' if orientation == 1 else 'Automatic'
        result['printer'] = printer_name
        
        # Set the output file as the print-to-file target
        # Note: This requires the printer to support file output
        # For "Microsoft Print to PDF", we need to use the print dialog or COM automation
        
        print(f"🎨 Printing to PDF...")
        
        # Print the network editor
        visum.Graphic.PrintNetEditor2D(
            NameOfPrintJob=os.path.basename(output_pdf_path),
            PrinterName=printer_name,
            PaperSize=paper_format,
            Orientation=orientation
        )
        
        # Note: The PDF will be saved to the default location for the printer
        # which is typically the user's Documents folder or a printer-specific location
        # We need to move it to our desired location
        
        # Wait a moment for the file to be created
        import time
        time.sleep(2)
        
        # Check if file was created in expected location
        # For "Microsoft Print to PDF", the user typically needs to specify the location
        # through the print dialog, which doesn't work well in automation
        
        result['note'] = 'PDF printed via Windows printer. Check printer output location.'
        result['success'] = True
        
        print(f"✅ Print job sent successfully")
        print(f"⚠️  Note: Check the printer's output location for the PDF file")
        print(f"   Typical location: Documents folder or printer-specific directory")
        
    except Exception as e:
        result['error'] = str(e)
        print(f"❌ Error: {e}")
    
    return result


def main():
    """Main function to export all .gpa files in project directory."""
    
    print("=" * 70)
    print("📄 GPA to PDF Export Tool")
    print("=" * 70)
    
    try:
        # Get project info
        project_path = visum.GetPath(1)
        project_dir = os.path.dirname(project_path)
        project_name = os.path.splitext(os.path.basename(project_path))[0]
        
        print(f"\n📂 Project: {project_name}")
        print(f"📁 Directory: {project_dir}")
        print(f"\n📄 Paper format: {PAPER_FORMAT}")
        print(f"📐 Orientation: {'Portrait' if ORIENTATION == 0 else 'Landscape' if ORIENTATION == 1 else 'Automatic'}")
        print(f"🖨️  Printer: {PDF_PRINTER}")
        
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
                gpa_name=gpa_name
            )
            output_path = os.path.join(project_dir, output_filename)
            
            # Export with paper format
            result = export_gpa_to_pdf(
                gpa_path,
                output_path,
                paper_format=PAPER_FORMAT,
                orientation=ORIENTATION,
                printer_name=PDF_PRINTER
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
            print(f"   - {r['gpa_file']} → Print job sent to {r.get('printer')}")
            if r.get('note'):
                print(f"     Note: {r['note']}")
        
        if failed:
            print(f"\n❌ Failed exports: {len(failed)}")
            for r in failed:
                print(f"   - {r['gpa_file']}: {r.get('error', 'Unknown error')}")
        
        print(f"\n📁 Output directory: Check printer output location")
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
