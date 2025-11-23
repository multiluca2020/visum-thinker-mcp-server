# 🗺️ Graphic Layout Export Workflow

Complete guide for exporting Visum graphic layouts (.gpa files) as PNG images.

## Overview

Export network visualization from Global Graphic Parameters files (.gpa) to high-resolution PNG images. The workflow automatically extracts network bounds from the layout's PrintArea settings.

## Tools Available

### 1. `project_export_graphic_layout`

Export a graphic layout as PNG (raster) or SVG (vector) with customizable resolution.

**Parameters:**
- `projectId` (required): Project identifier from `project_open`
- `gpaFile` (required): Filename or full path to .gpa file
- `outputFile` (optional): Custom output filename (default: `{gpaName}_export.png` or `.svg`)
- `format` (optional): Export format - png (default), jpg, svg
- `paperFormat` (optional): Paper format - A5, A5_portrait, A4, A4_portrait, A3, A3_portrait, custom (default). Only for raster formats.
- `width` (optional): Image width in pixels (default: 1920, raster only, ignored if paperFormat specified)
- `dpi` (optional): Resolution in DPI (default: 150, raster only)
- `quality` (optional): JPEG quality 0-100 (default: 95, only for .jpg)
- `svgNonScalingStroke` (optional): Keep line widths constant when scaling (default: true, SVG only)

**Example with paper format (PNG):**
```json
{
  "projectId": "S000009result_1278407893",
  "gpaFile": "Flussogramma_tpb.gpa",
  "format": "png",
  "paperFormat": "A4_portrait",
  "dpi": 150
}
```

**Example with custom size (PNG):**
```json
{
  "projectId": "S000009result_1278407893",
  "gpaFile": "Flussogramma_tpb.gpa",
  "format": "png",
  "paperFormat": "custom",
  "width": 2560,
  "dpi": 150
}
```

**Example with SVG (vector):**
```json
{
  "projectId": "S000009result_1278407893",
  "gpaFile": "Flussogramma_tpb.gpa",
  "format": "svg",
  "svgNonScalingStroke": true
}
```

**Output (PNG):**
```
✅ Layout Grafico Esportato

🗺️ GPA caricato: Flussogramma_tpb.gpa
📍 Coordinate rete:
   - Left: 8.924330
   - Bottom: 45.308337
   - Right: 10.257651
   - Top: 46.525534

🖼️ Immagine raster generata:
   - File: Flussogramma_tpb_export.png
   - Percorso: H:\go\reports\Input\Flussogramma_tpb_export.png
   - Formato: PNG (raster)
   - 📄 Formato carta: A4_portrait (297×210mm)
   - Dimensioni: 1754 × 2142 px
   - Aspect ratio: 1.221
   - Risoluzione: 150 DPI
   - Dimensione file: 1684.36 KB (1.64 MB)

💡 L'immagine è ottimizzata per stampa su formato A4_portrait a 150 DPI
```

**Output (SVG):**
```
✅ Layout Grafico Esportato

🗺️ GPA caricato: Flussogramma_tpb.gpa
📍 Coordinate rete:
   - Left: 8.924330
   - Bottom: 45.308337
   - Right: 10.257651
   - Top: 46.525534

🎨 Immagine vettoriale generata:
   - File: Flussogramma_tpb_export.svg
   - Percorso: H:\go\reports\Input\Flussogramma_tpb_export.svg
   - Formato: SVG (vettoriale, scalabile)
   - Aspect ratio: 1.221
   - Dimensione file: 324.18 KB (0.32 MB)

✨ Vantaggi SVG:
   - Scalabile senza perdita di qualità
   - Modificabile in Illustrator/Inkscape
   - Convertibile in PDF con strumenti esterni
   - File più piccolo rispetto a PNG ad alta risoluzione
```

## Interactive Workflow

**Recommended pattern for AI assistants:**

1. **List Available GPA Files** (if needed)
   - Check project directory for .gpa files
   - Show user available layouts with sizes

2. **User Selects Layout**
   - Ask which graphic layout to export
   - Suggest default resolution based on use case

3. **Export Image**
   - Call `project_export_graphic_layout` with user's choices
   - Confirm success and show file location

**Example conversation:**
```
User: "Esporta il layout grafico della rete"
AI: "Trovati 4 file .gpa:
     1. Flussogramma_tpb.gpa
     2. Flussogramma_tpb_zoom.gpa
     3. Flussogramma_tpr.gpa
     4. Flussogramma_tpr_zoom.gpa
     
     Quale vuoi esportare? In che formato? 
     - PNG/JPG: per stampa, immagini raster (A4, A5, A3, landscape/portrait)
     - SVG: vettoriale, scalabile, modificabile"
     
User: "Il primo in A4 portrait per stampa"
AI: [calls project_export_graphic_layout with format="png", gpaFile="Flussogramma_tpb.gpa", paperFormat="A4_portrait", dpi=150]
     "✅ Immagine esportata: Flussogramma_tpb_export.png (1.64 MB)
      📄 Formato A4 portrait (297×210mm) ottimizzato per stampa a 150 DPI"

User: "Esporta anche in SVG per modificarlo"
AI: [calls project_export_graphic_layout with format="svg", gpaFile="Flussogramma_tpb.gpa"]
     "✅ Immagine vettoriale esportata: Flussogramma_tpb_export.svg (324 KB)
      ✨ Scalabile senza perdita di qualità, modificabile in Illustrator/Inkscape"
```

