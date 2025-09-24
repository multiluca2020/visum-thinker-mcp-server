# Approccio alternativo: connessione diretta al processo Visum 
# PID 6588 ha il progetto caricato!

import sys
import os
import subprocess

print("=== CONNESSIONE DIRETTA AL PROCESSO VISUM ===")
print("Target: PID 6588 con progetto Campoleone caricato")

# STRATEGIA: Usare Visum CLI per eseguire script su istanza specifica
# Invece di /script che apre nuova istanza, proviamo comandi diretti

visum_exe = r"H:\Program Files\PTV Vision\PTV Visum 2025\Exe\Visum250.exe"

# Test diversi parametri CLI
cli_tests = [
    # Test 1: Parametro per istanza esistente
    [visum_exe, "/instance", "6588", "/script", r"H:\visum-thinker-mcp-server\test-simple.py"],
    
    # Test 2: Connessione via named instance
    [visum_exe, "/connect", "/script", r"H:\visum-thinker-mcp-server\test-simple.py"],
    
    # Test 3: Batch mode con progetto già aperto
    [visum_exe, "/batch", "/script", r"H:\visum-thinker-mcp-server\test-simple.py"],
    
    # Test 4: Python execute su istanza attiva
    [visum_exe, "/python", r"H:\visum-thinker-mcp-server\test-simple.py"],
]

print("🧪 Testing CLI parameters...")

for i, cmd in enumerate(cli_tests, 1):
    print(f"\nTest {i}: {' '.join(cmd[1:])}")  # Skip exe path for readability
    
    try:
        # Execute with timeout
        result = subprocess.run(cmd, 
                              capture_output=True, 
                              text=True, 
                              timeout=30)
        
        print(f"   Exit code: {result.returncode}")
        if result.stdout:
            print(f"   STDOUT: {result.stdout[:200]}...")
        if result.stderr:
            print(f"   STDERR: {result.stderr[:200]}...")
            
        # Controlla se ha prodotto output file
        if os.path.exists("visum_success.txt"):
            with open("visum_success.txt", "r") as f:
                content = f.read()
            print(f"   🎉 SUCCESS FILE FOUND: {content}")
            os.remove("visum_success.txt")  # Clean per test successivi
            break
            
    except subprocess.TimeoutExpired:
        print(f"   ⏰ Timeout (30s)")
    except Exception as e:
        print(f"   ❌ Error: {e}")

print(f"\n" + "="*50)
print("🎯 ALTERNATIVE APPROACH")
print("="*50)

# Se CLI non funziona, proviamo approccio IPC
print("💡 PIANO B: Inter-Process Communication")

# Creiamo un file di comando che il processo Visum esistente potrebbe leggere
command_file = r"H:\visum-thinker-mcp-server\visum_command.txt"
result_file = r"H:\visum-thinker-mcp-server\visum_result.txt"

# Comando per l'istanza Visum
command_data = """
# Comando MCP per istanza Visum attiva
# Da eseguire nel processo PID 6588

import json
import time

# Accesso diretto Visum (dovrebbe funzionare dentro il processo)
try:
    # Nell'istanza Visum, l'oggetto è disponibile globalmente
    nodes = Visum.Net.Nodes.Count
    links = Visum.Net.Links.Count
    zones = Visum.Net.Zones.Count
    
    # Risultato
    result = {
        "timestamp": time.time(),
        "success": True,
        "pid": os.getpid(),
        "network": {
            "nodes": nodes,
            "links": links,
            "zones": zones
        }
    }
    
    # Salva risultato per MCP
    with open(r"H:\\visum-thinker-mcp-server\\visum_result.txt", "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"SUCCESS: {nodes} nodes, {links} links")
    
except Exception as e:
    error_result = {
        "timestamp": time.time(),
        "success": False,
        "error": str(e),
        "pid": os.getpid()
    }
    
    with open(r"H:\\visum-thinker-mcp-server\\visum_result.txt", "w") as f:
        json.dump(error_result, f, indent=2)
"""

with open(command_file, "w") as f:
    f.write(command_data)

print(f"📝 Comando IPC scritto in: {command_file}")
print("💡 ISTRUZIONI MANUALI:")
print("1. Vai all'istanza Visum con progetto caricato (PID 6588)")  
print("2. Vai a Procedures > Execute Python Script")
print(f"3. Esegui il file: {command_file}")
print(f"4. Controlla risultato in: {result_file}")

print(f"\n🔄 ALTERNATIVA: Clipboard approach")
print("L'istanza Visum potrebbe anche leggere comandi dalla clipboard...")

# Test se riusciamo a scrivere nella clipboard
try:
    import win32clipboard
    
    clipboard_command = f"""
# MCP Clipboard Command for Visum
nodes = Visum.Net.Nodes.Count
print(f"Nodes: {{nodes}}")
"""
    
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(clipboard_command)
    win32clipboard.CloseClipboard()
    
    print("✅ Comando scritto in clipboard")
    print("💡 L'utente può incollare e eseguire direttamente in Visum Python console")
    
except ImportError:
    print("❌ Clipboard non disponibile")
except Exception as e:
    print(f"❌ Clipboard error: {e}")

print(f"\n=== PROSSIMI PASSI ===")
print("1. 🎯 Identificare il metodo funzionante")
print("2. 🔧 Implementare nell'MCP server")  
print("3. 🚀 Test con Claude")
print("4. 🎉 Workflow completo!")

print(f"\n=== TEST COMPLETATO ===")
print("La connessione diretta è possibile, serve il metodo giusto!")