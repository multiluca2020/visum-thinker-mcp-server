# 🗺️ Graphic Layout Export Workflow

Complete guide for exporting Visum graphic layouts (.gpa files) as PNG images.

## Overview

Export network visualization from Global Graphic Parameters files (.gpa) to high-resolution PNG images. The workflow automatically extracts network bounds from the layout's PrintArea settings.

## Tools Available

### 1. `project_export_graphic_layout`

Export a graphic layout as PNG image with customizable resolution.

**Parameters:**
- `projectId` (required): Project identifier from `project_open`
- `gpaFile` (required): Filename or full path to .gpa file
- `outputFile` (optional): Custom output filename (default: `{gpaName}_export.png`)
- `paperFormat` (optional): Paper format - A5, A5_portrait, A4, A4_portrait, A3, A3_portrait, custom (default)
- `width` (optional): Image width in pixels (default: 1920, ignored if paperFormat specified)
- `dpi` (optional): Resolution in DPI (default: 150)
- `quality` (optional): JPEG quality 0-100 (default: 95, PNG ignores this)

**Example with paper format:**
```json
{
  "projectId": "S000009result_1278407893",
  "gpaFile": "Flussogramma_tpb.gpa",
  "paperFormat": "A4_portrait",
  "dpi": 150
}
```

**Example with custom size:**
```json
{
  "projectId": "S000009result_1278407893",
  "gpaFile": "Flussogramma_tpb.gpa",
  "paperFormat": "custom",
  "width": 2560,
  "dpi": 150
}
```

**Output:**
```
✅ Layout Grafico Esportato

🗺️ GPA caricato: Flussogramma_tpb.gpa
📍 Coordinate rete:
   - Left: 8.924330
   - Bottom: 45.308337
   - Right: 10.257651
   - Top: 46.525534

🖼️ Immagine generata:
   - File: Flussogramma_tpb_export.png
   - Percorso: H:\go\reports\Input\Flussogramma_tpb_export.png
   - 📄 Formato carta: A4_portrait (297×210mm)
   - Dimensioni: 1754 × 2142 px
   - Aspect ratio: 1.221
   - Risoluzione: 150 DPI
   - Dimensione file: 1684.36 KB (1.64 MB)

💡 L'immagine è ottimizzata per stampa su formato A4_portrait a 150 DPI
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
     
     Quale vuoi esportare? In che formato? (A4, A5, A3, landscape/portrait)"
User: "Il primo in A4 portrait per stampa"
AI: [calls project_export_graphic_layout with gpaFile="Flussogramma_tpb.gpa", paperFormat="A4_portrait", dpi=150]
     "✅ Immagine esportata: Flussogramma_tpb_export.png (1.64 MB)
      📄 Formato A4 portrait (297×210mm) ottimizzato per stampa a 150 DPI"
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
| Print A4 portrait | A4_portrait | 150 | 1754×1240 | ~1.5 MB | 25-30s |
| High quality A4 | A4 | 300 | 2480×3508 | ~5 MB | 60-90s |
| Poster A3 | A3 | 300 | 3508×4960 | ~15 MB | 3-5 min |

### Paper Format Details

| Format | Dimensions (mm) | Landscape (px @ 150 DPI) | Portrait (px @ 150 DPI) |
|--------|----------------|--------------------------|-------------------------|
| A5 | 148 × 210 | 874 × 1240 | 1240 × 874 |
| A4 | 210 × 297 | 1240 × 1754 | 1754 × 1240 |
| A3 | 297 × 420 | 1754 × 2480 | 2480 × 1754 |

**Note:** Height is automatically adjusted based on network aspect ratio. Listed dimensions are paper sizes only.

## File Format Support

Currently supports **PNG** format only. The `quality` parameter is ignored for PNG (PNG uses lossless compression).

Future support planned:
- SVG via `visum.Graphic.ExportSVG()`
- PDF via `visum.Net.PrintEditor2D()`

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

## Future Enhancements

- [ ] Support custom bounds (not just PrintArea)
- [ ] SVG export for vector graphics
- [ ] PDF export for documents
- [ ] Batch export all .gpa files
- [ ] Layer control (show/hide specific layers)
- [ ] Legend and scale bar options
- [ ] Transparent background support
