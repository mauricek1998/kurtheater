# Dienstplan-App

Eine Webanwendung zur Verwaltung von Dienstplänen für das Kurtheater.

## Installation

1. Abhängigkeiten installieren:
```bash
pip install -r requirements.txt
```

2. Konfiguration anpassen (optional):
   - Bearbeiten Sie `config.py` für allgemeine Einstellungen
   - Bearbeiten Sie `gunicorn_config.py` für Server-Einstellungen

## Server starten

### Entwicklungsserver (Flask)

```bash
cd dienstplan_flask
python -m flask run
```

### Produktionsserver (Gunicorn)

#### Mit Startskript:

```bash
cd dienstplan_flask
./start_server.sh
```

#### Manuell:

```bash
cd dienstplan_flask
gunicorn --config gunicorn_config.py wsgi:application
```

Der Server ist dann unter http://localhost:8000 erreichbar.

## Anpassung der Servereinstellungen

Die Gunicorn-Konfiguration kann in der Datei `gunicorn_config.py` angepasst werden:

- `bind`: Ändert die IP-Adresse und den Port (Standard: "0.0.0.0:8000")
- `workers`: Anzahl der Worker-Prozesse
- `timeout`: Timeout für Anfragen in Sekunden
- `reload`: Automatisches Neuladen bei Codeänderungen (für Entwicklung) 