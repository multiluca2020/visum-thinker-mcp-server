#!/usr/bin/env node

/**
 * Direct PDF Processing Script
 * Processes large PDF files using the visum-thinker PDF processing capabilities
 */

import fs from 'fs';
import path from 'path';
import fsExtra from 'fs-extra';

// Dynamic import for pdf-parse to avoid startup issues
let pdfParse = null;

async function initializePdfParser() {
  try {
    if (!pdfParse) {
      // Try different import approaches
      try {
        const pdfParseModule = await import("pdf-parse");
        pdfParse = pdfParseModule.default;
      } catch (importError) {
        console.error("Primary import failed:", importError.message);
        
        // Try alternative import
        try {
          pdfParse = (await import("pdf-parse/lib/pdf-parse.js")).default;
        } catch (altError) {
          console.error("Alternative import failed:", altError.message);
          
          // Try require fallback (CommonJS style)
          try {
            const { createRequire } = await import('module');
            const require = createRequire(import.meta.url);
            pdfParse = require('pdf-parse');
          } catch (requireError) {
            console.error("Require fallback failed:", requireError.message);
            return null;
          }
        }
      }
    }
    
    // Test the parser with a minimal operation
    if (pdfParse && typeof pdfParse === 'function') {
      return pdfParse;
    } else {
      console.error("PDF parser is not a function:", typeof pdfParse);
      return null;
    }
  } catch (error) {
    console.error("Warning: PDF parsing unavailable:", error.message);
    return null;
  }
}

async function processLargePDF(filePath, options = {}) {
  const {
    chunkSizePages = 20,
    startPage = 1,
    endPage = null,
    outputSummary = true,
    outputFile = null
  } = options;

  try {
    console.log(`🔍 Processing PDF: ${filePath}`);
    
    // Check if file exists
    if (!fs.existsSync(filePath)) {
      throw new Error(`PDF file not found at path: ${filePath}`);
    }

    // Check file size
    const stats = fs.statSync(filePath);
    const fileSizeMB = stats.size / (1024 * 1024);
    console.log(`📄 File size: ${fileSizeMB.toFixed(2)} MB`);

    if (!filePath.toLowerCase().endsWith('.pdf')) {
      throw new Error('File must be a PDF');
    }

    // Initialize PDF parser
    const parser = await initializePdfParser();
    if (!parser) {
      throw new Error('PDF parsing library could not be loaded');
    }

    // Read PDF
    console.log('📖 Reading PDF file...');
    const pdfBuffer = fs.readFileSync(filePath);
    
    // Get metadata
    console.log('🔍 Extracting PDF metadata...');
    const pdfInfo = await parser(pdfBuffer, { 
      max: 1,
      version: 'v1.10.100' 
    });

    const totalPages = pdfInfo.numpages;
    const actualEndPage = endPage || totalPages;
    const pagesToProcess = actualEndPage - startPage + 1;
    const chunks = Math.ceil(pagesToProcess / chunkSizePages);

    console.log(`📊 Total pages: ${totalPages}`);
    console.log(`📈 Processing: pages ${startPage}-${actualEndPage} (${pagesToProcess} pages)`);
    console.log(`⚡ Chunks: ${chunks} chunks of ${chunkSizePages} pages each`);

    let processedContent = '';
    let processedPages = 0;
    let totalCharacters = 0;

    // Process in chunks
    for (let chunkIndex = 0; chunkIndex < chunks; chunkIndex++) {
      const chunkStart = startPage + (chunkIndex * chunkSizePages);
      const chunkEnd = Math.min(chunkStart + chunkSizePages - 1, actualEndPage);
      
      console.log(`🔄 Processing chunk ${chunkIndex + 1}/${chunks}: pages ${chunkStart}-${chunkEnd}`);

      try {
        // Process this chunk
        const chunkData = await parser(pdfBuffer, {
          max: chunkEnd,
          version: 'v1.10.100'
        });

        let chunkContent = chunkData.text;
        
        // For summary mode, truncate very long chunks
        if (outputSummary && chunkContent.length > 10000) {
          const chunkSummary = chunkContent.substring(0, 3000) + 
                             "\n\n[...content abbreviated for summary...]\n\n" +
                             chunkContent.substring(Math.max(0, chunkContent.length - 1000));
          processedContent += `\n\n=== CHUNK ${chunkIndex + 1} (Pages ${chunkStart}-${chunkEnd}) ===\n\n${chunkSummary}`;
          totalCharacters += chunkContent.length;
        } else {
          processedContent += `\n\n=== CHUNK ${chunkIndex + 1} (Pages ${chunkStart}-${chunkEnd}) ===\n\n${chunkContent}`;
          totalCharacters += chunkContent.length;
        }

        processedPages += (chunkEnd - chunkStart + 1);

        // Progress update
        const progress = ((chunkIndex + 1) / chunks * 100).toFixed(1);
        console.log(`✅ Chunk ${chunkIndex + 1} completed (${progress}% done)`);

        // Small delay to prevent memory issues
        if (chunkIndex < chunks - 1) {
          await new Promise(resolve => setTimeout(resolve, 100));
        }

      } catch (chunkError) {
        console.error(`❌ Error processing chunk ${chunkIndex + 1}:`, chunkError.message);
        processedContent += `\n\n=== CHUNK ${chunkIndex + 1} ERROR ===\n\nFailed to process pages ${chunkStart}-${chunkEnd}: ${chunkError.message}\n\n`;
      }
    }

    // Create results
    const results = {
      filename: path.basename(filePath),
      fileSizeMB: fileSizeMB,
      totalPages: totalPages,
      processedPages: `${startPage}-${actualEndPage}`,
      chunksUsed: chunks,
      chunkSize: chunkSizePages,
      summaryMode: outputSummary,
      originalCharacters: totalCharacters,
      processedCharacters: processedContent.length,
      processedAt: new Date(),
      content: processedContent
    };

    // Save to file if requested
    if (outputFile) {
      console.log(`💾 Saving results to: ${outputFile}`);
      await fsExtra.writeJson(outputFile, results, { spaces: 2 });
    }

    // Display summary
    console.log('\n🎉 PDF Processing Complete!');
    console.log('================================');
    console.log(`📄 File: ${results.filename}`);
    console.log(`📊 Size: ${results.fileSizeMB.toFixed(2)} MB`);
    console.log(`📖 Pages: ${results.totalPages} (processed ${results.processedPages})`);
    console.log(`⚡ Chunks: ${results.chunksUsed}`);
    console.log(`📝 Original: ${results.originalCharacters.toLocaleString()} chars`);
    console.log(`✨ Processed: ${results.processedCharacters.toLocaleString()} chars`);
    console.log(`🎯 Mode: ${results.summaryMode ? 'Summary (optimized)' : 'Full content'}`);
    
    // Show preview
    const preview = processedContent.substring(0, 500);
    console.log('\n📖 Content Preview:');
    console.log('==================');
    console.log(preview + (processedContent.length > 500 ? '...' : ''));

    return results;

  } catch (error) {
    console.error('❌ Error processing PDF:', error.message);
    throw error;
  }
}