## Technical Details

### Visum API Methods

```python
# 1. Load GPA file
visum.Net.GraphicParameters.Open(gpa_file_path)

# 2. Get network bounds from PrintArea
printArea = visum.Net.PrintParameters.PrintArea
left = printArea.AttValue('LEFTMARGIN')
bottom = printArea.AttValue('BOTTOMMARGIN')
right = printArea.AttValue('RIGHTMARGIN')
top = printArea.AttValue('TOPMARGIN')

# 3. Export image
visum.Graphic.ExportNetworkImageFile(
    output_file,
    left,      # xmin - network coordinates
    bottom,    # ymin - network coordinates
    right,     # xmax - network coordinates
    top,       # ymax - network coordinates
    width,     # image width in pixels
    dpi,       # resolution (default: 96)
    quality    # JPEG quality 0-100 (PNG ignores this)
)
```

### Coordinate System

**CRITICAL:** The bounds (xmin, ymin, xmax, ymax) are in **network coordinates** (geographic WGS84 or projected), NOT pixel coordinates.

- Left/Right: Longitude or X coordinate
- Bottom/Top: Latitude or Y coordinate
- Example: left=8.924, bottom=45.308, right=10.257, top=46.525 (Italian region)

### Image Dimensions

- **Width**: Specified explicitly in pixels
- **Height**: Auto-calculated from aspect ratio
  ```
  aspect_ratio = (top - bottom) / (right - left)
  height = width * aspect_ratio
  ```

### Resolution Guidelines

| Use Case | Paper Format | DPI | Pixel Size | File Size | Export Time |
|----------|--------------|-----|------------|-----------|-------------|
| Screen preview | custom (1280px) | 96 | 1280×1562 | ~800 KB | 15-20s |
| Print A5 | A5 | 150 | 874×1240 | ~600 KB | 18-22s |
| Print A4 | A4 | 150 | 1240×1754 | ~1.5 MB | 25-30s |
| High quality A5 | A5 | 300 | 1748×2480 | ~3 MB | 45-60s |
| High quality A4 | A4 | 300 | 2480×3508 | ~5 MB | 60-90s |
| Professional A5 | A5 | 600 | 3496×4960 | ~12 MB | 2-4 min |
| Professional A4 | A4 | 600 | 4960×7016 | ~20 MB | 4-8 min |
| Maximum detail A5 | A5 | 1200 | 6992×9921 | ~45 MB | 8-15 min |
| Maximum detail A4 | A4 | 1200 | 9921×14031 | ~90 MB | 15-25 min |
| Poster A3 | A3 | 300 | 3508×4960 | ~15 MB | 3-5 min |

### Paper Format Details - All DPI Options

| Format | Dimensions (mm) | 96 DPI | 150 DPI | 300 DPI | 600 DPI | 1200 DPI |
|--------|-----------------|--------|---------|---------|---------|----------|
| A5 landscape | 148 × 210 | 559×827 | 874×1240 | 1748×2480 | 3496×4960 | 6992×9921 |
| A5 portrait | 210 × 148 | 827×559 | 1240×874 | 2480×1748 | 4960×3496 | 9921×6992 |
| A4 landscape | 210 × 297 | 791×1119 | 1240×1754 | 2480×3508 | 4960×7016 | 9921×14031 |
| A4 portrait | 297 × 210 | 1119×791 | 1754×1240 | 3508×2480 | 7016×4960 | 14031×9921 |
| A3 landscape | 297 × 420 | 1119×1583 | 1754×2480 | 3508×4960 | 7016×9921 | 14031×19843 |
| A3 portrait | 420 × 297 | 1583×1119 | 2480×1754 | 4960×3508 | 9921×7016 | 19843×14031 |

**Note:** Height is automatically adjusted based on network aspect ratio. Listed dimensions are paper sizes only.

### DPI Selection Guide

**96 DPI (Screen/Web):**
- Use: Website, email, screen presentations
- Quality: Basic, visible pixels when zoomed
- File size: Small (~500 KB - 2 MB)

**150 DPI (Standard Print):**
- Use: Office documents, standard printing
- Quality: Good for most print needs
- File size: Medium (~1-5 MB)

**300 DPI (High Quality Print):**
- Use: Professional brochures, publications
- Quality: Excellent, recommended minimum for print
- File size: Large (~3-15 MB)

**600 DPI (Professional/Large Format):**
- Use: Large posters, trade show graphics, detailed technical drawings
- Quality: Ultra-high, suitable for close inspection
- File size: Very large (~12-45 MB)

