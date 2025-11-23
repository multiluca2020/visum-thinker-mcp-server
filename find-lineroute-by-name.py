# -*- coding: ascii -*-
"""
Script per vedere TUTTI gli attributi di un LineRoute
Utile per capire come identificare il LineRoute corretto
"""

TARGET_NAME = "R17_2002"

print("=" * 80)
print("RICERCA LINE ROUTE CON NOME: %s" % TARGET_NAME)
print("=" * 80)

try:
    line_routes = Visum.Net.LineRoutes
    print("Totale LineRoutes: %d\n" % line_routes.Count)
    
    # Cerca per LineName
    print("RICERCA PER LineName...")
    found = False
    for lr in line_routes:
        line_name = lr.AttValue("LineName")
        if TARGET_NAME in str(line_name):
            found = True
            print("\nTROVATO! Vediamo tutti gli attributi:")
            print("-" * 80)
            
            # Lista degli attributi da controllare
            attrs_to_check = [
                "Name",
                "LineName",
                "DirectionCode",
                "LineRouteName",
                "Code",
                "No",
                "ID",
                "Length",
                "TravelTime"
            ]
            
            for attr in attrs_to_check:
                try:
                    value = lr.AttValue(attr)
                    print("  %-20s = %s" % (attr, value))
                except:
                    print("  %-20s = (non esiste)" % attr)
            
            print("-" * 80)
            break
    
    if not found:
        print("NON TROVATO con LineName")
        print("\nPrimi 10 LineRoutes per riferimento:")
        print("-" * 80)
        count = 0
        for lr in line_routes:
            if count >= 10:
                break
            try:
                name = lr.AttValue("Name")
                line_name = lr.AttValue("LineName")
                direction = lr.AttValue("DirectionCode")
                print("  LineName: %-20s | Name: %-20s | Dir: %s" % (line_name, name, direction))
                count += 1
            except Exception as e:
                print("  Errore: %s" % e)

except Exception as e:
    print("ERRORE: %s" % str(e))
    import traceback
    traceback.print_exc()
