#!/bin/bash
# ==========================================
#  DETENER CENTRO DE MANDO GAMER - EL NINO
# ==========================================

echo 'Deteniendo Centro de Mando...'

# Intentar parar el servicio systemd
if systemctl --user is-active elnino.service >/dev/null 2>&1; then
    systemctl --user stop elnino.service 2>/dev/null
    echo 'Servicio systemd detenido'
fi

# Matar cualquier proceso residual
if pgrep -f server.py >/dev/null 2>&1; then
    pkill -f server.py 2>/dev/null
    sleep 1
    echo 'Servidor detenido'
else
    echo 'No habia servidor corriendo'
fi

echo 'Listo.'
exit 0
