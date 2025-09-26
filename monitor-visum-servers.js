#!/usr/bin/env node

/**
 * Monitor Server Visum - Monitoraggio continuo dei server TCP e processi Visum
 */

import { spawn } from 'child_process';

console.log('🔍 MONITOR SERVER VISUM - Avvio monitoraggio continuo...');
console.log('👀 Monitoraggio: Porte TCP 79xx, processi Visum, Python, Node');
console.log('⏰ Refresh ogni 5 secondi...\n');

let iteration = 0;

function checkServers() {
    iteration++;
    console.log(`\n${'='.repeat(60)}`);
    console.log(`📊 MONITOR #${iteration} - ${new Date().toLocaleTimeString()}`);
    console.log('='.repeat(60));
    
    // 1. Controllo porte TCP 79xx
    console.log('\n🔗 PORTE TCP 79xx (Server Visum):');
    const netstat = spawn('netstat', ['-ano']);
    let netstatOutput = '';
    
    netstat.stdout.on('data', (data) => {
        netstatOutput += data.toString();
    });
    
    netstat.on('close', () => {
        const tcpLines = netstatOutput.split('\n').filter(line => 
            line.includes(':79') && line.includes('LISTENING')
        );
        
        if (tcpLines.length === 0) {
            console.log('   ❌ Nessun server TCP attivo su porte 79xx');
        } else {
            tcpLines.forEach(line => {
                const parts = line.trim().split(/\s+/);
                console.log(`   ✅ ${parts[1]} - PID ${parts[4]}`);
            });
        }
        
        // 2. Controllo processi Visum
        setTimeout(() => {
            console.log('\n🖥️ PROCESSI VISUM:');
            const visumCheck = spawn('tasklist', ['/FI', 'IMAGENAME eq Visum*.exe']);
            let visumOutput = '';
            
            visumCheck.stdout.on('data', (data) => {
                visumOutput += data.toString();
            });
            
            visumCheck.on('close', () => {
                const visumLines = visumOutput.split('\n').filter(line => 
                    line.includes('Visum') && line.includes('.exe')
                );
                
                if (visumLines.length === 0) {
                    console.log('   ❌ Nessun processo Visum attivo');
                } else {
                    visumLines.forEach(line => {
                        const parts = line.trim().split(/\s+/);
                        console.log(`   ✅ ${parts[0]} - PID ${parts[1]} - ${parts[4]}`);
                    });
                }
                
                // 3. Controllo processi Python
                setTimeout(() => {
                    console.log('\n🐍 PROCESSI PYTHON:');
                    const pythonCheck = spawn('tasklist', ['/FI', 'IMAGENAME eq python.exe']);
                    let pythonOutput = '';
                    
                    pythonCheck.stdout.on('data', (data) => {
                        pythonOutput += data.toString();
                    });
                    
                    pythonCheck.on('close', () => {
                        const pythonLines = pythonOutput.split('\n').filter(line => 
                            line.includes('python.exe')
                        );
                        
                        if (pythonLines.length === 0) {
                            console.log('   ❌ Nessun processo Python attivo');
                        } else {
                            pythonLines.forEach(line => {
                                const parts = line.trim().split(/\s+/);
                                console.log(`   ✅ ${parts[0]} - PID ${parts[1]} - ${parts[4]}`);
                            });
                        }
                        
                        // 4. Controllo processi Node
                        setTimeout(() => {
                            console.log('\n📦 PROCESSI NODE:');
                            const nodeCheck = spawn('tasklist', ['/FI', 'IMAGENAME eq node.exe']);
                            let nodeOutput = '';
                            
                            nodeCheck.stdout.on('data', (data) => {
                                nodeOutput += data.toString();
                            });
                            
                            nodeCheck.on('close', () => {
                                const nodeLines = nodeOutput.split('\n').filter(line => 
                                    line.includes('node.exe')
                                );
                                
                                if (nodeLines.length === 0) {
                                    console.log('   ❌ Nessun processo Node attivo');
                                } else {
                                    nodeLines.forEach(line => {
                                        const parts = line.trim().split(/\s+/);
                                        console.log(`   ✅ ${parts[0]} - PID ${parts[1]} - ${parts[4]}`);
                                    });
                                }
                                
                                // 5. Controllo registry server
                                setTimeout(() => {
                                    console.log('\n📋 REGISTRY SERVER:');
                                    try {
                                        const fs = require('fs');
                                        if (fs.existsSync('server-registry.json')) {
                                            const registry = JSON.parse(fs.readFileSync('server-registry.json', 'utf8'));
                                            if (Object.keys(registry).length === 0) {
                                                console.log('   📁 Registry vuoto');
                                            } else {
                                                Object.entries(registry).forEach(([id, info]) => {
                                                    console.log(`   📊 ${info.projectName} - Porta ${info.port} - PID ${info.pid} - ${info.status}`);
                                                });
                                            }
                                        } else {
                                            console.log('   📁 Nessun registry trovato');
                                        }
                                    } catch (e) {
                                        console.log('   ❌ Errore lettura registry:', e.message);
                                    }
                                }, 100);
                            });
                        }, 100);
                    });
                }, 100);
            });
        }, 100);
    });
}

// Avvia monitoraggio
checkServers();
const monitor = setInterval(checkServers, 5000);

// Gestione Ctrl+C
process.on('SIGINT', () => {
    console.log('\n\n🛑 Monitor terminato dall\'utente');
    clearInterval(monitor);
    process.exit(0);
});

console.log('💡 Premi Ctrl+C per terminare il monitoraggio');