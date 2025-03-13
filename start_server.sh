#!/bin/bash

# Konfiguration
PORT=8080

# Wechsle in das Verzeichnis des Skripts
cd "$(dirname "$0")"

# Prüfe, ob der Port bereits verwendet wird
if lsof -i :$PORT > /dev/null 2>&1; then
    echo "Port $PORT wird bereits verwendet."
    read -p "Möchten Sie den laufenden Prozess beenden? (j/n): " choice
    if [[ "$choice" =~ ^[jJyY]$ ]]; then
        # Finde den Prozess und beende ihn
        PID=$(lsof -t -i :$PORT)
        if [ -n "$PID" ]; then
            echo "Beende Prozess $PID, der auf Port $PORT läuft..."
            kill -15 $PID
            sleep 1
            # Prüfe, ob der Prozess noch läuft
            if lsof -i :$PORT > /dev/null 2>&1; then
                echo "Prozess reagiert nicht, führe harten Abbruch durch..."
                kill -9 $PID
                sleep 1
            fi
            echo "Prozess auf Port $PORT wurde beendet."
        else
            echo "Konnte keinen Prozess finden, der auf Port $PORT läuft."
            exit 1
        fi
    else
        echo "Server-Start abgebrochen."
        exit 0
    fi
fi

# Ermittle die lokale IP-Adresse
IP_ADDRESS=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -n 1)
if [ -z "$IP_ADDRESS" ]; then
    IP_ADDRESS="localhost"
fi

# Starte den Server
echo "=========================================================="
echo "Starte Dienstplan-Server mit Gunicorn..."
echo "Die Anwendung ist unter folgenden Adressen erreichbar:"
echo "- Lokal:           http://localhost:$PORT"
echo "- Im Netzwerk:     http://$IP_ADDRESS:$PORT"
echo "=========================================================="
echo "Drücke STRG+C zum Beenden"
echo ""

# Setze Umgebungsvariablen
export PORT=$PORT

# Starte Gunicorn
gunicorn --config gunicorn_config.py wsgi:application 