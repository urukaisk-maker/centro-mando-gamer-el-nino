#!/bin/bash
# ==========================================
#  INICIAR CENTRO DE MANDO GAMER - EL NINO
# ==========================================

# Ir siempre al directorio del script
cd "$(dirname "$(readlink -f "$0")")" || exit 1
DISCO="$(pwd)"

echo "========================================"
echo "  Centro de Mando Gamer - El Nino"
echo "========================================"

# Verificar que existe el servidor
if [ ! -f "$DISCO/server.py" ]; then
    echo "ERROR: no encuentro server.py en $DISCO"
    exit 1
fi

# Buscar Python con prioridades
PYTHON=""
for p in python3 python python3.12 python3.11; do
    if command -v "$p" >/dev/null 2>&1; then
        PYTHON="$p"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    echo "ERROR: Python 3 no esta instalado"
    echo "Instalalo con: sudo pacman -S python"
    exit 1
fi

echo "Python detectado: $PYTHON"

# Matar servidor anterior
pkill -f "server.py" 2>/dev/null
sleep 1

# Intentar con systemd primero
SERVICIO_OK=0
if systemctl --user list-unit-files 2>/dev/null | grep -q elnino.service; then
    systemctl --user restart elnino.service 2>/dev/null
    sleep 2
    if curl -s -o /dev/null --max-time 2 http://localhost:8080/01_EL_NINO_LAUNCHER/index.html; then
        SERVICIO_OK=1
        echo "Servidor arrancado via systemd"
    fi
fi

# Si systemd no funciona, arrancar directamente
if [ "$SERVICIO_OK" -eq 0 ]; then
    echo "Arrancando servidor manualmente..."
    nohup "$PYTHON" "$DISCO/server.py" > /tmp/elnino_server.log 2>&1 &
    sleep 2

    if ! curl -s -o /dev/null --max-time 2 http://localhost:8080/01_EL_NINO_LAUNCHER/index.html; then
        echo "ERROR: el servidor no responde"
        echo "Revisa el log: cat /tmp/elnino_server.log"
        exit 1
    fi
fi

# Abrir navegador
URL="http://localhost:8080/01_EL_NINO_LAUNCHER/index.html"
echo "Servidor listo en $URL"

if command -v brave >/dev/null 2>&1; then
    nohup brave "$URL" >/dev/null 2>&1 &
elif command -v chromium >/dev/null 2>&1; then
    nohup chromium "$URL" >/dev/null 2>&1 &
elif command -v firefox >/dev/null 2>&1; then
    nohup firefox "$URL" >/dev/null 2>&1 &
else
    xdg-open "$URL" >/dev/null 2>&1 &
fi

echo "========================================"
echo "  Listo. Disfruta, Mario."
echo "========================================"
exit 0
