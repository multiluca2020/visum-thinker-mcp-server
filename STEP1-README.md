# STEP 1 - Versione Base Funzionante

**Data:** 2025-11-23

## File
`enable-stop-STEP1-WORKING.py`

## Funzionalità
✅ Abilita/disabilita fermate sul LineRoute  
✅ Calcola tempi corretti con interpolazione basata su distanze  
✅ Crea TimeProfileItem con Arr/Dep corretti  
✅ PreRunTime calcolato correttamente (~79 sec per fermata 370)  

## Sequenza Corretta
1. Imposta `IsRoutePoint=True` sul LineRouteItem
2. **Rilegge `AccumLength`** (aggiornato dopo abilitazione)
3. Calcola `PreRunTime` con proporzione: `(dist_prev_curr / dist_total) × time_total`
4. Calcola `Arr = Dep(prev) + PreRunTime` e `Dep = Arr + StopTime`
5. Crea `TimeProfileItem` con `tp.AddTimeProfileItem()`
6. Imposta `Arr` e `Dep` sul TimeProfileItem

## Formula Chiave
```
PreRunTime = (AccumLength(curr) - AccumLength(prev)) / (AccumLength(next) - AccumLength(prev)) × (Arr(next) - Dep(prev))
```

## Configurazione
```python
OPERATIONS = {
    370: {
        "action": "enable",
        "stop_time": 60  # secondi
    }
}
```

## Prossimi Sviluppi
- [ ] Gestione multipla fermate
- [ ] Aggiunta offset PreRun/PostRun personalizzati
- [ ] Supporto disable con ricalcolo tempi fermate adiacenti
- [ ] Validazione e error handling
