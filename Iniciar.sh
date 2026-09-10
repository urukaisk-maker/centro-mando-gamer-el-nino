#!/bin/bash
DISCO="$(dirname "$(readlink -f "$0")")"
cd "$DISCO"
pkill -f "server.py" 2>/dev/null
nohup python3 "$DISCO/server.py" > /tmp/elnino_server.log 2>&1 &
sleep 2
xdg-open "http://localhost:8080/01_EL_NINO_LAUNCHER/index.html"
echo "✅ Servidor iniciado en http://localhost:8080"
