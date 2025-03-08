#!/bin/bash

# Wechsle in das Verzeichnis des Skripts
cd "$(dirname "$0")"

# Starte Gunicorn mit der Konfigurationsdatei
echo "Starte Dienstplan-Server mit Gunicorn..."
gunicorn --config gunicorn_config.py wsgi:application 