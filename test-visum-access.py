# Test avanzato per accedere all'istanza Visum GUI già aperta
# Proviamo tutti i metodi possibili

import sys
import os
import time

print("=== TEST ACCESSO ISTANZA VISUM GUI APERTA ===")
print(f"Python version: {sys.version}")
print(f"Working directory: {os.getcwd()}")
print(f"Script path: {__file__ if '__file__' in globals() else 'Unknown'}")

# Informazioni ambiente Visum
visum_path = r"H:\Program Files\PTV Vision\PTV Visum 2025\Exe"
print(f"Visum path: {visum_path}")
print(f"Visum Python path: {visum_path}\\Python")

# Aggiungi path Visum Python
if visum_path not in sys.path:
    sys.path.insert(0, visum_path)
    sys.path.insert(0, os.path.join(visum_path, "Python"))
    print("✅ Visum paths added to sys.path")

print(f"Current sys.path (first 3): {sys.path[:3]}")

# TEST 1: Variabili globali disponibili
print(f"\n🔍 TEST 1: Global variables inspection")
global_vars = [var for var in dir() if not var.startswith('_')]
print(f"Available globals: {global_vars}")

# Cerca variabili che potrebbero essere Visum
visum_like = [var for var in global_vars if 'visum' in var.lower()]
if visum_like:
    print(f"Visum-like globals: {visum_like}")
    for var in visum_like:
        try:
            obj = globals()[var]
            print(f"   {var}: {type(obj)} - {obj}")
        except:
            pass

# TEST 2: Built-in globals che potrebbero essere iniettati da Visum
print(f"\n🔍 TEST 2: Checking for Visum built-ins")
possible_names = ['Visum', 'visum', 'VisumApp', 'Application', 'App']
visum_obj = None

for name in possible_names:
    try:
        if name in globals():
            visum_obj = globals()[name]
            print(f"✅ Found {name} in globals: {type(visum_obj)}")
            break
    except:
        pass

# TEST 3: __builtins__ inspection
print(f"\n🔍 TEST 3: Builtins inspection")
try:
    if hasattr(__builtins__, '__dict__'):
        builtins_dict = __builtins__.__dict__
    else:
        builtins_dict = __builtins__
    
    visum_builtins = [k for k in builtins_dict.keys() if 'visum' in k.lower()]
    if visum_builtins:
        print(f"Visum-like builtins: {visum_builtins}")
        for builtin in visum_builtins:
            try:
                obj = builtins_dict[builtin]
                print(f"   {builtin}: {type(obj)}")
                if not visum_obj:
                    visum_obj = obj
            except:
                pass
except Exception as e:
    print(f"Builtins inspection failed: {e}")

# TEST 4: sys.modules per moduli Visum
print(f"\n🔍 TEST 4: sys.modules inspection")
visum_modules = [name for name in sys.modules.keys() if 'visum' in name.lower() or 'ptv' in name.lower()]
if visum_modules:
    print(f"Visum-related modules: {visum_modules}")
    for mod_name in visum_modules:
        try:
            module = sys.modules[mod_name]
            print(f"   {mod_name}: {module}")
            # Cerca attributi Visum nel modulo
            if hasattr(module, 'Visum'):
                print(f"      Module has Visum attribute!")
                if not visum_obj:
                    visum_obj = module.Visum
        except:
            pass

# TEST 5: Import diretto moduli Visum
print(f"\n🔍 TEST 5: Direct Visum module imports")
import_attempts = [
    'import Visum',
    'import visum', 
    'import VisumPy',
    'import PTV',
    'import PTVVisum',
    'from Visum import *',
    'from visum import *'
]

for attempt in import_attempts:
    try:
        print(f"Trying: {attempt}")
        exec(attempt)
        print(f"✅ Success: {attempt}")
        
        # Controlla se ora abbiamo Visum
        if 'Visum' in globals() and not visum_obj:
            visum_obj = globals()['Visum']
            print(f"   Got Visum object: {type(visum_obj)}")
        
    except Exception as e:
        print(f"   Failed: {e}")

# TEST 6: COM con diversi approcci
print(f"\n🔍 TEST 6: COM access attempts")
try:
    import win32com.client
    
    com_attempts = [
        ('Dispatch', lambda: win32com.client.Dispatch("Visum.Visum")),
        ('DispatchEx', lambda: win32com.client.DispatchEx("Visum.Visum")),
        ('GetActiveObject', lambda: win32com.client.GetActiveObject("Visum.Visum")),
        ('GetObject', lambda: win32com.client.GetObject("Visum.Visum")),
        ('GetObject with file', lambda: win32com.client.GetObject(r"H:\go\italferr2025\Campoleone\100625_Versione_base_v0.3_sub_ok_priv.ver"))
    ]
    
    for method_name, method_func in com_attempts:
        try:
            print(f"Trying COM {method_name}...")
            com_obj = method_func()
            print(f"✅ {method_name} success: {type(com_obj)}")
            
            # Test accesso rete
            try:
                nodes = com_obj.Net.Nodes.Count
                print(f"   Network nodes: {nodes:,}")
                if nodes > 0 and not visum_obj:
                    visum_obj = com_obj
                    print("   🎯 This object has data!")
            except Exception as net_e:
                print(f"   Network access failed: {net_e}")
                
        except Exception as e:
            print(f"   {method_name} failed: {e}")

except ImportError:
    print("win32com.client not available")

# RISULTATO FINALE
print(f"\n" + "="*50)
print("🎯 RISULTATO FINALE")
print("="*50)

if visum_obj:
    print(f"✅ VISUM OBJECT FOUND!")
    print(f"Type: {type(visum_obj)}")
    print(f"Dir: {[attr for attr in dir(visum_obj) if not attr.startswith('_')][:10]}...")
    
    # Test funzionalità
    try:
        print(f"\n🧪 Testing functionality...")
        if hasattr(visum_obj, 'Net'):
            net = visum_obj.Net
            print(f"Net object: {type(net)}")
            
            if hasattr(net, 'Nodes'):
                nodes = net.Nodes.Count
                print(f"Nodes: {nodes:,}")
                
            if hasattr(net, 'Links'):
                links = net.Links.Count  
                print(f"Links: {links:,}")
                
            if nodes > 0 and links > 0:
                print(f"🎉 SUCCESS! Visum with loaded project accessed!")
                
                # Save success indicator
                with open(r"H:\visum-thinker-mcp-server\visum_access_success.txt", 'w') as f:
                    f.write(f"SUCCESS: Visum accessed with {nodes} nodes, {links} links")
                    
            else:
                print(f"⚠️ Visum accessed but no project loaded")
                
        else:
            print(f"❌ Object found but no Net attribute")
            
    except Exception as test_e:
        print(f"❌ Functionality test failed: {test_e}")
        
else:
    print(f"❌ NO VISUM OBJECT FOUND")
    print(f"The script is running but cannot access Visum instance")
    
    # Save failure indicator  
    with open(r"H:\visum-thinker-mcp-server\visum_access_failed.txt", 'w') as f:
        f.write("FAILED: Could not access any Visum object")

print(f"\n=== TEST COMPLETED ===")
print(f"Check output files for results")