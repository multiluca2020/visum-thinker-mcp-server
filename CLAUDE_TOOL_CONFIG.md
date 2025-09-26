# Claude MCP Tool Configuration

## ⚠️ IMPORTANTE - TOOL PREDEFINITO PER PROGETTI VISUM

### 🚀 SEMPRE USA QUESTO TOOL:
**`project_open`** - Per aprire/caricare/lanciare qualsiasi progetto Visum

### ❌ NON USARE MAI:
- `visum_launch_project` (DEPRECATED - obsoleto e lento)
- `project_start_instance` (uso specifico, non per apertura progetti)

## 📋 Istruzioni per Claude:

### Quando l'utente dice:
- "apri il progetto Campoleone"
- "carica il progetto"
- "lancia Visum con il progetto"
- "esegui il progetto"
- "avvia il progetto"

### 🎯 SEMPRE USARE:
```json
{
  "name": "project_open",
  "arguments": {
    "projectPath": "[PATH_COMPLETO_PROGETTO]"
  }
}
```

## 📍 Progetti Comuni:
- **Campoleone**: `H:\go\italferr2025\Campoleone\100625_Versione_base_v0.3_sub_ok_priv.ver`

## ✅ Comportamento Atteso:
1. Tool `project_open` risponde immediatamente
2. Server TCP si avvia (porta 7901+)
3. Progetto si carica in background (~30 secondi per Campoleone)
4. Claude riceve conferma con dettagli server TCP

## ⚡ Performance:
- Risposta MCP: < 1 secondo
- Caricamento Campoleone: ~30 secondi (normale per 196MB)
- Server TCP: Pronto per comandi ultra-veloci

## 🔄 Tool di Supporto Dopo Apertura:
- `project_execute_analysis` - Analisi veloci
- `project_health_check` - Stato server
- `project_instances_status` - Vista server attivi