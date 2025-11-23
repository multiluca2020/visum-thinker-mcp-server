#!/usr/bin/env node

/**
 * Send Congestion Analysis Script to Visum via TCP Server
 * 
 * Usage:
 *   node send-congestion-analysis.js <projectId> [analysisPeriod] [topN]
 * 
 * Examples:
 *   node send-congestion-analysis.js S000009result_1278407893
 *   node send-congestion-analysis.js S000009result_1278407893 AM 20
 */

import { spawn } from 'child_process';
import * as readline from 'readline';
import * as fs from 'fs';

// Parse command line arguments
const args = process.argv.slice(2);
if (args.length === 0) {
  console.error('❌ Error: Missing projectId argument');
  console.error('\nUsage:');
  console.error('  node send-congestion-analysis.js <projectId> [analysisPeriod] [topN]');
  console.error('\nExamples:');
  console.error('  node send-congestion-analysis.js S000009result_1278407893');
  console.error('  node send-congestion-analysis.js S000009result_1278407893 AM 20');
  process.exit(1);
}

const projectId = args[0];
const analysisPeriod = args[1] || 'AP';
const topN = args[2] ? parseInt(args[2]) : 10;

console.log('🚦 Visum Congestion Analysis via TCP');
console.log(`📊 Project ID: ${projectId}`);
console.log(`🕐 Analysis Period: ${analysisPeriod}`);
console.log(`🔢 Top N: ${topN}`);
console.log('═'.repeat(60));

// Read the inline script
const scriptPath = 'analyze-congestion-inline.py';
let scriptContent;

try {
  scriptContent = fs.readFileSync(scriptPath, 'utf-8');
} catch (err) {
  console.error(`❌ Error reading script file: ${scriptPath}`);
  console.error(err.message);
  process.exit(1);
}

// Customize the script with parameters
const customizedScript = scriptContent
  .replace(/ANALYSIS_PERIOD = "AP"/, `ANALYSIS_PERIOD = "${analysisPeriod}"`)
  .replace(/TOP_N = 10/, `TOP_N = ${topN}`);

// Write customized script to temp file
const tempScriptPath = 'analyze-congestion-temp.py';
fs.writeFileSync(tempScriptPath, customizedScript, 'utf-8');

console.log(`✅ Script customized and saved to: ${tempScriptPath}`);
console.log(`\n💡 To run the analysis, use one of these methods:`);
console.log(`\n1. From Visum Python Console:`);
console.log(`   exec(open('${tempScriptPath}').read())`);
console.log(`\n2. From PowerShell (standalone):`);
console.log(`   python ${tempScriptPath}`);
console.log(`\n3. Via MCP (if project_execute_python tool exists):`);
console.log(`   Use the MCP tool with projectId: ${projectId}`);

// For now, we'll just create the script file
// In the future, a generic execute_python tool could be added to MCP
console.log('═'.repeat(60));
process.exit(0);
