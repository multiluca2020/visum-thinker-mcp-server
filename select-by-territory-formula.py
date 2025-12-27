"""
Selezione spaziale link per territorio usando FORMULE di Visum
invece dell'API COM diretta
"""

def select_links_by_territories_formula(territory_no=1):
    """
    Seleziona link usando formule di Visum per controllare se i nodi
    sono dentro il territorio specificato.
    
    METODO ALTERNATIVO:
    Invece di usare SetTerritoryActive (che da errore COM),
    usiamo formule di Visum per calcolare la membership territoriale.
    
    Args:
        territory_no (int): Numero del territorio (default: 1)
    
    Returns:
        dict: Risultato con numero di link selezionati
    """
    result = {
        "status": "failed",
        "message": "",
        "selected_count": 0
    }
    
    try:
        visum = Visum
        
        print("=" * 70)
        print("SELEZIONE SPAZIALE VIA FORMULE")
        print("=" * 70)
        print("Territorio No: {}".format(territory_no))
        
        # Step 1: Deseleziona tutto
        print("\n1. Deseleziono tutti i link...")
        visum.Net.Links.SetAllAttValues("AddVal1", 0)
        visum.Net.Links.SetAllAttValues("Active", 0)
        
        # Step 2: Prova diverse formule per selezionare link nel territorio
        formulas_to_try = [
            # Formula 1: Entrambi i nodi nel territorio
            "([FromNodeNo\\TerritoryNo] = {0}) & ([ToNodeNo\\TerritoryNo] = {0})".format(territory_no),
            
            # Formula 2: Almeno un nodo nel territorio
            "([FromNodeNo\\TerritoryNo] = {0}) | ([ToNodeNo\\TerritoryNo] = {0})".format(territory_no),
            
            # Formula 3: Link con TypeNo > 0 e nodo From nel territorio
            "([TypeNo] > 0) & ([FromNodeNo\\TerritoryNo] = {0})".format(territory_no),
        ]
        
        for i, formula in enumerate(formulas_to_try, 1):
            print("\n{}. Provo formula {}:".format(i+1, i))
            print("   {}".format(formula))
            
            try:
                selected = visum.Net.Links.GetFilteredSet(formula)
                count = selected.Count
                print("   -> Trovati {} link".format(count))
                
                if count > 0:
                    # Usa questa formula
                    print("\n   SUCCESS! Uso questa formula.")
                    selected.SetAllAttValues("AddVal1", 1)
                    selected.SetAllAttValues("Active", 1)
                    
                    result["status"] = "success"
                    result["message"] = "Selezionati {} link con formula {}".format(count, i)
                    result["selected_count"] = count
                    result["formula"] = formula
                    
                    print("\n" + "=" * 70)
                    print("COMPLETATO: {} link con AddVal1=1".format(count))
                    print("=" * 70)
                    
                    return result
                    
            except Exception as e:
                print("   -> ERRORE: {}".format(str(e)))
                continue
        
        # Se nessuna formula ha funzionato
        result["message"] = "Nessuna formula ha prodotto risultati"
        result["status"] = "warning"
        
        return result
        
    except Exception as e:
        result["message"] = "Errore generale: {}".format(str(e))
        print("\nERRORE: {}".format(result["message"]))
        import traceback
        traceback.print_exc()
        return result


def select_links_simple(territory_no=1):
    """
    Versione SEMPLIFICATA - prova solo l'approccio più diretto
    """
    visum = Visum
    
    print("Selezione link nel territorio No={}...".format(territory_no))
    
    # Deseleziona
    visum.Net.Links.SetAllAttValues("AddVal1", 0)
    
    # Seleziona link dove almeno un nodo è nel territorio
    formula = "([FromNodeNo\\TerritoryNo] = {}) | ([ToNodeNo\\TerritoryNo] = {})".format(
        territory_no, territory_no)
    
    print("Formula: {}".format(formula))
    
    try:
        selected = visum.Net.Links.GetFilteredSet(formula)
        count = selected.Count
        print("Trovati: {} link".format(count))
        
        if count > 0:
            selected.SetAllAttValues("AddVal1", 1)
            print("Copiati in AddVal1=1")
            return {"success": True, "count": count}
        else:
            print("Nessun link trovato - verifica che i nodi abbiano TerritoryNo impostato")
            return {"success": False, "count": 0}
            
    except Exception as e:
        print("ERRORE: {}".format(str(e)))
        import traceback
        traceback.print_exc()
        return {"success": False, "count": 0, "error": str(e)}


# Test veloce
if __name__ == "__main__":
    print("Test 1: Funzione completa")
    print("-" * 70)
    result1 = select_links_by_territories_formula(territory_no=1)
    print("\nRisultato:", result1)
    
    print("\n\n")
    
    print("Test 2: Funzione semplice")
    print("-" * 70)
    result2 = select_links_simple(territory_no=1)
    print("\nRisultato:", result2)
