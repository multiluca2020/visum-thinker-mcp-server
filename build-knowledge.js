#!/usr/bin/env node

/**
 * Knowledge Base Builder
 * Creates comprehensive domain-specific knowledge bases from multiple PDFs
 */

import { processLargePDF, processMultiplePDFs } from './process-pdf.js';
import fs from 'fs';
import path from 'path';
import fsExtra from 'fs-extra';

async function buildDomainKnowledge(domain, filePaths, options = {}) {
  console.log(`🧠 Building ${domain.toUpperCase()} Knowledge Base`);
  console.log(`📚 Processing ${filePaths.length} documents...`);
  
  const knowledgeBase = {
    domain: domain,
    createdAt: new Date(),
    sources: [],
    totalPages: 0,
    totalSizeMB: 0,
    sections: {},
    searchIndex: {},
    content: ''
  };

  let allContent = '';
  
  for (let i = 0; i < filePaths.length; i++) {
    const filePath = filePaths[i];
    
    try {
      console.log(`\n📖 Processing: ${path.basename(filePath)}`);
      
      const result = await processLargePDF(filePath, {
        chunkSizePages: 15,
        outputSummary: true,
        outputFile: null
      });

      // Add to knowledge base
      const docId = `doc_${i + 1}`;
      knowledgeBase.sources.push({
        id: docId,
        filename: result.filename,
        pages: result.totalPages,
        sizeMB: result.fileSizeMB,
        processedAt: result.processedAt
      });

      knowledgeBase.totalPages += result.totalPages;
      knowledgeBase.totalSizeMB += result.fileSizeMB;

      // Section the content
      const sectionContent = `\n\n=== ${domain.toUpperCase()} DOCUMENT ${i + 1}: ${result.filename} ===\n`;
      const documentContent = sectionContent + result.content;
      
      knowledgeBase.sections[docId] = {
        title: result.filename,
        content: documentContent,
        pages: result.totalPages,
        characters: documentContent.length
      };

      allContent += documentContent;

      console.log(`✅ Added ${result.filename} to ${domain} knowledge base`);

    } catch (error) {
      console.error(`❌ Failed to process ${filePath}:`, error.message);
    }
  }

  // Build search index (simple keyword extraction)
  const keywords = extractKeywords(allContent);
  knowledgeBase.searchIndex = keywords;
  knowledgeBase.content = allContent;
  knowledgeBase.totalCharacters = allContent.length;

  // Save knowledge base
  const outputPath = `${domain}-knowledge-base.json`;
  await fsExtra.writeJson(outputPath, knowledgeBase, { spaces: 2 });

  console.log('\n🎉 Domain Knowledge Base Complete!');
  console.log('===================================');
  console.log(`🎯 Domain: ${domain.toUpperCase()}`);
  console.log(`📚 Sources: ${knowledgeBase.sources.length}`);
  console.log(`📄 Total pages: ${knowledgeBase.totalPages.toLocaleString()}`);
  console.log(`📊 Total size: ${knowledgeBase.totalSizeMB.toFixed(2)} MB`);
  console.log(`📝 Content: ${knowledgeBase.totalCharacters.toLocaleString()} chars`);
  console.log(`🔍 Keywords: ${Object.keys(keywords).length}`);
  console.log(`💾 Saved to: ${outputPath}`);

  return knowledgeBase;
}

function extractKeywords(content) {
  // Simple keyword extraction
  const words = content.toLowerCase()
    .replace(/[^\w\s]/g, ' ')
    .split(/\s+/)
    .filter(word => word.length > 3);
  
  const wordCount = {};
  words.forEach(word => {
    wordCount[word] = (wordCount[word] || 0) + 1;
  });

  // Return top keywords
  return Object.entries(wordCount)
    .sort(([,a], [,b]) => b - a)
    .slice(0, 1000)
    .reduce((obj, [word, count]) => {
      obj[word] = count;
      return obj;
    }, {});
}

// Domain-specific builders
async function buildTransportationKnowledge(filePaths) {
  return buildDomainKnowledge('transportation', filePaths);
}

async function buildAcademicKnowledge(filePaths) {
  return buildDomainKnowledge('academic', filePaths);
}

async function buildTechnicalKnowledge(filePaths) {
  return buildDomainKnowledge('technical', filePaths);
}

// CLI Usage
async function main() {
  const args = process.argv.slice(2);
  
  if (args.length < 2) {
    console.log(`
🧠 Knowledge Base Builder

Usage: node build-knowledge.js <domain> <pdf-files...>

Domains:
  transportation  - Traffic engineering, urban planning, transportation
  academic       - Research papers, journals, academic content  
  technical      - Manuals, specifications, technical documentation
  custom         - General purpose knowledge base

Examples:
  node build-knowledge.js transportation visum-manual.pdf traffic-handbook.pdf
  node build-knowledge.js academic paper1.pdf paper2.pdf research.pdf
  node build-knowledge.js custom ~/Documents/*.pdf
`);
    return;
  }

  const domain = args[0];
  const filePaths = args.slice(1);

  try {
    await buildDomainKnowledge(domain, filePaths);
  } catch (error) {
    console.error('❌ Knowledge base creation failed:', error.message);
    process.exit(1);
  }
}

if (import.meta.url === `file://${process.argv[1]}` || 
    import.meta.url.endsWith(process.argv[1])) {
  main();
}

export { buildDomainKnowledge, buildTransportationKnowledge, buildAcademicKnowledge, buildTechnicalKnowledge };