**1200 DPI (Maximum Detail):**
- Use: Photo-quality reproduction, archival prints, extreme enlargements
- Quality: Maximum possible detail
- File size: Extremely large (~45-150 MB)
- Warning: Very long export times (10-25 minutes)

## File Format Support

### Supported Formats

**Raster Formats (pixel-based):**
- **PNG**: Lossless, high quality, larger file size (~1-5 MB)
- **JPG**: Lossy compression, smaller file size, use `quality` parameter (0-100)

**Vector Format (scalable):**
- **SVG**: Scalable Vector Graphics, resolution-independent, editable
  - File size: ~200-500 KB (much smaller than high-res PNG)
  - Advantages: Scalable, editable in Illustrator/Inkscape, convertible to PDF
  - Limitation: Requires Visum GUI to be visible (not headless)

### Format Comparison

| Feature | PNG/JPG | SVG |
|---------|---------|-----|
| Quality | DPI-dependent | Resolution-independent |
| File Size | Large (1-5 MB) | Small (200-500 KB) |
| Scalability | Pixelated when scaled | Perfect at any scale |
| Editing | Not editable | Editable (vector paths) |
| Headless support | ✅ Yes | ❌ No (requires GUI) |
| Print ready | ✅ Yes (300 DPI) | ✅ Yes (infinite resolution) |
| PDF conversion | Insert as image | Direct conversion available |

### Future Support

- **PDF direct export**: Limited by Visum API (requires manual dialog interaction)
  - Workaround: Use PNG @ 300 DPI or convert SVG to PDF with external tools

## Troubleshooting

### Error: "GPA file not found"

**Cause:** File path incorrect or .gpa not in project directory

**Solution:**
- Use `project_list_available_layouts` to see available files
- Provide full path if file is outside project directory
- Check file extension is exactly `.gpa`

### Error: "Parameter not optional"

**Cause:** Missing network bounds (internal error)

**Solution:**
- Ensure GPA file loaded successfully
- Verify PrintArea parameters are set in .gpa file
- Try loading GPA manually in Visum GUI to check validity

### Export timeout (>5 minutes)

**Cause:** Image resolution too high or network very complex

**Solution:**
- Reduce width parameter (try 1920 or 1280)
- Lower DPI setting (try 96 or 72)
- Check if GPA contains excessive graphic elements

### Image appears cropped or empty

**Cause:** PrintArea bounds don't match actual network extent

**Solution:**
- Open .gpa in Visum GUI and verify PrintArea settings
- Use "Fit to Network" in Print Parameters
- Save .gpa and re-export

## Performance Notes

**Typical export times (Campoleone project: 166K nodes, 409K links):**
- 1920×2344 px @ 150 DPI: ~27 seconds
- 1280×1562 px @ 96 DPI: ~18 seconds
- 3840×4688 px @ 300 DPI: ~75 seconds

**Factors affecting speed:**
- Image resolution (width × height)
- Network complexity (node/link count)
- Graphic elements (labels, symbols, colors)
- System resources (CPU, RAM)

## Related Documentation

- `GLOBAL_LAYOUTS_WORKFLOW.md` - Loading .lay layout files
- `TABLE_EXPORT_WORKFLOW.md` - Exporting visible tables from layouts
- `visum-com-docs/VISUMLIB~IGraphic~ExportNetworkImageFile.html` - API reference

## Standalone Script

For direct Python usage without MCP:

**File:** `export-gpa-to-image.py`

```python
# Usage
python export-gpa-to-image.py

# Exports network_export.png using first .gpa file found
```

## PDF Export Limitation

**Why no direct PDF export?**

Visum's `PrintNetEditor2D()` method can print to PDF, but it requires:
- Windows print dialog interaction (manual file save location selection)
- No programmatic way to specify output file path
- Not suitable for automation

**Workarounds:**

1. **High-resolution PNG** (Current implementation):
   ```json
   {"paperFormat": "A4", "dpi": 300}
   ```
   - 300 DPI produces print-ready quality
   - A4 @ 300 DPI = 2480×3508 pixels
   - Can be inserted into PDF documents

2. **SVG Export** (Future):
   - Vector format (scalable without quality loss)
   - Use `visum.Graphic.ExportSVG()` 
   - Convert SVG→PDF with external tools (Inkscape, CairoSVG)

3. **Print automation** (Complex):
   - Use PyAutoGUI or AutoIt to automate print dialog
   - Requires screen coordinates, fragile
   - Not recommended for production

**Recommended approach:** Use PNG @ 300 DPI for printing, which provides excellent quality and is the most reliable solution.

## Future Enhancements

- [ ] Support custom bounds (not just PrintArea)
- [ ] SVG export for vector graphics
- [ ] Batch export all .gpa files
- [ ] Layer control (show/hide specific layers)
- [ ] Legend and scale bar options
- [ ] Transparent background support
