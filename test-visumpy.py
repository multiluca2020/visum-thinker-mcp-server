# Test VisumPy - API Python ufficiale PTV
import sys
import os

print("=== TEST VISUMPY API ===")
print("Testing official PTV Python API for Visum")

# Aggiungi path Visum
visum_path = r"H:\Program Files\PTV Vision\PTV Visum 2025\Exe"
python_path = os.path.join(visum_path, "Python")

if visum_path not in sys.path:
    sys.path.insert(0, visum_path)
if python_path not in sys.path:
    sys.path.insert(0, python_path)

print(f"Python paths: {sys.path[:3]}")

# TEST 1: Import VisumPy
print(f"\n🔍 TEST 1: VisumPy import")
try:
    import VisumPy
    print(f"✅ VisumPy imported successfully!")
    print(f"VisumPy type: {type(VisumPy)}")
    print(f"VisumPy dir: {[attr for attr in dir(VisumPy) if not attr.startswith('_')]}")
    
    # Cerca metodi di connessione
    connection_methods = [attr for attr in dir(VisumPy) if any(word in attr.lower() for word in ['connect', 'attach', 'get', 'active', 'instance'])]
    if connection_methods:
        print(f"🎯 Connection methods found: {connection_methods}")
    
except ImportError as e:
    print(f"❌ VisumPy import failed: {e}")
    print("Trying alternative import paths...")
    
    # Prova import alternativi
    alternatives = [
        "import visum",
        "import Visum", 
        "from VisumPy import *",
        "import VisumPy.Helpers",
        "import PTV.VisumPy"
    ]
    
    for alt in alternatives:
        try:
            print(f"   Trying: {alt}")
            exec(alt)
            print(f"   ✅ Success: {alt}")
            break
        except ImportError as alt_e:
            print(f"   ❌ Failed: {alt_e}")

# TEST 2: Cerca moduli Visum nelle librerie
print(f"\n🔍 TEST 2: Search for Visum modules")
visum_modules = []

# Controlla se ci sono moduli .pyd o .dll relativi a Visum
for root, dirs, files in os.walk(python_path):
    for file in files:
        if any(keyword in file.lower() for keyword in ['visum', 'ptv']) and file.endswith(('.pyd', '.dll', '.py')):
            visum_modules.append(os.path.join(root, file))
            if len(visum_modules) > 10:  # Limita per non sovraccaricare
                break
    if len(visum_modules) > 10:
        break

if visum_modules:
    print(f"📚 Found Visum-related modules:")
    for module in visum_modules[:10]:
        print(f"   {os.path.basename(module)} in {os.path.dirname(module)}")
else:
    print(f"❌ No Visum-related modules found")

# TEST 3: Controlla site-packages
print(f"\n🔍 TEST 3: Site-packages inspection")
site_packages = os.path.join(python_path, "Lib", "site-packages")
if os.path.exists(site_packages):
    print(f"✅ Site-packages found: {site_packages}")
    
    packages = [d for d in os.listdir(site_packages) 
                if os.path.isdir(os.path.join(site_packages, d)) and 
                any(keyword in d.lower() for keyword in ['visum', 'ptv'])]
    
    if packages:
        print(f"🎯 Visum-related packages: {packages}")
        
        # Prova ad importare i package trovati
        for package in packages:
            try:
                print(f"   Testing import {package}...")
                exec(f"import {package}")
                print(f"   ✅ {package} imported!")
                
                # Cerca metodi di connessione nel package
                package_obj = eval(package)
                if hasattr(package_obj, '__dict__'):
                    attrs = [attr for attr in dir(package_obj) if not attr.startswith('_')]
                    connection_attrs = [attr for attr in attrs if any(word in attr.lower() for word in ['connect', 'attach', 'get', 'visum'])]
                    if connection_attrs:
                        print(f"      Connection methods: {connection_attrs}")
                
            except Exception as pkg_e:
                print(f"   ❌ {package} import failed: {pkg_e}")
    else:
        print(f"❌ No Visum packages in site-packages")
else:
    print(f"❌ Site-packages not found: {site_packages}")

# TEST 4: VisumPy connection methods (se importato)
print(f"\n🔍 TEST 4: VisumPy connection test")
try:
    # Se VisumPy è stato importato, proviamo i metodi
    if 'VisumPy' in locals() or 'VisumPy' in globals():
        visum_py = VisumPy if 'VisumPy' in locals() else globals()['VisumPy']
        
        print("Testing VisumPy connection methods...")
        
        # Metodi comuni VisumPy
        connection_tests = [
            ("VisumPy.Visum()", lambda: VisumPy.Visum()),
            ("VisumPy.Connect()", lambda: VisumPy.Connect()),
            ("VisumPy.GetActiveVisum()", lambda: VisumPy.GetActiveVisum()),
            ("VisumPy.Helpers.GetVisum()", lambda: VisumPy.Helpers.GetVisum()),
        ]
        
        for method_name, method_func in connection_tests:
            try:
                print(f"   Trying {method_name}...")
                visum_obj = method_func()
                print(f"   ✅ {method_name} SUCCESS!")
                print(f"   Type: {type(visum_obj)}")
                
                # Test accesso rete
                if hasattr(visum_obj, 'Net'):
                    nodes = visum_obj.Net.Nodes.Count
                    print(f"   📊 Nodes: {nodes:,}")
                    
                    if nodes > 0:
                        print(f"   🎉 VISUM WITH DATA FOUND!")
                        
                        # Salva successo VisumPy
                        import json
                        success_data = {
                            "timestamp": time.time(),
                            "method": method_name,
                            "api": "VisumPy",
                            "nodes": nodes,
                            "status": "SUCCESS"
                        }
                        
                        with open(r"H:\visum-thinker-mcp-server\visumpy_success.json", 'w') as f:
                            json.dump(success_data, f, indent=2)
                        
                        break
                        
                else:
                    print(f"   ❌ No Net attribute")
                    
            except Exception as method_e:
                print(f"   ❌ {method_name} failed: {method_e}")
                
    else:
        print("❌ VisumPy not available for testing")
        
except Exception as e:
    print(f"❌ VisumPy connection test failed: {e}")

print(f"\n=== VISUMPY TEST COMPLETED ===")
print("VisumPy might be the key to direct instance connection!")
print("Check visumpy_success.json if connection succeeded.")