# Large PDF Processing Support

## Overview

The Visum Thinker MCP Server now includes enhanced support for processing large PDF files (50MB+), which was added to handle PDFs that are too large to load directly in Claude Desktop.

## New Features

### 1. Enhanced `load_pdf` Tool

The original `load_pdf` tool has been enhanced with:

- **Memory optimization** for large files (>50MB)
- **Intelligent content truncation** to prevent memory overload
- **File size reporting** and warnings
- **Processing status** and optimization details
- **Page limiting** support (`maxPages` parameter)

**Usage:**
```json
{
  "tool": "load_pdf",
  "arguments": {
    "filePath": "/absolute/path/to/large.pdf",
    "maxPages": 100,
    "chunkSize": 10
  }
}
```

### 2. New `process_large_pdf` Tool

Specifically designed for very large PDFs (>85MB):

- **Chunked processing** in smaller page groups
- **Memory-efficient streaming**
- **Summary mode** for content optimization
- **Progressive loading** with status updates
- **Error recovery** for problematic chunks

**Usage:**
```json
{
  "tool": "process_large_pdf",
  "arguments": {
    "filePath": "/absolute/path/to/very-large.pdf",
    "chunkSizePages": 10,
    "startPage": 1,
    "endPage": 50,
    "outputSummary": true
  }
}
```

### 3. Enhanced `analyze_pdf_section` Tool

Improved search and analysis capabilities:

- **Fuzzy matching** when exact matches aren't found
- **Configurable context windows**
- **Position-based results** for large documents
- **Case-sensitive search options**
- **Performance optimization** for large texts

**Usage:**
```json
{
  "tool": "analyze_pdf_section",
  "arguments": {
    "query": "machine learning algorithms",
    "contextWindow": 3000,
    "maxMatches": 15,
    "caseSensitive": false
  }
}
```

## Handling 85MB+ PDF Files

For very large PDFs that cannot be loaded in Claude Desktop:

### Method 1: Direct Processing
```json
{
  "tool": "process_large_pdf",
  "arguments": {
    "filePath": "/path/to/85MB-document.pdf",
    "chunkSizePages": 5,
    "outputSummary": true
  }
}
```

### Method 2: Selective Processing
```json
{
  "tool": "process_large_pdf",
  "arguments": {
    "filePath": "/path/to/85MB-document.pdf",
    "startPage": 1,
    "endPage": 25,
    "chunkSizePages": 5,
    "outputSummary": false
  }
}
```

### Method 3: Search-Focused Analysis
1. First, load with summary mode:
```json
{
  "tool": "process_large_pdf",
  "arguments": {
    "filePath": "/path/to/85MB-document.pdf",
    "outputSummary": true
  }
}
```

2. Then search for specific content:
```json
{
  "tool": "analyze_pdf_section",
  "arguments": {
    "query": "specific topic or keyword",
    "contextWindow": 2000,
    "maxMatches": 10
  }
}
```

## Memory Management

The server implements several strategies for large PDF processing:

1. **Dynamic imports** - PDF parsing library loaded on-demand
2. **Chunked processing** - Large files processed in smaller sections
3. **Content optimization** - Intelligent truncation while preserving context
4. **Memory monitoring** - File size warnings and recommendations
5. **Error handling** - Graceful degradation for problematic content

## Performance Tips

### For 50-85MB PDFs:
- Use `load_pdf` with `maxPages` limit
- Enable content optimization automatically

### For 85MB+ PDFs:
- Always use `process_large_pdf`
- Start with `chunkSizePages: 5-10`
- Use `outputSummary: true` initially
- Process specific page ranges as needed

### Memory Optimization:
- Close other applications when processing large PDFs
- Process during low system usage times
- Use smaller chunk sizes for very large files
- Consider processing overnight for massive documents

## Troubleshooting

### Error: "ENOENT: no such file or directory"
- Verify the absolute file path is correct
- Ensure the file exists and is accessible
- Check file permissions

### Error: "Insufficient system memory"
- Reduce `chunkSizePages` to 3-5
- Enable `outputSummary` mode
- Close other memory-intensive applications
- Consider processing smaller page ranges

### Error: "PDF parsing failed"
- Check if PDF is corrupted or password-protected
- Try processing with smaller chunks
- Verify PDF version compatibility

### Performance Issues:
- Use `outputSummary: true` for initial processing
- Limit page ranges with `startPage`/`endPage`
- Reduce `contextWindow` size in search
- Process during low system activity

## Technical Details

- **PDF Library**: pdf-parse with dynamic loading
- **Memory Management**: Intelligent content truncation
- **Chunk Processing**: Page-based segmentation
- **Error Recovery**: Graceful handling of problematic sections
- **Content Optimization**: Context-preserving summarization

The server is now capable of handling PDF files that would previously crash or be rejected due to size constraints, making it suitable for processing large academic papers, technical manuals, legal documents, and other substantial PDF content.
