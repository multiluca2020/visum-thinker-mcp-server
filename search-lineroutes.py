# -*- coding: ascii -*-
"""
Cerca tutti i LineRoutes che contengono R17
"""

SEARCH_TEXT = "R17"

print("=" * 80)
print("RICERCA LINEROUTES CHE CONTENGONO: %s" % SEARCH_TEXT)
print("=" * 80)

try:
    line_routes = Visum.Net.LineRoutes
    print("Totale LineRoutes nel network: %d\n" % line_routes.Count)
    
    matches = []
    for lr in line_routes:
        name = lr.AttValue("Name")
        line_name = lr.AttValue("LineName")
        
        if SEARCH_TEXT in str(name) or SEARCH_TEXT in str(line_name):
            matches.append({
                'Name': name,
                'LineName': line_name,
                'DirectionCode': lr.AttValue("DirectionCode")
            })
    
    print("Trovati %d LineRoutes:" % len(matches))
    print("-" * 80)
    print("%-30s | %-20s | %-10s" % ("Name", "LineName", "Direction"))
    print("-" * 80)
    
    for m in matches:
        print("%-30s | %-20s | %-10s" % (m['Name'], m['LineName'], m['DirectionCode']))
    
    if len(matches) == 0:
        print("\nNessun LineRoute trovato con '%s'" % SEARCH_TEXT)
        print("\nProva a cercare altri pattern. Esempi visti:")
        print("  R32, R32_1, R33, R33_1, R3_3, R3_5, R6, etc.")

except Exception as e:
    print("ERRORE: %s" % str(e))
    import traceback
    traceback.print_exc()
