# Test VisumPy - Esplorazione approfondita
import sys
import os
import time
import inspect

print("=== DEEP VISUMPY ANALYSIS ===")

# Aggiungi paths
visum_path = r"H:\Program Files\PTV Vision\PTV Visum 2025\Exe"
python_path = os.path.join(visum_path, "Python")

if visum_path not in sys.path:
    sys.path.insert(0, visum_path)
if python_path not in sys.path:
    sys.path.insert(0, python_path)

# Import VisumPy
try:
    import VisumPy
    print(f"✅ VisumPy imported: {VisumPy}")
    print(f"VisumPy __file__: {getattr(VisumPy, '__file__', 'Not available')}")
    print(f"VisumPy __path__: {getattr(VisumPy, '__path__', 'Not available')}")
    print(f"VisumPy __package__: {getattr(VisumPy, '__package__', 'Not available')}")
    
    # Ispezione completa
    print(f"\n🔍 Complete VisumPy inspection:")
    all_attrs = dir(VisumPy)
    print(f"All attributes: {all_attrs}")
    
    for attr in all_attrs:
        if not attr.startswith('_'):
            try:
                obj = getattr(VisumPy, attr)
                print(f"  {attr}: {type(obj)} = {obj}")
                
                # Se è un oggetto callable, prova ad eseguirlo
                if callable(obj) and attr.lower() in ['visum', 'connect', 'get']:
                    try:
                        print(f"    Trying to call {attr}()...")
                        result = obj()
                        print(f"    ✅ {attr}() = {result} (type: {type(result)})")
                        
                        # Se ha Net, potrebbe essere Visum!
                        if hasattr(result, 'Net'):
                            nodes = result.Net.Nodes.Count
                            print(f"    🎉 FOUND VISUM INSTANCE! Nodes: {nodes:,}")
                            
                    except Exception as call_e:
                        print(f"    ❌ {attr}() failed: {call_e}")
                        
            except Exception as attr_e:
                print(f"  {attr}: Error accessing - {attr_e}")
    
    # Cerca submoduli
    print(f"\n🔍 Searching VisumPy submodules:")
    if hasattr(VisumPy, '__path__'):
        for path in VisumPy.__path__:
            print(f"  Scanning path: {path}")
            try:
                for item in os.listdir(path):
                    if item.endswith('.py') or os.path.isdir(os.path.join(path, item)):
                        print(f"    Found: {item}")
                        
                        # Prova import submodulo
                        if item.endswith('.py'):
                            module_name = item[:-3]
                            try:
                                submodule = __import__(f'VisumPy.{module_name}', fromlist=[module_name])
                                print(f"    ✅ Imported VisumPy.{module_name}")
                                
                                # Cerca metodi Visum nel submodulo
                                sub_attrs = [attr for attr in dir(submodule) if not attr.startswith('_')]
                                visum_attrs = [attr for attr in sub_attrs if any(word in attr.lower() for word in ['visum', 'connect', 'get', 'active'])]
                                if visum_attrs:
                                    print(f"      🎯 Visum methods: {visum_attrs}")
                                    
                                    # Prova i metodi più promettenti
                                    for method in visum_attrs[:3]:  # Prova max 3
                                        try:
                                            method_obj = getattr(submodule, method)
                                            if callable(method_obj):
                                                print(f"      Trying {method}()...")
                                                result = method_obj()
                                                print(f"      ✅ {method}() = {type(result)}")
                                                
                                                if hasattr(result, 'Net'):
                                                    nodes = result.Net.Nodes.Count
                                                    print(f"      🎉 VISUM CONNECTION! Nodes: {nodes:,}")
                                                    
                                        except Exception as method_e:
                                            print(f"      ❌ {method} failed: {method_e}")
                                
                            except ImportError as import_e:
                                print(f"    ❌ Import failed: {import_e}")
                                
            except Exception as scan_e:
                print(f"  ❌ Path scan failed: {scan_e}")
    
    # Prova anche import diretti comuni
    print(f"\n🔍 Testing common VisumPy imports:")
    common_imports = [
        'VisumPy.Visum',
        'VisumPy.visum',
        'VisumPy.COM',
        'VisumPy.com',
        'VisumPy.Application',
        'VisumPy.app',
        'VisumPy.Connect',
        'VisumPy.connect'
    ]
    
    for import_name in common_imports:
        try:
            print(f"  Trying: from {import_name}")
            parts = import_name.split('.')
            if len(parts) == 2:
                module = __import__(parts[0], fromlist=[parts[1]])
                obj = getattr(module, parts[1])
                print(f"  ✅ {import_name}: {type(obj)}")
                
                if callable(obj):
                    try:
                        result = obj()
                        print(f"    {import_name}() = {type(result)}")
                        if hasattr(result, 'Net'):
                            nodes = result.Net.Nodes.Count
                            print(f"    🎉 FOUND ACTIVE VISUM! Nodes: {nodes:,}")
                            
                            # Salva successo
                            import json
                            success_data = {
                                "timestamp": time.time(),
                                "method": import_name,
                                "api": "VisumPy_detailed",
                                "nodes": nodes,
                                "status": "SUCCESS"
                            }
                            
                            with open(r"H:\visum-thinker-mcp-server\visumpy_success.json", 'w') as f:
                                json.dump(success_data, f, indent=2)
                            
                            print(f"    💾 Success saved to visumpy_success.json")
                            break
                            
                    except Exception as call_e:
                        print(f"    ❌ Call failed: {call_e}")
                        
        except Exception as test_e:
            print(f"  ❌ {import_name} failed: {test_e}")

except ImportError as e:
    print(f"❌ VisumPy not available: {e}")

# TEST finale: COM con VisumPy hints
print(f"\n🔍 Final COM test with VisumPy environment:")
try:
    import win32com.client as win32
    
    # Prova GetActiveObject con diversi ProgID che VisumPy potrebbe usare
    progids = [
        'Visum.Visum',
        'Visum.Application', 
        'PTV.Visum',
        'PTV.Visum.Application',
        'VisumPy.Visum',
        'VisumCOM.Application'
    ]
    
    for progid in progids:
        try:
            print(f"  Trying GetActiveObject('{progid}')...")
            visum = win32.GetActiveObject(progid)
            print(f"  ✅ {progid}: {type(visum)}")
            
            if hasattr(visum, 'Net'):
                nodes = visum.Net.Nodes.Count
                print(f"  🎉 ACTIVE VISUM FOUND via {progid}! Nodes: {nodes:,}")
                
        except Exception as progid_e:
            print(f"  ❌ {progid} failed: {progid_e}")

except Exception as final_e:
    print(f"❌ Final COM test failed: {final_e}")

print(f"\n=== DEEP VISUMPY ANALYSIS COMPLETED ===")
print("If no success found, VisumPy might not be the solution we need.")