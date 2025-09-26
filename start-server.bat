@echo off
echo Avvio Visum Server in background...
echo.
echo ATTENZIONE: Questo server rimarra' attivo fino a terminazione manuale
echo Usa Ctrl+C nella finestra del server per fermarlo
echo.
start "Visum Server" cmd /k "node visum-server.mjs"
echo Server avviato in finestra separata.
echo Ora puoi usare: node visum-client.mjs per testare
echo.
pause