async function processMultiplePDFs(filePaths, options = {}) {
  const { merge = false, outputFile = null, ...processOptions } = options;

  console.log(`🚀 Processing ${filePaths.length} PDF files...`);
  console.log(`📋 Mode: ${merge ? 'Merged knowledge base' : 'Separate processing'}`);

  if (merge) {
    // Merge all files into one comprehensive knowledge base
    let mergedContent = '';
    const mergedResults = {
      files: [],
      totalPages: 0,
      totalSizeMB: 0,
      processedAt: new Date(),
      mergingStrategy: 'sequential',
      content: ''
    };

    for (let i = 0; i < filePaths.length; i++) {
      const filePath = filePaths[i];
      
      console.log(`\n📖 Processing file ${i + 1}/${filePaths.length}: ${path.basename(filePath)}`);
      
      try {
        // Check if file exists
        if (!fs.existsSync(filePath)) {
          console.error(`⚠️  Skipping missing file: ${filePath}`);
          continue;
        }

        const result = await processLargePDF(filePath, { 
          ...processOptions, 
          outputFile: null // Don't save individual files when merging
        });

        // Add to merged knowledge
        mergedContent += `\n\n=== DOCUMENT ${i + 1}: ${result.filename} ===\n`;
        mergedContent += `File Size: ${result.fileSizeMB.toFixed(2)} MB | Pages: ${result.totalPages} | Mode: ${result.summaryMode ? 'Summary' : 'Full'}\n`;
        mergedContent += `Processed: ${result.processedAt}\n\n`;
        mergedContent += result.content;

        // Track merged stats
        mergedResults.files.push({
          filename: result.filename,
          pages: result.totalPages,
          sizeMB: result.fileSizeMB,
          originalChars: result.originalCharacters,
          processedChars: result.processedCharacters
        });

        mergedResults.totalPages += result.totalPages;
        mergedResults.totalSizeMB += result.fileSizeMB;

        console.log(`✅ Added ${result.filename} to knowledge base`);

      } catch (fileError) {
        console.error(`❌ Failed to process ${filePath}:`, fileError.message);
        mergedContent += `\n\n=== DOCUMENT ${i + 1}: ERROR ===\n`;
        mergedContent += `File: ${path.basename(filePath)}\n`;
        mergedContent += `Error: ${fileError.message}\n\n`;
      }
    }

    mergedResults.content = mergedContent;
    mergedResults.totalCharacters = mergedContent.length;

    // Save merged results
    if (outputFile) {
      console.log(`\n💾 Saving merged knowledge base to: ${outputFile}`);
      await fsExtra.writeJson(outputFile, mergedResults, { spaces: 2 });
    }

    // Display merged summary
    console.log('\n🎉 Multiple PDF Processing Complete!');
    console.log('=====================================');
    console.log(`📚 Files processed: ${mergedResults.files.length}`);
    console.log(`📄 Total pages: ${mergedResults.totalPages.toLocaleString()}`);
    console.log(`📊 Total size: ${mergedResults.totalSizeMB.toFixed(2)} MB`);
    console.log(`📝 Total content: ${mergedResults.totalCharacters.toLocaleString()} chars`);
    console.log(`🎯 Knowledge base: ${outputFile || 'In-memory only'}`);
    
    console.log('\n📚 Included Documents:');
    mergedResults.files.forEach((file, index) => {
      console.log(`  ${index + 1}. ${file.filename} (${file.pages} pages, ${file.sizeMB.toFixed(1)}MB)`);
    });

    return mergedResults;

  } else {
    // Process files separately
    const results = [];
    
    for (let i = 0; i < filePaths.length; i++) {
      const filePath = filePaths[i];
      
      console.log(`\n📖 Processing file ${i + 1}/${filePaths.length}: ${path.basename(filePath)}`);
      
      try {
        if (!fs.existsSync(filePath)) {
          console.error(`⚠️  Skipping missing file: ${filePath}`);
          continue;
        }

        const separateOutputFile = outputFile ? 
          `${path.parse(outputFile).name}_${i + 1}_${path.parse(filePath).name}.json` : 
          null;

        const result = await processLargePDF(filePath, {
          ...processOptions,
          outputFile: separateOutputFile
        });

        results.push(result);
        console.log(`✅ Completed ${result.filename}`);

      } catch (fileError) {
        console.error(`❌ Failed to process ${filePath}:`, fileError.message);
        results.push({ 
          filename: path.basename(filePath), 
          error: fileError.message 
        });
      }
    }

    console.log('\n🎉 Batch Processing Complete!');
    console.log('==============================');
    console.log(`📚 Files attempted: ${filePaths.length}`);
    console.log(`✅ Files successful: ${results.filter(r => !r.error).length}`);
    console.log(`❌ Files failed: ${results.filter(r => r.error).length}`);

    return results;
  }
}

