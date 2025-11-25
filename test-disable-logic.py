"""
Test della logica di disabilitazione fermate
Simula il comportamento senza Visum per verificare i calcoli
"""

def test_disable_logic():
    print("=" * 70)
    print("TEST LOGICA DISABILITAZIONE FERMATA")
    print("=" * 70)
    
    # Scenario: 3 fermate A, B, C tutte abilitate
    print("\n1) SITUAZIONE INIZIALE (tutte abilitate):")
    print("   Fermata A:")
    print("     Arr:  900")
    print("     Dep: 1000  (StopTime: 100 sec)")
    print("   Fermata B:")
    print("     Arr: 1030  (PreRun da A: 30 sec)")
    print("     Dep: 1090  (StopTime: 60 sec)")
    print("   Fermata C:")
    print("     Arr: 1120  (PostRun da B: 30 sec)")
    print("     Dep: 1180  (StopTime: 60 sec)")
    
    # Disabilitazione di B
    print("\n2) DISABILITAZIONE FERMATA B:")
    print("   a) Visum rimuove TimeProfileItem di B")
    print("      → Visum ricalcola automaticamente Arr(C) togliendo StopTime(B)")
    print("      → Nuovo Arr(C) = 1120 - 60 = 1060")
    
    print("\n   b) Script sottrae offset (PreRun + PostRun = 60 sec) dal PostRunTime di A")
    print("      → Modifica Arr(C) = 1060 - 60 = 1000")
    
    # Calcolo finale
    arr_c_initial = 1120
    stoptime_b = 60
    offset_remove = 60  # 30 PreRun + 30 PostRun
    
    arr_c_after_visum = arr_c_initial - stoptime_b
    arr_c_final = arr_c_after_visum - offset_remove
    
    print("\n3) RISULTATO FINALE:")
    print("   Fermata A:")
    print("     Arr:  900")
    print("     Dep: 1000")
    print("   Fermata B: DISABILITATA")
    print("   Fermata C:")
    print("     Arr: %d  (era 1120 → Visum -60 = 1060 → Script -60 = 1000)" % arr_c_final)
    print("     Dep: 1060  (StopTime: 60 sec)")
    
    # Verifica
    dep_a = 1000
    print("\n4) VERIFICA:")
    print("   Travel time A→C = Arr(C) - Dep(A) = %d - %d = %d sec" % (arr_c_final, dep_a, arr_c_final - dep_a))
    print("   ✓ Se A e C sono adiacenti, questo dovrebbe essere il tempo naturale di viaggio")
    
    # Test con travel time reale
    print("\n5) ESEMPIO CON TRAVEL TIME REALE:")
    print("   Se travel time naturale A→C = 40 sec:")
    travel_time_ac = 40
    arr_c_expected = dep_a + travel_time_ac
    print("   Arr(C) atteso = Dep(A) + Travel = 1000 + 40 = %d" % arr_c_expected)
    print("   Arr(C) effettivo = %d" % arr_c_final)
    
    if arr_c_final == arr_c_expected:
        print("   ✓ CORRETTO!")
    else:
        diff = arr_c_final - arr_c_expected
        print("   ✗ DIFFERENZA: %d sec" % diff)
        if diff == 0:
            print("     → Perfetto per fermate adiacenti senza travel time")
        elif diff > 0:
            print("     → Visum calcolerà il travel time reale A→C")

if __name__ == "__main__":
    test_disable_logic()
    
    print("\n" + "=" * 70)
    print("Per testare con Visum reale:")
    print("  1) Apri Visum Console: Ctrl+P")
    print("  2) exec(open(r'h:\\visum-thinker-mcp-server\\manage-stops-workflow.py').read())")
    print("  3) exec(open(r'h:\\visum-thinker-mcp-server\\disable-stop-2.py').read())")
    print("=" * 70)
