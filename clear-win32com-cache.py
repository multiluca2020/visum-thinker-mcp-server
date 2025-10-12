"""
Script per pulire la cache win32com che causa errori con Visum
"""
import shutil
import os
import tempfile

# Trova la directory gen_py nella cache win32com
gen_py_path = os.path.join(tempfile.gettempdir(), 'gen_py')

print("🧹 Pulizia cache win32com...")
print(f"📂 Percorso: {gen_py_path}")

if os.path.exists(gen_py_path):
    try:
        shutil.rmtree(gen_py_path)
        print("✅ Cache pulita con successo!")
        print("💡 Ora puoi riaprire il progetto Visum")
    except Exception as e:
        print(f"❌ Errore durante la pulizia: {e}")
        print("💡 Prova a chiudere tutte le istanze di Python/Visum e riprova")
else:
    print("⚠️  Directory gen_py non trovata")
    print(f"💡 Cerca manualmente in: {tempfile.gettempdir()}")

# Mostra anche altre possibili location
import win32com
win32com_path = os.path.dirname(win32com.__file__)
alt_gen_py = os.path.join(win32com_path, 'gen_py')

print(f"\n📍 Altra possibile location: {alt_gen_py}")
if os.path.exists(alt_gen_py):
    print("   Trovata! Vuoi pulire anche questa? (esegui manualmente)")
