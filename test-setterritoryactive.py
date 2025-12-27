"""
Test diretto di SetTerritoryActive con diversi metodi
"""

def test_setterritoryactive():
    """Test SetTerritoryActive con vari approcci"""
    
    visum = Visum
    
    print("=" * 70)
    print("TEST SetTerritoryActive")
    print("=" * 70)
    
    # Ottieni primo territorio
    territories = visum.Net.Territories
    print("\nNumero territori: {}".format(territories.Count))
    
    if territories.Count == 0:
        print("Nessun territorio trovato!")
        return
    
    terr = territories.ItemByKey(1)
    terr_no = terr.AttValue("No")
    terr_name = terr.AttValue("Name") if terr.AttValue("Name") else "(senza nome)"
    
    print("Territorio di test:")
    print("  No: {}".format(terr_no))
    print("  Name: {}".format(terr_name))
    
    # Conta link prima
    total_links = visum.Net.Links.Count
    print("\nLink totali: {}".format(total_links))
    
    # Deseleziona tutto
    visum.Net.Links.SetAllAttValues("Active", 0)
    print("Link deselezionati (Active=0)")
    
    # TEST 1: Passa il numero del territorio
    print("\n" + "=" * 70)
    print("TEST 1: SetTerritoryActive(terr_no) - NUMERO")
    print("=" * 70)
    try:
        visum.Net.SetTerritoryActive(terr_no)
        active_links = visum.Net.Links.GetFilteredSet("[Active] = 1")
        print("SUCCESS! Link attivati: {}".format(active_links.Count))
        return {"method": "numero", "success": True, "count": active_links.Count}
    except Exception as e:
        print("FALLITO: {}".format(str(e)))
        print("Tipo errore: {}".format(type(e).__name__))
        import traceback
        traceback.print_exc()
    
    # Deseleziona di nuovo
    visum.Net.Links.SetAllAttValues("Active", 0)
    
    # TEST 2: Passa l'oggetto territorio
    print("\n" + "=" * 70)
    print("TEST 2: SetTerritoryActive(territory) - OGGETTO")
    print("=" * 70)
    try:
        visum.Net.SetTerritoryActive(terr)
        active_links = visum.Net.Links.GetFilteredSet("[Active] = 1")
        print("SUCCESS! Link attivati: {}".format(active_links.Count))
        return {"method": "oggetto", "success": True, "count": active_links.Count}
    except Exception as e:
        print("FALLITO: {}".format(str(e)))
        print("Tipo errore: {}".format(type(e).__name__))
        import traceback
        traceback.print_exc()
    
    # TEST 3: Prova a convertire in int esplicitamente
    print("\n" + "=" * 70)
    print("TEST 3: SetTerritoryActive(int(terr_no)) - INT ESPLICITO")
    print("=" * 70)
    try:
        visum.Net.SetTerritoryActive(int(terr_no))
        active_links = visum.Net.Links.GetFilteredSet("[Active] = 1")
        print("SUCCESS! Link attivati: {}".format(active_links.Count))
        return {"method": "int esplicito", "success": True, "count": active_links.Count}
    except Exception as e:
        print("FALLITO: {}".format(str(e)))
        print("Tipo errore: {}".format(type(e).__name__))
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("TUTTI I TEST FALLITI")
    print("=" * 70)
    return {"method": None, "success": False, "count": 0}

# Esegui il test
if __name__ == "__main__":
    result = test_setterritoryactive()
    print("\n\nRISULTATO FINALE:")
    print(result)
