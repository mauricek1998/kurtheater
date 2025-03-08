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

### Produktionsserver (Gunicorn)

#### Unter Linux/macOS:

```bash
cd dienstplan_flask
./start_server.sh
```

Optional können Sie einen anderen Port angeben:
```bash
./start_server.sh 5000
```

#### Unter Windows:

```bash
cd dienstplan_flask
start_server.bat
```

Der Server ist dann unter folgenden Adressen erreichbar:
- Lokal: http://localhost:8000
- Im lokalen Netzwerk: http://[Ihre-IP-Adresse]:8000

Die genauen URLs werden beim Start des Servers angezeigt.

### Entwicklungsserver (Flask)

```bash
cd dienstplan_flask
python -m flask run --host=0.0.0.0
```

Der Entwicklungsserver ist dann unter http://localhost:5000 und im lokalen Netzwerk unter http://[Ihre-IP-Adresse]:5000 erreichbar.

### Manueller Start mit Gunicorn

```bash
cd dienstplan_flask
gunicorn --config gunicorn_config.py wsgi:application
```

## Anpassung der Servereinstellungen

Die Gunicorn-Konfiguration kann in der Datei `gunicorn_config.py` angepasst werden:

- `bind`: Ändert die IP-Adresse und den Port (Standard: "0.0.0.0:8000")
- `workers`: Anzahl der Worker-Prozesse
- `timeout`: Timeout für Anfragen in Sekunden
- `reload`: Automatisches Neuladen bei Codeänderungen (für Entwicklung)

## Zugriff im lokalen Netzwerk

Die Anwendung ist standardmäßig im lokalen Netzwerk unter der IP-Adresse Ihres Computers erreichbar. Andere Geräte im selben Netzwerk können über einen Browser mit der URL `http://[Ihre-IP-Adresse]:8000` auf die Anwendung zugreifen.

### Firewall-Einstellungen

Falls die Anwendung nicht im Netzwerk erreichbar ist, überprüfen Sie Ihre Firewall-Einstellungen:

- **Windows**: Erlauben Sie eingehende Verbindungen für den Port 8000 in der Windows-Firewall
- **macOS**: Überprüfen Sie die Firewall-Einstellungen in den Systemeinstellungen
- **Linux**: Überprüfen Sie iptables oder ufw-Einstellungen 

# Dienstplan-Server

## Schnellstart

Um den Server zu starten, führen Sie einfach folgendes Kommando aus:

```bash
python start_server.py
```

Das Skript prüft automatisch, ob bereits ein Prozess auf Port 8005 läuft und bietet an, diesen zu beenden, bevor der neue Server gestartet wird.

## Voraussetzungen

Folgende Python-Pakete werden benötigt:

- Flask (und alle anderen Abhängigkeiten der Anwendung)
- gunicorn
- psutil

Installation der Abhängigkeiten:

```bash
pip install gunicorn psutil
```

## Zugriff auf die Anwendung

Nach dem Start ist die Anwendung unter folgenden URLs erreichbar:

- Lokal: http://localhost:8005
- Im Netzwerk: http://[Ihre-IP-Adresse]:8005

## Server beenden

Drücken Sie `STRG+C` im Terminal, um den Server zu beenden.

## Konfiguration

Die Server-Konfiguration kann in folgenden Dateien angepasst werden:

- `start_server.py`: Grundlegende Einstellungen wie Port
- `gunicorn_config.py`: Erweiterte Gunicorn-Konfiguration

## Fehlerbehebung

Falls der Server nicht startet, prüfen Sie:

1. Ob der Port 8005 bereits verwendet wird
2. Ob alle erforderlichen Abhängigkeiten installiert sind
3. Ob die Anwendung selbst korrekt konfiguriert ist 