# Legend Auto-Scaling Test Results

## Problem Statement

When exporting Visum .gpa (Graphic Parameters) files to images with different paper formats or DPI settings, the **legend text size remained fixed**. This caused:

- **Small formats (A5)**: Legend appeared too large, wasting space
- **Large formats (A3)**: Legend appeared too small, hard to read  
- **High DPI (600+)**: Legend appeared tiny compared to scaled network
- **Low DPI (96)**: Legend appeared oversized

## Solution Implemented

Automatic legend text scaling based on **paper format** and **DPI** settings!

### How It Works

1. **Reference Baseline**: A4 landscape @ 150 DPI (1240px width)
2. **Scale Factor**: `current_width_pixels / 1240`
3. **Scaled Elements**:
   - Title text
   - Element labels
   - Attribute text
   - Label text
   - Sub-element text
   - Graphic scale text

### Algorithm

```python
# Reference: A4 landscape @ 150 DPI = 1240px width
reference_width = 1240

# Calculate current dimensions
width_px = int((paper_width_mm / 25.4) * dpi)

# Calculate scale factor
scale_factor = width_px / reference_width

# Apply to all legend text elements
legend.TitleTextParameters.SetAttValue('TEXTSIZE', old_size * scale_factor)
legend.ElementTextParameters.SetAttValue('TEXTSIZE', old_size * scale_factor)
# ... and so on for all text elements
```

## Test Cases

### Test Configuration Matrix

| Format | DPI | Width (px) | Scale Factor | Label |
|--------|-----|------------|--------------|-------|
| A5 | 150 | 874 | 0.70× | small |
| A4 | 150 | 1240 | 1.00× | standard (baseline) |
| A4 | 300 | 2480 | 2.00× | high_quality |
| A5 | 600 | 3496 | 2.82× | professional |
| A4 | 600 | 4960 | 4.00× | ultra_high |

### Example Output

```
🔧 Scaling legend text by 0.70x (for A5 @ 150 DPI)...
   ✅ Legend scaled:
      • Title: 3.50 → 2.45mm
      • Elements: 2.50 → 1.75mm
      • Attributes: 2.00 → 1.40mm
      • Labels: 2.00 → 1.40mm
```

```
🔧 Scaling legend text by 4.00x (for A4 @ 600 DPI)...
   ✅ Legend scaled:
      • Title: 3.50 → 14.00mm
      • Elements: 2.50 → 10.00mm
      • Attributes: 2.00 → 8.00mm
      • Labels: 2.00 → 8.00mm
```

## Running the Test

### Prerequisites

1. Visum 2025 64-bit installed
2. Active Visum project with .gpa files
3. Python with `win32com` package

### Execute Test

```bash
# Edit test configuration
# Set PROJECT_PATH and GPA_FILE in test-legend-scaling.py

# Run test
python test-legend-scaling.py
```

### Test Output

The script will:
1. Load your Visum project
2. Export the same .gpa file with 4 different configurations
3. Scale legend text appropriately for each
4. Save results to `test-exports/` directory

Expected output files:
- `test_legend_A5_150dpi_small.png`
- `test_legend_A4_150dpi_standard.png`
- `test_legend_A4_300dpi_high_quality.png`
- `test_legend_A5_600dpi_professional.png`

## Visual Comparison

Compare the exported images side-by-side to see:

✅ **Legend proportional to paper size**
✅ **Text readable at all DPI levels**
✅ **Consistent visual weight across formats**

## Integration

This feature is automatically enabled in:

- ✅ **Standalone script**: `export-gpa-to-image.py`
- ⏳ **MCP tool**: `project_export_graphic_layout` (to be updated)

### Usage in Script

```python
# Automatic when using paper formats
python export-gpa-to-image.py

# Configure in script:
PAPER_FORMAT = 'A5'  # or A4, A3, A5_portrait, etc.
IMAGE_DPI = 600      # Higher DPI = larger legend text
```

Scale factor is calculated automatically based on your settings!

## Technical Details

### API Used

```python
# Visum COM API
visum.Net.GraphicParameters.LegendParameters
visum.Net.GraphicParameters.LegendParameters.LegendGeneralParameters
visum.Net.GraphicParameters.LegendParameters.LegendGeneralParameters.TitleTextParameters
# ... and other text parameter objects

# Attributes
TextParameters.AttValue('TEXTSIZE')  # Get current size (mm)
TextParameters.SetAttValue('TEXTSIZE', new_size)  # Set new size
```

### Limitations

- **Only works with .gpa files that have legends**
- **TextSize is in millimeters** (not pixels or points)
- **No scaling for symbol sizes** (only text)
- **Legend position not adjusted** (only text size)

## Future Enhancements

Potential improvements:

- [ ] Scale legend symbol sizes
- [ ] Adjust legend position based on format
- [ ] Scale line widths in legend
- [ ] Auto-adjust legend column count
- [ ] Support for multiple legends

## Troubleshooting

### "LegendParameters not available"

Your .gpa file doesn't include a legend. This is normal for some graphic configurations.

### "Legend scaling skipped"

The GPA has a legend but it's not accessible via API. The export will still work, just without legend scaling.

### Text appears wrong after export

Check that:
1. Original .gpa has correct text sizes
2. Scale factor is reasonable (0.5× to 4.0×)
3. DPI and paper format are set correctly

## Credits

Developed: October 30, 2025
Feature: Automatic legend text scaling for Visum GPA exports
Status: ✅ Implemented and tested
