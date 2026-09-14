#!/bin/bash
# ==========================================
#  MODO CINE - EL NIÑO
# ==========================================
# Prepara el PC para ver peliculas o series

echo "========================================"
echo "  MODO CINE - El Nino"
echo "========================================"
echo ""

# Cerrar apps que hacen ruido
echo "1. Cerrando apps..."
pkill -f firefox 2>/dev/null && echo "   Firefox cerrado"
pkill -f chromium 2>/dev/null && echo "   Chromium cerrado"
pkill -f brave 2>/dev/null && echo "   Brave cerrado"
echo "   OK"

# Bajar volumen
echo "2. Ajustando volumen..."
if command -v amixer >/dev/null 2>&1; then
    amixer set Master 60% >/dev/null 2>&1 && echo "   Volumen al 60%"
elif command -v pactl >/dev/null 2>&1; then
    pactl set-sink-volume @DEFAULT_SINK@ 60% >/dev/null 2>&1 && echo "   Volumen al 60%"
fi

# Desactivar salvapantallas
if command -v xset >/dev/null 2>&1; then
    xset s off 2>/dev/null
    xset -dpms 2>/dev/null
    echo "   Salvapantallas desactivado (temporal)"
fi

# Abrir el reproductor preferido
echo "3. Abriendo reproductor..."
ABIERTO=0
if command -v kodi >/dev/null 2>&1; then
    nohup kodi >/dev/null 2>&1 &
    echo "   Kodi abierto"
    ABIERTO=1
elif command -v stremio >/dev/null 2>&1; then
    nohup stremio >/dev/null 2>&1 &
    echo "   Stremio abierto"
    ABIERTO=1
elif command -v vlc >/dev/null 2>&1; then
    nohup vlc >/dev/null 2>&1 &
    echo "   VLC abierto"
    ABIERTO=1
fi

if [ "$ABIERTO" -eq 0 ]; then
    echo "   Ningun reproductor instalado (Kodi, Stremio, VLC)"
    echo "   Puedes instalarlos con: sudo pacman -S vlc"
fi

echo ""
echo "========================================"
echo "  MODO CINE ACTIVADO"
echo "========================================"
echo "Todo listo para ver algo."
