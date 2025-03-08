import multiprocessing

# Bind auf alle Interfaces auf Port 8000
bind = "0.0.0.0:8000"

# Anzahl der Worker-Prozesse
workers = multiprocessing.cpu_count() * 2 + 1

# Worker-Klasse
worker_class = "sync"

# Timeout in Sekunden
timeout = 120

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