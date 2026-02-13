#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Lista tutti i demand segments PRT disponibili nel progetto
"""

print("\n" + "=" * 70)
print("DEMAND SEGMENTS PRT NEL PROGETTO")
print("=" * 70)

try:
    # Lista tutti i demand segments
    all_segments = Visum.Net.DemandSegments.GetAll
    
    print("\nTotale demand segments: {}".format(len(all_segments)))
    
    # Filtra quelli PRT (con MODE = C, H, M per CAR, HGV, MOTO)
    prt_segments = []
    segments_by_mode = {}
    
    print("\n{:<30} {:<10} {:<15}".format("CODE", "MODE", "TSYS"))
    print("-" * 70)
    
    for seg in all_segments:
        code = seg.AttValue("CODE")
        mode = seg.AttValue("MODE")
        
        # Cerca TSys associato
        tsys = ""
        try:
            tsys = seg.AttValue("TSYS")
        except:
            try:
                tsys = seg.AttValue("TSYSCODE")
            except:
                pass
        
        # Filtra per modi PRT (C=CAR, H=HGV, M=MOTO)
        if mode in ["C", "H", "M"]:
            prt_segments.append(code)
            
            if mode not in segments_by_mode:
                segments_by_mode[mode] = []
            segments_by_mode[mode].append(code)
            
            print("{:<30} {:<10} {:<15}".format(code, mode, tsys))
    
    print("\n" + "=" * 70)
    print("RIEPILOGO PER MODO")
    print("=" * 70)
    
    for mode, segs in sorted(segments_by_mode.items()):
        print("\nModo '{}': {} segments".format(mode, len(segs)))
        dsegset = ",".join(segs)
        print("  DSEGSET: {}".format(dsegset))
    
    # Tutti i segments PRT
    print("\n" + "=" * 70)
    print("TUTTI I SEGMENTS PRT (per DSEGSET)")
    print("=" * 70)
    all_prt_dsegset = ",".join(prt_segments)
    print("\n{}".format(all_prt_dsegset))
    print("\nTotale: {} segments".format(len(prt_segments)))
    
except Exception as e:
    print("\n✗ ERRORE: {}".format(str(e)))
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