// CLI Usage
async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.log(`
🎯 Visum Thinker PDF Processor

Usage: node process-pdf.js <pdf-file(s)> [options]

Single File:
  node process-pdf.js document.pdf

Multiple Files:
  node process-pdf.js file1.pdf file2.pdf file3.pdf
  node process-pdf.js *.pdf
  node process-pdf.js ~/Documents/*.pdf

Options:
  --chunks=N          Number of pages per chunk (default: 20)
  --start=N           Starting page (default: 1)  
  --end=N             Ending page (default: all)
  --full              Full content mode (default: summary)
  --output=file.json  Save results to JSON file
  --merge             Merge all files into single knowledge base
  --separate          Process files separately (default)

Examples:
  node process-pdf.js document.pdf
  node process-pdf.js *.pdf --merge --output=combined-knowledge.json
  node process-pdf.js file1.pdf file2.pdf --separate --chunks=10
  node process-pdf.js ~/Documents/*.pdf --merge --full
`);
    return;
  }

  // Separate file paths from options
  const filePaths = [];
  const options = {};
  let merge = false;

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg.startsWith('--chunks=')) {
      options.chunkSizePages = parseInt(arg.split('=')[1]);
    } else if (arg.startsWith('--start=')) {
      options.startPage = parseInt(arg.split('=')[1]);
    } else if (arg.startsWith('--end=')) {
      options.endPage = parseInt(arg.split('=')[1]);
    } else if (arg.startsWith('--output=')) {
      options.outputFile = arg.split('=')[1];
    } else if (arg === '--full') {
      options.outputSummary = false;
    } else if (arg === '--merge') {
      merge = true;
    } else if (arg === '--separate') {
      merge = false;
    } else if (!arg.startsWith('--')) {
      // This is a file path
      filePaths.push(arg);
    }
  }

  if (filePaths.length === 0) {
    console.error('❌ No PDF files specified');
    process.exit(1);
  }

  try {
    if (filePaths.length === 1) {
      // Single file processing
      await processLargePDF(filePaths[0], options);
    } else if (merge) {
      // Merge multiple files into one knowledge base
      await processMultiplePDFs(filePaths, { ...options, merge: true });
    } else {
      // Process files separately
      await processMultiplePDFs(filePaths, { ...options, merge: false });
    }
  } catch (error) {
    console.error('❌ Processing failed:', error.message);
    console.error('Full error:', error);
    process.exit(1);
  }
}

// Fix for ES module main detection
const isMain = import.meta.url === `file://${process.argv[1]}` || 
               import.meta.url.endsWith(process.argv[1]);

if (isMain) {
  main().catch(error => {
    console.error('❌ Fatal error:', error);
    process.exit(1);
  });
}

export { processLargePDF, processMultiplePDFs };
