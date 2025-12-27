"""
Versione MINIMA per test - solo operazioni basilari
"""

def test_basic_operations():
    """Test se le operazioni COM base funzionano"""
    
    print("TEST 1: Conta link totali")
    try:
        count = Visum.Net.Links.Count
        print("  OK - Link totali: {}".format(count))
    except Exception as e:
        print("  FALLITO: {}".format(e))
        return False
    
    print("\nTEST 2: Leggi un attributo")
    try:
        first_link = Visum.Net.Links.ItemByKey(1, 2)  # Link da nodo 1 a nodo 2
        type_no = first_link.AttValue("TypeNo")
        print("  OK - TypeNo primo link: {}".format(type_no))
    except Exception as e:
        print("  FALLITO: {}".format(e))
        return False
    
    print("\nTEST 3: Modifica AddVal1 su UN link")
    try:
        first_link.SetAttValue("AddVal1", 999)
        val = first_link.AttValue("AddVal1")
        print("  OK - AddVal1 impostato: {}".format(val))
    except Exception as e:
        print("  FALLITO: {}".format(e))
        return False
    
    print("\n" + "=" * 70)
    print("TUTTI I TEST PASSATI - Visum risponde correttamente")
    print("=" * 70)
    return True


def select_manual_gui():
    """
    Assume che l'utente abbia GIA' marcato i link con il tool GUI.
    Copia semplicemente la selezione.
    """
    print("Cerco link con Active=1 (marcati da GUI)...")
    
    try:
        # Conta link attivi
        all_links = Visum.Net.Links
        active_count = 0
        
        for link in all_links:
            if link.AttValue("Active") == 1:
                active_count += 1
                link.SetAttValue("AddVal1", 1)
        
        print("Link copiati: {}".format(active_count))
        return {"success": True, "count": active_count}
        
    except Exception as e:
        print("ERRORE: {}".format(e))
        return {"success": False, "count": 0}


if __name__ == "__main__":
    print("=" * 70)
    print("TEST VISUM COM - Versione minima")
    print("=" * 70)
    print()
    
    if test_basic_operations():
        print("\nVisum funziona! Ora prova select_manual_gui()")
    else:
        print("\nVisum NON risponde - RIAVVIA Visum e riprova")
