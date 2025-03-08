#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import signal
import socket
import subprocess
import time
import platform
import psutil

# Konfiguration
PORT = 8005
HOST = "0.0.0.0"  # Auf allen Interfaces lauschen

def get_ip_address():
    """Ermittelt die lokale IP-Adresse des Computers im Netzwerk"""
    try:
        # Erstelle einen temporären Socket, um die lokale IP zu ermitteln
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Google DNS verwenden
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        # Fallback, wenn keine Verbindung möglich ist
        return "localhost"

def is_port_in_use(port):
    """Prüft, ob der angegebene Port bereits verwendet wird"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def find_process_by_port(port):
    """Findet den Prozess, der auf dem angegebenen Port lauscht"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            for conn in proc.connections(kind='inet'):
                if conn.laddr.port == port:
                    return proc
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            pass
    return None

def kill_process_on_port(port):
    """Beendet den Prozess, der auf dem angegebenen Port lauscht"""
    process = find_process_by_port(port)
    if process:
        print(f"Beende Prozess {process.pid} ({process.name()}), der auf Port {port} läuft...")
        try:
            process.terminate()
            # Warte bis zu 5 Sekunden auf Beendigung
            process.wait(5)
        except psutil.TimeoutExpired:
            # Wenn der Prozess nicht reagiert, hart beenden
            print("Prozess reagiert nicht, führe harten Abbruch durch...")
            process.kill()
        return True
    return False

def start_server():
    """Startet den Dienstplan-Server mit Gunicorn"""
    # Wechsle in das Verzeichnis des Skripts
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Setze Umgebungsvariablen
    env = os.environ.copy()
    env["PORT"] = str(PORT)
    
    # Ermittle die lokale IP-Adresse
    ip_address = get_ip_address()
    
    print("=" * 60)
    print("Starte Dienstplan-Server mit Gunicorn...")
    print("Die Anwendung ist unter folgenden Adressen erreichbar:")
    print(f"- Lokal:           http://localhost:{PORT}")
    print(f"- Im Netzwerk:     http://{ip_address}:{PORT}")
    print("=" * 60)
    print("Drücke STRG+C zum Beenden")
    print("")
    
    # Starte Gunicorn mit der Konfigurationsdatei
    try:
        subprocess.run(["gunicorn", "--config", "gunicorn_config.py", "wsgi:application"], env=env)
    except KeyboardInterrupt:
        print("\nServer wird beendet...")
    except FileNotFoundError:
        print("\nFehler: Gunicorn wurde nicht gefunden.")
        print("Bitte installieren Sie Gunicorn mit: pip install gunicorn")
        sys.exit(1)

def main():
    """Hauptfunktion"""
    # Prüfe, ob psutil installiert ist
    try:
        import psutil
    except ImportError:
        print("Das Modul 'psutil' ist nicht installiert.")
        print("Bitte installieren Sie es mit: pip install psutil")
        sys.exit(1)
    
    # Prüfe, ob der Port bereits verwendet wird
    if is_port_in_use(PORT):
        print(f"Port {PORT} wird bereits verwendet.")
        choice = input("Möchten Sie den laufenden Prozess beenden? (j/n): ").lower()
        if choice in ['j', 'ja', 'y', 'yes']:
            if kill_process_on_port(PORT):
                print(f"Prozess auf Port {PORT} wurde beendet.")
                # Kurz warten, damit der Port freigegeben wird
                time.sleep(1)
            else:
                print(f"Konnte keinen Prozess finden, der auf Port {PORT} läuft.")
                print("Bitte beenden Sie den Prozess manuell oder wählen Sie einen anderen Port.")
                sys.exit(1)
        else:
            print("Server-Start abgebrochen.")
            sys.exit(0)
    
    # Starte den Server
    start_server()

if __name__ == "__main__":
    main()
