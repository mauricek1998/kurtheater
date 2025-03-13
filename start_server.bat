@echo off
setlocal

REM Definiere den Port
set PORT=8005

REM Zeige die lokale IP-Adresse an
echo Ermittle lokale IP-Adresse...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /r "IPv4.*[0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*"') do (
    set IP=%%a
    goto :found_ip
)

:found_ip
set IP=%IP:~1%

if "%IP%"=="" (
    echo Konnte keine lokale IP-Adresse ermitteln. Verwende localhost.
    set IP=localhost
)

echo ==========================================================
echo Starte Dienstplan-Server mit Gunicorn...
echo Die Anwendung ist unter folgenden Adressen erreichbar:
echo - Lokal:           http://localhost:%PORT%
echo - Im Netzwerk:     http://%IP%:%PORT%
echo ==========================================================
echo Drücke STRG+C zum Beenden

REM Starte Gunicorn mit der Konfigurationsdatei
python -m gunicorn.app.wsgiapp --config gunicorn_config.py wsgi:application

endlocal 