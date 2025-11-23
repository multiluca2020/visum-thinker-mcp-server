# -*- coding: ascii -*-
"""
Cerca metodi di commit/save/update su Visum e LineRoute
"""

try:
    print("=" * 80)
    print("METODI DI COMMIT/SAVE/UPDATE")
    print("=" * 80)
    
    print("\n1. METODI SU VISUM (oggetto principale):")
    print("-" * 80)
    
    visum_methods = []
    for attr in dir(Visum):
        attr_lower = attr.lower()
        if any(keyword in attr_lower for keyword in ['commit', 'save', 'update', 'refresh', 'apply', 'flush']):
            visum_methods.append(attr)
    
    if visum_methods:
        for method in visum_methods:
            print("  - %s" % method)
    else:
        print("  Nessun metodo trovato")
    
    # Trova il LineRoute
    print("\n2. METODI SU LINEROUTE:")
    print("-" * 80)
    
    lr = None
    for lineroute in Visum.Net.LineRoutes:
        name = lineroute.AttValue("Name")
        if name == "R17_2":
            lr = lineroute
            break
    
    if lr:
        lr_methods = []
        for attr in dir(lr):
            attr_lower = attr.lower()
            if any(keyword in attr_lower for keyword in ['commit', 'save', 'update', 'refresh', 'apply', 'flush']):
                lr_methods.append(attr)
        
        if lr_methods:
            for method in lr_methods:
                print("  - %s" % method)
        else:
            print("  Nessun metodo trovato")
    
    # TimeProfile
    print("\n3. METODI SU TIMEPROFILE:")
    print("-" * 80)
    
    if lr:
        tp = None
        for time_profile in lr.TimeProfiles:
            tp = time_profile
            break
        
        if tp:
            tp_methods = []
            for attr in dir(tp):
                attr_lower = attr.lower()
                if any(keyword in attr_lower for keyword in ['commit', 'save', 'update', 'refresh', 'apply', 'flush', 'calc']):
                    tp_methods.append(attr)
            
            if tp_methods:
                for method in tp_methods:
                    print("  - %s" % method)
            else:
                print("  Nessun metodo trovato")
    
    # Net
    print("\n4. METODI SU VISUM.NET:")
    print("-" * 80)
    
    net_methods = []
    for attr in dir(Visum.Net):
        attr_lower = attr.lower()
        if any(keyword in attr_lower for keyword in ['commit', 'save', 'update', 'refresh', 'apply', 'flush']):
            net_methods.append(attr)
    
    if net_methods:
        for method in net_methods:
            print("  - %s" % method)
    else:
        print("  Nessun metodo trovato")
    
    print("\n" + "=" * 80)
    print("PROVA QUESTI COMANDI:")
    print("=" * 80)
    print("  Visum.SaveVersion()")
    print("  Visum.Net.RefreshAll()")
    print("  Visum.Graphics.RefreshAll()")
    print("=" * 80)

except Exception as e:
    print("\nERRORE: %s" % str(e))
    import traceback
    traceback.print_exc()
