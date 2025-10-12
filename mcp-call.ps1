# MCP Call Helper - Invia comando e termina dopo la risposta
param(
    [Parameter(Mandatory=$true)]
    [string]$Command
)

# Scrivi il comando
$Command | node build/index.js &

# Aspetta 3 secondi per la risposta
Start-Sleep -Seconds 3

# Termina il processo node
Get-Process node -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -eq "" } | Stop-Process -Force
