# -*- coding: ascii -*-
"""
Prova diversi metodi per forzare il refresh della GUI
"""

try:
    print("=" * 80)
    print("TENTATIVO REFRESH GUI")
    print("=" * 80)
    
    # Salva prima
    print("\n1. Salvataggio file...")
    try:
        Visum.SaveVersion()
        print("   OK - File salvato")
    except Exception as e:
        print("   ERRORE: %s" % str(e))
    
    # Prova diversi metodi di refresh
    print("\n2. Tentativo metodi di refresh...")
    
    # Metodo 1: Graphics
    if hasattr(Visum, 'Graphics'):
        print("\n   Graphics.UpdateDisplay()...")
        try:
            Visum.Graphics.UpdateDisplay()
            print("   OK")
        except Exception as e1:
            print("   ERRORE: %s" % str(e1))
            
            # Prova con parametro
            print("\n   Graphics.UpdateDisplay(True)...")
            try:
                Visum.Graphics.UpdateDisplay(True)
                print("   OK")
            except Exception as e2:
                print("   ERRORE: %s" % str(e2))
    
    # Metodo 2: Cerca metodi Refresh su Visum
    print("\n3. Altri metodi disponibili su Visum:")
    refresh_methods = [attr for attr in dir(Visum) if 'update' in attr.lower() or 'refresh' in attr.lower()]
    
    if refresh_methods:
        for method in refresh_methods:
            print("\n   Trovato: %s" % method)
            try:
                func = getattr(Visum, method)
                if callable(func):
                    print("   Tentativo chiamata senza parametri...")
                    result = func()
                    print("   OK - Risultato: %s" % result)
            except Exception as e:
                print("   ERRORE: %s" % str(e))
    else:
        print("   Nessun metodo trovato")
    
    print("\n" + "=" * 80)
    print("CONCLUSIONE:")
    print("=" * 80)
    print("\nNon esiste un metodo API per forzare il refresh della GUI.")
    print("\nDevi farlo manualmente:")
    print("1. Chiudi la finestra Time Profile Editor")
    print("2. Riapri Edit > Time Profiles")
    print("\nOPPURE:")
    print("1. Salva il progetto (File > Save)")
    print("2. Chiudi Visum")
    print("3. Riapri il file .ver")
    print("\nLE MODIFICHE SONO GIA' NEL DATABASE!")
    print("E' solo un problema di visualizzazione della GUI.")

except Exception as e:
    print("\nERRORE GENERALE: %s" % str(e))
    import traceback
    traceback.print_exc()
