# Fix win32com Cache - Risolve errore CLSIDToClassMap

import shutil
import os
import sys

# Percorso cache win32com
cache_path = os.path.join(os.environ['LOCALAPPDATA'], 'Temp', 'gen_py')

print(f"🔧 Pulizia cache win32com...")
print(f"📂 Percorso: {cache_path}")

if os.path.exists(cache_path):
    try:
        # Rimuovi tutta la cache
        shutil.rmtree(cache_path)
        print("✅ Cache rimossa con successo!")
        print("🔄 La cache verrà rigenerata automaticamente al prossimo avvio di Visum")
    except Exception as e:
        print(f"❌ Errore rimozione cache: {e}")
        print("💡 Prova a chiudere tutti i processi Python e Visum, poi riprova")
else:
    print("ℹ️  Cache non trovata (già pulita)")

print("\n📝 Percorsi alternativi da controllare:")
print(f"   1. {os.path.join(sys.prefix, 'Lib', 'site-packages', 'win32com', 'gen_py')}")
print(f"   2. {os.path.join(os.environ.get('APPDATA', ''), 'Python', 'win32com', 'gen_py')}")

input("\n✅ Pulizia completata. Premi INVIO per uscire...")
