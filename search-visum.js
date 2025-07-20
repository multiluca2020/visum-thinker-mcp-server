#!/usr/bin/env node

/**
 * Visum Knowledge Base Search Tool
 * Search your comprehensive PTV Visum knowledge base
 */

import fs from 'fs';
import path from 'path';

async function searchVisumKnowledge(searchTerm, options = {}) {
  const {
    maxResults = 10,
    contextSize = 300,
    caseSensitive = false
  } = options;

  try {
    // Load the knowledge base
    console.log('📚 Loading Visum knowledge base...');
    const knowledgeBase = JSON.parse(fs.readFileSync('visum-complete-knowledge.json', 'utf8'));
    
    console.log(`🔍 Searching for: "${searchTerm}"`);
    console.log(`📊 Knowledge base: ${knowledgeBase.totalPages} pages, ${knowledgeBase.files.length} documents`);
    
    const content = knowledgeBase.content;
    const searchText = caseSensitive ? content : content.toLowerCase();
    const query = caseSensitive ? searchTerm : searchTerm.toLowerCase();

    // Find all matches
    const matches = [];
    let position = 0;

    while (position < searchText.length && matches.length < maxResults) {
      const matchIndex = searchText.indexOf(query, position);
      if (matchIndex === -1) break;

      // Extract context around the match
      const start = Math.max(0, matchIndex - contextSize);
      const end = Math.min(content.length, matchIndex + query.length + contextSize);
      const context = content.substring(start, end);

      matches.push({
        position: matchIndex,
        context: context.trim(),
      });

      position = matchIndex + 1;
    }

    // Display results
    console.log(`\n🎯 Found ${matches.length} matches:\n`);
    
    matches.forEach((match, index) => {
      console.log(`**Match ${index + 1}** (Position: ${match.position.toLocaleString()})`);
      console.log('─'.repeat(60));
      console.log(match.context.replace(/\n+/g, '\n').trim());
      console.log('');
    });

    if (matches.length === 0) {
      console.log('❌ No matches found. Try different keywords or broader terms.');
    } else if (matches.length >= maxResults) {
      console.log(`📝 Showing first ${maxResults} matches. Use --max=${maxResults * 2} to see more.`);
    }

    return matches;

  } catch (error) {
    console.error('❌ Error searching knowledge base:', error.message);
    return [];
  }
}

// CLI Usage
async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.log(`
🔍 Visum Knowledge Base Search

Usage: node search-visum.js <search-term> [options]

Options:
  --max=N         Maximum results (default: 10)
  --context=N     Context size around matches (default: 300)
  --case          Case sensitive search

Examples:
  node search-visum.js "traffic assignment"
  node search-visum.js "COM API" --max=5
  node search-visum.js "public transport" --context=500
  node search-visum.js "calibration" --case
`);
    return;
  }

  const searchTerm = args[0];
  const options = {};

  // Parse options
  for (let i = 1; i < args.length; i++) {
    const arg = args[i];
    if (arg.startsWith('--max=')) {
      options.maxResults = parseInt(arg.split('=')[1]);
    } else if (arg.startsWith('--context=')) {
      options.contextSize = parseInt(arg.split('=')[1]);
    } else if (arg === '--case') {
      options.caseSensitive = true;
    }
  }

  await searchVisumKnowledge(searchTerm, options);
}

if (import.meta.url === `file://${process.argv[1]}` || 
    import.meta.url.endsWith(process.argv[1])) {
  main();
}

export { searchVisumKnowledge };
