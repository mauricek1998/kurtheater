#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gunicorn-Konfigurationsdatei für den Dienstplan-Server
"""

import multiprocessing
import os

# Bind auf alle Interfaces, damit die App im lokalen Netzwerk erreichbar ist
# Verwende den PORT aus Umgebungsvariablen oder Standard-Port 8005
port = os.environ.get('PORT', '8005')
bind = f"0.0.0.0:{port}"

# Anzahl der Worker-Prozesse
workers = multiprocessing.cpu_count() * 2 + 1

# Worker-Klasse
worker_class = "sync"
threads = 2

# Timeout in Sekunden
timeout = 120
keepalive = 5

# Maximale Anzahl gleichzeitiger Clients
max_requests = 1000

# Automatischer Neustart nach max_requests Anfragen
max_requests_jitter = 50

# Logging
accesslog = "-"  # Ausgabe auf stdout
errorlog = "-"   # Ausgabe auf stderr
loglevel = "info"

# Prozess-Name
proc_name = "dienstplan_app"

# Aktiviere Debugging-Funktionen
reload = True  # Automatisches Neuladen bei Codeänderungen

# Sicherheitseinstellungen
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# Logging-Konfiguration
accesslog = '-'  # Ausgabe auf stdout
errorlog = '-'   # Ausgabe auf stderr
loglevel = 'info'

# Reload bei Codeänderungen (nur für Entwicklung)
reload = True  # Automatisches Neuladen bei Codeänderungen 